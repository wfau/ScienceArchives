--=============================================================================
--
-- $Id: GES_SpectrumSchema.sql 650 2017-11-29 14:28:50Z EckhardSutorius $
--
-- Database schema file containing SQL to create the GES spectrum and
-- related tables.
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
CREATE TABLE GES.SpecFrame(
-------------------------------------------------------------------------------
--/H Details of individual specFrames.
--
--/T The specFrame table lists details of individual specFrames present
--/T in the survey.  A specFrame contains a set of spectra extracted from
--/T a single twoDFrame.  Thus usually there is a 1:1 relation between
--/T specFrames and twoDFrames.  However, it is possible for several
--/T reasons (e.g. a 2d bias or other calibration frame), to have a twoDFrame for which there is no
--/T corresponding specFrame.  A specFrame, however, must necessarily have
--/T a corresponding twoDFrame from which it has been created. The distinction between
--/T a specFrame and its source twoDFrame is that the latter is the spectrograph image
--/T prior to spectral extraction (so may contain curved orders with spectra spread over
--/T more than one column, and the pixel counts will be source plus sky) while a specFrame
--/T is the result of pipeline spectral extraction run on the twoDFrame, and will contain
--/T individual extracted spectra (or echelle orders) in the individual lines (think IRAF
--/T multispec format).
--/T
--/T Required constraints: primary key is (specFrameID)
-------------------------------------------------------------------------------
specFrameID  INTEGER  not null default -99999999,      --/D SpecFrame identifier: unique identifier for each specFrame
fileName     varchar(256) not null default 'NONE', --/D The GES Science Archive filename at WFAU for the specFrame, eg. /path/filename.fits --/C ID_FILE --/Q fitsfilename
gesField     varchar(32)  not null default 'NONE', --/D GES name of the field observed (also name of enclosing directory) --/K GES_FLD
--
--
-- Keywords from primary image:
-- ===========================
--
nAxis       SMALLINT not null default 0,      --/D Number of data axes --/K NAXIS --/N 0
nDispElems  INTEGER not null default -99999999,          --/D Length of data axis 1 of the specFrame in the dispersion direction i.e. the number of wavelength elements --/K NAXIS1
nSpectra    INTEGER not null default -99999999,          --/D Length of data axis 2 of the specFrame in the spatial direction i.e. number of spectra/fibres --/K NAXIS2
utDate      TIMESTAMP not null default '9999-12-31 23:59:59',     --/D UT date when this file was written --/K DATE --/U MM-DD-YYYY --/C TIME_DATE  --/Q dateObs  --/N 12-31-9999 --/R 20111001,None
origin      varchar(64) not null default 'NONE',  --/D European Southern Observatory --/K ORIGIN --/N NONE
telescope   varchar(16) not null default 'NONE',  --/D Telescope name --/K TELESCOP
instrument  varchar(8) not null default 'NONE',   --/D Instrument name --/K INSTRUME 
grating     varchar(5) not null default 'NONE', --/D Grating central wavelength (as string to guarantee formatting) --/U nm --/K HIERARCH ESO INS GRAT WLEN
gesType     varchar(8) not null default 'NONE',   --/D GES Type --/K GES_TYPE
object      varchar(64) not null default 'NONE',  --/D Name of the frame (often the name of the guide star or a bright nearby object) --/K OBJECT 
raBase      real not null default -9.999995e+08,         --/D Right ascension of base pointing (J2000) --/U hours --/K RA --/Q raBase --/N -9.999995e+08 --/R 0.0,360.0
decBase     real not null default -9.999995e+08,         --/D Declination of base pointing (J2000) --/U degrees --/K DEC --/N -9.999995e+08 --/R -90.0,90.0
equinox     real not null default -9.999995e+08,         --/D Standard FK5 (years) --/U years --/K EQUINOX --/N -9.999995e+08
raDecSys    varchar(4) not null default 'NONE',   --/D Coordinate reference frame --/K RADECSYS 
--
-- The following rows on times and dates are relevant to the individual spectra of which the stacked spectra are comprised, stacked spectra
-- may comprise data from several nights whose individual dates are stored in the inputinfo table of the spectral FITS files.
-- The values for the individual exposures should be linked to the individual spectra: these are to be reviewed when the metadata for
-- the individual spectra are ingested/the schema for these are being finalised (see message from Anna, 13/5/14).
expTime     real not null default -9.999995e+08,         --/D Total integration time --/U seconds --/K EXPTIME --/N -9.999995e+08  --/R 0.,None
mjdObs      float not null default -9.999995e+08,        --/D Modified Julian Date of the observation start --/C TIME_DATE --/K MJD-OBS --/N -0.9999995e9 --/R 54700.,None --/E MJD-OBS
mjdEnd      float not null default -9.999995e+08,        --/D Modified Julian Date of the observation end --/C TIME_DATE --/K MJD-END --/N -0.9999995e9 --/R 54700.,None --/E MJD-END
dateObs     TIMESTAMP not null default '9999-12-31 23:59:59',     --/D Observing date --/C TIME_DATE --/K DATE-OBS --/N 12-31-9999 --/G Multiframe::dateObs
utc         real not null default -9.999995e+08,         --/D UTC at start --/U seconds  --/K UTC --/N -9.999995e+08
lst         real not null default -9.999995e+08,         --/D LST at start --/U seconds  --/K LST --/N -9.999995e+08
piCoi       varchar(64) not null default 'NONE',  --/D PI-COI name --/K PI-COI
observer    varchar(64) not null default 'NONE',  --/D Name of observer. --/K OBSERVER
skySub      SMALLINT not null default 0,      --/D Flag: spectra are sky subtracted? --/K SKYSUB
tipRes      SMALLINT not null default 0,      --/D Flag: sky residuals fixed? --/K TIPRES
--
-- External files.
--
originalFileName  varchar(32) not null default 'NONE',  --/D Original File Name from observatory  --/K ORIGFILE  --/N NONE
archiveFileName   varchar(64) not null default 'NONE',  --/D Archive File Name (ESO-SAF or CASU repository?) --/K ARCFILE  --/N NONE
traceFile         varchar(64) not null default 'NONE',  --/D File used for fibre trace  --/K TRACFILE  --/N NONE
profFile          varchar(64) not null default 'NONE',  --/D File used for extraction profile  --/K PROFFILE  --/N NONE
waveFile          varchar(64) not null default 'NONE',  --/D File with wavelength solution  --/K WAVEFILE  --/N NONE
flatFile          varchar(64) not null default 'NONE',  --/D File used for flat division  --/K FLATFILE  --/N NONE
--
-- Software versioning.
--
cirVers   varchar(24) not null default 'NONE',  --/D CIRDR Version --/K CIR_VERS     
softVers  varchar(32) not null default 'NONE',  --/D CIRDR Version --/K SOFTVERS 
softDate  varchar(32) not null default 'NONE',  --/D CIRDR release date --/K SOFTDATE 
softAuth  varchar(32) not null default 'NONE',  --/D Contact for bug reports --/K SOFTAUTH
softInst  varchar(32) not null default 'NONE',  --/D CASU URL --/K SOFTINST
--
-- Axis calibration / WCS.
--
cType1  varchar(8) not null default 'NONE', --/D Grating dispersion function  --/K CTYPE1
cType2  varchar(8) not null default 'NONE', --/D Number of spectrum --/K CTYPE2
crPix1  real not null default -9.999995e+08, --/D Pixel zeropoint --/K CRPIX1
crPix2  real not null default -9.999995e+08, --/D Pixel zeropoint --/K CRPIX2
crVal1  real not null default -9.999995e+08, --/D Wavelength zeropoint --/K CRVAL1
crVal2  real not null default -9.999995e+08, --/D Value of ref pixel --/K CRVAL2    
cUnit1  varchar(16) not null default 'NONE', --/D Units of first array axis --/K CUNIT1
cUnit2  varchar(16) not null default 'NONE', --/D Units of second array axis --/K CUNIT2
cd1_1   real not null default -9.999995e+08, --/D  Wavelength increment --/K CD1_1
cd1_2   real not null default -9.999995e+08, --/D ??? --/K CD1_2
cd2_1   real not null default -9.999995e+08, --/D ??? --/K CD2_1
cd2_2   real not null default -9.999995e+08, --/D ??? --/K CD2_2
--
-- Keywords from the FITS binary tables:
-- =====================================
--
-- IMPLEMENTATION NOTE: ad-hoc K tag used to specify which (of several) table extensions the metadata come from
--
actMjd      real not null default -9.999995e+08,     --/D Actual MJD of tweak time --/K BINTABLE.Fibinfo.ACTMJD
actUtc      TIMESTAMP not null default '9999-12-31 23:59:59', --/D Actual UTC of tweak time --/K BINTABLE.Fibinfo.ACTUTC
allocGui    smallint not null default -9999, --/D Number of allocated FACB stars --/K BINTABLE.Fibinfo.ALLOCGUI
allocObj    smallint not null default -9999, --/D Number of allocated objects --/K BINTABLE.Fibinfo.ALLOCOBJ
allocSky    smallint not null default -9999, --/D Number of allocated sky positions --/K BINTABLE.Fibinfo.ALLOCSKY
unallocGui  smallint not null default -9999, --/D Number of unallocated FACB stars --/K BINTABLE.Fibinfo.UNALLGUI
unallocObj  smallint not null default -9999, --/D Number of unallocated objects --/K BINTABLE.Fibinfo.UNALLOBJ
unallocSky  smallint not null default -9999, --/D Number of unallocated sky positions --/K BINTABLE.Fibinfo.UNALLSKY
argUsed     smallint not null default -9999, --/D Flag indicating if ARGUS is used --/K BINTABLE.Fibinfo.ARGSUSED
atmosPressure  real not null default -9.999995e+08,  --/D Atmospheric pressure --/U millibars --/K BINTABLE.Fibinfo.ATMPRES
atmosHumid     real not null default -9.999995e+08,  --/D Atmospheric relative humidity --/U percentage --/K BINTABLE.Fibinfo.ATMRHUM
atmosTemp      real not null default -9.999995e+08,  --/D Atmospheric temperature --/U Celsius --/K BINTABLE.Fibinfo.ATMTEMP
cenRa          real not null default -9.999995e+08,  --/D Field centre mean RA --/U Degrees --/K BINTABLE.Fibinfo.CENRA
cenDec         real not null default -9.999995e+08,  --/D Field centre mean Dec --/U Degrees --/K BINTABLE.Fibinfo.CENDEC
cenEquinox     real not null default -9.999995e+08,  --/D Equinox of Field Centre (FK5 Julian) --/K BINTABLE.Fibinfo.CENEQNX
duration       real not null default -9.999995e+08,  --/D Duration centered around ACTMJD --/U Seconds --/K BINTABLE.Fibinfo.DURATION
facbWavelen    real not null default -9.999995e+08,  --/D FACB wavelength --/U nanometres --/K BINTABLE.Fibinfo.FACBWLEN
confFileName   varchar(64) not null default 'NONE', --/D Configuration file name --/K BINTABLE.Fibinfo.FILENAME
insRotOff      real not null default -9.999995e+08,        --/D Instrument rotator offset used --/U Degrees --/K BINTABLE.Fibinfo.INSROT
label          varchar(64) not null default 'NONE', --/D Label used for field --/K BINTABLE.Fibinfo.LABEL
plate          SMALLINT not null default 0,     --/D Identifier of the used positioner plate --/K BINTABLE.Fibinfo.PLATE
confWavelen    real not null default -9.999995e+08,        --/D Wavelength used by Configure program --/U nanometre --/K BINTABLE.Fibinfo.WLEN
--
-- Telescope model parameters.
--
telModelParN SMALLINT not null, --/D Number of telescope model parameters --/K BINTABLE.Fibinfo.TELMDLN
telPar01 real not null default -9.999995e+08,  --/D Telescope model parameter 1 --/K BINTABLE.Fibinfo.TELPAR1
telPar02 real not null default -9.999995e+08,  --/D Telescope model parameter 2 --/K BINTABLE.Fibinfo.TELPAR2
telPar03 real not null default -9.999995e+08,  --/D Telescope model parameter 3 --/K BINTABLE.Fibinfo.TELPAR3
telPar04 real not null default -9.999995e+08,  --/D Telescope model parameter 4 --/K BINTABLE.Fibinfo.TELPAR4
telPar05 real not null default -9.999995e+08,  --/D Telescope model parameter 5 --/K BINTABLE.Fibinfo.TELPAR5
telPar06 real not null default -9.999995e+08,  --/D Telescope model parameter 6 --/K BINTABLE.Fibinfo.TELPAR6
telPar07 real not null default -9.999995e+08,  --/D Telescope model parameter 7 --/K BINTABLE.Fibinfo.TELPAR7
telPar08 real not null default -9.999995e+08,  --/D Telescope model parameter 8 --/K BINTABLE.Fibinfo.TELPAR8
telPar09 real not null default -9.999995e+08,  --/D Telescope model parameter 9 --/K BINTABLE.Fibinfo.TELPAR9
telPar10 real not null default -9.999995e+08,  --/D Telescope model parameter 10 --/K BINTABLE.Fibinfo.TELPAR10
telPar11 real not null default -9.999995e+08,  --/D Telescope model parameter 11 --/K BINTABLE.Fibinfo.TELPAR11
telPar12 real not null default -9.999995e+08,  --/D Telescope model parameter 12 --/K BINTABLE.Fibinfo.TELPAR12
telPar13 real not null default -9.999995e+08,  --/D Telescope model parameter 13 --/K BINTABLE.Fibinfo.TELPAR13
telPar14 real not null default -9.999995e+08,  --/D Telescope model parameter 14 --/K BINTABLE.Fibinfo.TELPAR14
telPar15 real not null default -9.999995e+08,  --/D Telescope model parameter 15 --/K BINTABLE.Fibinfo.TELPAR15
telPar16 real not null default -9.999995e+08,  --/D Telescope model parameter 16 --/K BINTABLE.Fibinfo.TELPAR16
telPar17 real not null default -9.999995e+08,  --/D Telescope model parameter 17 --/K BINTABLE.Fibinfo.TELPAR17
telPar18 real not null default -9.999995e+08,  --/D Telescope model parameter 18 --/K BINTABLE.Fibinfo.TELPAR18
telPar19 real not null default -9.999995e+08,  --/D Telescope model parameter 19 --/K BINTABLE.Fibinfo.TELPAR19
telPar20 real not null default -9.999995e+08,  --/D Telescope model parameter 20 --/K BINTABLE.Fibinfo.TELPAR20
--
-- WFAU curation attributes
--
deprecated INTEGER not null default 0,  --/D Deprecated flag: coded as current=0 or deprecated !=0   --/C CODE_MISC  --/N 0  --/G allTables::deprecated
cuEventID  INTEGER not null,            --/D UID of curation event giving rise to this record  --/C REFER_CODE
CONSTRAINT pk_SpecFrame PRIMARY KEY (specFrameID)
)GO

