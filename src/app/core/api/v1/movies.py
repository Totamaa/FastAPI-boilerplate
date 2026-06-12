from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status

from app.core.api.dependencies.auth import verify_api_key
from app.modules.movie_details.dependencies import get_movie_detail_service
from app.modules.movie_details.schemas import MovieDetailCreate, MovieDetailResponse
from app.modules.movie_details.service import MovieDetailService
from app.modules.movies.dependencies import get_movie_service
from app.modules.movies.enums import MovieStatus
from app.modules.movies.schemas import (
    MovieCreate,
    MovieDetailedResponse,
    MovieResponse,
    MovieUpdate,
)
from app.modules.movies.service import MovieService

router = APIRouter()


@router.get("/", response_model=list[MovieResponse], status_code=http_status.HTTP_200_OK)
async def list_movies(
    status: MovieStatus | None = None,
    release_year: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: MovieService = Depends(get_movie_service),
) -> list[MovieResponse]:
    return await service.get_all(
        status=status, release_year=release_year, limit=limit, offset=offset
    )


@router.post(
    "/",
    response_model=MovieResponse,
    status_code=http_status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_movie(
    payload: MovieCreate,
    service: MovieService = Depends(get_movie_service),
) -> MovieResponse:
    return await service.create(payload)


@router.get("/{id}", response_model=MovieDetailedResponse, status_code=http_status.HTTP_200_OK)
async def get_movie(
    id: UUID,
    service: MovieService = Depends(get_movie_service),
) -> MovieDetailedResponse:
    return await service.get_detailed(id)


@router.put(
    "/{id}",
    response_model=MovieResponse,
    status_code=http_status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def update_movie(
    id: UUID,
    payload: MovieUpdate,
    service: MovieService = Depends(get_movie_service),
) -> MovieResponse:
    return await service.update(id, payload)


@router.delete(
    "/{id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
)
async def delete_movie(
    id: UUID,
    service: MovieService = Depends(get_movie_service),
) -> None:
    await service.delete(id)


@router.post(
    "/{id}/restore",
    response_model=MovieResponse,
    status_code=http_status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def restore_movie(
    id: UUID,
    service: MovieService = Depends(get_movie_service),
) -> MovieResponse:
    return await service.restore(id)


@router.patch(
    "/{id}/details",
    response_model=MovieDetailResponse,
    status_code=http_status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def upsert_movie_details(
    id: UUID,
    payload: MovieDetailCreate,
    service: MovieDetailService = Depends(get_movie_detail_service),
) -> MovieDetailResponse:
    return await service.upsert(id, payload)
