from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.api.dependencies.auth import verify_api_key
from app.modules.actors.dependencies import get_actor_service
from app.modules.actors.schemas import ActorCreate, ActorResponse, ActorUpdate
from app.modules.actors.service import ActorService

router = APIRouter()

_INCLUDE_DESCRIPTION = (
    "Comma-separated relations to embed in the response. "
    "Supported: movies — embeds filmography with role info (filmography: null when absent). "
    "Example: ?include=movies"
)


@router.get("/", response_model=list[ActorResponse], status_code=status.HTTP_200_OK)
async def list_actors(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ActorService = Depends(get_actor_service),
) -> list[ActorResponse]:
    return await service.get_all(limit=limit, offset=offset)


@router.post(
    "/",
    response_model=ActorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_actor(
    payload: ActorCreate,
    service: ActorService = Depends(get_actor_service),
) -> ActorResponse:
    return await service.create(payload)


@router.get("/{id}", response_model=ActorResponse, status_code=status.HTTP_200_OK)
async def get_actor(
    id: UUID,
    # cas 3 — simple include: ?include=movies populates filmography in ActorResponse
    include: str | None = Query(None, description=_INCLUDE_DESCRIPTION),
    service: ActorService = Depends(get_actor_service),
) -> ActorResponse:
    includes = set(include.split(",")) if include else set()
    return await service.get_by_id(id, include_movies="movies" in includes)


@router.put(
    "/{id}",
    response_model=ActorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def update_actor(
    id: UUID,
    payload: ActorUpdate,
    service: ActorService = Depends(get_actor_service),
) -> ActorResponse:
    return await service.update(id, payload)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_api_key)],
)
async def delete_actor(
    id: UUID,
    service: ActorService = Depends(get_actor_service),
) -> None:
    await service.delete(id)
