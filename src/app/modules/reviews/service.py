from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.logs import LoggerManager
from app.modules.movies.exceptions import MovieNotFoundException
from app.modules.movies.repository import MovieRepository
from app.modules.reviews.exceptions import (
    ReviewAlreadyExistsException,
    ReviewForbiddenException,
    ReviewNotFoundException,
)
from app.modules.reviews.model import ReviewModel
from app.modules.reviews.repository import ReviewRepository
from app.modules.reviews.schemas import (
    ReviewCreate,
    ReviewDetailedResponse,
    ReviewResponse,
    ReviewUpdate,
)


class ReviewService:
    def __init__(
        self,
        logger: LoggerManager,
        session: AsyncSession,
        request_id: str,
        review_repository: ReviewRepository,
        movie_repository: MovieRepository,
    ):
        self.tag = "SERVICE:Review"
        self.logger = logger
        self.session = session
        self.request_id = request_id
        self.review_repository = review_repository
        self.movie_repository = movie_repository

    async def get_by_movie(
        self,
        movie_id: UUID,
        limit: int,
        offset: int,
    ) -> list[ReviewDetailedResponse]:
        reviews = await self.review_repository.get_by_movie(
            movie_id=movie_id,
            db=self.session,
            limit=limit,
            offset=offset,
        )
        return [ReviewDetailedResponse.from_model(r) for r in reviews]

    async def get_by_user(self, user_id: UUID) -> list[ReviewResponse]:
        reviews = await self.review_repository.get_by_user(
            user_id=user_id,
            db=self.session,
        )
        return [ReviewResponse.from_model(r) for r in reviews]

    async def create(self, user_id: UUID, data: ReviewCreate) -> ReviewResponse:
        self.logger.info(
            tag=self.tag,
            message=f"Creating review user_id={user_id} movie_id={data.movie_id}",
            extra=self.request_id,
        )
        movie = await self.movie_repository.get_by_id(id=data.movie_id, db=self.session)
        if not movie:
            raise MovieNotFoundException(id=data.movie_id)

        existing = await self.review_repository.get_by_user_and_movie(
            user_id=user_id,
            movie_id=data.movie_id,
            db=self.session,
        )
        if existing:
            raise ReviewAlreadyExistsException(movie_id=data.movie_id)

        review = ReviewModel(
            user_id=user_id,
            movie_id=data.movie_id,
            rating=data.rating,
            title=data.title,
            body=data.body,
            contains_spoilers=data.contains_spoilers,
        )
        review = await self.review_repository.create(review=review, db=self.session)
        return ReviewResponse.from_model(review)

    async def update(
        self,
        review_id: UUID,
        user_id: UUID,
        data: ReviewUpdate,
    ) -> ReviewResponse:
        self.logger.info(
            tag=self.tag,
            message=f"Updating review review_id={review_id} user_id={user_id}",
            extra=self.request_id,
        )
        review = await self.review_repository.get_by_id(id=review_id, db=self.session)
        if not review:
            raise ReviewNotFoundException(id=review_id)

        if review.user_id != user_id:
            raise ReviewForbiddenException()

        patch = {k: v for k, v in data.model_dump().items() if v is not None}
        review = await self.review_repository.update(review=review, data=patch, db=self.session)
        return ReviewResponse.from_model(review)

    async def delete(self, review_id: UUID, user_id: UUID) -> UUID:
        """Deletes the review and returns the movie_id for post-deletion background tasks."""
        self.logger.info(
            tag=self.tag,
            message=f"Deleting review review_id={review_id} user_id={user_id}",
            extra=self.request_id,
        )
        review = await self.review_repository.get_by_id(id=review_id, db=self.session)
        if not review:
            raise ReviewNotFoundException(id=review_id)

        if review.user_id != user_id:
            raise ReviewForbiddenException()

        movie_id = review.movie_id
        await self.review_repository.delete(review=review, db=self.session)
        return movie_id
