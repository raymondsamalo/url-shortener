"""
main backend for our app
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.schemas import UrlMapCreateRequest, UrlMapCreateResponse
from app.dependencies import repo
router = APIRouter()

slug_dict = {}
url_dict = {}

reserved_slug = ["docs","ui"]

@router.post("/", response_model=UrlMapCreateResponse, summary="Create new url to slug map")
async def create_new_url(req: UrlMapCreateRequest) -> UrlMapCreateResponse:
    if req.slug in reserved_slug:
        raise HTTPException(status_code=400, detail="slug docs is reserved")
    if req.slug:
        existing_url =  await repo.get_url_from_slug(req.slug)
        if existing_url is None:
            # no existing url
            await repo.store_url_and_slug(slug=req.slug, url=str(req.original_url))
        elif existing_url != req.original_url:
            raise HTTPException(
                status_code=400, detail=f"slug {req.slug} already exist with different url")
    else:
        # no slug is given, we need to create our own shortened url or slug
        pass
    slug = req.slug
    return UrlMapCreateResponse(url=req.original_url,
                                slug=slug,
                                detail="mapped successfully")


@router.get("/{slug}")
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
