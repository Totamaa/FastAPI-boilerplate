from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.api.dependencies.auth import verify_api_key
from app.modules.directors.dependencies import get_director_service
from app.modules.directors.schemas import DirectorCreate, DirectorResponse, DirectorUpdate
from app.modules.directors.service import DirectorService
from app.modules.movies.dependencies import get_movie_service
from app.modules.movies.schemas import MovieResponse
from app.modules.movies.service import MovieService

router = APIRouter()


@router.get("/", response_model=list[DirectorResponse], status_code=status.HTTP_200_OK)
async def list_directors(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # cas 2 — cross-resource filter: directors an actor has worked with
    actor_id: UUID | None = Query(
        None, description="Filter to directors who have worked with this actor"
    ),
    service: DirectorService = Depends(get_director_service),
) -> list[DirectorResponse]:
    if actor_id is not None:
        return await service.get_all_for_actor(actor_id, limit=limit, offset=offset)
    return await service.get_all(limit=limit, offset=offset)


@router.post(
    "/",
    response_model=DirectorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_director(
    payload: DirectorCreate,
    service: DirectorService = Depends(get_director_service),
) -> DirectorResponse:
    return await service.create(payload)


@router.get("/{id}", response_model=DirectorResponse, status_code=status.HTTP_200_OK)
async def get_director(
    id: UUID,
    service: DirectorService = Depends(get_director_service),
) -> DirectorResponse:
    return await service.get_by_id(id)


# cas 1 — sub-resource: movies by this director, served by MovieService
@router.get("/{id}/movies", response_model=list[MovieResponse], status_code=status.HTTP_200_OK)
async def list_director_movies(
    id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    director_service: DirectorService = Depends(get_director_service),
    movie_service: MovieService = Depends(get_movie_service),
) -> list[MovieResponse]:
    await director_service.get_by_id(id)  # 404 if director does not exist
    return await movie_service.get_all(director_id=id, limit=limit, offset=offset)


@router.put(
    "/{id}",
    response_model=DirectorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def update_director(
    id: UUID,
    payload: DirectorUpdate,
    service: DirectorService = Depends(get_director_service),
) -> DirectorResponse:
    return await service.update(id, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
)
async def delete_director(
    id: UUID,
    service: DirectorService = Depends(get_director_service),
) -> None:
    await service.delete(id)
