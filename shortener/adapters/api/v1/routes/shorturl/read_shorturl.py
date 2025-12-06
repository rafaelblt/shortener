from http import HTTPStatus

from fastapi.responses import JSONResponse

from shortener.adapters.api.v1 import dependencies
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.responses import ErrorResponse
from shortener.adapters.api.v1.schemas.responses.shorturl import ShortURLReadSuccessResponse
from shortener.adapters.api.v1.schemas.responses.types import RouteResponseSpec

from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shorturl.exceptions import ShortURLNotFoundError

from .api_router import router


responses = RouteResponseSpec()
responses.add_json_response(
    status_code=HTTPStatus.OK,
    description="ShortURL found.",
    model=ShortURLReadSuccessResponse,
    examples={
        "default": ShortURLReadSuccessResponse.get_example().model_dump()
    }
)
responses.add_json_response(
    status_code=HTTPStatus.NOT_FOUND,
    description="ShortURL not found.",
    model=ErrorResponse,
    examples={
        "default": ErrorResponse(
            code=ApiErrorCode.ITEM_NOT_FOUND,
            detail="No ShortURL was found with the provided ID."
        ).model_dump()
    }
)


@router.get(
    "/{id}", responses=responses.get_schema()
)
async def read_shorturl(
    id: int,
    use_case: dependencies.ReadShortURLOfUserUseCaseDependency,
    uow: dependencies.UnitOfWorkDependency,
    user: dependencies.CurrentUserDependency,
):
    shorturl_id = id
    try:
        async with uow.transaction():
            shorturl = await use_case.execute(
                shorturl_pk=PrimaryKey.create_pk_id(shorturl_id),
                user_pk=user.pk
            )
    except ShortURLNotFoundError:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content=responses.get_example(HTTPStatus.NOT_FOUND, "default")
        )
    
    return ShortURLReadSuccessResponse.with_shorturl(shorturl)
