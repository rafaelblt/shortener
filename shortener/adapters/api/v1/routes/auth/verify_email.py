from shortener.adapters.api.v1.schemas import MessageResponse
from shortener.adapters.api.v1.dependencies import (
    VerifyEmailUseCaseDependency,
    VerifyEmailExceptionHandlerDependency,
)

from . import router


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    use_case: VerifyEmailUseCaseDependency,
    exception_handler: VerifyEmailExceptionHandlerDependency
):
    try:
        await use_case.execute(token)
    except Exception as error:
        exception_handler.handle(error)
    
    return {"message": "Email successfully verified."}
