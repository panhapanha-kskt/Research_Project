from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .db import Base, engine, SessionLocal
from .models import User

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user")
def create_user(name: str, email: str, age: int, db: Session = Depends(get_db)):
    user = User(name=name, email=email, age=age)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "saved", "user": {"id": user.id, "name": user.name}}


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
