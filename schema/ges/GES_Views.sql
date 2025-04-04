--=============================================================================
--
-- $Id: GES_Views.sql 644 2017-10-20 16:13:26Z EckhardSutorius $
--
-- Database schema file containing SQL to create the GES views.
--
-- Original author: 
--   Clive Davenhall, Information Services, University of Edinburgh.
--
--=============================================================================
--
-- USE GES
--GO
--
-------------------------------------------------------------------------------
-- ****************************************************************************
-- Views for the various selections on the line list table; just atomic lines
-- with hyper-fine splitting, just molecular lines etc.

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='LineMolAtomHfs')
   DROP VIEW LineMolAtomHfs
GO
CREATE VIEW GES.LineMolAtomHfs
-------------------------------------------------------------------------------
--/H LineMolAtomHfs contains molecular lines and atomic lines with HFS.
--
--/T View LineMolAtomHfs contains all the molecular lines and atomic lines
--/T including data for unresolved fine, hyper-fine or isotopic splitting,
--/T if present.

--/T 
--/T The contents of this view are more full documented in 'Line-lists
--/T for the Gaia-ESO Survey', version 4, produced by the GES line-list
--/T group, see:
--/T
--/T <a href="http://ges.roe.ac.uk/docs/linelists_report_v4.pdf">Line-lists for the Gaia-ESO Survey</a>
--/T   
--/T Note that this report describes FITS files containing the atomic data,
--/T not the database table available here.  The table contains exactly the
--/T same data, but obviously the FITS-specific parts of the document are not
--/T relevant.
--/T
--/T Also, for convenience the Line-list group has prepared a
--/T <a href="http://ges.roe.ac.uk/docs/GESreferencesv4all.bib">Bibtex file</a>
--/T containing all the references listed in the report and included as
--/T reference columns in the table (these columns have names of the form
--/T <i>something</i>Ref).
-------------------------------------------------------------------------------
AS
SELECT 
  l.*
FROM
  LineList l
WHERE
  l.ltype in (1, 2);
GO

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='LineMol')
   DROP VIEW LineMol
GO
CREATE VIEW GES.LineMol
-------------------------------------------------------------------------------
--/H LineMol contains only molecular lines.
--
--/T View LineMol contains only the complete set of molecular lines.
--/T 
--/T The contents of this view are more full documented in 'Line-lists
--/T for the Gaia-ESO Survey', version 4, produced by the GES line-list
--/T group, see:
--/T
--/T <a href="http://ges.roe.ac.uk/docs/linelists_report_v4.pdf">Line-lists for the Gaia-ESO Survey</a>
--/T   
--/T Note that this report describes FITS files containing the atomic data,
--/T not the database table available here.  The table contains exactly the
--/T same data, but obviously the FITS-specific parts of the document are not
--/T relevant.
--/T
--/T Also, for convenience the Line-list group has prepared a
--/T <a href="http://ges.roe.ac.uk/docs/GESreferencesv4all.bib">Bibtex file</a>
--/T containing all the references listed in the report and included as
--/T reference columns in the table (these columns have names of the form
--/T <i>something</i>Ref).
-------------------------------------------------------------------------------
AS
SELECT 
  l.*
FROM 
  LineList l 
WHERE 
  l.ltype = 1;


-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='LineAtomHfs')
   DROP VIEW LineAtomHfs

CREATE VIEW GES.LineAtomHfs
-------------------------------------------------------------------------------
--/H LineAtomHfs contains only atomic lines with HFS
--
--/T View LineAtomHfs contains only atomic lines including data for unresolved
--/T fine, hyper-fine or isotopic splitting, if present.

