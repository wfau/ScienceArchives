--=============================================================================
--
-- $Id: GES_NeighboursSchema.sql 653 2017-11-30 13:51:24Z EckhardSutorius $
--
-- Database schema file containing SQL to create the GES cross-neighbour
-- tables.
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

-- ----------------------------------------------------------------------------
CREATE TABLE GES.TargetXGAIADR1gaia_source(
-------------------------------------------------------------------------------
--/H Cross-neighbours between the GES Target catalogue and the Gaia DR1 main catalogue
--
--/T All Gaia DR1 sources within 10 arcsec of
--/T each star in the GES Target catalogue are recorded in this cross-neighbour
--/T table.  The Target table was joined to the GAIADR1..gaia_source table to create
--/T these cross-neighbours.  Use this table for any cross-querying of GES
--/T target stars with Gaia DR1 sources.
-------------------------------------------------------------------------------
masterObjID  bigint not null, --/D The unique ID in Target (=targetID ) --/C meta.id;meta.main
slaveObjID   bigint not null, --/D The unique ID of the neighbour in GAIADR1..gaia_source (=source_id) --/C meta.id.cross
distanceMins real not null,   --/D Angular separation between neighbours --/U arcminutes --/C pos.angDistance
CONSTRAINT pk_TargetXGAIADR1gaia_source PRIMARY KEY (masterObjID, slaveObjID)
) 

-- ----------------------------------------------------------------------------
CREATE TABLE GES.TargetXGAIADR1tgas_source(
-------------------------------------------------------------------------------
--/H Cross-neighbours between the GES Target catalogue and the Gaia DR1 TGAS catalogue
--
--/T All Gaia DR1 sources within 10 arcsec of
--/T each star in the GES Target catalogue are recorded in this cross-neighbour
--/T table.  The Target table was joined to the GAIADR1..tgas_source table to create
--/T these cross-neighbours.  Use this table for any cross-querying of GES
--/T target stars with Gaia DR1 sources.
-------------------------------------------------------------------------------
masterObjID  bigint not null, --/D The unique ID in Target (=targetID ) --/C meta.id;meta.main
slaveObjID   bigint not null, --/D The unique ID of the neighbour in GAIADR1..gaia_source (=source_id) --/C meta.id.cross
distanceMins real not null,   --/D Angular separation between neighbours --/U arcminutes --/C pos.angDistance
CONSTRAINT pk_TargetXGAIADR1tgas_source PRIMARY KEY (masterObjID, slaveObjID)
) 

-- ----------------------------------------------------------------------------
CREATE TABLE GES.TargetXSSASource(
-------------------------------------------------------------------------------
--/H Cross-neighbours between the GES Target catalogue and the SSA.
--
--/T All SSA (SuperCOSMOS Science Archive) point sources within 10 arcsec of
--/T each star in the GES Target catalogue are recorded in this cross-neighbour
--/T table.  The Target table was joined to the SSA..Source table to create
--/T these cross-neighbours.  Use this table for any cross-querying of GES
--/T target stars with SSA sources.
-------------------------------------------------------------------------------
masterObjID  bigint not null, --/D The unique ID in Target (=targetID ) --/C meta.id;meta.main
slaveObjID   bigint not null, --/D The unique ID of the neighbour in SSA..Source (=objID) --/C meta.id.cross
distanceMins real not null,   --/D Angular separation between neighbours --/U arcminutes --/C pos.angDistance
CONSTRAINT pk_TargetXSSASource PRIMARY KEY (masterObjID, slaveObjID)
) 

-- ----------------------------------------------------------------------------
CREATE TABLE GES.TargetXtwomass_psc(
-------------------------------------------------------------------------------
--/H Cross-neighbours between the GES Target catalogue and the 2MASS PSC.
--
--/T All sources in the 2MASS point source catalogue (PSC) within 10 arcsec of
--/T each star in the GES Target catalogue are recorded in this cross-neighbour
--/T table.  The Target table was joined to the TWOMASS.. Twomass_psc table to
--/T create these cross-neighbours.  Use this table for any cross-querying of
--/T GES target stars with 2MASS point sources.
-------------------------------------------------------------------------------
masterObjID  bigint not null, --/D The unique ID in Target (=targetID ) --/C meta.id;meta.main
slaveObjID   bigint not null, --/D The unique ID of the neighbour in TWOMASS..Twomass_psc (=pts_key) --/C meta.id.cross
distanceMins real not null,   --/D Angular separation between neighbours --/U arcminutes --/C pos.angDistance
CONSTRAINT pk_TargetXtwomass_psc PRIMARY KEY (masterObjID, slaveObjID)
) 

-- ----------------------------------------------------------------------------
CREATE TABLE GES.TargetXvhsDR4Source(
-------------------------------------------------------------------------------
--/H Cross-neighbours between the GES Target catalogue and the VISTA VHS.
--
--/T All the sources in the VISTA VHSDR4 Source catalogue within 10 arcsec of
--/T each star in the GES Target catalogue are recorded in this cross-neighbour
--/T table.  The Target table was joined to the VSA..vhsSource table to create
--/T these cross-neighbours.  Use this table for any cross-querying of GES
--/T target stars with VISTA VHS sources.
-------------------------------------------------------------------------------
masterObjID  bigint not null, --/D The unique ID in Target (=targetID ) --/C meta.id;meta.main
slaveObjID   bigint not null, --/D The unique ID of the neighbour in VSA..vhsSource (=sourceID) --/C meta.id.cross
distanceMins real not null,   --/D Angular separation between neighbours --/U arcminutes --/C pos.angDistance
CONSTRAINT pk_TargetXvhsDR4Source PRIMARY KEY (masterObjID, slaveObjID)
) 

-- ----------------------------------------------------------------------------
CREATE TABLE GES.TargetXatlasDR3Source(
-------------------------------------------------------------------------------
--/H Cross-neighbours between the GES Target catalogue and the VST Atlas survey.
--
--/T All the sources in the VST AtlasDR3 source catalogue within 10 arcsec of
--/T each star in the GES Target catalogue are recorded in this cross-neighbour
--/T table.  The Target table was joined to the OSA..atlasSource table to 
--/T create these cross-neighbours.  Use this table for any cross-querying 
--/T of GES target stars with VST Atlas sources.
-------------------------------------------------------------------------------
masterObjID  bigint not null, --/D The unique ID in Target (=targetID ) --/C meta.id;meta.main
slaveObjID   bigint not null, --/D The unique ID of the neighbour in OSA..atlasSource (=sourceID) --/C meta.id.cross
distanceMins real not null,   --/D Angular separation between neighbours --/U arcminutes --/C pos.angDistance
CONSTRAINT pk_TargetXatlasDR3Source PRIMARY KEY (masterObjID, slaveObjID)
) 

-- ----------------------------------------------------------------------------
