from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas import ReviewCreate, ReviewUpdate, ReviewResponse 
from app.reviews_repo import ReviewRepository
from app.models import UserActivityLog

router = APIRouter()
review_repo = ReviewRepository()

@router.post("/reviews/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate):
    review_id = await review_repo.create_review(
        movie_id=review.movie_id,
        user_id=review.user_id,
        rating=review.rating,
        review_text=review.review_text,
    )
    await UserActivityLog.create(
        user_id=review.user_id,
        movie_id=review.movie_id,
        action="reviewed",
        details={"rating": review.rating, "review_text": review.review_text}
    )
    return await review_repo.get_review_by_id(review_id)

@router.get("/reviews/{movie_id}/", response_model=List[ReviewResponse])
async def get_reviews_by_movie(movie_id: int):
    reviews = await review_repo.get_reviews_by_movie(movie_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this movie")
    return reviews

@router.put("/reviews/{review_id}/", response_model=ReviewResponse)
async def update_review(review_id: int, review_update: ReviewUpdate):
    updated = await review_repo.update_review(
        review_id=review_id,
        rating=review_update.rating,
        review_text=review_update.review_text,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found or update failed")
    return await review_repo.get_review_by_id(review_id)

@router.delete("/reviews/{review_id}/")
async def delete_review(review_id: int):
    deleted = await review_repo.delete_review(review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"status": "success", "message": "Review deleted"}
@router.get("/users/{user_id}/activity-log/")
async def get_activity_log(user_id: int):
    logs = await UserActivityLog.filter(user_id=user_id).order_by("-timestamp")
    return {"status": "success", "data": logs}
