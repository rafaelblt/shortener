from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from shortener.use_cases import (
    CreateShortURLUseCase,
    GetShortURLUseCase,
    DeleteShortURLUseCase
)

from shortener.adapters.api.dependencies import (
    make_create_shorturl_use_case,
    make_get_shorturl_use_case,
    make_delete_shorturl_use_case
)
from shortener.adapters.api.schemas import (
    ShortURLSchema, ShortURLCreateSchema
)


router = APIRouter(prefix="/shorturls", tags=["shorturls"])


@router.get("/")
def list_shorturls():
    return {"message": "List all shorturls"} # TODO


@router.get("/{id}", response_model=ShortURLSchema)
def get_shorturl(
    id: int,
    use_case: GetShortURLUseCase = Depends(make_get_shorturl_use_case)
):
    shorturl = use_case.get_by_id(id)

    if shorturl is None:
        return JSONResponse(
            status_code=HTTPStatus.NOT_FOUND,
            content={"message": "ShortURL not found"}
        )

    response_data = ShortURLSchema.from_domain(shorturl).model_dump()

    return response_data


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ShortURLSchema)
def create_shorturl(
    data: ShortURLCreateSchema,
    use_case: CreateShortURLUseCase = Depends(make_create_shorturl_use_case)
):    
    shorturl = use_case.execute(
        original_url=data.original_url,
        custom_slug=data.custom_slug,
        owner_id=data.owner_id,
        expires_at=data.expires_at
    )
    
    response_data = ShortURLSchema.from_domain(shorturl).model_dump()
    response_data = jsonable_encoder(response_data)
    
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=response_data,
        headers={"Location": f"/shorturls/{shorturl.id}"}
    )


@router.delete("/{id}")
def delete_shorturl(
    id: int,
    use_case: DeleteShortURLUseCase = Depends(make_delete_shorturl_use_case)
):
    shorturl = use_case.delete_by_id(id)
    response_data = ShortURLSchema.from_domain(shorturl).model_dump()

    return response_data
