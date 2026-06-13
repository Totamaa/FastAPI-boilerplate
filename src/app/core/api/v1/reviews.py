from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.background.tasks.movie_stats import update_movie_stats_after_review
from app.core.api.dependencies.auth import get_current_user, verify_api_key
from app.core.api.dependencies.cache import short_cache
from app.core.api.dependencies.db import get_session
from app.modules.reviews.dependencies import get_review_service
from app.modules.reviews.schemas import (
    ReviewCreate,
    ReviewDetailedResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.modules.reviews.service import ReviewService
from app.modules.users.model import UserModel

router = APIRouter()


@router.get(
    "/",
    response_model=list[ReviewDetailedResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[short_cache()],
)
async def list_reviews(
    movie_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ReviewService = Depends(get_review_service),
) -> list[ReviewDetailedResponse]:
    return await service.get_by_movie(movie_id, limit=limit, offset=offset)


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    review = await service.create(user_id=current_user.id, data=payload)
    background_tasks.add_task(update_movie_stats_after_review, review.movie_id, db)
    return review


@router.put("/{id}", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
async def update_review(
    id: UUID,
    payload: ReviewUpdate,
    current_user: UserModel = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    return await service.update(review_id=id, user_id=current_user.id, data=payload)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    id: UUID,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_session),
) -> None:
    movie_id = await service.delete(review_id=id, user_id=current_user.id)
    background_tasks.add_task(update_movie_stats_after_review, movie_id, db)


@router.post(
    "/{id}/restore",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def restore_review(
    id: UUID,
    background_tasks: BackgroundTasks,
    service: ReviewService = Depends(get_review_service),
    db: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    review = await service.restore(review_id=id)
    background_tasks.add_task(update_movie_stats_after_review, review.movie_id, db)
    return review
