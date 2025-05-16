--=============================================================================
--
-- $Id: GES_CurationLogsSchema.sql 632 2017-07-21 11:00:11Z EckhardSutorius $
--
-- Database schema file containing SQL to create the GES curation tables.
--
-- Original author: 
--   Clive Davenhall, Information Services, University of Edinburgh.
--
--=============================================================================
--
-- USE GES
--GO
--
-- ---------------------------------------------------------------------------- 


-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='LineList') DROP TABLE LineList
CREATE TABLE GES.LineList(
-------------------------------------------------------------------------------
--/H Table to hold all the line data used in the analysis of spectra.
--
--/T A simple table to hold all the atomic and molecular line data used in the
--/T astrophysical analysis of spectra.  All spectroscopic analyses within
--/T the GES Survey use these atomic data.
--/T 
--/T The contents of this table are more full documented in 'Line-lists
--/T for the Gaia-ESO Survey', version 5 (for the molecular line data) and 
--/T version 6 (for the atomic line data), produced by the GES line-list
--/T group, see:
--/T
--/T <a href="http://ges.roe.ac.uk/docs/GES_linelist_v5_report.pdf">Line-lists for the Gaia-ESO Survey (v5)</a>
--/T <a href="http://ges.roe.ac.uk/docs/GES_linelist_v6_report.pdf">Line-lists for the Gaia-ESO Survey (v6)</a>
--/T   
--/T Note that this report describes FITS files containing the atomic data,
--/T not the database table available here.  The table contains exactly the
--/T same data, but obviously the FITS-specific parts of the document are not
--/T relevant.
--/T
--/T Also, for convenience the Line-list group has prepared a
--/T <a href="http://ges.roe.ac.uk/docs/v5.bib">Bibtex file</a>
--/T containing all the references listed in the report and included as
--/T reference columns in the table (these columns have names of the form
--/T <i>something</i>Ref).
--/T
--/T Required constraints: primary key is (lineID)
-------------------------------------------------------------------------------
lineID       bigint not null default -99999999,    --/D Line identifier: unique identifier for each line.
name1        varchar(6) not null default '--',     --/D Name, first line: chemical symbol for element.   --/F NAME  --/A 1
name2        varchar(6) not null default '--',     --/D Name, second line.  --/F NAME  --/A 2
name3        varchar(6) not null default '--',     --/D Name third line.   --/F NAME  --/A 3
ion          INTEGER not null default -99999999,       --/D Ionisation stage of atom or molecule, eg. 1  --/F ION
isotope1     bigint not null default -99999999,    --/D Isotope information for element (0 if only one isotope present).  --/F ISOTOPE  --/A 1
isotope2     bigint not null default -99999999,    --/D Isotope information for element (0 if only one isotope present).  --/F ISOTOPE  --/A 2
isotope3     bigint not null default -99999999,    --/D Isotope information for element (0 if only one isotope present).  --/F ISOTOPE  --/A 3
lambda       float not null default -9.999995e+08, --/D Wavelength  --/U Angstrom --/F LAMBDA
lambdaRef    varchar(8) not null default 'NONE',   --/D Reference for column lambda.  --/F LAMBDA_REF
loggf        real not null default -9.999995e+08,  --/D Logarithm of gf-value.  --/F LOG_GF
loggfErr     real not null default -9.999995e+08,  --/D Experimental error in column logGf (if applicable).  --/F LOG_GF_ERR
loggfRef     varchar(64) not null default 'NONE',  --/D Reference for column logGf. --/F LOG_GF_REF
loggfFlag    varchar(1) not null default '-',      --/D Flag: relative quality of column logGf: Y - recommended; U - undecided (maybe); N - not recommended.  --/F LOG_GF_FLAG
labelLow     varchar(128) not null default 'NONE', --/D Lower level electron configuration.  --/F LABEL_LOW
labelUp      varchar(128) not null default 'NONE', --/D Upper level electron configuration.  --/F LABEL_UP
eLow         real not null default -9.999995e+08,  --/D Lower energy level.  --/U eV  --/F E_LOW
eLowRef      varchar(8) not null default 'NONE',   --/D Reference for column eLow  --/F E_LOW_REF
jLow         real not null default -9.999995e+08,  --/D Lower level J-value.  --/F J_LOW
eUp          real not null default -9.999995e+08,  --/D Upper energy level  --/U eV  --/F E_UP
eUpRef       varchar(8) not null default 'NONE',   --/D Reference for column eUp --/F E_UP_REF
jUp          real not null default -9.999995e+08,  --/D Upper level J-value.   --/F J_UP
landeLow     real not null default -9.999995e+08,  --/D Lower level Lande factor.  --/F LANDE_LOW
landeUp      real not null default -9.999995e+08,  --/D Upper level Lande factor.  --/F LANDE_UP
landeMean    real not null default -9.999995e+08,  --/D Mean Lande factor.  --/F LANDE_MEAN
landeRef     varchar(8) not null default 'NONE',   --/D Reference for Lande factors (columns landeLow, landeUp and landeMean). --/F LANDE_REF
radDamp      real not null default -9.999995e+08,  --/D Radiation damping (log(FWHM)).  --/U rad/s  --/F RAD_DAMP
radDampRef   varchar(8) not null default 'NONE',   --/D Reference for column radDamp.  --/F RAD_DAMP_REF
starkDamp    real not null default -9.999995e+08,  --/D Stark broadening per perturber at 10,000 K (log(FWHM).   --/U rad/s  --/F STARK_DAMP
starkDampRef varchar(8) not null default 'NONE',   --/D Reference for column starkDamp.  --/F STARK_DAMP_REF
vdwDamp      real not null default -9.999995e+08,  --/D >0: Broadening by HI, INTEGER(sigma), alpha ABO theory; <0: Van der Waals broad. per perturber at 10,000 K  (log(FWHM). --/U rad/s/cm**3 --/F VDW_DAMP
vdwDampRef   varchar(8) not null default 'NONE',   --/D Reference for column vdwDamp  --/F VDW_DAMP_REF
depth        real not null default -9.999995e+08,  --/D Central line depth in Arcturus.  --/F DEPTH
synFlag      varchar(1) not null default '-',      --/D Blending quality for synthesis: Y - relatively unblended; U - maybe useful for some stars; N - badly blended and not recommended.  --/F SYN_FLAG
ewFlag1      real not null default -9.999995e+08,  --/D Usefulness for EW analysis.  --/F EW_FLAG  --/A 1
ewFlag2      real not null default -9.999995e+08,  --/D Usefulness for EW analysis.  --/F EW_FLAG  --/A 2
ewFlag3      real not null default -9.999995e+08,  --/D Usefulness for EW analysis.  --/F EW_FLAG  --/A 3
ewFlag4      real not null default -9.999995e+08,  --/D Usefulness for EW analysis.  --/F EW_FLAG  --/A 4
lType        SMALLINT not null default 0,           --/D Line type: <table border="1" class='v'> <tr> <th>ltype</th> <th>Description</th> </tr> <tr> <td>1</td> <td>Molecular lines only.</td> </tr> <tr> <td>2</td> <td>Atomic lines including data for unresolved fine, hyper-fine or isotopic splitting, if present.</td> </tr> <tr> <td>3</td> <td>Atomic lines excluding data for unresolved fine, hyper-fine or isotopic splitting.</td> </tr> </table>
deprecated   SMALLINT not null default 0,           --/D Deprecation code: a value other than 0 means the data are deprecated and should not be used  --/N 0
CONSTRAINT pk_LineList PRIMARY KEY (lineID)
);

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='Target') DROP TABLE Target
CREATE TABLE GES.Target(
-------------------------------------------------------------------------------
--/H The Target table contains the master target list of stars observed in the GES survey.
--
--/T The Target table is the master target list of stars observed in the GES
--/T survey.  For each star, in addition to the identifier and celestial
--/T coordinates, some summary parameters derived from analysis of the spectra
--/T are included for convenience.
--/T
--/T The target list was defined by the GES Consortium.
--
--/T Required constraints: primary key is (targetID)
-------------------------------------------------------------------------------
targetID   bigint not null default -99999999,     --/D Unique ID for each target object
esoName    varchar(32) not null default 'NONE',   --/D ESO name of target object; used to name FITS file --/F PHOTOM.OBJECT 
cName      varchar(16) not null default 'NONE',   --/D Unique Gaia-ESO Survey object name formed from the coordinates of the object (can be used in place of object to give a unique name) --/F PHOTOM.Cname
ra         float  not null default -9.999995e+08, --/D RA of object (J2000; decimal degrees) --/U degrees --/F PHOTOM.RA
dec        float  not null default -9.999995e+08, --/D Dec of object (J2000; decimal degrees) --/U degrees --/F PHOTOM.DEC
htmID      bigint not null default -99999999,     --/D Hierarchical Triangular Mesh (20-deep) number, mainly useful internally for indexing on position  --/Q ra,dec  --/C POS_GENERAL  --/L 20 
cx         float  not null default -9.999995e+08, --/D Cartesian x of unit (RA, Dec) vector on celestial sphere  --/Q ra,dec
cy         float  not null default -9.999995e+08, --/D Cartesian y of unit (RA, Dec) vector on celestial sphere  --/Q ra,dec
cz         float  not null default -9.999995e+08, --/D Cartesian z of unit (RA, Dec) vector on celestial sphere  --/Q ra,dec
gl         float  not null default -9.999995e+08, --/D Galactic longitude  --/U degrees  --/Q ra,dec
gb         float  not null default -9.999995e+08, --/D Galactic latitude   --/U degrees  --/Q ra,dec
--
-- Add additional columns for basic parameters and summary/best derived parameters as required.
-- A few are included as examples.
--
--vr           real not null default -9.999995e+08,  --/D Heliocentric radial velocity  --/U Km/sec  --/N -9.999995e+08
--Te           real not null default -9.999995e+08,  --/D Effective temperature  --/U Kelvin  --/N -9.999995e+08
--surfaceGravity real not null default -9.999995e+08,      --/D Surface Gravity  --/U m/sec**2  --/N -9.999995e+08
--specClass    varchar(10) not null default 'NONE',  --/D Spectral classification  --/N NONE
--metal        real not null default -9.999995e+08,  --/D Metallicity  --/N -9.999995e+08
jMag         real not null default -9.999995e+08,  --/D VISTA VHS or VVV J magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.j_vista
jMagErr      real not null default -9.999995e+08,  --/D VISTA VHS or VVV J magnitude error --/U mag  --/N -9.999995e+08  --/F PHOTOM.j_vista_err
hMag         real not null default -9.999995e+08,  --/D VISTA VHS or VVV H magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.h_vista
hMagErr      real not null default -9.999995e+08,  --/D VISTA VHS or VVV H magnitude error --/U mag  --/N -9.999995e+08  --/F PHOTOM.h_vista_err
ksMag        real not null default -9.999995e+08,  --/D VISTA VHS or VVV Ks magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.k_vista
ksMagErr     real not null default -9.999995e+08,  --/D VISTA VHS or VVV Ks magnitude error --/U mag  --/N -9.999995e+08  --/F PHOTOM.k_vista_err
distVISTA    real not null default -9.999995e+08,  --/D VISTA VHS or VVV source separation distance from GES target  --/U arcsec  --/F PHOTOM.dist_vista
jMag2mass    real not null default -9.999995e+08,  --/D 2MASS J magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.j_2mass
jMag2massErr real not null default -9.999995e+08,  --/D 2MASS J magnitude error --/U mag  --/N -9.999995e+08  --/F PHOTOM.j_2mass_err
hMag2mass    real not null default -9.999995e+08,  --/D 2MASS H magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.h_2mass
hMag2massErr real not null default -9.999995e+08,  --/D 2MASS H magnitude error --/U mag  --/N -9.999995e+08  --/F PHOTOM.h_2mass_err
kMag2mass    real not null default -9.999995e+08,  --/D 2MASS K magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.k_2mass
kMag2massErr real not null default -9.999995e+08,  --/D 2MASS K magnitude error --/U mag  --/N -9.999995e+08  --/F PHOTOM.k_2mass_err
dist2mass    real not null default -9.999995e+08,  --/D 2MASS source separation distance from GES target  --/U arcsec  --/F PHOTOM.dist_2mass
--
-- The following columns contain magnitudes and separations from other surveys.
-- They were added following a request from Anna (message 13/5/14)/8/14.
--
jMagUkidss    real not null default -9.999995e+08,  --/D UKIDSS j magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.j_ukidss
jMagUkidssErr real not null default -9.999995e+08,  --/D Error on UKIDSS j magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.j_ukidss_err
hMagUkidss    real not null default -9.999995e+08,  --/D UKIDSS h magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.h_ukidss
hMagUkidssErr real not null default -9.999995e+08,  --/D Error on UKIDSS h magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.h_ukidss_err
kMagUkidss    real not null default -9.999995e+08,  --/D UKIDSS k magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.k_ukidss
kMagUkidssErr real not null default -9.999995e+08,  --/D Error on UKIDSS k magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.k_ukidss_err	
distUkidss    real not null default -9.999995e+08,  --/D Separation between UKIDSS and GES coordinates  --/U arcsec  --/N -9.999995e+08  --/F PHOTOM.dist_ukidss
uMagSdss      real not null default -9.999995e+08,  --/D SDSS u magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.u_sdss
uMagSdssErr   real not null default -9.999995e+08,  --/D Error on SDSS u magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.u_sdss_err
gMagSdss      real not null default -9.999995e+08,  --/D SDSS g magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.g_sdss
gMagSdssErr   real not null default -9.999995e+08,  --/D Error on SDSS g magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.g_sdss_err
rMagSdss      real not null default -9.999995e+08,  --/D SDSS r magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.r_sdss
rMagSdssErr   real not null default -9.999995e+08,  --/D Error on SDSS r magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.r_sdss_err
iMagSdss      real not null default -9.999995e+08,  --/D SDSS i magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.i_sdss
iMagSdssErr   real not null default -9.999995e+08,  --/D Error on SDSS i magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.i_sdss_err
zMagSdss      real not null default -9.999995e+08,  --/D SDSS z magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.z_sdss
zMagSdssErr   real not null default -9.999995e+08,  --/D Error on SDSS z magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.z_sdss_err
distSdss      real not null default -9.999995e+08,  --/D Separation between SDSS and GES coordinates --/U arcsec  --/N -9.999995e+08  --/F PHOTOM.dist_sdss
vMagApass     real not null default -9.999995e+08,  --/D APASS v magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.v_apass
vMagApassErr  real not null default -9.999995e+08,  --/D Error on APASS v magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.v_apass_err
bMagApass     real not null default -9.999995e+08,  --/D APASS b magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.b_apass
bMagApassErr  real not null default -9.999995e+08,  --/D Error on APASS b magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.b_apass_err
gMagApass     real not null default -9.999995e+08,  --/D APASS g magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.g_apass
gMagApassErr  real not null default -9.999995e+08,  --/D Error on APASS g magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.g_apass_err
rMagApass     real not null default -9.999995e+08,  --/D APASS r magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.r_apass
rMagApassErr  real not null default -9.999995e+08,  --/D Error on APASS r magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.r_apass_err
iMagApass     real not null default -9.999995e+08,  --/D APASS i magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.i_apass
iMagApassErr  real not null default -9.999995e+08,  --/D Error on APASS i magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.i_apass_err
distApass     real not null default -9.999995e+08,  --/D Separation between APASS and GES coordinates --/U arcsec  --/N -9.999995e+08  --/F PHOTOM.dist_apass
-- 
uMag         real not null default -9.999995e+08,  --/D Johnson U magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.umag
--uMagErr      real not null default -9.999995e+08,  --/D Error on Johnson U magnitude --/U mag  --/N -9.999995e+08
bMag         real not null default -9.999995e+08,  --/D Johnson B magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.bmag
--bMagErr      real not null default -9.999995e+08,  --/D Error on Johnson B magnitude --/U mag  --/N -9.999995e+08
vMag         real not null default -9.999995e+08,  --/D Johnson V magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.vmag
--vMagErr      real not null default -9.999995e+08,  --/D Error on Johnson V magnitude --/U mag  --/N -9.999995e+08
rMag         real not null default -9.999995e+08,  --/D R magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.rmag
--rMagErr      real not null default -9.999995e+08,  --/D Error on R magnitude --/U mag  --/N -9.999995e+08
iMag         real not null default -9.999995e+08,  --/D I magnitude --/U mag  --/N -9.999995e+08  --/F PHOTOM.imag
--iMagErr      real not null default -9.999995e+08,  --/D Error on I magnitude --/U mag  --/N -9.999995e+08
eBV           real not null default -9.999995e+08,  --/D The galactic dust extinction value (Schlegel SFD98) --/U mag  --/N -9.999995e+08  --/F PHOTOM.EB_V
pmRaPpmxl     real not null default -9.999995e+08,  --/D PPMXL proper motion in ra  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmra_ppmxl
pmRaErrPpmxl  real not null default -9.999995e+08,  --/D Error on PPMXL proper motion in ra  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmra_ppmxl_err
pmDecPpmxl    real not null default -9.999995e+08,  --/D PPMXL proper motion in dec  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmdec_ppmxl
pmDecErrPpmxl real not null default -9.999995e+08,  --/D Error on PPMXL proper motion in dec  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmdec_ppmxl_err
distPpmxl     real not null default -9.999995e+08,  --/D PPMXL source separation distance from GES target  --/U arcsec  --/N -9.999995e+08  --/F PHOTOM.dist_ppmxl
pmRaUcac      real not null default -9.999995e+08,  --/D UCAC proper motion in ra  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmra_ucac
pmRaErrUcac   real not null default -9.999995e+08,  --/D Error on UCAC proper motion in ra  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmra_ucac_err
pmDecUcac     real not null default -9.999995e+08,  --/D UCAC proper motion in dec  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmdec_ucac
pmDecErrUcac  real not null default -9.999995e+08,  --/D Error on UCAC proper motion in dec  --/U marcsec/yr  --/N -9.999995e+08  --/F PHOTOM.pmdec_ucac_err
distUcac      real not null default -9.999995e+08,  --/D UCAC source separation distance from GES target  --/U arcsec  --/N -9.999995e+08  --/F PHOTOM.dist_ucac
CONSTRAINT pk_Target PRIMARY KEY (targetID)
);

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='CnameAlias') DROP TABLE CnameAlias
CREATE TABLE GES.CnameAlias(
-------------------------------------------------------------------------------
--/H Table of aliases for cNames.
--
--/T Table of aliases for cNames.
--
--/T Required constraints: primary key is (targetID)
-------------------------------------------------------------------------------
cNameAlias  varchar(16) not null default 'NONE',   --/D Unique Gaia-ESO Survey object name formed from the coordinates of the object (at epoch of first observation) --/F FIBINFO.CNAME
cName       varchar(16) not null default 'NONE',   --/D Definitive unique Gaia-ESO Survey object name formed from the coordinates of the object (at epoch of observation) --/F FIBINFO.Cname_alias
CONSTRAINT pk_CnameAlias PRIMARY KEY (cNameAlias)
);

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='Programme') DROP TABLE Programme
CREATE TABLE GES.Programme(
-------------------------------------------------------------------------------
--/H List of programmes comprising the GES survey.
--
--/T This table contains details of the individual programmes which comprise
--/T the GES survey.
--/T
--/T TODO
--/T Two columns are currently retained from the corresponding VSA table.
--/T Experience will show whether they are needed in GES
--/T
--/T Required constraints: primary key is (programmeID)
-------------------------------------------------------------------------------
programmeID        INTEGER not null,                   --/D Unique identifier for the programme  --/C ID_SURVEY
title varchar(64) not null default 'NONE',         --/D a short title for the programme, eg. "Bulge Survey"   --/C NOTE
description varchar(256) not null default 'NONE',  --/D a concise description of the programme   --/C NOTE
institution varchar(20) not null default 'NONE',   --/D Institution responsible for the programme
workGroup  varchar(20) not null default 'NONE',    --/D GES working group responsible for the programme
reference  varchar(40) not null default 'NONE',    --/D Bibliographic reference to a publication describing the programme
url        varchar(80) not null default 'NONE',    --/D URL for a Web page describing the programme
--
-- TODO
-- Note the following two columns are retained from the corresponding VSA table.
-- Experience will show whether they are needed in GES.
--
propPeriod         INTEGER not null default -99999999,       --/D the proprietory period for any data taken for the programme in months, e.g. 12 for open time --/U months  --/C TIME_PERIOD
dfsIDString        varchar(64) not null default 'NONE',  --/D The description used within the data flow system (i.e. the value of the appropriate FITS keyword) --/C ??
CONSTRAINT pk_Programme PRIMARY KEY (programmeID)
);

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='Release') DROP TABLE Release
CREATE TABLE GES.Release(
-------------------------------------------------------------------------------
--/H Details of each release of the GES survey.
--
--/T This table lists all the releases of the GES survey.  (There is a
--/T corresponding Release table for each (every?) survey curated by WFAU.)
--/T
--/T Required constraints: primary key is (surveyID, releaseNum)
--/T                       (surveyID) references Survey(surveyID)
-------------------------------------------------------------------------------
surveyID     INTEGER not null,          --/D The unique identifier for the survey  --/C ID_SURVEY
releaseNum   smallint not null,     --/D The release number   --/C ID_VERSION
releaseDate  TIMESTAMP not null,     --/D The release date --/U MM-DD-YYYY --/N 12-31-9999   --/C TIME_DATE
description  varchar(256) not null default 'NONE', --/D A brief description of the release  --/C NOTE
dbName       varchar(128) not null default 'NONE', --/D The name of the SQL Server database containing this release  --/C ??
deprecated   SMALLINT not null default 0,           --/D Deprecated flag: coded as current=0 or deprecated !=0   --/C CODE_MISC  --/N 0  --/G allTables::deprecated
CONSTRAINT pk_Release PRIMARY KEY (surveyID, releaseNum)
);

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='ArchiveCurationHistory') DROP TABLE ArchiveCurationHistory
CREATE TABLE GES.ArchiveCurationHistory(
-------------------------------------------------------------------------------
--/H Contains details of the matrix of the Archive's required curation tasks.
--
--/T This table contains details of the matrix of the curation tasks
--/T required for the archive; each time a curation task is run, this table
--/T gets updated with timestamps and indicating the status of the
--/T curation process.
--
--/T Required constraints: primary key is (cuEventID)
--/T                       (cuID) references CurationTask(cuID)
-------------------------------------------------------------------------------
cuEventID    INTEGER not null,                         --/D UID of curation event giving rise to this record  --/C REFER_CODE
cuID         smallint not null,                    --/D the unique curation task ID   --/C REFER_CODE
logFile      varchar(256) not null default 'NONE', --/D filename of verbose logged task output --/C ID_FILE
resultsFile  varchar(256) not null default 'NONE', --/D filename of any results file --/C ID_FILE
timeStamp    TIMESTAMP not null,                    --/D Time of the completion of the whole task --/U UTC   --/C TIME_DATE
curator      varchar(16) not null default 'NONE',  --/D The archive curation scientist responsible for this event --/C ??
comment      varchar(256) not null default 'NONE', --/D Comment string supplied by the curator --/C ??
rolledBack   SMALLINT not null,                     --/D Flag for roll-back of this event: 0=no, 1 = yes --/C ??
CONSTRAINT pk_Arc_Cur_Hist PRIMARY KEY (cuEventID)
);

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects where name='CurationTask') DROP TABLE CurationTask
CREATE TABLE GES.CurationTask(
-------------------------------------------------------------------------------
--/H Contains a list of all curation tasks that are used within the OSA.
--
--/T Required constraints: primary key is (cuID)
-------------------------------------------------------------------------------
cuID         smallint not null,                    --/D the unique curation task ID   --/C REFER_CODE
description  varchar(256) not null default 'NONE', --/D description in words for this task --/C NOTE
CONSTRAINT pk_Cur_Task PRIMARY KEY (cuID)
);
-- ----------------------------------------------------------------------------
