from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User
from schemas import User as User_schem, UserCreate
from db import get_db
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
o2auth_bearer = OAuth2PasswordBearer("auth/token")

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

@router.post("/register")
async def register_user(user : UserCreate, db : Session = Depends(get_db)):
    try:
        new_user = User(email = user.email, hashed_password = bcrypt_context.hash(user.password))

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already exist")
    
    except Exception as e:
        return {"Error" : str(e)}
    

@router.post("/token")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthenticateUser(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = CreateAccessToken(user.id, user.email, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}


def AuthenticateUser(email : str, password : str, db):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong password")
    
    return user

def CreateAccessToken(id : int, email : str, token_expire : timedelta):
    encode = {"id" : id, "email" : email}
    expire = datetime.utcnow() + token_expire
    encode.update({"exp" : expire})
    return jwt.encode(encode, key=SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(db : Session = Depends(get_db), token : str = Depends(o2auth_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        email = payload.get("email")
        if not email or not user_id:
            raise HTTPException(status_code=401, detail="Error, could not validate user")
        
        user = db.query(User).filter(User.id == user_id).first()

        return user
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Error, could not validate user")

@router.get("/user")
async def print_user(user : dict = Depends(get_current_user)):
    return {"id" : user.id, "email" : user.email}