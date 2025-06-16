from enum import StrEnum


XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
OAI_NS = "http://www.openarchives.org/OAI/2.0/"
RI_NS = "http://www.ivoa.net/xml/RegistryInterface/v1.0"
OAI_DC_NS = "http://www.openarchives.org/OAI/2.0/oai_dc/"
DC_NS = "http://purl.org/dc/elements/1.1/"

NS = {"oai": OAI_NS, "xsi": XSI_NS, "ri": RI_NS, "oai_dc": OAI_DC_NS, "dc": DC_NS}


class Verbs(StrEnum):
    IDENTIFY = "Identify"
    LIST_METADATA_FORMATS = "ListMetadataFormats"
    GET_RECORD = "GetRecord"
    LIST_SETS = "ListSets"
    LIST_RECORDS = "ListRecords"
    LIST_IDENTIFIERS = "ListIdentifiers"


class MetadataFormats(StrEnum):
    IVO_VOR = "ivo_vor"
    OAI_DC = "oai_dc"


class SetSpecs(StrEnum):
    IVO_MANAGED = "ivo_managed"


class QParams(StrEnum):
    VERB = "verb"
    IDENTIFIER = "identifier"
    METADATA_PREFIX = "metadataPrefix"
    FROM = "from"
    UNTIL = "until"
    SET = "set"
    RESUMPTION_TOKEN = "resumptionToken"


class Errors(StrEnum):
    BAD_VERB = "badVerb"
    BAD_ARGUMENT = "badArgument"
    ID_DOES_NOT_EXIST = "idDoesNotExist"
    CANNOT_DISSEMINATE_FORMAT = "cannotDisseminateFormat"
    NO_SET_HIERARCHY = "noSetHierarchy"
    BAD_RESUMPTION_TOKEN = "badResumptionToken"
    NO_RECORDS_MATCH = "noRecordsMatch"
