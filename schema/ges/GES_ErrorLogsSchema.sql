--=============================================================================
--
-- $Id: GES_ErrorLogsSchema.sql 632 2017-07-21 11:00:11Z EckhardSutorius $
--
-- GES_ErrorLogsSchema.sql
--
-- Database schema file containing SQL to create the GES error log tables.
--
-- Original author: 
--   Clive Davenhall, WFAU.
--
--=============================================================================
--
-- USE GES
--GO
--

-- ----------------------------------------------------------------------------
create table GES.ErrLogBadFileNames(
-------------------------------------------------------------------------------
--/H Log of bad file names encountered ingesting parameter analysis files.
--
--/T Log of bad file names encountered ingesting parameter analysis files.
--/T
--/T Required constraints:
-------------------------------------------------------------------------------
aaID        bigint not null default -99999999, --/D AstroAnalysis identifier: unique sequence no in the table.
cName       varchar(16) not null default 'NONE', --/D Object name formed from the coordinates of the object (can be used in place of object to give a unique name).
wg          varchar(4) not null default 'NONE',  --/D GES working group which provided the data (one of: WG10, WG11, WG12, WG13).
nodeName    varchar(32) not null default 'NONE', --/D Name of working group node that contributed this analysis (nodeName = wg for the recommended values from the combined analysis).
fieldName   varchar(32) not null default 'NONE', --/D GES field name.
instrument  varchar(8) not null default 'NONE',   --/D Instrument name. 
gratings    varchar(36) not null default 'NONE',    --/D Gratings setup.
givenFileName  varchar(256) not null default 'NONE', --/D Given file name.
singleSpecFile varchar(256) not null default 'NONE', --/D SingleSpec file name.
description varchar(256) not null default 'NONE' --/D Description of the problem.
)GO

-- ----------------------------------------------------------------------------
create table GES.ErrLogBadSpecGroups(
-------------------------------------------------------------------------------
--/H Log of bad spectrum groups encountered ingesting parameter analysis files.
--
--/T Log of bad spectrum groups encountered ingesting parameter analysis files.
--/T
--/T Required constraints:
-------------------------------------------------------------------------------
aaID        bigint not null default -99999999,    --/D AstroAnalysis identifier: unique sequence no in the table.
specGroupID bigint not null default -99999999,    --/D Spectrum group identifier: unique identifier for each group of spectra that went into an analysis.
gratings    varchar(36) not null default 'NONE',  --/D Gratings setup.
aaFileList  varchar(512) not null default 'NONE', --/D List of astroanalysis files in the group.
specGroup   varchar(512) not null default 'NONE', --/D Files defining the spectrum group.
description varchar(256) not null default 'NONE'  --/D Description of the problem.
)GO


-- ----------------------------------------------------------------------------
create table GES.ErrLogDupPrimKeys(
-------------------------------------------------------------------------------
--/H Log of duplicate primary keys encountered ingesting parameter analysis files.
--
--/T Log of duplicate primary keys encountered ingesting parameter analysis files.
--/T
--/T Required constraints:
-------------------------------------------------------------------------------
aaID        bigint not null default -99999999,   --/D AstroAnalysis identifier: unique sequence no in the table.
cName       varchar(16) not null default 'NONE', --/D Object name formed from the coordinates of the object (can be used in place of object to give a unique name).
wg          varchar(4) not null default 'NONE',  --/D GES working group which provided the data (one of: WG10, WG11, WG12, WG13).
nodeName    varchar(32) not null default 'NONE', --/D Name of working group node that contributed this analysis (nodeName = wg for the recommended values from the combined analysis).
fieldName   varchar(32) not null default 'NONE', --/D GES field name.
instrument  varchar(8) not null default 'NONE',  --/D Instrument name. 
gratings    varchar(36) not null default 'NONE', --/D Gratings setup.
specGroupID bigint not null default -99999999,   --/D Spectrum group identifier: unique identifier for each group of spectra that went into an analysis.
primKeyRepn varchar(256) not null default 'NONE' --/D Character representation of the primary key.
)GO

-- ----------------------------------------------------------------------------
create table GES.ErrLogBadSpecFrameFiles(
-------------------------------------------------------------------------------
--/H Log of bad specFrame files encountered ingesting parameter analysis files.
--
--/T Log of bad specFrame files encountered ingesting parameter analysis files.
--/T
--/T Required constraints:
-------------------------------------------------------------------------------
instrument   varchar(8) not null default 'NONE',   --/D Instrument name.
specID       bigint not null default -99999999,    --/D Spectrum identifier: unique identifier for the individual spectrum that contributed to the analysis.
cName        varchar(16) not null default 'NONE',  --/D Object name formed from the coordinates of the object (can be used in place of object to give a unique name).
manySpecFile varchar(256) not null default 'NONE', --/D ManySpec file name.
predSingleSpecFile varchar(256) not null default 'NONE', --/D Predicted singleSpec file name.
description  varchar(256) not null default 'NONE'  --/D Description of the problem.
)GO

-- ----------------------------------------------------------------------------
create table GES.ErrLogUvesSpecIngest(
-------------------------------------------------------------------------------
--/H Log of errors raised ingesting UVES single spec. files.
--
--/T Log of errors raised ingesting UVES single spec. files.
--/T
--/T Required constraints:
-------------------------------------------------------------------------------
errLevel    varchar(8) not null default 'NONE',     --/D Level of the message (one of: information, warning, error, abort).
errType     varchar(16) not null default 'NONE',    --/D Code identifying the type of error.
filename    varchar(256) not null default 'NONE',   --/D Name of any file associated with the error.
manyspeckey varchar(512) not null default 'NONE',   --/D Name of any ManySpec provenance key associated with the error.
message     varchar(256) not null default 'NONE'    --/D Message associated with the error.
)GO

-- ----------------------------------------------------------------------------