--/T 
--/T The contents of this view are more full documented in 'Line-lists
--/T for the Gaia-ESO Survey', version 4, produced by the GES line-list
--/T group, see:
--/T
--/T <a href="http://ges.roe.ac.uk/docs/linelists_report_v4.pdf">Line-lists for the Gaia-ESO Survey</a>
--/T   
--/T Note that this report describes FITS files containing the atomic data,
--/T not the database table available here.  The table contains exactly the
--/T same data, but obviously the FITS-specific parts of the document are not
--/T relevant.
--/T
--/T Also, for convenience the Line-list group has prepared a
--/T <a href="http://ges.roe.ac.uk/docs/GESreferencesv4all.bib">Bibtex file</a>
--/T containing all the references listed in the report and included as
--/T reference columns in the table (these columns have names of the form
--/T <i>something</i>Ref).
-------------------------------------------------------------------------------
AS
SELECT 
  l.*
FROM 
  LineList l 
WHERE 
  l.ltype = 2;


-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='LineAtomNoHfs')
   DROP VIEW LineAtomNoHfs

CREATE VIEW GES.LineAtomNoHfs
-------------------------------------------------------------------------------
--/H LineAtomHfs contains only atomic lines without HFS
--
--/T View LineAtomHfs contains only atomic lines excluding data for unresolved
--/T fine, hyper-fine or isotopic splitting.

--/T 
--/T The contents of this view are more full documented in 'Line-lists
--/T for the Gaia-ESO Survey', version 4, produced by the GES line-list
--/T group, see:
--/T
--/T <a href="http://ges.roe.ac.uk/docs/linelists_report_v4.pdf">Line-lists for the Gaia-ESO Survey</a>
--/T   
--/T Note that this report describes FITS files containing the atomic data,
--/T not the database table available here.  The table contains exactly the
--/T same data, but obviously the FITS-specific parts of the document are not
--/T relevant.
--/T
--/T Also, for convenience the Line-list group has prepared a
--/T <a href="http://ges.roe.ac.uk/docs/GESreferencesv4all.bib">Bibtex file</a>
--/T containing all the references listed in the report and included as
--/T reference columns in the table (these columns have names of the form
--/T <i>something</i>Ref).
-------------------------------------------------------------------------------
AS
SELECT 
  l.*
FROM 
  LineList l 
WHERE 
  l.ltype = 3;


--
-------------------------------------------------------------------------------
-- ****************************************************************************
-- Views for the various selections on the AstroAnalysis table:
--   RecommendedAstroAnalysis:   consolidated, WG15 parameters and abundances
--   WgRecommendedAstroAnalysis: WG recommended parameters and abundances (by each WG)
--   WpNaAstroAnalysis:          WG parameters, node abundances
--   NpNaAstroAnalysis:          node parameters, node abundances

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='RecommendedAstroAnalysis')
   DROP VIEW RecommendedAstroAnalysis

