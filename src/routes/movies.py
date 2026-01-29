from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MovieModel
from database.session import get_db
from schemas.movies import MovieDetailResponseSchema, MovieListResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    total_stmt = select(func.count(MovieModel.id))
    total_items = (await db.execute(total_stmt)).scalar_one()

    if total_items == 0:
        raise HTTPException(404, "No movies found.")

    total_pages = (total_items + per_page - 1) // per_page
    offset = (page - 1) * per_page

    stmt = select(MovieModel).offset(offset).limit(per_page)
    movies = (await db.execute(stmt)).scalars().all()

    if not movies:
        raise HTTPException(404, "No movies found.")

    base_url = "/api/v1/theater/movies"
    return {
        "movies": movies,
        "prev_page": f"{base_url}?page={page-1}&per_page={per_page}" if page > 1 else None,
        "next_page": f"{base_url}?page={page+1}&per_page={per_page}" if page < total_pages else None,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_by_id(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(MovieModel).where(MovieModel.id == movie_id)
    movie = (await db.execute(stmt)).scalar_one_or_none()

    if movie is None:
        raise HTTPException(404, "Movie with the given ID was not found.")

    return movie
