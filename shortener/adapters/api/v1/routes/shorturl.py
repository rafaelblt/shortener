from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from shortener.domain.shorturl.exceptions import (
    ShortURLDeletionNotFoundError, ShortURLValidationError
)

from shortener.use_cases import (
    GetShortURLUseCase,
    ListShortURLUseCase,
    CreateShortURLUseCase,
    DeleteShortURLUseCase
)

from shortener.adapters.api.v1.dependencies import (
    make_create_shorturl_use_case,
    make_get_shorturl_use_case,
    make_delete_shorturl_use_case,
    make_list_shorturl_use_case
)
from shortener.adapters.api.v1.schemas import (
    ShortURLSchema, ShortURLCreateSchema
)


router = APIRouter(prefix="/api/v1/shorturls", tags=["shorturls"])


@router.get("/")
async def list_shorturls(
    use_case: ListShortURLUseCase = Depends(make_list_shorturl_use_case)
):
    return await use_case.list_all()


@router.get("/{id}", response_model=ShortURLSchema)
async def get_shorturl(
    id: int,
    use_case: GetShortURLUseCase = Depends(make_get_shorturl_use_case)
):
    shorturl = await use_case.get_by_id(id)

    if shorturl is None:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"message": "ShortURL not found"}
        )

    response_data = ShortURLSchema.from_domain(shorturl).model_dump()

    return response_data


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ShortURLSchema)
async def create_shorturl(
    data: ShortURLCreateSchema,
    use_case: CreateShortURLUseCase = Depends(make_create_shorturl_use_case)
):  
    try:  
        shorturl = await use_case.execute(
            original_url=data.original_url,
            custom_slug=data.custom_slug,
            owner_id=data.owner_id,
            expires_at=data.expires_at
        )
    except ShortURLValidationError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    response_data = ShortURLSchema.from_domain(shorturl).model_dump()
    response_data = jsonable_encoder(response_data)
    
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=response_data,
        headers={"Location": f"{router.prefix}/{shorturl.id}"}
    )


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_shorturl(
    id: int,
    use_case: DeleteShortURLUseCase = Depends(make_delete_shorturl_use_case)
):
    try:
        await use_case.delete_by_id(id)

    except ShortURLDeletionNotFoundError as e:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"message": str(e)},
        )
    
    else:
        return Response(status_code=HTTPStatus.NO_CONTENT)
