import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database import get_db, MovieModel
from schemas import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
        db: AsyncSession = Depends(get_db),
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=10, ge=1, le=20)
):
    total_items = await db.scalar(
        select(func.count()).select_from(MovieModel)
    )
    total_items = total_items or 0

    if total_items == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    total_pages = math.ceil(total_items / per_page)
    result = await db.scalars(
        select(MovieModel)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    movies = result.all()
    if not movies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    prev_page = (
        f"/theater/movies/?page={page - 1}&per_page={per_page}"
        if page > 1
        else None
    )

    next_page = (
        f"/theater/movies/?page={page + 1}&per_page={per_page}"
        if page < total_pages
        else None
    )

    return MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items
    )


@router.get(
    "/movies/{movie_id}/",
    response_model=MovieDetailResponseSchema
)
async def get_movie(
        movie_id: int,
        db: AsyncSession = Depends(get_db),
):
    movie = await db.scalar(
        select(MovieModel).where(MovieModel.id == movie_id)
    )
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )
    return movie