CREATE VIEW GES.RecommendedAstroAnalysis
-------------------------------------------------------------------------------
--/H Overall recommended astrophysical parameter and abundances analyses
--
--/T The final, overall astrophysical parameter and abundances for each star
--/T recommended by the GES Consortium.  These values have been collated and
--/T and assembled by GES working group 15.  They are the values most likely
--/T to be used by individuals not deeply involved in the GES Consortium.
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
-------------------------------------------------------------------------------
AS
SELECT specGroupID, nodeID, nodeName, recWg, ravailWg, wg, wgSource, isWgParams, GesType, specGroupStr, primKeyStr, uniqueness, aaID, releaseName, releaseDate, instrument, recGratings, ravailGratings, gratings, gesField, gesObject, constFiles, targetID, cName, Teff, TeffErr, nnTeff, ennTeff, nneTeff, logg, loggErr, nnlogg, ennlogg, nnelogg, limlogg, FeH, FeHErr, nnFeH, ennFeH, nneFeH, Xi, XiErr, nnXi, ennXi, nneXi, alphaFe, alphaFeErr, nnAlphaFe, alphaFeNodeErr, nnAlphaFeNodeErr, objRa, objDec, snr, radVel, radVelErr, rotVel, rotVelErr, Vrad, VradErr, VradProv, VradOffset, VradFilename, vsini, vsiniErr, vsiniLim, FbolIrfm, SpT, veil, veilErr, EWLi, limEWLi, EWLiErr, EWLiProv, EWcLi, EWcLiLim, EWcLiErr, EWHaAcc, EWHaAccErr, Ha10, Ha10Err, EWHaChr, EWHaChrErr, EWHbChr, EWHbChrErr, logMdotAcc, logMdotAccErr, peculi, remark, tech, TeffSysErr, loggSysErr, FeHSysErr, fHaChr, fHaChrErr, fHbChr, fHbSysErr, fwzi, fwziErr, gamma, gammaErr, mGrid, mName, vmic, vmac, limTeff, logQWind, logQWindErr, limLogQWind, nnLogQWind, pureVsini, vMacroturbulence, peculiHa, tau, tauErr, mu, muErr, alphaW, alphaWErr, alphaC, alphaCErr, betaT, betaTErr, gamma1, gamma1Err, zeta1, zeta1Err, Teff0, Teff0Err, logg0, logg0Err, Teff1, Teff1Err, logg1, logg1Err, FeH1, FeH1Err, Al1, upperCombinedAl1, Al1Err, nnAl1, nnAl1Err, nlAl1, Al1Prov, Al2, upperAl2, Al2Err, nnAl2, nnAl2Err, nlAl2, Al2Prov, Ba2, upperBa2, Ba2Err, nnBa2, nnBa2Err, nlBa2, Ba2Prov, C1, upperCombinedC1, C1Err, nnC1, nnC1Err, nlC1, C1Prov, C2, upperC2, C2Err, nnC2, nnC2Err, nlC2, C2Prov, C3, upperC3, C3Err, nnC3, nnC3Err, nlC3, C3Prov, CC2, upperCC2, CC2Err, nnCC2, nnCC2Err, nlCC2, CC2Prov, Ca1, upperCombinedCa1, Ca1Err, nnCa1, nnCa1Err, nlCa1, Ca1Prov, Ca2, upperCa2, Ca2Err, nnCa2, nnCa2Err, nlCa2, Ca2Prov, Ce2, upperCe2, Ce2Err, nnCe2, nnCe2Err, nlCe2, Ce2Prov, Co1, upperCombinedCo1, Co1Err, nnCo1, nnCo1Err, nlCo1, Co1Prov, Cr1, upperCombinedCr1, Cr1Err, nnCr1, nnCr1Err, nlCr1, Cr1Prov, Cr2, upperCr2, Cr2Err, nnCr2, nnCr2Err, nlCr2, Cr2Prov, Cu1, upperCombinedCu1, Cu1Err, nnCu1, nnCu1Err, nlCu1, Cu1Prov, Dy2, Eu2, upperCombinedEu2, Eu2Err, nnEu2, nnEu2Err, nlEu2, Eu2Prov, Fe1, upperCombinedFe1, Fe1Err, nnFe1, nnFe1Err, nlFe1, Fe1Prov, Fe2, upperFe2, Fe2Err, nnFe2, nnFe2Err, nlFe2, Fe2Prov, Fe3Err, nnFe3, nlGd2, He1, upperCombinedHe1, He1Err, nnHe1, nnHe1Err, nlHe1, He1Prov, La2, upperLa2, La2Err, nnLa2, nnLa2Err, nlLa2, La2Prov, Li1, upperCombinedLi1, Li1Err, nnLi1, nnLi1Err, nlLi1, Li1Prov, Mg1, upperCombinedMg1, Mg1Err, nnMg1, nnMg1Err, nlMg1, Mg1Prov, Mn1, upperCombinedMn1, Mn1Err, nnMn1, nnMn1Err, nlMn1, Mn1Prov, Mo1, upperCombinedMo1, Mo1Err, nnMo1, nnMo1Err, nlMo1, Mo1Prov, N3, upperN3, N3Err, nnN3, nnN3Err, nlN3, N3Prov, NCN, upperNCN, NCNErr, nnNCN, nnNCNErr, nlNCN, NCNProv, Na1, upperCombinedNa1, Na1Err, nnNa1, nnNa1Err, nlNa1, Na1Prov, Nd2, upperNd2, Nd2Err, nnNd2, nnNd2Err, nlNd2, Nd2Prov, Ni1, upperCombinedNi1, Ni1Err, nnNi1, nnNi1Err, nlNi1, Ni1Prov, O1, upperCombinedO1, O1Err, nnO1, nnO1Err, nlO1, O1Prov, O2, upperO2, O2Err, nnO2, nnO2Err, nlO2, O2Prov, S1, upperCombinedS1, S1Err, nnS1, nnS1Err, nlS1, S1Prov, Sc1, upperCombinedSc1, Sc1Err, nnSc1, nnSc1Err, nlSc1, Sc1Prov, Sc2, upperSc2, Sc2Err, nnSc2, nnSc2Err, nlSc2, Sc2Prov, Si1, upperCombinedSi1, Si1Err, nnSi1, nnSi1Err, nlSi1, Si1Prov, Si2, upperSi2, Si2Err, nnSi2, nnSi2Err, nlSi2, Si2Prov, Si3, upperSi3, Si3Err, nnSi3, nnSi3Err, nlSi3, Si3Prov, Si4, upperSi4, Si4Err, nnSi4, nnSi4Err, nlSi4, Si4Prov, Ti1, upperCombinedTi1, Ti1Err, nnTi1, nnTi1Err, nlTi1, Ti1Prov, Ti2, upperTi2, Ti2Err, nnTi2, nnTi2Err, nlTi2, Ti2Prov, V1, upperCombinedV1, V1Err, nnV1, nnV1Err, nlV1, V1Prov, Y2, upperY2, Y2Err, nnY2, nnY2Err, nlY2, Y2Prov, Zn1, upperCombinedZn1, Zn1Err, nnZn1, nnZn1Err, nlZn1, Zn1Prov, Zr1, upperCombinedZr1, Zr1Err, nnZr1, nnZr1Err, nlZr1, Zr1Prov, Zr2, upperZr2, Zr2Err, nnZr2, nnZr2Err, nlZr2, Zr2Prov, deprecated, cuEventID
  FROM AstroAnalysis
 WHERE nodeID = 1
   AND WG = 'WG15'
