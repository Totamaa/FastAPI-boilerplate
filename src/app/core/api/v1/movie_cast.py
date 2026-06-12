from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.api.dependencies.auth import verify_api_key
from app.modules.movie_cast.dependencies import get_movie_cast_service
from app.modules.movie_cast.schemas import (
    CastEntryCreate,
    CastEntryDetailedResponse,
    CastEntryResponse,
    CastEntryUpdate,
)
from app.modules.movie_cast.service import MovieCastService

router = APIRouter()


@router.get("/", response_model=list[CastEntryDetailedResponse], status_code=status.HTTP_200_OK)
async def list_cast_by_movie(
    movie_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MovieCastService = Depends(get_movie_cast_service),
) -> list[CastEntryDetailedResponse]:
    return await service.get_by_movie(movie_id, limit=limit, offset=offset)


@router.post(
    "/",
    response_model=CastEntryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def add_to_cast(
    payload: CastEntryCreate,
    service: MovieCastService = Depends(get_movie_cast_service),
) -> CastEntryResponse:
    return await service.add_to_cast(payload)


@router.put(
    "/{id}",
    response_model=CastEntryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def update_cast_entry(
    id: UUID,
    payload: CastEntryUpdate,
    service: MovieCastService = Depends(get_movie_cast_service),
) -> CastEntryResponse:
    return await service.update_cast_entry(id, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
)
async def remove_from_cast(
    id: UUID,
    service: MovieCastService = Depends(get_movie_cast_service),
) -> None:
    await service.remove_from_cast(id)
