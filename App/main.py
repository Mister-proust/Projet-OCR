from fastapi import FastAPI, Request, UploadFile, File, Query, Form, HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from passlib.context import CryptContext  
from sqlalchemy.orm import Session
from services.authentification import User, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta
from typing import Optional
import shutil
from services.tesseract_ocr import get_invoice_files, process_invoices
from services.qrcode_ocr import get_invoice_files, extract_qr_data
from Database.db_connection import SQLClient
from Database.models.table_database import Utilisateur, Facture, Article, Monitoring
import pandas as pd
from prometheus_fastapi_instrumentator import Instrumentator
import time
from collections import Counter


load_dotenv(override=True)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.mount("/static", StaticFiles(directory="./static"), name="static")

os.makedirs("static/uploads", exist_ok=True)

templates = Jinja2Templates(directory="./templates")

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
    response = RedirectResponse(url="/afterlogin", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response

@app.get("/afterlogin", response_class=HTMLResponse)
async def afterlogin(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("afterlogin.html", {"request": request, "nom_app": "PROCR"})

@app.get("/importfichier", response_class=HTMLResponse)
async def importfichier(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("importfichier.html", {"request": request, "nom_app": "PROCR"})

@app.get("/monitoring", response_class=HTMLResponse)
async def monitoring(request: Request, user: User = Depends(get_current_user)):
    client = SQLClient()
    with client.get_session() as session:
        monitoring_data = session.query(Monitoring).order_by(Monitoring.timestamp.desc()).all()
        return templates.TemplateResponse("monitoring.html", {"request": request, "nom_app": "PROCR", "monitoring_data": monitoring_data})

@app.get("/documentation", response_class=HTMLResponse)
async def documentation(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("documentation.html", {"request": request, "nom_app": "PROCR"})

@app.get("/qr_tesseract", response_class=HTMLResponse)
async def qrtesseract_page(    
    request: Request, 
    filename: str = Query(None) 
):
    if not filename:
        uploads_dir = "static/uploads"
        files = os.listdir(uploads_dir)
        if files:
            filename = files[-1]
    
    if not filename:
        return HTMLResponse(content="Aucun fichier trouvé", status_code=404)
    
    return templates.TemplateResponse("qr_tesseract.html", {
        "request": request, 
        "image_path": f"/static/uploads/{filename}"
    })

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
    
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "nom_app": "PROCR", "message": "Inscription réussie ! Vous pouvez maintenant vous connecter."}
    )

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")  
    return response

@app.get("/logout")
async def logout_get():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token") 
    return response

@app.post("/uploadfile")
async def upload_file(
    file: UploadFile = File(...), 
):
    if not file.filename:
        return {"error": "Pas de fichier sélectionné"}

    _, file_extension = os.path.splitext(file.filename)
    
    standard_filename = f"image_telecharge{file_extension}"
    file_path = f"static/uploads/{standard_filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return RedirectResponse(url=f"/qr_tesseract?filename={standard_filename}", status_code=303)

@app.post("/ocrtessqr")
async def ocr_tesseract_qr(request: Request):
    start_time = time.time()
    client = SQLClient()  
    try:
        print("Route /ocrtessqr appelée")
        print(f"Méthode de requête : {request.method}")
        uploads_dir = "static/uploads"
        files = os.listdir(uploads_dir)
        print(f"Fichiers disponibles : {files}")
        if not files:
            record_monitoring_data(client, "ocr_processing", status="failure", details="Aucun fichier trouvé")
            return JSONResponse(
                status_code=404,
                content={"error": "Aucun fichier trouvé"}
            )

        latest_file = os.path.join(uploads_dir, files[-1])

        qr_data = extract_qr_data(latest_file)
        ocr_text = process_invoices(latest_file)
        print(ocr_text)

        data = {
            "utilisateur": {},
            "facture": {},
            "articles": []
        }

        if qr_data:
            data["facture"]["nom_facture"] = qr_data.get("nom_facture", "")
            data["facture"]["date_facture"] = qr_data.get("date_facture", "")
            data["utilisateur"]["genre"] = qr_data.get("genre", "")
            data["utilisateur"]["date_anniversaire"] = qr_data.get("date_anniversaire", "")

        if "utilisateur" in ocr_text:
            data["utilisateur"].update(ocr_text["utilisateur"])
        if "facture" in ocr_text:
            data["facture"].update(ocr_text["facture"])
        if "articles" in ocr_text:
            data["articles"] = ocr_text["articles"]

        if data["facture"].get("nom_facture"):
            add_data_to_db(client, data)
            record_monitoring_data(client, "ocr_data_saved", status="success", details=f"Facture: {data['facture']['nom_facture']}")

        end_time = time.time()
        processing_time = end_time - start_time
        record_monitoring_data(client, "ocr_processing_time", value=processing_time, status="success")

        return JSONResponse(
            content={
                "message": "Données OCR et QR enregistrées avec succès !",
                "qr_code": bool(qr_data),
                "ocr_text": ocr_text
            }
        )
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        record_monitoring_data(client, "ocr_processing_time", value=processing_time, status="failure", details=str(e))
        record_monitoring_data(client, "ocr_processing", status="failure", details=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        pass 
    
def add_data_to_db(client, data):
    utilisateur = Utilisateur(**data["utilisateur"])
    client.insert(utilisateur)
    record_monitoring_data(client, "database_insert", value=1.0, details="Utilisateur ajouté")

    facture = Facture(**data["facture"])
    client.insert(facture)
    record_monitoring_data(client, "database_insert", value=1.0, details="Facture ajoutée")

    for article_data in data["articles"]:
        article = Article(**article_data)
        client.insert(article)
        record_monitoring_data(client, "database_insert", value=1.0, details="Article ajouté")

    print(f"Donnée de la facture ajoutée avec succès (nom : {data['facture']['nom_facture']})")

def get_dataframe(table: str):
    client = SQLClient()
    with client.get_session() as session:
        if table == 'Utilisateur':
            query = session.query(Utilisateur).all()
            data = [{
                'Email': utilisateur.email_personne,
                'Nom': utilisateur.nom_personne,
                'Genre': utilisateur.genre,
                'Ville': utilisateur.ville_personne,
                'Date Anniversaire': utilisateur.date_anniversaire
            } for utilisateur in query]
        elif table == 'Facture':
            query = session.query(Facture).all()
            data = [{
                'Nom Facture': facture.nom_facture,
                'Date Facture': facture.date_facture,
                'Total': facture.total_facture,
                'Email Utilisateur': facture.email_personne
            } for facture in query]
        elif table == 'Article':
            query = session.query(Article).all()
            data = [{
                'Nom Facture': article.nom_facture,
                'Nom Article': article.nom_article,
                'Quantité': article.quantite,
                'Prix': article.prix
            } for article in query]
        
        return pd.DataFrame(data)

@app.get("/bdd")
async def bdd(request: Request, table_name:Optional[str] = None, search: Optional[str] = None):

    search = None
    print(table_name, search)
    # Vérifier si la table est valide
    if table_name not in ['Utilisateur', 'Facture', 'Article']:
        table_name= "Article"
        
    df = get_dataframe(table_name)

    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    data = df.to_dict(orient='records')

    return templates.TemplateResponse("bdd.html", {
        "request": request,
        "nom_app": "PROCR",
        "data": data,  # Passer 'data' ici
        "table_name": table_name  # Passer 'table_name' pour l'afficher dans le titre
    })

def record_monitoring_data(client: SQLClient, metric_name: str, value: Optional[float] = None, status: Optional[str] = None, details: Optional[str] = None):
    monitoring_entry = Monitoring(
        metric_name=metric_name,
        value=value,
        status=status,
        details=details
    )
    client.insert(monitoring_entry)

def calculate_average_basket():
    client = SQLClient()
    with client.get_session() as session:
        factures = session.query(Facture).all()
        if not factures:
            return 0
        valid_factures = [facture for facture in factures if facture.total_facture is not None]
        if not valid_factures:
            return 0
        total_revenue = sum(facture.total_facture for facture in valid_factures)
        return total_revenue / len(valid_factures) if valid_factures else 0

def calculate_total_revenue():
    client = SQLClient()
    with client.get_session() as session:
        factures = session.query(Facture).all()
        return sum(facture.total_facture for facture in factures if facture.total_facture is not None)

def get_invoice_count():
    client = SQLClient()
    with client.get_session() as session:
        return session.query(Facture).count()

def get_unique_user_count():
    client = SQLClient()
    with client.get_session() as session:
        return session.query(Utilisateur.email_personne).distinct().count()

def get_most_prolific_clients(limit=5):
    client = SQLClient()
    with client.get_session() as session:
        results = session.query(Utilisateur.nom_personne, Utilisateur.email_personne, Facture.total_facture).\
            join(Facture, Utilisateur.email_personne == Facture.email_personne).\
            all()
        client_totals = {}
        for name, email, total in results:
            if total is not None:  
                if email not in client_totals:
                    client_totals[email] = {"name": name, "total": 0}
                client_totals[email]["total"] += total
        sorted_clients = sorted(client_totals.items(), key=lambda item: item[1]["total"], reverse=True)
        return [{"name": client[1]["name"], "email": client[0], "total_spent": client[1]["total"]} for client in sorted_clients[:limit]]

def get_most_regular_clients(limit=5):
    client = SQLClient()
    with client.get_session() as session:
        results = session.query(Utilisateur.nom_personne, Utilisateur.email_personne).\
            join(Facture, Utilisateur.email_personne == Facture.email_personne).\
            all()
        client_counts = {}
        for name, email in results:
            if email not in client_counts:
                client_counts[email] = {"name": name, "count": 0}
            client_counts[email]["count"] += 1

        sorted_clients = sorted(client_counts.items(), key=lambda item: item[1]["count"], reverse=True)
        return [{"name": client[1]["name"], "email": client[0], "invoice_count": client[1]["count"]} for client in sorted_clients[:limit]]

def get_most_demanding_cities(limit=5):
    client = SQLClient()
    with client.get_session() as session:
        results = session.query(Utilisateur.ville_personne).all()
        city_counts = Counter([result[0] for result in results])
        most_common_cities = city_counts.most_common(limit)
        return [{"city": city, "count": count} for city, count in most_common_cities]

def get_most_purchased_articles(limit=5):
    client = SQLClient()
    with client.get_session() as session:
        results = session.query(Article.nom_article, Article.quantite).all()
        article_counts = {}
        for name, quantity in results:
            article_counts[name] = article_counts.get(name, 0) + quantity

        sorted_articles = sorted(article_counts.items(), key=lambda item: item[1], reverse=True)
        return [{"article": article, "total_quantity": quantity} for article, quantity in sorted_articles[:limit]]

def get_null_total_facture_count():
    client = SQLClient()
    with client.get_session() as session:
        return session.query(Facture).filter(Facture.total_facture.is_(None)).count()

@app.get("/stats", response_class=HTMLResponse)
async def stats_dashboard(request: Request, user: User = Depends(get_current_user)):
    average_basket = calculate_average_basket()
    total_revenue = calculate_total_revenue()
    invoice_count = get_invoice_count()
    unique_user_count = get_unique_user_count()
    most_prolific_clients = get_most_prolific_clients()
    most_regular_clients = get_most_regular_clients()
    most_demanding_cities = get_most_demanding_cities()
    most_purchased_articles = get_most_purchased_articles()
    null_total_facture_count = get_null_total_facture_count()

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "nom_app": "PROCR",
            "average_basket": average_basket,
            "total_revenue": total_revenue,
            "invoice_count": invoice_count,
            "unique_user_count": unique_user_count,
            "most_prolific_clients": most_prolific_clients,
            "most_regular_clients": most_regular_clients,
            "most_demanding_cities": most_demanding_cities,
            "most_purchased_articles": most_purchased_articles,
            "null_total_facture_count": null_total_facture_count, 
        },
    )