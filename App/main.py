from fastapi import FastAPI, Request, UploadFile, File, Query, Form, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import subprocess
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from passlib.context import CryptContext  # Assurez-vous d'installer passlib avec pip install passlib[bcrypt]
from sqlalchemy.orm import Session
from services.authentification import User, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.security.utils import get_authorization_scheme_param

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "une_cle_secrete_temporaire_a_changer")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()

app.mount("/static", StaticFiles(directory="./webapp/static"), name="static")

templates = Jinja2Templates(directory="./webapp/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Identification impossible",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Essayez d'abord le token du header
    actual_token = token
    
    # Si pas de token dans le header, essayez le cookie
    if not actual_token:
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            if cookie_token.startswith("Bearer "):
                actual_token = cookie_token[7:]  # Enlever "Bearer "
            else:
                actual_token = cookie_token
    
    if not actual_token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(actual_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = get_user(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "nom_app": "PROCR"})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "nom_app": "PROCR"})

@app.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Ne pas préfixer le token avec "Bearer" dans le cookie
    response = RedirectResponse(url="/afterlogin", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response

@app.get("/afterlogin", response_class=HTMLResponse)
async def afterlogin(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("afterlogin.html", {"request": request, "nom_app": "PROCR"})

@app.get("/importfichier", response_class=HTMLResponse)
async def importfichier(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("importfichier.html", {"request": request, "nom_app": "PROCR"})

@app.get("/bdd", response_class=HTMLResponse)
async def bdd(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("bdd.html", {"request": request, "nom_app": "PROCR"})

@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("stats.html", {"request": request, "nom_app": "PROCR"})

@app.get("/documentation", response_class=HTMLResponse)
async def documentation(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("documentation.html", {"request": request, "nom_app": "PROCR"})

@app.get("/qr_tesseract", response_class=HTMLResponse)
async def qr_tesseract_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("qr_tesseract.html", {"request": request})

@app.get("/tesseract", response_class=HTMLResponse)
async def tesseract_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("tesseract.html", {"request": request})

@app.get("/azure", response_class=HTMLResponse)
async def azure_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("azure.html", {"request": request})

@app.get("/qr_azure", response_class=HTMLResponse)
async def azure_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("qr_azure.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "nom_app": "PROCR"})

@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "nom_app": "PROCR", "error": "Cet email est déjà utilisé."}
        )
    
    # Hashage du mot de passe et création de l'utilisateur
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    
    # Redirection vers la page de connexion
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "nom_app": "PROCR", "message": "Inscription réussie ! Vous pouvez maintenant vous connecter."}
    )

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")  # Supprime le token de connexion
    return response

@app.get("/logout")
async def logout_get():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")  # Supprime le token de connexion
    return response