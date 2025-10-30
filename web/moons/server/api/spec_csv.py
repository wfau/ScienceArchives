import io
import numpy as np
from astropy.io import fits
import astropy.units as u


# Input FITS path (yours)
# path = "/moons-flatfiles/products/ges/giraffe/stacked_v5.00/GES_MW_00_01/gir_00000014-6003143_H548.8.fit"
path = '/Users/amy/MOONS/development/data/GES_MW_00_01/gir_00000014-6003143_H548.8.fit'

def wavelength_axis(hdr, npix):
    """Build a 1D wavelength axis from FITS WCS (linear). Returns numpy array in Angstrom."""
    crpix = hdr.get("CRPIX1", 1.0)
    crval = hdr.get("CRVAL1")
    cdelt = hdr.get("CD1_1", hdr.get("CDELT1"))
    if crval is None or cdelt is None:
        raise ValueError("Missing CRVAL1 or CD1_1/CDELT1 in header.")
    # Pixel indices (FITS is 1-based)
    pix = np.arange(npix, dtype=float) + 1.0
    x = crval + (pix - crpix) * cdelt

    # Units and possible log encoding (not your case, but handled)
    ctype = (hdr.get("CTYPE1", "") or "").upper()
    cunit = hdr.get("CUNIT1", "Angstrom")
    try:
        unit = u.Unit(cunit)
    except Exception:
        unit = u.AA

    if "LOG" in ctype:
        lam = (10.0 ** x) * unit
    else:
        lam = x * unit

    # Normalize to Angstrom for output
    lam = lam.to(u.AA)
    return lam.value  # plain numpy array (Angstrom)

def sigma_from_ivar(ivar):
    """Compute 1-sigma uncertainty from inverse variance."""
    iv = np.array(ivar, dtype=float)
    sig = np.full_like(iv, np.nan, dtype=float)
    good = np.isfinite(iv) & (iv > 0)
    sig[good] = 1.0 / np.sqrt(iv[good])
    return sig

def get_csv(path):
    with fits.open(path, memmap=True) as hdul:
        print(f'open file {path}', flush=True)
        # Final spectrum and its inverse variance
        h_flux = hdul[0]   # final_spectrum (PrimaryHDU)
        h_ivar = hdul[1]   # final_ivar

        flux = np.array(h_flux.data, dtype=float)
        ivar = np.array(h_ivar.data, dtype=float)
        lam = wavelength_axis(h_flux.header, flux.size)  # Angstrom

        sigma = sigma_from_ivar(ivar)

        # Labels
        ctype = (h_flux.header.get("CTYPE1", "") or "").upper()
        air_tag = " (air)" if ctype.startswith("AWAV") else ""
        # Flux unit for y-label (values are already in this unit)
        bunit = h_flux.header.get("BUNIT", None)

        good = np.isfinite(sigma)
        f = io.StringIO()
        if np.any(good):
            flux_col = "flux" if not bunit else f"flux[{bunit}]"
            header = ",".join(["wavelength_Angstrom" + ("_air" if air_tag else ""), flux_col])
            data = np.column_stack([lam[good], (flux - sigma)[good], flux[good], (flux + sigma)[good]])
            f.write(header)
            f.write('\n')
            for r in data:
                # write special format for custom high/low bands
                f.write(f'{r[0]},{r[1]:.10g};{r[2]:.10g};{r[3]:.10g}\n')
            # np.savetxt(f, data, delimiter=",", header=header, comments="", fmt="%.10g")
        return f.getvalue()
