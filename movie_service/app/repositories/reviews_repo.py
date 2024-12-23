# app/repositories/reviews_repo.py
from typing import List, Optional
from tortoise.exceptions import DoesNotExist
from app.models import Review

class ReviewRepository:
    async def create_review(self, movie_id: int, user_id: int, rating: int, review_text: Optional[str]) -> int:
        review = await Review.create(
            movie_id=movie_id,
            user_id=user_id,
            rating=rating,
            review_text=review_text
        )
        return review.id

    async def get_reviews_by_movie(self, movie_id: int) -> List[Review]:
        return await Review.filter(movie_id=movie_id).all()

    async def update_review(self, review_id: int, rating: Optional[int], review_text: Optional[str]) -> bool:
        try:
            review = await Review.get(id=review_id)
        except DoesNotExist:
            return False

        if rating is not None:
            review.rating = rating
        if review_text is not None:
            review.review_text = review_text

        await review.save()
        return True

    async def delete_review(self, review_id: int) -> bool:
        deleted_count = await Review.filter(id=review_id).delete()
        return deleted_count > 0
