# Punto di ingresso FastAPI: registra i router e serve la pagina statica.
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import importanza, occupazione, produttivita, serie

Base.metadata.create_all(engine)  # crea le tabelle se non esistono ancora

app = FastAPI(
    title="FSD Esame 2023 — Settore Pesca Italia",
    description=(
        "API REST per dati regionali italiani sul settore della pesca: "
        "produttività, occupazione e importanza economica, "
        "con 5 serie statistiche aggregate per macro-area geografica."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produttivita.router)
app.include_router(occupazione.router)
app.include_router(importanza.router)
app.include_router(serie.router)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(str(STATIC_DIR / "index.html"))
