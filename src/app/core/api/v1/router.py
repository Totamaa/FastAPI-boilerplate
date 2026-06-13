from fastapi import APIRouter

from app.core.api.v1.actors import router as actors_router
from app.core.api.v1.auth import router as auth_router
from app.core.api.v1.directors import router as directors_router
from app.core.api.v1.feature_flags import router as feature_flags_router
from app.core.api.v1.genres import router as genres_router
from app.core.api.v1.movie_cast import router as movie_cast_router
from app.core.api.v1.movies import router as movies_router
from app.core.api.v1.reviews import router as reviews_router
from app.core.api.v1.users import router as users_router

# No global auth dependency — each route declares its own (public / api-key / JWT)
router_v1 = APIRouter()

router_v1.include_router(auth_router, prefix="/auth", tags=["Auth"])
router_v1.include_router(directors_router, prefix="/directors", tags=["Directors"])
router_v1.include_router(genres_router, prefix="/genres", tags=["Genres"])
router_v1.include_router(actors_router, prefix="/actors", tags=["Actors"])
router_v1.include_router(movies_router, prefix="/movies", tags=["Movies"])
router_v1.include_router(movie_cast_router, prefix="/movie-cast", tags=["Movie Cast"])
router_v1.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
router_v1.include_router(users_router, prefix="/users", tags=["Users"])
router_v1.include_router(feature_flags_router, prefix="/feature-flags", tags=["Feature Flags"])
