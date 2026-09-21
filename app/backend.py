"""
main backend for our app
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.schemas import UrlMapCreateRequest, UrlMapCreateResponse, LinkPath
from app.dependencies import repo
from app.util.slugify import slugify_md5_base62
router = APIRouter()

slug_dict = {}
url_dict = {}

reserved_link = ["docs","ui", "map","auto_map"]

@router.delete("/", response_model=UrlMapCreateResponse, summary="Delete an url map")
async def delete_alias(link: LinkPath) -> UrlMapCreateResponse:
    """
    Map and store url to link
    """
    url = str(req.original_url)
    link = str(req.link)
    if link in reserved_link:
        raise HTTPException(
            status_code=400, detail=f"link {link} is reserved and cannot be used to map url")
    existing_url =  await repo.get_url_from_link(link)
    if existing_url is None:
        # no existing url
        await repo.store_url_and_link(link=link, url=url)
        return UrlMapCreateResponse(url=url, link=link, detail="mapped successfully")
    if existing_url == url:
        return UrlMapCreateResponse(url=url, link=link,detail=f"url already mapped to {link}")
    raise HTTPException(
            status_code=400, detail=f"link {link} already exist with different url")

@router.post("/", response_model=UrlMapCreateResponse, summary="Create new url to link map")
async def create_new_alias(req: UrlMapCreateRequest) -> UrlMapCreateResponse:
    """
    Map and store url to link
    """
    url = str(req.original_url)
    link = str(req.link)
    if link in reserved_link:
        raise HTTPException(
            status_code=400, detail=f"link {link} is reserved and cannot be used to map url")
    existing_url =  await repo.get_url_from_link(link)
    if existing_url is None:
        # no existing url
        await repo.store_url_and_link(link=link, url=url)
        return UrlMapCreateResponse(url=url, link=link, detail="mapped successfully")
    if existing_url == url:
        return UrlMapCreateResponse(url=url, link=link,detail=f"url already mapped to {link}")
    raise HTTPException(
            status_code=400, detail=f"link {link} already exist with different url")


# """
# This is not in requirements at least as far as I understand it
# Hence let us comment it out for now
# """
# @router.post("/auto_map", response_model=UrlMapCreateResponse, summary="Create new url to automatically ")
# async def create_new_alias_automatically(req: UrlMapCreateRequestNoLink) -> UrlMapCreateResponse:
#     """
#     Map and store url to link
#     """
#     url = str(req.original_url)
#     # no link is given,
#     # we need to find if link already existed 
#     # if not existed then we need to create our own shortened url or link
#     existing_links = await repo.get_links_from_url(url)
#     if existing_links:
#         return UrlMapCreateResponse(url=url, detail=f"url already mapped to existing links {existing_links}")
#     link = slugify_md5_base62(url, length=20)
#     await repo.store_url_and_link(link=link, url=url)
#     return UrlMapCreateResponse(url=url, link=link, detail="mapped successfully")
    
        
@router.get("/")
async def redirect_root():
    """
    redirect root access to ui 
    we put this here to take precendence above our /{link}
    """
    return RedirectResponse(url="/ui/")


@router.get("/{link}")
async def redirect(link: str):
    """
    redirect upon request to access link if link exist in our storage
    :param link: Description
    :type link: str
    """
    # redirect to our ui
    if link=="ui":
        return RedirectResponse(url="/ui/")

    existing_url = await repo.get_url_from_link(link=link)
    if existing_url is None:
        raise HTTPException(status_code=404, detail=f"Not found {link}")
    return RedirectResponse(url=existing_url)
