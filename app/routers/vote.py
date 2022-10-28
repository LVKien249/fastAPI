from statistics import mode
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
import schemas, database, models, auth_2
from sqlalchemy.orm import Session

router = APIRouter(
    prefix = '/vote',
    tags = ["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote: schemas.Vote, db:Session = Depends(database.get_db), current_user: int = Depends(auth_2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="doesn exist post")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, 
                                    models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"already vote")
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message" : "vote successfully"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vote doesn exist")
        
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message" : "successfully delete vote"}