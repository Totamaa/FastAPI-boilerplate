from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.api.dependencies.auth import verify_api_key
from app.core.api.dependencies.cache import long_cache
from app.modules.genres.dependencies import get_genre_service
from app.modules.genres.schemas import GenreCreate, GenreResponse
from app.modules.genres.service import GenreService

router = APIRouter()


@router.get(
    "/",
    response_model=list[GenreResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[long_cache()],
)
async def get_all_genres(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: GenreService = Depends(get_genre_service),
) -> list[GenreResponse]:
    return await service.get_all(limit=limit, offset=offset)


@router.post(
    "/",
    response_model=GenreResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_genre(
    payload: GenreCreate,
    service: GenreService = Depends(get_genre_service),
) -> GenreResponse:
    return await service.create(payload)


@router.get(
    "/{id}",
    response_model=GenreResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[long_cache()],
)
async def get_genre(
    id: UUID,
    service: GenreService = Depends(get_genre_service),
) -> GenreResponse:
    return await service.get_by_id(id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
)
async def delete_genre(
    id: UUID,
    service: GenreService = Depends(get_genre_service),
) -> None:
    await service.delete(id)


@router.post(
    "/{id}/restore",
    response_model=GenreResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def restore_genre(
    id: UUID,
    service: GenreService = Depends(get_genre_service),
) -> GenreResponse:
    return await service.restore(id)
