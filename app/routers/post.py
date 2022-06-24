from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas, oauth2
from app.database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), 
            limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print(current_user.email)
    new_post = models.Post(
        user_id=current_user.id,
        **post.dict()
        )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}/", response_model=schemas.PostOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db), 
            current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.id == str(id)).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id: {id} was not found."
            )

    return post


@router.put("/{id}/", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == str(id))
    if post_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Post with id: {id} was not found."
            )
    if post_query.first().user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform request action"
            )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


@router.patch("/{id}/")
def patch_post():
    return {"data": "Getting your posts"}


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == str(id))
    if post.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found."
        )
    if post.first().user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to perform request action"
            )
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)