-- ----------------------------------------------------------------------------
CREATE TABLE GES.Spectrum(
-------------------------------------------------------------------------------
--/H Details of individual spectra.
--
--/T The Spectrum table lists details of individual spectra observed during
--/T the survey.  Note that a given target star may (and often will) be
--/T observed more than once during the survey, so a given targetID may have
--/T several entries in the table; furthermore, early data releases may well
--/T contain several pipeline processed versions of the same data for a given
--/T target.
--/T
--/T Required constraints: primary key is (specID)
--/T                       (targetID) references Target(targetID)
--/T                       (specFrameID) references SpecFrame(specFrameID)
-------------------------------------------------------------------------------
specID      bigint not null default -99999999, --/D Spectrum identifier: unique identifier for each spectrum (4 MSB are the specFrameID; 4 LSB are the nSpec) --/Q specFrameID,nSpec
specFrameID INTEGER not null default -99999999,    --/D SpecFrame identifier of the SpecFrame from which the spectrum was extracted
targetID    bigint not null default -99999999, --/D Target identifer of the star being observed
fileName    varchar(256) not null default 'NONE', --/D The GES Science Archive filename at WFAU for the specFrame, eg. /path/filename.fits. Only for UVES SingleSpec files.  --/C ID_FILE --/Q fitsfilename
--
-- Columns derived from FITS binary table "Fibinfo" (as output by CASU pipeline; some in common with Keele and Arcetri (UVES) pipeline output in FITS table extensions #4 and #3 respectively):
--
-- IMPLEMENTATION NOTE: ad-hoc F tag (schema-driven functionality from FITS table attributes): 
--   + means use these columns to associate records across FITS table extensions; 
--   comma specifies column must be present in one OR another extension (exclusive OR: only one extension specified should be present!);
--   NoNameX specifies an unnamed extension at position X (counting from 0 for the PHDU).  
nSpec      INTEGER not null default -99999999,       --/D The number of the spectrum --/F velclass.Nspec+Fibinfo.Nspec,NoName4.NSPEC,NoName3.NSPEC
nSpecOld   INTEGER not null default -99999999,       --/D The number of the spectrum before unused fibres were culled (equivalent to the number of the fibre) --/F velclass.Nspec_old+Fibinfo.Nspec_old,NoName3.NSPEC_OLD
--specFrameIndex INTEGER not null,                     --/D Index of the spectrum in the SpecFrame identified by specFrameID
--obsDate    TIMESTAMP  not null,                   --/D Date of observation (UT) --/U MM-DD-YYYY
cName      varchar(16) not null default 'NONE', --/D Object name formed from the coordinates of the object (can be used in place of object to give a unique name) --/F Fibinfo.Cname
type       varchar(32) not null default 'NONE', --/D M for programme objects or S for sky fibres --/F Fibinfo.TYPE,NoName4.TYPE,NoName3.TYPE
spClass    varchar(8) not null default 'NONE',  --/D The spectral class (STAR, SKY or LOWSN; the latter two classes do not have spectral fits done for them) --/F Fibinfo.OBJ_CLASS,velclass.SPCLASS
mag        real not null default -9.999995e+08, --/D A magnitude estimate --/U mag --/F Fibinfo.MAGNITUDE,NoName4.MAGNITUDE
priority   INTEGER not null default -99999999,      --/D Observation priority --/F Fibinfo.GES_RANK,Fibinfo.PRIORITY,NoName4.PRIORITY
snr        real not null default -9.999995e+08, --/D The mean signal-to-noise ratio in the spectrum --/F Fibinfo.S_N,velclass.S_N
skyOff     real not null default -9.999995e+08, --/D Offset to get the mean sky into coincidence with the current spectrum --/U pixels --/F Fibinfo.sky_off
skyScale   real not null default -9.999995e+08, --/D The scaling factor applied to the mean sky before subtracting from the current spectrum --/F Fibinfo.sky_scale,NoName4.SKY_SCALE
--
-- For the stacked spectra [expTime] should be the total integration time from the primary header and for the individual component spectra it should
-- come from the inputinfo FITS extension (see message from Anna, 13/5/14).
expTime    real not null default -9.999995e+08, --/D Total integration time --/U seconds --/F Fibinfo.exptime --/N -9.999995e+08
rmsTrace   real not null default -9.999995e+08, --/D The RMS of the fit to the curvature of the spectrum on the detector --/U pixels --/F Fibinfo.RMS_trace
rmsArc     real not null default -9.999995e+08, --/D The RMS of the wavelength solution --/U Angstroms --/F Fibinfo.RMS_arc,NoName4.RMS_ARC
resArc     real not null default -9.999995e+08, --/D The resolution of the arclines --/F Fibinfo.RES_arc
fwhmArc    real not null default -9.999995e+08, --/D The FWHM of the arclines --/F Fibinfo.FWHM_arc
ccfMax     real not null default -9.999995e+08, --/D The peak value of the cross correlation function --/F Fibinfo.CCFmax,NoName4.CCFMAX
ccfWidth   real not null default -9.999995e+08, --/D Width of the peak of the cross correlation function --/U km/s --/F Fibinfo.ccfwidth
rvRedshift real not null default -9.999995e+08, --/D The radial velocity measured from the cross correlation --/U km/s --/F Fibinfo.rv_redshift
rv         float not null default -9.999995e+08, --/D The measured radial velocity from the cross correlation --/U km/s --/F Fibinfo.RV,velclass.VEL
rvErr      float not null default -9.999995e+08, --/D Error on the measured radial velocity from the cross correlation --/U km/s --/F Fibinfo.RV_ERR,velclass.EVEL
rvVar      float not null default -9.999995e+08, --/D Variance? on the measured radial velocity from the cross correlation --/U km/s --/F Fibinfo.RV_VAR
vRot       float not null default -9.999995e+08, --/D The best fit rotational velocity --/U km/s --/F Fibinfo.VROT,velclass.VROT
vRotErr    float not null default -9.999995e+08, --/D Error on vRot --/U km/s --/F Fibinfo.VROT_ERR,NoName1.evrot
helioCor   real not null default -9.999995e+08, --/D The heliocentric correction --/U km/s --/F Fibinfo.Helio_cor,Fibinfo.HELIOCOR,NoName4.HELIO_COR
simcalCor  real not null default -9.999995e+08, --/D The correction to be applied to correct for wavelength drift calculated from simcal observations --/U km/s --/F Fibinfo.Simcal_cor,NoName4.SIMCAL_COR
simcalRms  real not null default -9.999995e+08, --/D The RMS on simcalCor --/U km/s --/F Fibinfo.Simcal_rms,NoName4.SIMCAL_RMS
skylineCor real not null default -9.999995e+08, --/D The correction to be applied to correct for wavelength drift calculated from the sky lines in the observations --/U km/s --/F Fibinfo.Skyline_cor,NoName4.SKYLINE_COR
skylineRms real not null default -9.999995e+08, --/D The RMS on skylineCor --/U km/s --/F Fibinfo.Skyline_rms,NoName4.SKYLINE_RMS
vacuumCor  real not null default -9.999995e+08, --/D The correction to be applied to the measured redshift if the spectral features in the template are defined in vacuum rather than at STP --/U km/s --/F Fibinfo.Vacuum_cor,NoName4.VACUUM_COR
bestTempl  varchar(64) not null default 'NONE', --/D A designation for the best fitting radial velocity template --/F Fibinfo.Best_tmpl,NoName4.BEST_TMPL
tmplTemp   real not null default -9.999995e+08, --/D The temperature for the best fitting radial velocity template --/U K --/F Fibinfo.Tmpl_temp,NoName4.TMPL_TEMP
tmplLogg   real not null default -9.999995e+08, --/D The value of log(g) for the best fitting radial velocity template --/F Fibinfo.Tmpl_logg,NoName4.TMPL_LOGG
tmplFeH    real not null default -9.999995e+08, --/D The value of [Fe/H] for the best fitting radial velocity template --/F Fibinfo.Tmpl_feh,NoName4.TEMPL_FEH
--
-- Columns derived from FITS ASCII table extension 4 in Keele pipeline output (will be default for other pipelines):
--
--r     float not null default -9.999995e+08, --/D Unknown --/F NoName4.R
--rError     float not null default -9.999995e+08, --/D Unknown --/F NoName4.R_ERROR
--theta     float not null default -9.999995e+08, --/D Unknown --/F NoName4.THETA
--thetaError     float not null default -9.999995e+08, --/D Unknown --/F NoName4.THETA_ERROR
--button INTEGER not null default -99999999, --/D Unknown --/F NoName4.BUTTON
--orient float not null default -9.999995e+08, --/D Unknown --/F NoName4.ORIENT
--inTol varchar(1) not null default '-', --/D Unknown --/F NoName4.IN_TOL
--comment varchar(256) not null default 'NONE', --/D A comment --/F NoName4.COMMENT 
--ccdRON float not null default -9.999995e+08, --/D Detector readout noise --/F NoName4.CCDRON
--ccdGain float not null default -9.999995e+08, --/D Detector gain --/F NoName4.CCDGAIN
--numObs INTEGER not null default -99999999, --/D Number of observations coadded --/F NoName4.NUM_OBS
--snrMean float not null default -9.999995e+08, --/D Mean signal-to-noise ratio --/F NoName4.SNR_MEAN
--rvCcfWid float not null default -9.999995e+08, --/D Unknown --/F NoName4.RV_CCFWID
--rvCcfSnr float not null default -9.999995e+08, --/D Unknown --/F NoName4.RV_CCFSNR
--rvAbs float not null default -9.999995e+08, --/D Unknown --/F NoName4.RV_ABS
--wlCor float not null default -9.999995e+08, --/D Unknown --/F NoName4.WL_COR
--field varchar(32) not null default 'NONE', --/D The name of the observed GES field --/F NoName4.FIELD
--filter varchar(8) not null default 'NONE', --/D The filter used in the observation --/F NoName4.FILTER
--tempData float not null default -9.999995e+08, --/D Unknown --/F NoName4.TEMP_DATA
--gravData varchar(16) not null default 'NONE', --/D Unknown --/F NoName4.GRAV_DATA
--mhData varchar(16) not null default 'NONE', --/D Unknown --/F NoName4.MH_DATA
--rbName varchar(32) not null default 'NONE', --/D Unknown --/F NoName4.RBNAME
--version varchar(4) not null default 'NONE', --/D Unknown --/F NoName4.VERSION
--fibreAtn float not null default -9.999995e+08, --/D Unknown --/F NoName4.FIBRE_ATN
--skyType INTEGER not null default -99999999, --/D Unknown --/F NoName4.SKY_TYPE
--telSet INTEGER not null default -99999999, --/D Unknown --/F NoName4.TEL_SET
--rvType INTEGER not null default -99999999, --/D Unknown --/F NoName4.RV_TYPE
--fibreName varchar(4) not null default 'NONE', --/D Unknown --/F NoName4.FIBRE_NAME
--stat INTEGER not null default -99999999, --/D Unknown --/F NoName4.STAT
--rvStdNum INTEGER not null default -99999999, --/D Unknown --/F NoName4.RVSTD_NUM
--vFit float not null default -9.999995e+08, --/D Unkown --/F NoName4.VFIT
--rvAbsRms float not null default -9.999995e+08, --/D Unknown --/F NoName4.RVABS_RMS
--wlCorRms float not null default -9.999995e+08, --/D Unknown --/F NoName4.WLCOR_RMS
--vsini float not null default -9.999995e+08, --/D Unknown --/F NoName4.VSINI
--
-- Columns dervied from FITS binary table extension 3 of Arcetri (UVES) pipeline (will be default for other pipelines):
--
-- No further attributes presently.
--
--  Columns derived from FITS binary table "velclass" (will be default if that extension is not present):
--
--object    varchar(32) not null default 'NONE', --/D The object name as defined in the OB --/F velclass.OBJECT 
chi2dof   real not null default -9.999995e+08, --/D Chi-squared of the template fit --/F velclass.CHI2_DOF
chi2cont  real not null default -9.999995e+08, --/D Chi-squared of the continuum-only fit --/F velclass.CHI2_CONT
templDist real not null default -9.999995e+08, --/D Something to do with the radial velocity template --/F velclass.TEMPL_DISTANCE
logg      real not null default -9.999995e+08, --/D The value of log(g) of the best fitting template --/F velclass.LOGG
logTeff   real not null default -9.999995e+08, --/D The value of log(Teff) of the best fitting template --/F velclass.LOGTEFF
FeH       real not null default -9.999995e+08, --/D The value of [Fe/H] of the best fitting template --/F velclass.FEH
--
--   Other WFAU-added attributes:
--
deprecated INTEGER not null default 0,  --/D Deprecated flag: coded as current=0 or deprecated !=0   --/C CODE_MISC  --/N 0  --/G allTables::deprecated
CONSTRAINT pk_Spectrum PRIMARY KEY (specID)
)GO

-- ----------------------------------------------------------------------------
CREATE TABLE GES.SpectrumNightly(
-------------------------------------------------------------------------------
--/H Details of individual nightly spectra.
--
--/T The Spectrum table lists details of individual nightly spectra observed 
--/T during the survey.  Note that a given target star may (and often will) be
--/T observed more than once during the survey, so a given targetID may have
--/T several entries in this table.
--/T
--/T Required constraints: primary key is (specNightlyID)
--/T                       (specID) references Spectrum(specID)
-------------------------------------------------------------------------------
specNightlyID bigint not null default -99999999,  --/D Nightly Spectrum identifier: unique identifier for each nightly spectrum 
specID     bigint not null default -99999999, --/D Spectrum identifier: unique identifier for each spectrum (4 MSB are the specFrameID; 4 LSB are the nSpec) --/Q specFrameID,nSpec
fileName   varchar(256) not null default 'NONE',  --/D The GES Science Archive filename at WFAU for the nightly spectrum, eg. /path/filename.fits --/C ID_FILE
nSpec      smallint not null default -9999,   --/D The number of the spectrum  --/F INPUTINFO.Nspec,INPUTINFO.NSPEC
nSpecOld   smallint not null default -9999,   --/D The number of the spectrum before unused fibres were culled (equivalent to the number of the fibr,e counting from left to right on the original raw image.)  --/F INPUTINFO.Nspec_old,INPUTINFO.NSPEC_OLD
rmsTrace   real not null default -9.999995e+08,   --/D The RMS of the fit to the curvature of the spectrum on the detector  --/U pixels  --/F INPUTINFO.RMS_trace         
rmsArc     real not null default -9.999995e+08,   --/D The RMS in Angstroms of the wavelength solution  --/U Angstrom  --/F INPUTINFO.RMS_arc,INPUTINFO.RMS_ARC
rvRedshift real not null default -9.999995e+08,   --/D The radial velocity measured from the cross correlation, computed using a template from the Munari grid.  Use the velocity in column VEL should in preference to this one.  --/U km/sec  --/F INPUTINFO.RV_redshift       
helioCor   real not null default -9.999995e+08,   --/D The heliocentric correction  --/U km/sec  --/F INPUTINFO.Helio_cor,INPUTINFO.HELIOCOR      
simcalCor  real not null default -9.999995e+08,   --/D The correction to be applied to correct for wavelength drift calculated from simcal observations  --/U Angstrom  --/F INPUTINFO.Simcal_cor        
simcalRms  real not null default -9.999995e+08,   --/D The RMS of simcalCor  --/U Angstrom  --/F INPUTINFO.Simcal_rms        
skylineCor real not null default -9.999995e+08,   --/D The correction to be applied to correct for wavelength drift calculated from the sky lines in the observations  --/U Angstrom  --/F INPUTINFO.Skyline_cor       
skylineRms real not null default -9.999995e+08,   --/D The RMS of skylineCor  --/U Angstrom  --/F INPUTINFO.Skyline_rms       
vacuumCor  real not null default -9.999995e+08,   --/D The correction to be applied to the measured redshift if the spectral features in the template are defined in vacuum rather than in air at STP  --/U km/sec  --/F INPUTINFO.Vacuum_cor        
skyScale   real not null default -9.999995e+08,   --/D The scaling factor applied to the mean sky before subtracting from the current spectrum  --/F INPUTINFO.sky_scale         
vel        float not null default -9.999995e+08,  --/D The measured radial velocity from the cross correlation (using the Munari grid)  --/U km/sec  --/F INPUTINFO.VEL               
velErr     float not null default -9.999995e+08,  --/D The error on vel  --/U km/sec  --/F INPUTINFO.EVEL              
snrMean    float not null default -9.999995e+08,  --/D The mean signal-to-noise ratio in the spectrum  --/F INPUTINFO.S_N                     
snrMedian  float not null default -9.999995e+08,  --/D The median signal-to noise ratio of the spectrum  --/F INPUTINFO.S_N           
chi2dof    float not null default -9.999995e+08,  --/D Chi-squared of the template fit  --/F INPUTINFO.CHI2_DOF          
chi2cont   float not null default -9.999995e+08,  --/D Chi-squared of the continuum-only fit  --/F INPUTINFO.CHI2_CONT         
templDist  float not null default -9.999995e+08,  --/D A weighted L2 distance to the best fitting template  --/F INPUTINFO.TEMPL_DISTANCE    
logg       float not null default -9.999995e+08,  --/D The value of log(g) of the best fitting template  --/F INPUTINFO.LOGG              
logTeff    float not null default -9.999995e+08,  --/D The value of log(Teff) of the best fitting template  --/U K  --/F INPUTINFO.LOGTEFF           
FeH        float not null default -9.999995e+08,  --/D The value of [Fe/H] of the best fitting template  --/F INPUTINFO.FEH               
vRot       float not null default -9.999995e+08,  --/D The best fit rotational velocity  --/U km/sec  --/F INPUTINFO.VROT,INPUTINFO.VROT          
vRotErr    float not null default -9.999995e+08,  --/D Error on vRot  --/U km/sec  --/F INPUTINFO.EVROT,INPUTINFO.VROT_ERR      
rvSb1      INTEGER not null default -99999999,        --/D Flag for multiple CCF peaks  --/F INPUTINFO.RV_SB1            
rvSb2      INTEGER not null default -99999999,        --/D Flag for RV variability. 1 if variability detected, 0 if not.  --/F INPUTINFO.RV_SB2            
rvQFlag    INTEGER not null default -99999999,        --/D Quality flag for Giraffe radial velocity (Vel). If rvQflg=1, error on radial velocity may be higher than quoted.  --/F INPUTINFO.RV_Qflag,INPUTINFO.RV_Qflg       
rv         float not null default -9.999995e+08,  --/D The measured radial velocity from the cross correlation (GES grid used).  --/F INPUTINFO.RV            
rvErr      float not null default -9.999995e+08,  --/D Error on the measured radial velocity from the cross correlation  --/F INPUTINFO.RV_ERR        
spClass    varchar(5) not null default 'NONE',    --/D The spectral class (STAR, SKY or LOWSN; the latter two classes do not have spectral fits done for them)  --/F INPUTINFO.SPCLASS           
expTime    real not null default -9.999995e+08,   --/D The exposure time of this spectrum  --/U seconds  --/F INPUTINFO.exptime,INPUTINFO.EXPTIME       
dateObs    varchar(25) not null default 'NONE',   --/D The date and time of the observation  --/F INPUTINFO.date_obs,INPUTINFO.DATE_OBS      
mjdObs     float not null default -9.999995e+08,  --/D Modified Julian Date of the start of the observation  --/F INPUTINFO.mjd_obs,INPUTINFO.MJD_OBS       
mjdEnd     float not null default -9.999995e+08,  --/D Modified Julian Date of the end of the observation  --/U days  --/F INPUTINFO.mjd_end,INPUTINFO.MJD_END
airmassStart real not null default -9.999995e+08, --/D Air mass at start of observation  --/F INPUTINFO.airmass_start,INPUTINFO.AIRMASS_START 
airmassEnd real not null default -9.999995e+08,   --/D Air mass at end of observation  --/F INPUTINFO.airmass_end,INPUTINFO.AIRMASS_END   
obid       bigint not null default -99999999,     --/D The ID number of the OB for this observation  --/F INPUTINFO.obid,INPUTINFO.OBID          
utc        real not null default -9.999995e+08,   --/D Coordinated Universal Time at the start of the observation  --/U seconds  --/F INPUTINFO.utc,INPUTINFO.UTC
lst        real not null default -9.999995e+08,   --/D Local sidereal time at the start of the observation  --/U seconds  --/F INPUTINFO.lst,INPUTINFO.LST           
seeing     real not null default -9.999995e+08,   --/D Estimate of seeing for the observation  --/U arcsec  --/F INPUTINFO.seeing,INPUTINFO.SEEING        
moonAng    real not null default -9.999995e+08,   --/D The angular distance between the field centre and the moon  --/U degrees  --/F INPUTINFO.moon_ang,INPUTINFO.MOON_ANG      
archiveFileName varchar(34) not null default 'NONE', --/D The ESO ARCFILE specification for the raw data for this observation  --/F INPUTINFO.arcfile,INPUTINFO.ARCFILE       
inputFileName   varchar(32) not null default 'NONE', --/D The manyspec product file from which this spectrum was extracted  --/F INPUTINFO.input_filename,INPUTINFO.INPUT_FILENAME
ccfMax     float not null default -9.999995e+08,  --/D The peak value of the cross correlation function for the best fitting radial velocity template  --/F INPUTINFO.CCFMAX        
ccfWidth   float not null default -9.999995e+08,  --/D Width of the peak of the cross correlation function  --/U km/sec  --/F INPUTINFO.CCFWIDTH      
fwhmArc    float not null default -9.999995e+08,  --/D The average FWHM of the arc lines  --/U Angstrom  --/F INPUTINFO.FWHM_ARC      
resArc     float not null default -9.999995e+08,  --/D The average resolution of the arc lines  --/U Angstrom  --/F INPUTINFO.RES_ARC       
--
--   Other WFAU-added attributes:
--
deprecated INTEGER not null default 0,                --/D Deprecated flag: coded as current=0 or deprecated !=0   --/C CODE_MISC  --/N 0  --/G allTables::deprecated
CONSTRAINT pk_SpectrumNightly PRIMARY KEY (specNightlyID)
)GO

-- ----------------------------------------------------------------------------
CREATE TABLE GES.SpecFrameFitsKey(
-------------------------------------------------------------------------------
--/H List of FITS keywords extracted from the headers of SpecFrames.
--
--/T This table lists all the FITS keywords in all the SpecFrames ingested into
--/T the archive.  It is not anticipated that these keywords will be accessed 
--/T often, since the most useful metadata keys are present as attributes in the
--/T SpecFrame table. If, however, information from this table is required, note
--/T that all data are stored as FITS key character strings so use of the built-in
--/T SQL function CAST is required to perform operations within expressions on these
--/T attributes. 
--/T
--/T Required constraints: primary key is (specFrameID, extNum, name)
--/T                       (specFrameID) references SpecFrame(specFrameID)
-------------------------------------------------------------------------------
specFrameID INTEGER not null default -99999999,        --/D specFrameID of the specFrame from which the keyword was extracted.
extNum      smallint not null default -9999,       --/D Extension number (0 corresponds to the primary HDU)
name        varchar(128) not null default 'NONE',  --/D Name of the FITS keyword
value       varchar(128) not null default 'NONE',  --/D Value of the FITS keyword (copied as a character string)
units       varchar(128) not null default 'NONE',  --/D Any units for the FITS keyword
description varchar(128) not null default 'NONE',  --/D  Description of the FITS keyword
CONSTRAINT pk_SpecFrameFitsKey PRIMARY KEY (specFrameID, extNum, name)
)GO

-- ----------------------------------------------------------------------------
CREATE TABLE GES.SpectrumGroup(
-------------------------------------------------------------------------------
--/H Defines the group of spectra that make up an analysis in AstroAnalysis.
--
--/T Links the group of spectra that make up an analysis in AstroAnalysis to
--/T the individual spectrum entries in the Spectrum table.
--/T
--/T Required constraints: primary key is (specGroupID, specID, fileName)
--/T                       (specID) references Spectrum(specID)
-------------------------------------------------------------------------------
specGroupID  bigint not null default -99999999,    --/D Spectrum group identifier: unique identifier for each group of spectra that went into an analysis.
specID       bigint not null default -99999999,    --/D Spectrum identifier: unique identifier for the individual spectrum that contributed to the analysis.
fileName     varchar(256) not null default 'NONE', --/D File name of the spectrum with full path within the GES Science Archive eg. /path/filename.fits --/C ID_FILE
completeness varchar(1) not null default 'U' --/D Flag, is the spectrum group complete: R - all files resolved ok; U one or more files undefined.
-- HACK: Primary key should be (specGroupID, specID) but we don't have all spectra
CONSTRAINT pk_SpectrumGroup PRIMARY KEY (specGroupID, specID, fileName)
)GO


-------------------------------------------------------------------------------
CREATE TABLE GES.AstroAnalysis(
-------------------------------------------------------------------------------
--/H Combined results table for all GES spectral analysis.
--
--/T This table contains the individual node and recommended astrophysical 
--/T parameters & abundances provided by the GES consortium for all stars 
--/T included in the survey.
--/T It includes results provided by all the working groups and from both the 
--/T UVES and Giraffe spectrographs.
--/T 
--/T Notes:
--/T   All abundances of element X are given in the following format:
--/T   
--/T     log &epsilon;(X) = log(N<sub>X</sub>/N<sub>H</sub>) + 12.0
--/T   
--/T   Upper_Combined_X allowed flag values are:
--/T     0 = neutral detection;
--/T     1 = neutral upper limit;
--/T     2 = detection for combined results (neutral & ionised element);
--/T     3 = upper limit for combined results (neutral & ionised element)
--/T
--/T   Upper_X allowed flag values are:
--/T     0 = ionised detection
--/T     1 = ionised upper limit
--/T   
--/T   Allowed values for limit flags on abundances derived from equivalent 
--/T   widths and photometric temperatures:
--/T     0 = detection;
--/T     1 = upper limit
--/T
--/T Required constraints: primary key is (specGroupID, wg, nodeID, isWgParams, uniqueness)
--/T                       (targetID) references Target(targetID)
-------------------------------------------------------------------------------
specGroupID bigint not null default -99999999,   --/D Spectrum group identifier: unique identifier for each group of spectra that went into the analysis.
nodeID      SMALLINT not null default 0,          --/D Node identifier: unique identifier, only within a given working group, for the node that contributed this analysis (nodeID = 1 for the recommended values from the combined analysis).
nodeName    varchar(32) not null default 'NONE', --/D Name of working group node that contributed this analysis (nodeName = wg for the recommended values from the combined analysis).  --/K NODE1
recWg varchar(8) not null default 'NONE', --/D Recommended Results taken from this GES Working Group  --/F NONAME1.REC_WG
ravailWg varchar(23) not null default 'NONE', --/D All WGs that produced results for this target  --/F NONAME1.RAVAIL_WG
wg          varchar(4) not null default 'NONE',  --/D GES working group performing the analysis (one of: WG10, WG11, WG12, etc).
wgSource    varchar(23) not null default 'NONE',  --/D GES working group performing the analysis (one of: WG10, WG11, WG12, etc).  --/F NONAME1.WG
isWgParams  SMALLINT not null default 0,          --/D Flag; 1 = working group recommend parameters, 0 = node analysis parameters
GesType varchar(20) not null default 'NONE', --/D GES Target Classification --/F NONAME1.GES_TYPE
specGroupStr varchar(600) not null default 'NONE', --/D string representation of the spectrum group
primKeyStr varchar(600) not null default 'NONE', --/D string representation of the primary key.
uniqueness smallint not null default 0, --/D Sequence number for occurrences of primKeyStr.
aaID bigint not null default -99999999, --/D AstroAnalysis identifier: unique sequence no in the table.
releaseName varchar(10) not null default 'NONE',  --/D Data release, e.g. iDR1  --/K RELEASE
releaseDate TIMESTAMP not null default '9999-12-31 23:59:59',  --/D The date that the results were tabulated.  --/K DATETAB
instrument  varchar(8) not null default 'NONE',  --/D FLAMES instrument for these results ('UVES' or 'GIRAFFE')
recGratings varchar(64) not null default 'NONE', --/D Recommended TEFF,LOGG,FEH,ALPHA_FE taken from this grating  --/F NONAME1.REC_SETUP
ravailGratings varchar(80) not null default 'NONE', --/D All gratings for which results were produced for this target  --/F NONAME1.RAVAIL_SETUP
gratings    varchar(64) not null default 'NONE',    --/D All gratings with which the target was observed irrespective of whether or not results were produced --/F NONAME1.SETUP
gesField   varchar(32) not null default 'NONE', --/D GES field name from CASU (=parent directory). --/F NONAME1.GES_FLD
gesObject   varchar(74) not null default 'NONE', --/D GES object name from OB --/F NONAME1.OBJECT
constFiles  varchar(200) not null default 'NONE', --/D Names (without dir. spec.) of files used in analysis  --/F NONAME1.FILENAME
targetID    bigint not null default -99999999,   --/D Target identifer of the star being observed
cName varchar(16) not null default 'NONE', --/D GES object name from coordinates --/F NONAME1.CNAME
Teff real not null default -9.999995e+08, --/D Effective Temperature --/F NONAME1.TEFF --/U K
TeffErr real not null default -9.999995e+08, --/D Error on Teff --/F NONAME1.E_TEFF --/U K
nnTeff smallint not null default -9999, --/D Number of Node results used for Teff  --/N -1 --/F NONAME1.NN_TEFF
ennTeff real not null default -9.999995e+08, --/D Error on Teff from Node errors --/F NONAME1.ENN_TEFF --/U K --/N -1.0
nneTeff smallint not null default -9999, --/D Number of Node results used for ennTeff  --/N -1 --/F NONAME1.NNE_TEFF
logg real not null default -9.999995e+08, --/D Log surface gravity (gravity in cms<sup>-2</sup>) --/F NONAME1.LOGG --/U dex
loggErr real not null default -9.999995e+08, --/D Error on logg --/F NONAME1.E_LOGG --/U dex
nnlogg smallint not null default -9999, --/D Number of node results used for logg  --/N -1 --/F NONAME1.NN_LOGG
ennlogg real not null default -9.999995e+08, --/D Error on logg from Node errors --/F NONAME1.ENN_LOGG --/U dex --/N -1.0
nnelogg smallint not null default -9999, --/D Number of node results used for ennlogg  --/N -1 --/F NONAME1.NNE_LOGG
limlogg smallint not null default -9999, --/D Flag on lower and upper limits of LOGG --/N -1 --/F NONAME1.LIM_LOGG
FeH real not null default -9.999995e+08, --/D Metallicity from Fe lines --/F NONAME1.FEH --/U dex
FeHErr real not null default -9.999995e+08, --/D Error on FeH --/F NONAME1.E_FEH --/U dex
nnFeH smallint not null default -9999, --/D Number of node results used for FeH  --/N -1 --/F NONAME1.NN_FEH
ennFeH real not null default -9.999995e+08, --/D Error on FeH from Node errors --/F NONAME1.ENN_FEH --/U dex --/N -1.0
nneFeH smallint not null default -9999, --/D Number of node results used for ennFeH  --/N -1 --/F NONAME1.NNE_FEH
Xi real not null default -9.999995e+08, --/D Microturbulence --/F NONAME1.XI --/U km/sec
XiErr real not null default -9.999995e+08, --/D Error on XI --/F NONAME1.E_XI --/U km/sec
nnXi smallint not null default -9999, --/D Number of Node results used for XI  --/N -1 --/F NONAME1.NN_XI
ennXi real not null default -9.999995e+08, --/D Error on XI from Node errors --/F NONAME1.ENN_XI --/U km/sec --/N -1.0
nneXi smallint not null default -9999, --/D Number of Node results used for ennXI  --/N -1 --/F NONAME1.NNE_XI
MH real not null default -9.999995e+08, --/D Global Metallicity from metal lines --/F NONAME1.MH --/U dex
MHErr real not null default -9.999995e+08, --/D Error on MH --/F NONAME1.E_MH --/U dex
nnMH smallint not null default -9999, --/D Number of node results used for MH  --/N -1 --/F NONAME1.NN_MH
nnMHErr real not null default -9.999995e+08, --/D Error on MH from Node errors --/F NONAME1.ENN_MH --/U dex --/N -1.0
nneMHErr smallint not null default -9999, --/D Number of Node results used for nnMHErr --/F NONAME1.NNE_MH --/N -1
alphaFe real not null default -9.999995e+08, --/D Global alpha element to Fe ratio --/F NONAME1.ALPHA_FE --/U dex
alphaFeErr real not null default -9.999995e+08, --/D Error on alphaFe --/F NONAME1.E_ALPHA_FE --/U dex
nnAlphaFe smallint not null default -9999, --/D Number of Node results used for ALPHA_FE  --/N -1 --/F NONAME1.NN_ALPHA_FE 
alphaFeNodeErr  real not null default -9.999995e+08, --/D Error on ALPHA_FE from Node errors  --/F NONAME1.ENN_ALPHA_FE --/U dex
nnAlphaFeNodeErr  smallint not null default -9999, --/D Number of node results used for alphaFeNodeErr --/N -1 --/F NONAME1.NNE_ALPHA_FE
objRa real not null default -9.999995e+08, --/D Object Right Ascension --/U degrees --/F NONAME1.RA
objDec real not null default -9.999995e+08, --/D Object Declination --/U degrees --/F NONAME1.DEC
snr real not null default -9.999995e+08, --/D S/N ratio from CASU/Arcetri pipeline --/F NONAME1.SNR
radVel real not null default -9.999995e+08,  --/D Radial Velocity from CASU/Arcetri pipeline --/U km/s --/F NONAME1.VEL
radVelErr real not null default -9.999995e+08,  --/D Error on VEL from CASU/Arcetri pipeline --/U km/s --/F NONAME1.E_VEL
rotVel real not null default -9.999995e+08,  --/D Rotational Velocity from CASU/Arcetri pipeline --/U km/s --/F NONAME1.VROT
rotVelErr real not null default -9.999995e+08,  --/D Error on VROT from CASU/Arcetri pipeline --/U km/s --/F NONAME1.E_VROT
Vrad real not null default -9.999995e+08, --/D Radial Velocity from Node/WG analysis --/F NONAME1.VRAD --/U km/sec
VradErr real not null default -9.999995e+08, --/D Error on Vrad --/F NONAME1.E_VRAD --/U km/sec
VradProv varchar(64) not null default 'NONE', --/D Provenance of VRAD (SNR & VSINI) by source and setup, eg. CASU|HR10  --/F NONAME1.PROV_VRAD
VradOffset real not null default -9.999995e+08, --/D Offset applied to VRAD calculated per SETUP to HR10 (Full details in WG15 report) --/F NONAME1.VRAD_OFFSET --/U km/sec
VradFilename varchar(400) not null default 'NONE', --/D Spectral file(s) used for determination of VRAD (SNR & VSINI) Recommended Result --/F NONAME1.VRAD_FILENAME
vsini real not null default -9.999995e+08, --/D Rotational Velocity from Node/WG analysis --/F NONAME1.VSINI --/U km/sec
vsiniErr real not null default -9.999995e+08, --/D Error on Vsini --/F NONAME1.E_VSINI --/U km/sec
vsiniLim smallint not null default -9999, --/D Flag on upper limits of vsini  --/N -1 --/F NONAME1.LIM_VSINI
TeffPhot real not null default -9.999995e+08, --/D Photometric Effective Temperature --/F NONAME1.TEFF_PHOT --/U K
TeffPhotErr real not null default -9.999995e+08, --/D Error on TeffPhot --/F NONAME1.E_TEFF_PHOT --/U K
TeffIrfm real not null default -9.999995e+08, --/D IRFM weighted average from 2MASS J,H,Ks Bands --/U K --/F NONAME1.TEFF_IRFM
TeffIrfmErr real not null default -9.999995e+08, --/D Error on TeffIrfm  --/F NONAME1.E_TEFF_IRFM
FbolIrfm real not null default -9.999995e+08, --/D Bolometric Flux from 2MASS  --/F NONAME1.FBOL_IRFM          
SpT varchar(10) not null default 'NONE', --/D Spectral type --/F NONAME1.SPT
veil real not null default -9.999995e+08, --/D Veiling --/F NONAME1.VEIL
veilErr real not null default -9.999995e+08, --/D Error on veil  --/F NONAME1.E_VEIL
EWLi real not null default -9.999995e+08, --/D Equivalent width of Li(6708) --/F NONAME1.EW_LI --/U mAngstroms
limEWLi smallint not null default -9999, --/D Upper limit flag on EWLi --/F NONAME1.LIM_EW_LI --/N -1
EWLiErr real not null default -9.999995e+08, --/D Error on EWLi --/F NONAME1.E_EW_LI --/U mAngstroms
EWLiProv varchar(4) not null default 'NONE',  --/D EWLi provenance; WG from which it is sourced  --/F NONAME1.PROVENANCE_EW_LI
EWcLi real not null default -9.999995e+08, --/D Blends-corrected Li(6708A) equivalent width --/F NONAME1.EWC_LI --/U mAngstroms
EWcLiLim smallint not null default -9999, --/D Flag on upper limit on EWcLi  --/N -1 --/F NONAME1.LIM_EWC_LI
EWcLiErr real not null default -9.999995e+08, --/D Error on EWcLi --/F NONAME1.E_EWC_LI --/U mAngstroms
EWHaAcc real not null default -9.999995e+08, --/D Equivalent width of Halpha (accretion) --/F NONAME1.EW_HA_ACC --/U Angstroms
EWHaAccErr real not null default -9.999995e+08, --/D Error on EWHaAcc --/F NONAME1.E_EW_HA_ACC --/U Angstroms
Ha10 real not null default -9.999995e+08, --/D Halpha width at 10% of peak (accretion) --/F NONAME1.HA10 --/U km/sec
Ha10Err real not null default -9.999995e+08, --/D Error on Ha10 --/F NONAME1.E_HA10 --/U km/sec
EWHaChr real not null default -9.999995e+08, --/D Equivalent width of Halpha (chromospheric activity) --/F NONAME1.EW_HA_CHR --/U Angstroms
EWHaChrErr real not null default -9.999995e+08, --/D Error on EWHaChr --/F NONAME1.E_EW_HA_CHR --/U Angstroms
EWHbChr real not null default -9.999995e+08, --/D Equivalent width of Hbeta (chromospheric activity) --/F NONAME1.EW_HB_CHR --/U Angstroms
EWHbChrErr real not null default -9.999995e+08, --/D Error on EWHbChr --/F NONAME1.E_EW_HB_CHR --/U Angstroms
logMdotAcc real not null default -9.999995e+08, --/D The log of the accretion rate --/F NONAME1.LOG_MDOT_ACC --/U Msolar/yr
logMdotAccErr real not null default -9.999995e+08, --/D Error on logMdotAcc --/F NONAME1.E_LOG_MDOT_ACC --/U Msolar/yr
logLAcc real not null default -9.999995e+08, --/D The log of the luminosity accretion rate --/F NONAME1.LOG_L_ACC --/U Msolar/yr
logLAccErr real not null default -9.999995e+08, --/D Error on LogLAcc --/F NONAME1.E_LOG_L_ACC --/U Msolar/yr
convol real not null default -9.999995e+08, --/D Synthetic spectra convolution factor --/F NONAME1.CONVOL --/U km/sec
convolErr real not null default -9.999995e+08, --/D Error on convol --/F NONAME1.E_CONVOL --/U km/sec
peculi varchar(256) not null default '  ', --/D Peculiarity Flag(s): WG14 Dict.1000-2999 --/F NONAME1.PECULI
remark varchar(100) not null default '  ', --/D Spec. Class. Flags(s): WG14 Dict. 3000-8999 --/F NONAME1.REMARK
tech varchar(2515) not null default '  ', --/D Technical Flag(s): WG14 Dict. 9000–15000 --/F NONAME1.TECH
TeffSysErr real not null default -9.999995e+08, --/D Systematic Error of the Effective Temperature --/F NONAME1.SYS_ERR_TEFF --/U K
loggSysErr real not null default -9.999995e+08, --/D Systematic Error of the Log Surface Gravity --/F NONAME1.SYS_ERR_LOGG --/U dex
FeHSysErr real not null default -9.999995e+08, --/D Systematic Error of the Metallicity from Fe line --/F NONAME1.SYS_ERR_FEH --/U dex
fHaChr real not null default -9.999995e+08, --/D H-alpha chromospheric flux --/F NONAME1.FHA_CHR --/U erg/cm^2/s/A
fHaChrErr real not null default -9.999995e+08, --/D Error on fHaChr --/F NONAME1.E_FHA_CHR --/U erg/cm^2/s/A
fHbChr real not null default -9.999995e+08, --/D H-beta chromospheric flux --/F NONAME1.FHB_CHR --/U erg/cm^2/s/A
fHbSysErr real not null default -9.999995e+08, --/D Error on fHbChr --/F NONAME1.E_FHB_CHR --/U erg/cm^2/s/A
fwzi real not null default -9.999995e+08, --/D H-alpha Full Width at Zero Intensity (accretion) --/F NONAME1.FWZI --/U Angstrom
fwziErr real not null default -9.999995e+08, --/D Error on fwzi --/F NONAME1.E_FWZI --/U Angstrom
gamma real not null default -9.999995e+08, --/D Gravity sensitive spectral index --/F NONAME1.GAMMA
gammaErr real not null default -9.999995e+08, --/D Error on gamma --/F NONAME1.E_GAMMA
mAlpha  real not null default -9.999995e+08, --/D MyGIsFOS grid interpolated [alpha/Fe] --/F NONAME1.M_ALPHA  --/U  dex
mGrid   varchar(3) not null default '---', --/D MyGIsFOS grid employed  --/F NONAME1.M_GRID        
mBroad  real not null default -9.999995e+08, --/D MyGISFOS broad applied to grid  --/F NONAME1.M_BROAD --/U km/sec
mLoops  smallint not null default -9999, --/D MyGIsFOS number of iterations  --/F NONAME1.M_LOOPS  --/N -1
mName varchar(20) not null default 'NONE', --/D MyGIsFOS internal unique dataset name  --/F NONAME1.M_NAME 
vmic real not null default -9.999995e+08, --/D Microturbulent velocity determined by Node --/F NONAME1.VMIC
vmac real not null default -9.999995e+08, --/D Macroturbulent velocity determined by Node --/F NONAME1.VMAC
limTeff smallint not null default -9999, --/D Flag on lower/upper limits of Teff --/F NONAME1.LIM_TEFF --/N -1
logQWind real not null default -9.999995e+08, --/D Stellar wind Q parameter --/F NONAME1.LOG_Q_WIND --/U dex
logQWindErr real not null default -9.999995e+08, --/D Error on stellar wind Q parameter --/F NONAME1.E_LOG_Q_WIND --/U dex
limLogQWind smallint not null default -9999, --/D Flag on lower/upper limits of LogQWind --/F NONAME1.LIM_LOG_Q_WIND --/N -1
nnLogQWind smallint not null default -9999, --/D Number of Node results used for logQWind --/F NONAME1.NN_LOG_Q_WIND --/N -1
pureVsini real not null default -9.999995e+08, --/D Pure rotational velocity calculated by node --/F NONAME1.PURE_VSINI --/U dex
vMacroturbulence real not null default -9.999995e+08, --/D Macroturbulent velocity --/F NONAME1.V_MACROTURBULENCE --/U dex
peculiHa varchar(16) not null default 'NONE', --/D PECULI flag per exposure, delimiter= --/F NONAME1.HALPHA_PECULI
tau real not null default -9.999995e+08, --/D Index tau from Damiani+2014 --/F NONAME1.TAU
tauErr real not null default -9.999995e+08, --/D Index tau error --/F NONAME1.TAU_ERR
mu real not null default -9.999995e+08, --/D Index mu from Damiani+2014 --/F NONAME1.MU
muErr real not null default -9.999995e+08, --/D Index mu error --/F NONAME1.MU_ERR
alphaW real not null default -9.999995e+08, --/D Index alpha_w from Damiani+2014 --/F NONAME1.ALPHA_W
alphaWErr real not null default -9.999995e+08, --/D Index alpha_w error --/F NONAME1.ALPHA_W_ERR
alphaC real not null default -9.999995e+08, --/D Index alpha_c from Damiani+2014 --/F NONAME1.ALPHA_C
alphaCErr real not null default -9.999995e+08, --/D Index alpha_c error --/F NONAME1.ALPHA_C_ERR
betaT real not null default -9.999995e+08, --/D Index beta_t from Damiani+2014 --/F NONAME1.BETA_T
betaTErr real not null default -9.999995e+08, --/D Index beta_t error --/F NONAME1.BETA_T_ERR
gamma1 real not null default -9.999995e+08, --/D Index gamma_1 from Damiani+2014 --/F NONAME1.GAM_1
gamma1Err real not null default -9.999995e+08, --/D Index gamma_1 error --/F NONAME1.GAM_1_ERR
zeta1 real not null default -9.999995e+08, --/D Index zeta_1 from Damiani+2014 --/F NONAME1.ZETA_1
zeta1Err real not null default -9.999995e+08, --/D Index zeta_1 error --/F NONAME1.ZETA_1_ERR
Teff0 real not null default -9.999995e+08, --/D Teff_0 assuming solar metallicity --/F NONAME1.TEFF_0
Teff0Err real not null default -9.999995e+08, --/D Teff_0 error --/F NONAME1.TEFF_0_ERR
logg0 real not null default -9.999995e+08, --/D log_g_0 assuming solar metallicity --/F NONAME1.LOGG_0
logg0Err real not null default -9.999995e+08, --/D log_g_0 error --/F NONAME1.LOGG_0_ERR
Teff1 real not null default -9.999995e+08, --/D Teff_1 before vsini/veiling correction --/F NONAME1.TEFF_1
Teff1Err real not null default -9.999995e+08, --/D Teff_1 error --/F NONAME1.TEFF_1_ERR
logg1 real not null default -9.999995e+08, --/D log_g_1 before vsini/veiling correction --/F NONAME1.LOGG_1
logg1Err real not null default -9.999995e+08, --/D log_g_1 error --/F NONAME1.LOGG_1_ERR
FeH1 real not null default -9.999995e+08, --/D Fe/H_1 before vsini/veiling correction --/F NONAME1.FEH_1
FeH1Err real not null default -9.999995e+08, --/D Fe/H_1 error --/F NONAME1.FEH_1_ERR
--
-- Insert abundance columns here.
--
Al1 real not null default -9.999995e+08, --/D aluminium I: abundance  --/F NONAME1.AL1 --/U dex
upperCombinedAl1 smallint not null default 0, --/D aluminium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_AL1
Al1Err real not null default -9.999995e+08, --/D aluminium I: error  --/F NONAME1.E_AL1 --/U dex
nnAl1 smallint not null default -9999, --/D aluminium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_AL1
nnAl1Err real not null default -9.999995e+08, --/D aluminium I: error from node errors  --/F NONAME1.ENN_AL1 --/U dex --/N -1.0
nlAl1 smallint not null default -9999, --/D aluminium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_AL1
Al1Prov varchar(4) not null default 'NONE',  --/D aluminium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_AL1
Al2 real not null default -9.999995e+08, --/D aluminium II: abundance  --/F NONAME1.AL2 --/U dex
upperAl2 smallint not null default 0, --/D aluminium II: flag on AL2 measurement type --/N -1 --/F NONAME1.UPPER_AL2
Al2Err real not null default -9.999995e+08, --/D aluminium II: error  --/F NONAME1.E_AL2 --/U dex
nnAl2 smallint not null default -9999, --/D aluminium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_AL2
nnAl2Err real not null default -9.999995e+08, --/D aluminium II: error from node errors  --/F NONAME1.ENN_AL2 --/U dex --/N -1.0
nlAl2 smallint not null default -9999, --/D aluminium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_AL2
Al2Prov varchar(4) not null default 'NONE',  --/D aluminium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_AL2
Al3 real not null default -9.999995e+08, --/D aluminium III: abundance  --/F NONAME1.AL3 --/U dex
upperAl3 smallint not null default 0, --/D  Carbon II: flag on AL3 measurement type --/N -1 --/F NONAME1.UPPER_AL3
Al3Err real not null default -9.999995e+08, --/D aluminium III: error  --/F NONAME1.E_AL3 --/U dex
nnAl3 smallint not null default -9999, --/D aluminium III: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_AL3
nnAl3Err real not null default -9.999995e+08, --/D aluminium III: error from node errors  --/F NONAME1.ENN_AL3 --/U dex --/N -1.0
nlAl3 smallint not null default -9999, --/D aluminium III: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_AL3
Al3Prov varchar(4) not null default 'NONE',  --/D aluminium III: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_AL3
Ba2 real not null default -9.999995e+08, --/D Barium II: abundance  --/F NONAME1.BA2 --/U dex
upperBa2 smallint not null default 0, --/D Barium II: flag on BA2 measurement type --/N -1 --/F NONAME1.UPPER_BA2
Ba2Err real not null default -9.999995e+08, --/D Barium II: error  --/F NONAME1.E_BA2 --/U dex
nnBa2 smallint not null default -9999, --/D Barium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_BA2
nnBa2Err real not null default -9.999995e+08, --/D Barium II: error from node errors  --/F NONAME1.ENN_BA2 --/U dex --/N -1.0
nlBa2 smallint not null default -9999, --/D Barium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_BA2
Ba2Prov varchar(4) not null default 'NONE',  --/D Barium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_BA2
C1 real not null default -9.999995e+08, --/D  Carbon I: abundance  --/F NONAME1.C1 --/U dex
upperCombinedC1 smallint not null default 0, --/D  Carbon I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_C1
C1Err real not null default -9.999995e+08, --/D  Carbon I: error  --/F NONAME1.E_C1 --/U dex
nnC1 smallint not null default -9999, --/D  Carbon I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_C1
nnC1Err real not null default -9.999995e+08, --/D  Carbon I: error from node errors  --/F NONAME1.ENN_C1 --/U dex --/N -1.0
nlC1 smallint not null default -9999, --/D  Carbon I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_C1
C1Prov varchar(4) not null default 'NONE',  --/D  Carbon I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_C1
C2 real not null default -9.999995e+08, --/D  Carbon II: abundance  --/F NONAME1.C2 --/U dex
upperC2 smallint not null default 0, --/D  Carbon II: flag on C2 measurement type --/N -1 --/F NONAME1.UPPER_C2
C2Err real not null default -9.999995e+08, --/D  Carbon II: error  --/F NONAME1.E_C2 --/U dex
nnC2 smallint not null default -9999, --/D  Carbon II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_C2
nnC2Err real not null default -9.999995e+08, --/D  Carbon II: error from node errors  --/F NONAME1.ENN_C2 --/U dex --/N -1.0
nlC2 smallint not null default -9999, --/D  Carbon II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_C2
C2Prov varchar(4) not null default 'NONE',  --/D  Carbon II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_C2
C3 real not null default -9.999995e+08, --/D  Carbon III: abundance  --/F NONAME1.C3 --/U dex
upperC3 smallint not null default 0, --/D  Carbon II: flag on C3 measurement type --/N -1 --/F NONAME1.UPPER_C3
C3Err real not null default -9.999995e+08, --/D  Carbon III: error  --/F NONAME1.E_C3 --/U dex
nnC3 smallint not null default -9999, --/D  Carbon III: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_C3
nnC3Err real not null default -9.999995e+08, --/D  Carbon III: error from node errors  --/F NONAME1.ENN_C3 --/U dex --/N -1.0
nlC3 smallint not null default -9999, --/D  Carbon III: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_C3
C3Prov varchar(4) not null default 'NONE',  --/D  Carbon III: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_C3
CC2 real not null default -9.999995e+08, --/D C2 Molecular Bands: abundance  --/F NONAME1.C_C2 --/U dex
upperCC2 smallint not null default 0, --/D C2 Molecular Bands: flag on C_C2 measurement type  --/N -1 --/F NONAME1.UPPER_C_C2
CC2Err real not null default -9.999995e+08, --/D C2 Molecular Bands: error  --/F NONAME1.E_C_C2 --/U dex
nnCC2 smallint not null default -9999, --/D C2 Molecular Bands: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_C_C2
nnCC2Err real not null default -9.999995e+08, --/D C2 Molecular Bands: error from node errors  --/F NONAME1.ENN_C_C2 --/U dex --/N -1.0
nlCC2 smallint not null default -9999, --/D C2 Molecular Bands: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_C_C2
CC2Prov varchar(4) not null default 'NONE',  --/D C2 Molecular Bands: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_C_C2
Ca1 real not null default -9.999995e+08, --/D Calcium I: abundance  --/F NONAME1.CA1 --/U dex
upperCombinedCa1 smallint not null default 0, --/D Calcium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_CA1
Ca1Err real not null default -9.999995e+08, --/D Calcium I: error  --/F NONAME1.E_CA1 --/U dex
nnCa1 smallint not null default -9999, --/D Calcium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CA1
nnCa1Err real not null default -9.999995e+08, --/D Calcium I: error from node errors  --/F NONAME1.ENN_CA1 --/U dex --/N -1.0
nlCa1 smallint not null default -9999, --/D Calcium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CA1
Ca1Prov varchar(4) not null default 'NONE',  --/D Calcium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CA1
Ca2 real not null default -9.999995e+08, --/D Calcium I: abundance  --/F NONAME1.CA2 --/U dex
upperCa2 smallint not null default 0, --/D Calcium I: flag on CA2 measurement type --/N -1 --/F NONAME1.UPPER_CA2
Ca2Err real not null default -9.999995e+08, --/D Calcium I: error  --/F NONAME1.E_CA2 --/U dex
nnCa2 smallint not null default -9999, --/D Calcium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CA2
nnCa2Err real not null default -9.999995e+08, --/D Calcium I: error from node errors  --/F NONAME1.ENN_CA2 --/U dex --/N -1.0
nlCa2 smallint not null default -9999, --/D Calcium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CA2
Ca2Prov varchar(4) not null default 'NONE',  --/D Calcium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CA2
Ce2 real not null default -9.999995e+08, --/D Cerium II: abundance  --/F NONAME1.CE2 --/U dex
upperCe2 smallint not null default 0, --/D Cerium II: flag on CE2 measurement type --/N -1 --/F NONAME1.UPPER_CE2
Ce2Err real not null default -9.999995e+08, --/D Cerium II: error  --/F NONAME1.E_CE2 --/U dex
nnCe2 smallint not null default -9999, --/D Cerium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CE2
nnCe2Err real not null default -9.999995e+08, --/D Cerium II: error from node errors  --/F NONAME1.ENN_CE2 --/U dex --/N -1.0
nlCe2 smallint not null default -9999, --/D Cerium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CE2
Ce2Prov varchar(4) not null default 'NONE',  --/D Cerium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CE2
Co1 real not null default -9.999995e+08, --/D Cobalt I: abundance  --/F NONAME1.CO1 --/U dex
upperCombinedCo1 smallint not null default 0, --/D Cobalt I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_CO1
Co1Err real not null default -9.999995e+08, --/D Cobalt I: error  --/F NONAME1.E_CO1 --/U dex
nnCo1 smallint not null default -9999, --/D Cobalt I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CO1
nnCo1Err real not null default -9.999995e+08, --/D Cobalt I: error from node errors  --/F NONAME1.ENN_CO1 --/U dex --/N -1.0
nlCo1 smallint not null default -9999, --/D Cobalt I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CO1
Co1Prov varchar(4) not null default 'NONE',  --/D Cobalt I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CO1
Cr1 real not null default -9.999995e+08, --/D Chromium I: abundance  --/F NONAME1.CR1 --/U dex
upperCombinedCr1 smallint not null default 0, --/D Chromium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_CR1
Cr1Err real not null default -9.999995e+08, --/D Chromium I: error  --/F NONAME1.E_CR1 --/U dex
nnCr1 smallint not null default -9999, --/D Chromium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CR1
nnCr1Err real not null default -9.999995e+08, --/D Chromium I: error from node errors  --/F NONAME1.ENN_CR1 --/U dex --/N -1.0
nlCr1 smallint not null default -9999, --/D Chromium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CR1
Cr1Prov varchar(4) not null default 'NONE',  --/D Chromium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CR1
Cr2 real not null default -9.999995e+08, --/D Chromium II: abundance  --/F NONAME1.CR2 --/U dex
upperCr2 smallint not null default 0, --/D Chromium II: flag on CR2 measurement type --/N -1 --/F NONAME1.UPPER_CR2
Cr2Err real not null default -9.999995e+08, --/D Chromium II: error  --/F NONAME1.E_CR2 --/U dex
nnCr2 smallint not null default -9999, --/D Chromium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CR2
nnCr2Err real not null default -9.999995e+08, --/D Chromium II: error from node errors  --/F NONAME1.ENN_CR2 --/U dex --/N -1.0
nlCr2 smallint not null default -9999, --/D Chromium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CR2
Cr2Prov varchar(4) not null default 'NONE',  --/D Chromium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CR2
Cu1 real not null default -9.999995e+08, --/D Copper I: abundance  --/F NONAME1.CU1 --/U dex
upperCombinedCu1 smallint not null default 0, --/D Copper I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_CU1
Cu1Err real not null default -9.999995e+08, --/D Copper I: error  --/F NONAME1.E_CU1 --/U dex
nnCu1 smallint not null default -9999, --/D Copper I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_CU1
nnCu1Err real not null default -9.999995e+08, --/D Copper I: error from node errors  --/F NONAME1.ENN_CU1 --/U dex --/N -1.0
nlCu1 smallint not null default -9999, --/D Copper I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_CU1
Cu1Prov varchar(4) not null default 'NONE',  --/D Copper I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_CU1
Dy2 real not null default -9.999995e+08, --/D Dysprosium II: abundance  --/F NONAME1.DY2 --/U dex
upperDy2 smallint not null default 0, --/D Dysprosium II: flag on DY2 measurement type --/N -1 --/F NONAME1.UPPER_DY2
Dy2Err real not null default -9.999995e+08, --/D Dysprosium II: error  --/F NONAME1.E_DY2 --/U dex
nnDy2 smallint not null default -9999, --/D Dysprosium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_DY2
nnDy2Err real not null default -9.999995e+08, --/D Dysprosium II: error from node errors  --/F NONAME1.ENN_DY2 --/U dex --/N -1.0
nlDy2 smallint not null default -9999, --/D Dysprosium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_DY2
Dy2Prov varchar(4) not null default 'NONE',  --/D Dysprosium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_DY2
Eu2 real not null default -9.999995e+08, --/D Europium II: abundance  --/F NONAME1.EU2 --/U dex
upperCombinedEu2 smallint not null default 0, --/D Europium II: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_EU2
Eu2Err real not null default -9.999995e+08, --/D Europium II: error  --/F NONAME1.E_EU2 --/U dex
nnEu2 smallint not null default -9999, --/D Europium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_EU2
nnEu2Err real not null default -9.999995e+08, --/D Europium II: error from node errors  --/F NONAME1.ENN_EU2 --/U dex --/N -1.0
nlEu2 smallint not null default -9999, --/D Europium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_EU2
Eu2Prov varchar(4) not null default 'NONE',  --/D Europium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_EU2
Fe1 real not null default -9.999995e+08, --/D Iron I: abundance  --/F NONAME1.FE1 --/U dex
upperCombinedFe1 smallint not null default 0, --/D Iron I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_FE1
Fe1Err real not null default -9.999995e+08, --/D Iron I: error  --/F NONAME1.E_FE1 --/U dex
nnFe1 smallint not null default -9999, --/D Iron I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_FE1
nnFe1Err real not null default -9.999995e+08, --/D Iron I: error from node errors  --/F NONAME1.ENN_FE1 --/U dex --/N -1.0
nlFe1 smallint not null default -9999, --/D Iron I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_FE1
Fe1Prov varchar(4) not null default 'NONE',  --/D Iron I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_FE1
Fe2 real not null default -9.999995e+08, --/D Iron II: abundance  --/F NONAME1.FE2 --/U dex
upperFe2 smallint not null default 0, --/D Iron II: flag on FE2 measurement type --/N -1 --/F NONAME1.UPPER_FE2
Fe2Err real not null default -9.999995e+08, --/D Iron II: error  --/F NONAME1.E_FE2 --/U dex
nnFe2 smallint not null default -9999, --/D Iron II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_FE2
nnFe2Err real not null default -9.999995e+08, --/D Iron II: error from node errors  --/F NONAME1.ENN_FE2 --/U dex --/N -1.0
nlFe2 smallint not null default -9999, --/D Iron II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_FE2
Fe2Prov varchar(4) not null default 'NONE',  --/D Iron II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_FE2
Fe3 real not null default -9.999995e+08, --/D Iron III: abundance  --/F NONAME1.FE3 --/U dex
upperFe3 smallint not null default 0, --/D  Carbon II: flag on FE3 measurement type --/N -1 --/F NONAME1.UPPER_FE3
Fe3Err real not null default -9.999995e+08, --/D Iron III: error  --/F NONAME1.E_FE3 --/U dex
nnFe3 smallint not null default -9999, --/D Iron III: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_FE3
nnFe3Err real not null default -9.999995e+08, --/D Iron III: error from node errors  --/F NONAME1.ENN_FE3 --/U dex --/N -1.0
nlFe3 smallint not null default -9999, --/D Iron III: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_FE3
Fe3Prov varchar(4) not null default 'NONE',  --/D Iron III: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_FE3
Gd2 real not null default -9.999995e+08, --/D Gadolinium II: abundance  --/F NONAME1.GD2 --/U dex
upperGd2 smallint not null default 0, --/D Gadolinium II: flag on GD2 measurement type --/N -1 --/F NONAME1.UPPER_GD2
Gd2Err real not null default -9.999995e+08, --/D Gadolinium II: error  --/F NONAME1.E_GD2 --/U dex
nnGd2 smallint not null default -9999, --/D Gadolinium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_GD2
nnGd2Err real not null default -9.999995e+08, --/D Gadolinium II: error from node errors  --/F NONAME1.ENN_GD2 --/U dex --/N -1.0
nlGd2 smallint not null default -9999, --/D Gadolinium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_GD2
Gd2Prov varchar(4) not null default 'NONE',  --/D Gadolinium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_GD2
He1 real not null default -9.999995e+08, --/D Helium I: abundance  --/F NONAME1.HE1 --/U dex
upperCombinedHe1 smallint not null default 0, --/D Helium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_HE1
He1Err real not null default -9.999995e+08, --/D Helium I: error  --/F NONAME1.E_HE1 --/U dex
nnHe1 smallint not null default -9999, --/D Helium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_HE1
nnHe1Err real not null default -9.999995e+08, --/D Helium I: error from node errors  --/F NONAME1.ENN_HE1 --/U dex --/N -1.0
nlHe1 smallint not null default -9999, --/D Helium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_HE1
He1Prov varchar(4) not null default 'NONE',  --/D Helium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_HE1
La2 real not null default -9.999995e+08, --/D Lanthanum II: abundance  --/F NONAME1.LA2 --/U dex
upperLa2 smallint not null default 0, --/D Lanthanum II: flag on LA2 measurement type --/N -1 --/F NONAME1.UPPER_LA2
La2Err real not null default -9.999995e+08, --/D Lanthanum II: error  --/F NONAME1.E_LA2 --/U dex
nnLa2 smallint not null default -9999, --/D Lanthanum II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_LA2
nnLa2Err real not null default -9.999995e+08, --/D Lanthanum II: error from node errors  --/F NONAME1.ENN_LA2 --/U dex --/N -1.0
nlLa2 smallint not null default -9999, --/D Lanthanum II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_LA2
La2Prov varchar(4) not null default 'NONE',  --/D Lanthanum II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_LA2
Li1 real not null default -9.999995e+08, --/D Lithium I: abundance  --/F NONAME1.LI1 --/U dex
upperCombinedLi1 smallint not null default 0, --/D Lithium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_LI1
Li1Err real not null default -9.999995e+08, --/D Lithium I: error  --/F NONAME1.E_LI1 --/U dex
nnLi1 smallint not null default -9999, --/D Lithium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_LI1
nnLi1Err real not null default -9.999995e+08, --/D Lithium I: error from node errors  --/F NONAME1.ENN_LI1 --/U dex --/N -1.0
nlLi1 smallint not null default -9999, --/D Lithium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_LI1
Li1Prov varchar(4) not null default 'NONE',  --/D Lithium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_LI1
Mg1 real not null default -9.999995e+08, --/D Magnesium I: abundance  --/F NONAME1.MG1 --/U dex
upperCombinedMg1 smallint not null default 0, --/D Magnesium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_MG1
Mg1Err real not null default -9.999995e+08, --/D Magnesium I: error  --/F NONAME1.E_MG1 --/U dex
nnMg1 smallint not null default -9999, --/D Magnesium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_MG1
nnMg1Err real not null default -9.999995e+08, --/D Magnesium I: error from node errors  --/F NONAME1.ENN_MG1 --/U dex --/N -1.0
nlMg1 smallint not null default -9999, --/D Magnesium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_MG1
Mg1Prov varchar(4) not null default 'NONE',  --/D Magnesium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_MG1
Mg2 real not null default -9.999995e+08, --/D Magnesium II: abundance  --/F NONAME1.MG2 --/U dex
upperMg2 smallint not null default 0, --/D Magnesium II: flag on MG2 measurement type --/N -1 --/F NONAME1.UPPER_MG2
Mg2Err real not null default -9.999995e+08, --/D Magnesium II: error  --/F NONAME1.E_MG2 --/U dex
nnMg2 smallint not null default -9999, --/D Magnesium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_MG2
nnMg2Err real not null default -9.999995e+08, --/D Magnesium II: error from node errors  --/F NONAME1.ENN_MG2 --/U dex --/N -1.0
nlMg2 smallint not null default -9999, --/D Magnesium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_MG2
Mg2Prov varchar(4) not null default 'NONE',  --/D Magnesium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_MG2
Mn1 real not null default -9.999995e+08, --/D Manganese I: abundance  --/F NONAME1.MN1 --/U dex
upperCombinedMn1 smallint not null default 0, --/D Manganese I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_MN1
Mn1Err real not null default -9.999995e+08, --/D Manganese I: error  --/F NONAME1.E_MN1 --/U dex
nnMn1 smallint not null default -9999, --/D Manganese I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_MN1
nnMn1Err real not null default -9.999995e+08, --/D Manganese I: error from node errors  --/F NONAME1.ENN_MN1 --/U dex --/N -1.0
nlMn1 smallint not null default -9999, --/D Manganese I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_MN1
Mn1Prov varchar(4) not null default 'NONE',  --/D Manganese I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_MN1
Mo1 real not null default -9.999995e+08, --/D Molybdenum I: abundance  --/F NONAME1.MO1 --/U dex
upperCombinedMo1 smallint not null default 0, --/D Molybdenum I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_MO1
Mo1Err real not null default -9.999995e+08, --/D Molybdenum I: error  --/F NONAME1.E_MO1 --/U dex
nnMo1 smallint not null default -9999, --/D Molybdenum I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_MO1
nnMo1Err real not null default -9.999995e+08, --/D Molybdenum I: error from node errors  --/F NONAME1.ENN_MO1 --/U dex --/N -1.0
nlMo1 smallint not null default -9999, --/D Molybdenum I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_MO1
Mo1Prov varchar(4) not null default 'NONE',  --/D Molybdenum I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_MO1
N2 real not null default -9.999995e+08, --/D  Nitrogen II: abundance  --/F NONAME1.N2 --/U dex
upperN2 smallint not null default 0, --/D  Nitrogen II: flag on N2 measurement type --/N -1 --/F NONAME1.UPPER_N2
N2Err real not null default -9.999995e+08, --/D  Nitrogen II: error  --/F NONAME1.E_N2 --/U dex
nnN2 smallint not null default -9999, --/D  Nitrogen II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_N2
nnN2Err real not null default -9.999995e+08, --/D  Nitrogen II: error from node errors  --/F NONAME1.ENN_N2 --/U dex --/N -1.0
nlN2 smallint not null default -9999, --/D  Nitrogen II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_N2
N2Prov varchar(4) not null default 'NONE',  --/D  Nitrogen II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_N2
N3 real not null default -9.999995e+08, --/D  Nitrogen III: abundance  --/F NONAME1.N3 --/U dex
upperN3 smallint not null default 0, --/D  Carbon II: flag on N3 measurement type --/N -1 --/F NONAME1.UPPER_N3
N3Err real not null default -9.999995e+08, --/D  Nitrogen III: error  --/F NONAME1.E_N3 --/U dex
nnN3 smallint not null default -9999, --/D  Nitrogen III: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_N3
nnN3Err real not null default -9.999995e+08, --/D  Nitrogen III: error from node errors  --/F NONAME1.ENN_N3 --/U dex --/N -1.0
nlN3 smallint not null default -9999, --/D  Nitrogen III: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_N3
N3Prov varchar(4) not null default 'NONE',  --/D  Nitrogen III: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_N3
NCN real not null default -9.999995e+08, --/D  CN Molecular Bands: abundance  --/F NONAME1.N_CN --/U dex
upperNCN smallint not null default 0, --/D  CN Molecular Bands: flag on N_CN measurement type --/N -1 --/F NONAME1.UPPER_N_CN
NCNErr real not null default -9.999995e+08, --/D  CN Molecular Bands: error  --/F NONAME1.E_N_CN --/U dex
nnNCN smallint not null default -9999, --/D  CN Molecular Bands: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_N_CN
nnNCNErr real not null default -9.999995e+08, --/D  CN Molecular Bands: error from node errors  --/F NONAME1.ENN_N_CN --/U dex --/N -1.0
nlNCN smallint not null default -9999, --/D  CN Molecular Bands: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_N_CN
NCNProv varchar(4) not null default 'NONE',  --/D  CN Molecular Bands: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_N_CN
Na1 real not null default -9.999995e+08, --/D Sodium I: abundance  --/F NONAME1.NA1 --/U dex
upperCombinedNa1 smallint not null default 0, --/D Sodium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_NA1
Na1Err real not null default -9.999995e+08, --/D Sodium I: error  --/F NONAME1.E_NA1 --/U dex
nnNa1 smallint not null default -9999, --/D Sodium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_NA1
nnNa1Err real not null default -9.999995e+08, --/D Sodium I: error from node errors  --/F NONAME1.ENN_NA1 --/U dex --/N -1.0
nlNa1 smallint not null default -9999, --/D Sodium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_NA1
Na1Prov varchar(4) not null default 'NONE',  --/D Sodium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_NA1
Nb1 real not null default -9.999995e+08, --/D Niobium I: abundance  --/F NONAME1.NB1 --/U dex
upperCombinedNb1 smallint not null default 0, --/D Niobium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_NB1
Nb1Err real not null default -9.999995e+08, --/D Niobium I: error  --/F NONAME1.E_NB1 --/U dex
nnNb1 smallint not null default -9999, --/D Niobium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_NB1
nnNb1Err real not null default -9.999995e+08, --/D Niobium I: error from node errors  --/F NONAME1.ENN_NB1 --/U dex --/N -1.0
nlNb1 smallint not null default -9999, --/D Niobium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_NB1
Nb1Prov varchar(4) not null default 'NONE',  --/D Niobium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_NB1
Nd2 real not null default -9.999995e+08, --/D Neodymium II: abundance  --/F NONAME1.ND2 --/U dex
upperNd2 smallint not null default 0, --/D Neodymium II: flag on ND2 measurement type --/N -1 --/F NONAME1.UPPER_ND2
Nd2Err real not null default -9.999995e+08, --/D Neodymium II: error  --/F NONAME1.E_ND2 --/U dex
nnNd2 smallint not null default -9999, --/D Neodymium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_ND2
nnNd2Err real not null default -9.999995e+08, --/D Neodymium II: error from node errors  --/F NONAME1.ENN_ND2 --/U dex --/N -1.0
nlNd2 smallint not null default -9999, --/D Neodymium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_ND2
Nd2Prov varchar(4) not null default 'NONE',  --/D Neodymium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_ND2
Ne1 real not null default -9.999995e+08, --/D Neon I: abundance  --/F NONAME1.NE1 --/U dex
upperCombinedNe1 smallint not null default 0, --/D Neon I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_NE1
Ne1Err real not null default -9.999995e+08, --/D Neon I: error  --/F NONAME1.E_NE1 --/U dex
nnNe1 smallint not null default -9999, --/D Neon I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_NE1
nnNe1Err real not null default -9.999995e+08, --/D Neon I: error from node errors  --/F NONAME1.ENN_NE1 --/U dex --/N -1.0
nlNe1 smallint not null default -9999, --/D Neon I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_NE1
Ne1Prov varchar(4) not null default 'NONE',  --/D Neon I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_NE1
Ne2 real not null default -9.999995e+08, --/D Neon II: abundance  --/F NONAME1.NE2 --/U dex
upperNe2 smallint not null default 0, --/D Neon II: flag on NE2 measurement type --/N -1 --/F NONAME1.UPPER_NE2
Ne2Err real not null default -9.999995e+08, --/D Neon II: error  --/F NONAME1.E_NE2 --/U dex
nnNe2 smallint not null default -9999, --/D Neon II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_NE2
nnNe2Err real not null default -9.999995e+08, --/D Neon II: error from node errors  --/F NONAME1.ENN_NE2 --/U dex --/N -1.0
nlNe2 smallint not null default -9999, --/D Neon II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_NE2
Ne2Prov varchar(4) not null default 'NONE',  --/D Neon II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_NE2
Ni1 real not null default -9.999995e+08, --/D Nickel I: abundance  --/F NONAME1.NI1 --/U dex
upperCombinedNi1 smallint not null default 0, --/D Nickel I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_NI1
Ni1Err real not null default -9.999995e+08, --/D Nickel I: error  --/F NONAME1.E_NI1 --/U dex
nnNi1 smallint not null default -9999, --/D Nickel I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_NI1
nnNi1Err real not null default -9.999995e+08, --/D Nickel I: error from node errors  --/F NONAME1.ENN_NI1 --/U dex --/N -1.0
nlNi1 smallint not null default -9999, --/D Nickel I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_NI1
Ni1Prov varchar(4) not null default 'NONE',  --/D Nickel I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_NI1
O1 real not null default -9.999995e+08, --/D  Oxygen I: abundance  --/F NONAME1.O1 --/U dex
upperCombinedO1 smallint not null default 0, --/D  Oxygen I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_O1
O1Err real not null default -9.999995e+08, --/D  Oxygen I: error  --/F NONAME1.E_O1 --/U dex
nnO1 smallint not null default -9999, --/D  Oxygen I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_O1
nnO1Err real not null default -9.999995e+08, --/D  Oxygen I: error from node errors  --/F NONAME1.ENN_O1 --/U dex --/N -1.0
nlO1 smallint not null default -9999, --/D  Oxygen I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_O1
O1Prov varchar(4) not null default 'NONE',  --/D  Oxygen I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_O1
O2 real not null default -9.999995e+08, --/D  Oxygen II: abundance  --/F NONAME1.O2 --/U dex
upperO2 smallint not null default 0, --/D  Oxygen II: flag on O2 measurement type --/N -1 --/F NONAME1.UPPER_O2
O2Err real not null default -9.999995e+08, --/D  Oxygen II: error  --/F NONAME1.E_O2 --/U dex
nnO2 smallint not null default -9999, --/D  Oxygen II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_O2
nnO2Err real not null default -9.999995e+08, --/D  Oxygen II: error from node errors  --/F NONAME1.ENN_O2 --/U dex --/N -1.0
nlO2 smallint not null default -9999, --/D  Oxygen II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_O2
O2Prov varchar(4) not null default 'NONE',  --/D  Oxygen II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_O2
Pr2 real not null default -9.999995e+08, --/D Praseodymium II: abundance  --/F NONAME1.PR2 --/U dex
upperPr2 smallint not null default 0, --/D Praseodymium II: flag on PR2 measurement type --/N -1 --/F NONAME1.UPPER_PR2
Pr2Err real not null default -9.999995e+08, --/D Praseodymium II: error  --/F NONAME1.E_PR2 --/U dex
nnPr2 smallint not null default -9999, --/D Praseodymium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_PR2
nnPr2Err real not null default -9.999995e+08, --/D Praseodymium II: error from node errors  --/F NONAME1.ENN_PR2 --/U dex --/N -1.0
nlPr2 smallint not null default -9999, --/D Praseodymium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_PR2
Pr2Prov varchar(4) not null default 'NONE',  --/D Praseodymium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_PR2
Ru1 real not null default -9.999995e+08, --/D Ruthenium I: abundance  --/F NONAME1.RU1 --/U dex
upperCombinedRu1 smallint not null default 0, --/D Ruthenium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_RU1
Ru1Err real not null default -9.999995e+08, --/D Ruthenium I: error  --/F NONAME1.E_RU1 --/U dex
nnRu1 smallint not null default -9999, --/D Ruthenium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_RU1
nnRu1Err real not null default -9.999995e+08, --/D Ruthenium I: error from node errors  --/F NONAME1.ENN_RU1 --/U dex --/N -1.0
nlRu1 smallint not null default -9999, --/D Ruthenium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_RU1
Ru1Prov varchar(4) not null default 'NONE',  --/D Ruthenium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_RU1
S1 real not null default -9.999995e+08, --/D  Sulfur I: abundance  --/F NONAME1.S1 --/U dex
upperCombinedS1 smallint not null default 0, --/D  Sulfur I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_S1
S1Err real not null default -9.999995e+08, --/D  Sulfur I: error  --/F NONAME1.E_S1 --/U dex
nnS1 smallint not null default -9999, --/D  Sulfur I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_S1
nnS1Err real not null default -9.999995e+08, --/D  Sulfur I: error from node errors  --/F NONAME1.ENN_S1 --/U dex --/N -1.0
nlS1 smallint not null default -9999, --/D  Sulfur I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_S1
S1Prov varchar(4) not null default 'NONE',  --/D  Sulfur I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_S1
S2 real not null default -9.999995e+08, --/D  Sulfur II: abundance  --/F NONAME1.S2 --/U dex
upperS2 smallint not null default 0, --/D  Sulfur II: flag on S2 measurement type  --/N -1 --/F NONAME1.UPPER_S2
S2Err real not null default -9.999995e+08, --/D  Sulfur II: error  --/F NONAME1.E_S2 --/U dex
nnS2 smallint not null default -9999, --/D  Sulfur II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_S2
nnS2Err real not null default -9.999995e+08, --/D  Sulfur II: error from node errors  --/F NONAME1.ENN_S2 --/U dex --/N -1.0
nlS2 smallint not null default -9999, --/D  Sulfur II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_S2
S2Prov varchar(4) not null default 'NONE',  --/D  Sulfur II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_S2
S3 real not null default -9.999995e+08, --/D  Sulfur III: abundance  --/F NONAME1.S3 --/U dex
upperS3 smallint not null default 0, --/D  Carbon II: flag on S3 measurement type --/N -1 --/F NONAME1.UPPER_S3
S3Err real not null default -9.999995e+08, --/D  Sulfur III: error  --/F NONAME1.E_S3 --/U dex
nnS3 smallint not null default -9999, --/D  Sulfur III: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_S3
nnS3Err real not null default -9.999995e+08, --/D  Sulfur III: error from node errors  --/F NONAME1.ENN_S3 --/U dex --/N -1.0
nlS3 smallint not null default -9999, --/D  Sulfur III: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_S3
S3Prov varchar(4) not null default 'NONE',  --/D  Sulfur III: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_S3
Sc1 real not null default -9.999995e+08, --/D Scandium I: abundance  --/F NONAME1.SC1 --/U dex
upperCombinedSc1 smallint not null default 0, --/D Scandium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_SC1
Sc1Err real not null default -9.999995e+08, --/D Scandium I: error  --/F NONAME1.E_SC1 --/U dex
nnSc1 smallint not null default -9999, --/D Scandium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SC1
nnSc1Err real not null default -9.999995e+08, --/D Scandium I: error from node errors  --/F NONAME1.ENN_SC1 --/U dex --/N -1.0
nlSc1 smallint not null default -9999, --/D Scandium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SC1
Sc1Prov varchar(4) not null default 'NONE',  --/D Scandium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SC1
Sc2 real not null default -9.999995e+08, --/D Scandium II: abundance  --/F NONAME1.SC2 --/U dex
upperSc2 smallint not null default 0, --/D Scandium II: flag on SC2 measurement type --/N -1 --/F NONAME1.UPPER_SC2
Sc2Err real not null default -9.999995e+08, --/D Scandium II: error  --/F NONAME1.E_SC2 --/U dex
nnSc2 smallint not null default -9999, --/D Scandium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SC2
nnSc2Err real not null default -9.999995e+08, --/D Scandium II: error from node errors  --/F NONAME1.ENN_SC2 --/U dex --/N -1.0
nlSc2 smallint not null default -9999, --/D Scandium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SC2
Sc2Prov varchar(4) not null default 'NONE',  --/D Scandium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SC2
Si1 real not null default -9.999995e+08, --/D Silicon I: abundance  --/F NONAME1.SI1 --/U dex
upperCombinedSi1 smallint not null default 0, --/D Silicon I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_SI1
Si1Err real not null default -9.999995e+08, --/D Silicon I: error  --/F NONAME1.E_SI1 --/U dex
nnSi1 smallint not null default -9999, --/D Silicon I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SI1
nnSi1Err real not null default -9.999995e+08, --/D Silicon I: error from node errors  --/F NONAME1.ENN_SI1 --/U dex --/N -1.0
nlSi1 smallint not null default -9999, --/D Silicon I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SI1
Si1Prov varchar(4) not null default 'NONE',  --/D Silicon I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SI1
Si2 real not null default -9.999995e+08, --/D Silicon II: abundance  --/F NONAME1.SI2 --/U dex
upperSi2 smallint not null default 0, --/D Silicon II: flag on SI2 measurement type  --/N -1 --/F NONAME1.UPPER_SI2
Si2Err real not null default -9.999995e+08, --/D Silicon II: error  --/F NONAME1.E_SI2 --/U dex
nnSi2 smallint not null default -9999, --/D Silicon II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SI2
nnSi2Err real not null default -9.999995e+08, --/D Silicon II: error from node errors  --/F NONAME1.ENN_SI2 --/U dex --/N -1.0
nlSi2 smallint not null default -9999, --/D Silicon II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SI2
Si2Prov varchar(4) not null default 'NONE',  --/D Silicon II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SI2
Si3 real not null default -9.999995e+08, --/D Silicon III: abundance  --/F NONAME1.SI3 --/U dex
upperSi3 smallint not null default 0, --/D  Carbon II: flag on SI3 measurement type --/N -1 --/F NONAME1.UPPER_SI3
Si3Err real not null default -9.999995e+08, --/D Silicon III: error  --/F NONAME1.E_SI3 --/U dex
nnSi3 smallint not null default -9999, --/D Silicon III: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SI3
nnSi3Err real not null default -9.999995e+08, --/D Silicon III: error from node errors  --/F NONAME1.ENN_SI3 --/U dex --/N -1.0
nlSi3 smallint not null default -9999, --/D Silicon III: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SI3
Si3Prov varchar(4) not null default 'NONE',  --/D Silicon III: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SI3
Si4 real not null default -9.999995e+08, --/D Silicon IV: abundance  --/F NONAME1.SI4 --/U dex
upperSi4 smallint not null default 0, --/D  Carbon II: flag on SI4 measurement type --/N -1 --/F NONAME1.UPPER_SI4
Si4Err real not null default -9.999995e+08, --/D Silicon IV: error  --/F NONAME1.E_SI4 --/U dex
nnSi4 smallint not null default -9999, --/D Silicon IV: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SI4
nnSi4Err real not null default -9.999995e+08, --/D Silicon IV: error from node errors  --/F NONAME1.ENN_SI4 --/U dex --/N -1.0
nlSi4 smallint not null default -9999, --/D Silicon IV: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SI4
Si4Prov varchar(4) not null default 'NONE',  --/D Silicon IV: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SI4
Sm2 real not null default -9.999995e+08, --/D Samarium II: abundance  --/F NONAME1.SM2 --/U dex
upperSm2 smallint not null default 0, --/D Samarium II: flag on SM2 measurement type --/N -1 --/F NONAME1.UPPER_SM2
Sm2Err real not null default -9.999995e+08, --/D Samarium II: error  --/F NONAME1.E_SM2 --/U dex
nnSm2 smallint not null default -9999, --/D Samarium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SM2
nnSm2Err real not null default -9.999995e+08, --/D Samarium II: error from node errors  --/F NONAME1.ENN_SM2 --/U dex --/N -1.0
nlSm2 smallint not null default -9999, --/D Samarium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SM2
Sm2Prov varchar(4) not null default 'NONE',  --/D Samarium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SM2
Sr1 real not null default -9.999995e+08, --/D Strontium I: abundance  --/F NONAME1.SR1 --/U dex
upperCombinedSr1 smallint not null default 0, --/D Strontium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_SR1
Sr1Err real not null default -9.999995e+08, --/D Strontium I: error  --/F NONAME1.E_SR1 --/U dex
nnSr1 smallint not null default -9999, --/D Strontium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_SR1
nnSr1Err real not null default -9.999995e+08, --/D Strontium I: error from node errors  --/F NONAME1.ENN_SR1 --/U dex --/N -1.0
nlSr1 smallint not null default -9999, --/D Strontium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_SR1
Sr1Prov varchar(4) not null default 'NONE',  --/D Strontium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_SR1
Ti1 real not null default -9.999995e+08, --/D Titanium I: abundance  --/F NONAME1.TI1 --/U dex
upperCombinedTi1 smallint not null default 0, --/D Titanium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_TI1
Ti1Err real not null default -9.999995e+08, --/D Titanium I: error  --/F NONAME1.E_TI1 --/U dex
nnTi1 smallint not null default -9999, --/D Titanium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_TI1
nnTi1Err real not null default -9.999995e+08, --/D Titanium I: error from node errors  --/F NONAME1.ENN_TI1 --/U dex --/N -1.0
nlTi1 smallint not null default -9999, --/D Titanium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_TI1
Ti1Prov varchar(4) not null default 'NONE',  --/D Titanium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_TI1
Ti2 real not null default -9.999995e+08, --/D Titanium II: abundance  --/F NONAME1.TI2 --/U dex
upperTi2 smallint not null default 0, --/D Titanium II: flag on TI2 measurement type --/N -1 --/F NONAME1.UPPER_TI2
Ti2Err real not null default -9.999995e+08, --/D Titanium II: error  --/F NONAME1.E_TI2 --/U dex
nnTi2 smallint not null default -9999, --/D Titanium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_TI2
nnTi2Err real not null default -9.999995e+08, --/D Titanium II: error from node errors  --/F NONAME1.ENN_TI2 --/U dex --/N -1.0
nlTi2 smallint not null default -9999, --/D Titanium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_TI2
Ti2Prov varchar(4) not null default 'NONE',  --/D Titanium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_TI2
V1 real not null default -9.999995e+08, --/D  Vanadium I: abundance  --/F NONAME1.V1 --/U dex
upperCombinedV1 smallint not null default 0, --/D  Vanadium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_V1
V1Err real not null default -9.999995e+08, --/D  Vanadium I: error  --/F NONAME1.E_V1 --/U dex
nnV1 smallint not null default -9999, --/D  Vanadium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_V1
nnV1Err real not null default -9.999995e+08, --/D  Vanadium I: error from node errors  --/F NONAME1.ENN_V1 --/U dex --/N -1.0
nlV1 smallint not null default -9999, --/D  Vanadium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_V1
V1Prov varchar(4) not null default 'NONE',  --/D  Vanadium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_V1
V2 real not null default -9.999995e+08, --/D  Vanadium II: abundance  --/F NONAME1.V2 --/U dex
upperV2 smallint not null default 0, --/D  Vanadium II: flag on V2 measurement type --/N -1 --/F NONAME1.UPPER_V2
V2Err real not null default -9.999995e+08, --/D  Vanadium II: error  --/F NONAME1.E_V2 --/U dex
nnV2 smallint not null default -9999, --/D  Vanadium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_V2
nnV2Err real not null default -9.999995e+08, --/D  Vanadium II: error from node errors  --/F NONAME1.ENN_V2 --/U dex --/N -1.0
nlV2 smallint not null default -9999, --/D  Vanadium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_V2
V2Prov varchar(4) not null default 'NONE',  --/D  Vanadium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_V2
Y1 real not null default -9.999995e+08, --/D  Yttrium I: abundance  --/F NONAME1.Y1 --/U dex
upperCombinedY1 smallint not null default 0, --/D  Yttrium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_Y1
Y1Err real not null default -9.999995e+08, --/D  Yttrium I: error  --/F NONAME1.E_Y1 --/U dex
nnY1 smallint not null default -9999, --/D  Yttrium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_Y1
nnY1Err real not null default -9.999995e+08, --/D  Yttrium I: error from node errors  --/F NONAME1.ENN_Y1 --/U dex --/N -1.0
nlY1 smallint not null default -9999, --/D  Yttrium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_Y1
Y1Prov varchar(4) not null default 'NONE',  --/D  Yttrium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_Y1
Y2 real not null default -9.999995e+08, --/D  Yttrium I: abundance  --/F NONAME1.Y2 --/U dex
upperY2 smallint not null default 0, --/D  Yttrium I: flag on Y2 measurement type --/N -1 --/F NONAME1.UPPER_Y2
Y2Err real not null default -9.999995e+08, --/D  Yttrium I: error  --/F NONAME1.E_Y2 --/U dex
nnY2 smallint not null default -9999, --/D  Yttrium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_Y2
nnY2Err real not null default -9.999995e+08, --/D  Yttrium I: error from node errors  --/F NONAME1.ENN_Y2 --/U dex --/N -1.0
nlY2 smallint not null default -9999, --/D  Yttrium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_Y2
Y2Prov varchar(4) not null default 'NONE',  --/D  Yttrium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_Y2
Zn1 real not null default -9.999995e+08, --/D Zinc I: abundance  --/F NONAME1.ZN1 --/U dex
upperCombinedZn1 smallint not null default 0, --/D Zinc I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_ZN1
Zn1Err real not null default -9.999995e+08, --/D Zinc I: error  --/F NONAME1.E_ZN1 --/U dex
nnZn1 smallint not null default -9999, --/D Zinc I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_ZN1
nnZn1Err real not null default -9.999995e+08, --/D Zinc I: error from node errors  --/F NONAME1.ENN_ZN1 --/U dex --/N -1.0
nlZn1 smallint not null default -9999, --/D Zinc I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_ZN1
Zn1Prov varchar(4) not null default 'NONE',  --/D Zinc I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_ZN1
Zr1 real not null default -9.999995e+08, --/D Zirconium I: abundance  --/F NONAME1.ZR1 --/U dex
upperCombinedZr1 smallint not null default 0, --/D Zirconium I: combined upper limit flag  --/N -1 --/F NONAME1.UPPER_COMBINED_ZR1
Zr1Err real not null default -9.999995e+08, --/D Zirconium I: error  --/F NONAME1.E_ZR1 --/U dex
nnZr1 smallint not null default -9999, --/D Zirconium I: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_ZR1
nnZr1Err real not null default -9.999995e+08, --/D Zirconium I: error from node errors  --/F NONAME1.ENN_ZR1 --/U dex --/N -1.0
nlZr1 smallint not null default -9999, --/D Zirconium I: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_ZR1
Zr1Prov varchar(4) not null default 'NONE',  --/D Zirconium I: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_ZR1
Zr2 real not null default -9.999995e+08, --/D Zirconium II: abundance  --/F NONAME1.ZR2 --/U dex
upperZr2 smallint not null default 0, --/D Zirconium II: flag on ZR2 measurement type --/N -1 --/F NONAME1.UPPER_ZR2
Zr2Err real not null default -9.999995e+08, --/D Zirconium II: error  --/F NONAME1.E_ZR2 --/U dex
nnZr2 smallint not null default -9999, --/D Zirconium II: number of node results used to compute abundance  --/N -1 --/F NONAME1.NN_ZR2
nnZr2Err real not null default -9.999995e+08, --/D Zirconium II: error from node errors  --/F NONAME1.ENN_ZR2 --/U dex --/N -1.0
nlZr2 smallint not null default -9999, --/D Zirconium II: number of spectral lines used used to compute abundance  --/N -1 --/F NONAME1.NL_ZR2
Zr2Prov varchar(4) not null default 'NONE',  --/D Zirconium II: provenance; WG from which abundance is sourced  --/F NONAME1.PROVENANCE_ZR2
--
-- End of abundance columns.
--
deprecated INTEGER not null default 0,         --/D Deprecated flag: coded as current=0 or deprecated !=0  --/C CODE_MISC  --/N 0  --/G allTables::deprecated
cuEventID  INTEGER not null default -99999999, --/D Unique identifier of ingestion event 
CONSTRAINT pk_AstroAnalysis PRIMARY KEY (specGroupID, wg, nodeID, isWgParams, uniqueness)
)GO

-- ----------------------------------------------------------------------------