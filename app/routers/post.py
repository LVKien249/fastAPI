from statistics import mode
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from auth_2 import get_current_user
import schemas, models, utils, auth_2
from sqlalchemy.orm import Session
from database import engine, get_db
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix = "/posts",
    tags = ['Posts']
)

# @router.get("/", response_model = List[schemas.Post])
@router.get("/", response_model = List[schemas.PostVote])
def get_posts(db: Session = Depends(get_db), current_id:int = Depends(auth_2.get_current_user),
     limit:int = 10, skip: int = 0, search:Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_id.id).all()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    res = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
                    models.Vote, models.Vote.post_id == models.Post.id).group_by(models.Post.id).all()
    
    return res

@router.post("/", status_code = status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(auth_2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, publisher) VALUES (%s, %s, %s)
    # RETURNING *
    # """, (post.title, post.content, post.publisher))
    # new_post = cursor.fetchone()
    # connection.commit()
    new_post = models.Post(owner_id = current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model = schemas.PostVote)
def get_post(id: str, db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""", str(id))
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    res = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
                    models.Vote, models.Vote.post_id == models.Post.id).group_by(models.Post.id).first()
    
    return res
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
    return  post

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(auth_2.get_current_user)):
    # cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", str(id))
    # del_post = cursor.fetchone()
    # connection.commit()

    del_post = db.query(models.Post).filter(models.Post.id == id)
    post = del_post.first()

    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"{id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "not authorized")

    del_post.delete(synchronize_session=False)
    db.commit()
    return  Response(status_code = status.HTTP_200_OK)

@router.put("/{id}", response_model = schemas.Post)
def update_post(id: int, update_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(auth_2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, publisher = %s
    # WHERE id = %s RETURNING *""", (post.title, post.content, post.publisher))
    # update_p = cursor.fetchone()
    # connection.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"{id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "not authorized")

    post_query.update(update_post.dict(), synchronize_session = False)
    db.commit()
    return post_query.first()