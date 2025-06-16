import logging
from functools import lru_cache
from importlib.metadata import version
from typing import Annotated

from fastapi import Depends, FastAPI, Header, Query, Request, Response
from fastapi.responses import FileResponse, PlainTextResponse
from lxml import etree

from vo_registry.errors import bad_verb
from vo_registry.config import CONTACT_NAME, CONTACT_EMAIL, TITLE
from vo_registry.constants import QParams, Verbs
from vo_registry.oai import oai_wrap
from vo_registry.resources import ResourceRepo
from vo_registry.validation import validate_query_params
from vo_registry.verbs.getrecord import getrecord
from vo_registry.verbs.identify import identify
from vo_registry.verbs.listidentifiers import listidentifiers
from vo_registry.verbs.listmetadataformats import listmetadataformats
from vo_registry.verbs.listrecords import listrecords
from vo_registry.verbs.listsets import listsets


logger = logging.getLogger("uvicorn.error")
registry_version = version("vo-registry")
app = FastAPI(
    title=TITLE,
    version=registry_version,
    contact={"name": CONTACT_NAME, "email": CONTACT_EMAIL},
    license_info={
        "name": "BSD-3-Clause",
        "url": "https://gitlab.com/nsf-noirlab/csdc/vo-registry/"
        "-/blob/main/LICENSE?ref_type=heads",
    },
)


@app.get("/")
def hello_world() -> str:
    return "Hello World"


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse("./vo_registry/favicon.ico")


@app.get("/robots.txt", include_in_schema=False, response_class=PlainTextResponse)
def robots() -> str:
    data = "User-agent: *\nDisallow: /registry"
    return data


@lru_cache
def get_resource_repo() -> ResourceRepo:
    return ResourceRepo()


class CustomQueryParams:
    verb_str = (
        "OAI-PMH verb. Valid options are Identify, GetRecord, "
        "ListIdentifiers, ListRecords, ListsMetadataFormats, ListSets"
    )
    id_str = (
        "VOResource identifier. e.g. 'ivo://example.edu/registry'. "
        "Required by GetRecord, optional for ListMetadataFormats"
    )
    mdp_str = (
        "ivo_vor or oai_dc are the only supported metadata formats. "
        "Required by GetRecord, ListIdentifiers, and ListRecords"
    )
    set_str = (
        "ivo_managed is the only supported set. "
        "Optional for ListIdentifiers and ListRecords"
    )
    from_str = (
        "Return only records modified after this date(time). Must be "
        "formatted as either YYYY-MM-DD or YYYY-MM-DDThh-mm-ssZ. "
        "Optional for ListIdentifiers and ListRecords."
    )
    until_str = (
        "Return only records modified before this date(time). Must be "
        "formatted as either YYYY-MM-DD or YYYY-MM-DDThh-mm-ssZ. "
        "Optional for ListIdentifiers and ListRecords."
    )
    resumption_str = "Unsupported, any token will produce an error"

    def __init__(
        self,
        verb: str = Query(None, description=verb_str),
        identifier: str = Query(None, description=id_str),
        metadataPrefix: str = Query(None, description=mdp_str),
        set_query: str = Query(None, description=set_str, alias="set"),
        from_query: str = Query(None, description=from_str, alias="from"),
        until: str = Query(None, description=until_str),
        resumptionToken: str = Query(None, description=resumption_str),
    ):
        pass  # This is just for documentation, we access the Request object


@app.get("/registry")
@app.post("/registry")
def verb_selector(
    request: Request,
    query_params: CustomQueryParams = Depends(),
    x_forwarded_proto: Annotated[str | None, Header(include_in_schema=False)] = None,
    repo: ResourceRepo = Depends(get_resource_repo),
) -> Response:
    logger.info(f"Registry request received with query params: {request.query_params}")
    data = validate_query_params(request.query_params, repo)
    verb = request.query_params.get(QParams.VERB)

    if data is None:
        match verb:
            case Verbs.IDENTIFY:
                logger.info("Processing IDENTIFY request")
                data = identify(repo, **request.query_params)
            case Verbs.LIST_METADATA_FORMATS:
                logger.info("Processing LIST_METADATA_FORMATS request")
                data = listmetadataformats(repo, **request.query_params)
            case Verbs.LIST_SETS:
                logger.info("Processing LIST_SETS request")
                data = listsets(repo, **request.query_params)
            case Verbs.LIST_RECORDS:
                logger.info("Processing LIST_RECORDS request")
                data = listrecords(repo, **request.query_params)
            case Verbs.LIST_IDENTIFIERS:
                logger.info("Processing LIST_IDENTIFIERS request")
                data = listidentifiers(repo, **request.query_params)
            case Verbs.GET_RECORD:
                logger.info("Processing GET_RECORD request")
                data = getrecord(repo, **request.query_params)
            case _:
                logger.info("Processing BAD_VERB request")
                data = [bad_verb(verb)]

    url = request.url
    if x_forwarded_proto:
        request_url = f"{x_forwarded_proto}://{url.netloc}{url.path}"
    else:
        request_url = f"{url.scheme}://{url.netloc}{url.path}"

    response_data = oai_wrap(data, request.query_params, request_url)
    xml_string = etree.tostring(
        response_data,
        xml_declaration=True,
        encoding=response_data.docinfo.encoding,
        pretty_print=True,
    )

    return Response(content=xml_string, media_type="application/xml")
