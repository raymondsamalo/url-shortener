"""
main backend for our app
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.schemas import UrlMapCreateRequest, UrlMapCreateResponse, UrlMapCreateRequestNoSlug
from app.dependencies import repo
from app.util.slugify import slugify_md5_base62
router = APIRouter()

slug_dict = {}
url_dict = {}

reserved_slug = ["docs","ui"]

@router.post("/map", response_model=UrlMapCreateResponse, summary="Create new url to slug map")
async def create_new_alias(req: UrlMapCreateRequest) -> UrlMapCreateResponse:
    """
    Map and store url to slug
    """
    url = str(req.original_url)
    slug = str(req.slug)
    existing_url =  await repo.get_url_from_slug(slug)
    if existing_url is None:
        # no existing url
        await repo.store_url_and_slug(slug=slug, url=url)
        return UrlMapCreateResponse(url=url, slug=slug, detail="mapped successfully")
    if existing_url == url:
        return UrlMapCreateResponse(url=url, slug=slug,detail=f"url already mapped to {slug}")
    raise HTTPException(
            status_code=400, detail=f"slug {slug} already exist with different url")

@router.post("/auto_map", response_model=UrlMapCreateResponse, summary="Create new url to automatically ")
async def create_new_alias_automatically(req: UrlMapCreateRequestNoSlug) -> UrlMapCreateResponse:
    """
    Map and store url to slug
    """
    url = str(req.original_url)
    # no slug is given,
    # we need to find if slug already existed 
    # if not existed then we need to create our own shortened url or slug
    existing_slugs = await repo.get_slugs_from_url(url)
    if existing_slugs:
        return UrlMapCreateResponse(url=url, detail=f"url already mapped to existing slugs {existing_slugs}")
    slug = slugify_md5_base62(url, length=20)
    await repo.store_url_and_slug(slug=slug, url=url)
    return UrlMapCreateResponse(url=url, slug=slug, detail="mapped successfully")
    
        


@router.get("/map/{slug}")
async def redirect(slug: str):
    """
    redirect upon request to access slug if slug exist in our storage
    :param slug: Description
    :type slug: str
    """
    existing_url = await repo.get_url_from_slug(slug=slug)
    if existing_url is None:
        raise HTTPException(status_code=404, detail=f"Not found {slug}")
    return RedirectResponse(url=existing_url)
