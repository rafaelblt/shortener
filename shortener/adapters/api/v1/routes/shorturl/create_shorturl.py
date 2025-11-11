from http import HTTPStatus

from shortener.adapters.api.v1 import dependencies
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.payloads.shorturl import CreateShortURLPayload
from shortener.adapters.api.v1.schemas.responses.shorturl import CreateShortURLSuccess
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from shortener.domain.shorturl.exceptions import ShortURLSlugAlreadyExistsError
from shortener.domain.user.exceptions import ShortURLLimitReachedError, UserNotFoundError

from shortener.infra.translations.i18n import get_translator

from .api_router import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.CREATED,
    description="ShortURL created.",
    model=CreateShortURLSuccess
)
responses.set_error_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Provided Owner ID not found.",
    error_code=ApiErrorCode.ITEM_NOT_FOUND
)
responses.set_error_response(
    status_code=HTTPStatus.CONFLICT,
    description="Provided slug already exists.",
    error_code=ApiErrorCode.ALREADY_PROCESSED
)
responses.set_error_response(
    status_code=HTTPStatus.FORBIDDEN,
    description="The owner has reached the limit for ShortURLs.",
    error_code=ApiErrorCode.LIMIT_REACHED
)


@router.post(
    "/", status_code=HTTPStatus.CREATED, responses=responses.get_schema(),
)
async def create_shorturl(
    payload: CreateShortURLPayload,
    use_case: dependencies.CreateShortURLForUserUseCaseDependency,
    language: dependencies.LanguageParserDependency,
    uow: dependencies.UnitOfWorkDependency,
    user: dependencies.CurrentUserDependency
): 
    _  = get_translator(language)
    try:
        async with uow.transaction():
            shorturl = await use_case.execute(
                original_url=payload.convert_original_url(),
                custom_slug=payload.convert_custom_slug(),
                owner_pk=user.pk
            )
    except ShortURLSlugAlreadyExistsError:
        detail = _("The slug provided already exists.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.CONFLICT, {"detail": detail}
        )
    except UserNotFoundError:
        detail = _("The owner_id provided was not found.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.BAD_REQUEST, {"detail": detail}
        )
    except ShortURLLimitReachedError:
        detail = _("The owner has reached the limit for ShortURLs in their plan.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.FORBIDDEN, {"detail": detail}
        )

    return CreateShortURLSuccess.with_shorturl(shorturl)
