from fastapi import FastAPI, Request, UploadFile, File, Query, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import subprocess
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

app = FastAPI()

app.mount("/static", StaticFiles(directory="./webapp/static"), name="static")

templates = Jinja2Templates(directory="./webapp/templates")



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "nom_app": "PROCR"})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "nom_app": "PROCR"})


@app.get("/afterlogin", response_class=HTMLResponse)
async def afterlogin(request: Request):
    return templates.TemplateResponse("afterlogin.html", {"request": request, "nom_app": "PROCR"})

@app.get("/importfichier", response_class=HTMLResponse)
async def importfichier(request: Request):
    return templates.TemplateResponse("importfichier.html", {"request": request, "nom_app": "PROCR"})

@app.get("/bdd", response_class=HTMLResponse)
async def bdd(request: Request):
    return templates.TemplateResponse("bdd.html", {"request": request, "nom_app": "PROCR"})

@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request, "nom_app": "PROCR"})

@app.get("/documentation", response_class=HTMLResponse)
async def documentation(request: Request):
    return templates.TemplateResponse("documentation.html", {"request": request, "nom_app": "PROCR"})

@app.get("/qr_tesseract", response_class=HTMLResponse)
async def qr_tesseract_page(request: Request):
    return templates.TemplateResponse("qr_tesseract.html", {"request": request})

@app.get("/tesseract", response_class=HTMLResponse)
async def tesseract_page(request: Request):
    return templates.TemplateResponse("tesseract.html", {"request": request})

@app.get("/azure", response_class=HTMLResponse)
async def azure_page(request: Request):
    return templates.TemplateResponse("azure.html", {"request": request})

@app.get("/qr_azure", response_class=HTMLResponse)
async def azure_page(request: Request):
    return templates.TemplateResponse("qr_azure.html", {"request": request})