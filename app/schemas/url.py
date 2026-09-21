import re
from typing import Annotated
from pydantic import (
    BaseModel, Field,
    AfterValidator, BeforeValidator,
    AnyHttpUrl)

# Regex to enforce alphanumeric characters, hyphens, and underscores only.
# Change constraints (like length) as needed.
SHORT_LINK_PATH_REGEX = re.compile(r"^[a-zA-Z0-9\-_]{3,20}$")


def remove_whitespace(v: str) -> str:
    """
    remove whitespace validator tool
    """
    if isinstance(v, str):
        return v.strip()
    return v


def validate_short_path(v: str) -> str:
    """Validate that a short URL path matches the allowed format."""
    if not SHORT_LINK_PATH_REGEX.match(v):
        raise ValueError(
            "Invalid short URL path. Must be 3-20 characters long and contain "
            "only alphanumeric characters, hyphens, or underscores."
        )
    return v


# Reusable custom type type for your models
LinkPath = Annotated[str, BeforeValidator(
    remove_whitespace), AfterValidator(validate_short_path)]


# class UrlMapCreateRequestNoLink(BaseModel):
#     """Schema for creating a shortened URL entry."""

#     original_url: AnyHttpUrl = Field(alias="url")

class UrlMapCreateRequest(BaseModel):
    """Schema for creating a shortened URL entry."""

    url: AnyHttpUrl
    link: LinkPath


class UrlMapCreateResponse(BaseModel):
    """ schema UrlCreateResponse    """
    url: str
    link: str | None = Field(default=None)
    detail: str


class UrlMapDeleteResponse(BaseModel):
    """Schema for creating a shortened URL entry."""

    link: LinkPath
    detail: str


class UrlMapUpdateRequest(BaseModel):
    """Schema for creating a shortened URL entry."""

    url: AnyHttpUrl


class UrlMapUpdateResponse(BaseModel):
    """ schema UrlCreateResponse    """
    link: str | None = Field(default=None)
    url: str
    detail: str