GO

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='WgRecommendedAstroAnalysis')
   DROP VIEW WgRecommendedAstroAnalysis
GO
CREATE VIEW GES.WgRecommendedAstroAnalysis
-------------------------------------------------------------------------------
--/H Individual working group recommended astrophysical parameter and abundances analyses
--
--/T The astrophysical parameter and abundances recommended by individual
--/T working groups of the GES COnsortium.  Values are included for working groups
--/T 10 to 14.
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
-------------------------------------------------------------------------------
AS
SELECT *
  FROM AstroAnalysis
 WHERE nodeID = 1
   AND WG != 'WG15'
GO

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='WpNaAstroAnalysis')
   DROP VIEW WpNaAstroAnalysis
GO
CREATE VIEW GES.WpNaAstroAnalysis
-------------------------------------------------------------------------------
--/H Individual node abundances with working group parameters
--
--/T Astrophysical parameter and abundances analyses computed by individual nodes
--/T in the various working groups (10-13) of the GES Consortium.  Here the
--/T node has adopted the parameters recommended by its parent working group
--/T and computed abundances with these parameters.
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
-------------------------------------------------------------------------------
AS
SELECT *
  FROM AstroAnalysis
 WHERE nodeID != 1
   AND isWgParams = 1
GO

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='NpNaAstroAnalysis')
   DROP VIEW NpNaAstroAnalysis
GO
CREATE VIEW GES.NpNaAstroAnalysis
-------------------------------------------------------------------------------
--/H Individual node parameters and abundances
--
--/T Astrophysical parameter and abundances analyses computed by individual nodes
--/T in the various working groups (10-13) of the GES Consortium.  Here the
--/T node has computed both the astrophysical parameters and the abundances.
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
-------------------------------------------------------------------------------
AS
SELECT *
  FROM AstroAnalysis
 WHERE nodeID != 1
   AND isWgParams = 0
GO

-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='SpectrumAndFrame')
   DROP VIEW SpectrumAndFrame
GO
CREATE VIEW GES.SpectrumAndFrame
-------------------------------------------------------------------------------
--/H Spectrum and SpecFrame combination 
--
--/T Extended details for each spectrum: all the columns from table 'Spectrum'
--/T combined with some columns from its parent 'SpecFrame'.
-------------------------------------------------------------------------------
AS
SELECT sp.*, frame.instrument, frame.grating, frame.gesType, frame.object
  FROM Spectrum sp,
       SpecFrame frame
 WHERE sp.specFrameId = frame.specFrameId



-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='RecommendedOutlierAnalysis')
   DROP VIEW RecommendedOutlierAnalysis

CREATE VIEW GES.RecommendedOutlierAnalysis
-------------------------------------------------------------------------------
--/H Flags identifying and characterising outlier stars.
--
--/T This view contains the results of the analyses performed by WG14 to
--/T identify outlier spectra joined to the WG15 recommended analyses.
--/T The WG14 analyses pertain to spectra characterised by large
--/T residuals when processed using automatic classification tools and
--/T typically correspond to stars with unusual characteristics.
--/T
--/T In iDR2 the outlier analyses generates the columns of flags peculi,
--/T remark and tech.  In subsequent releases additional columns may be
--/T generated.
--/T
--/T The corresponding WG15 flags are also included.
-------------------------------------------------------------------------------
AS
SELECT
  wg14.specGroupID AS WG14_specGroupId,
  wg15.specGroupID AS WG15_specGroupId,
  spg14.specID AS specId,
  spg14.fileName AS fileName,
  wg15.cName AS cName,
  wg15.instrument AS instrument,
  wg15.gratings AS gratings,
  wg15.gesField AS gesField,
  wg14.peculi AS WG14_peculi,
  wg14.remark AS WG14_remark,
  wg14.tech AS WG14_tech,
  wg15.peculi AS WG15_peculi,
  wg15.remark AS WG15_remark,
  wg15.tech AS WG15_tech
FROM
  AstroAnalysis AS wg14,
  AstroAnalysis AS wg15,
  SpectrumGroup AS spg14,
  SpectrumGroup AS spg15
WHERE wg14.wg = 'WG14'
  AND wg15.wg = 'WG15'
  AND wg14.specGroupID = spg14.specGroupID
  AND wg15.specGroupID = spg15.specGroupID
  AND spg14.specID = spg15.specID



-- ----------------------------------------------------------------------------
IF EXISTS (SELECT * FROM sysobjects WHERE NAME='SpectrumOutlierAnalysis')
   DROP VIEW SpectrumOutlierAnalysis

CREATE VIEW GES.SpectrumOutlierAnalysis
-------------------------------------------------------------------------------
--/H Flags identifying and characterising outlier stars.
--
--/T This view contains the results of the analyses performed by WG14 to
--/T identify outlier spectra joined to the individual spectra on which the
--/T analyses were performed.
--/T
--/T The WG14 analyses pertain to spectra characterised by large
--/T residuals when processed using automatic classification tools and
--/T typically correspond to stars with unusual characteristics.
--/T
--/T In iDR2 the outlier analyses generates the columns of flags peculi,
--/T remark and tech.  In subsequent releases additional columns may be
--/T generated.
-------------------------------------------------------------------------------
AS
SELECT 
  spg.specID AS specId, 
  wg14.targetID AS targetId, 
  wg14.cName AS cName, 
  spg.fileName AS fileName, 
  wg14.instrument AS instrument, 
  wg14.gratings AS gratings, 
  wg14.gesField AS gesField,
  wg14.peculi AS peculi, 
  wg14.remark AS remark, 
  wg14.tech AS tech, 
  wg14.deprecated AS deprecated
FROM
  WgRecommendedAstroAnalysis AS wg14,
  SpectrumGroup spg
WHERE wg14.wg='WG14'
  AND wg14.specGroupID = spg.specGroupID

