from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Postavke baze podataka
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "lozinka")
DB_NAME = os.environ.get("DB_NAME", "todo_baza")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="frontend")


class Zadatak(Base):
    __tablename__ = "zadaci"
    id = Column(Integer, primary_key=True, index=True)
    naslov = Column(String(100), nullable=False)
    obavljeno = Column(Boolean, default=False)


class ZadatakUnos(BaseModel):
    naslov: str

class ZadatakPrikaz(BaseModel):
    id: int
    naslov: str
    obavljeno: bool

    class Config:
        orm_mode = True


@app.on_event("startup")
def inicijaliziraj_bazu():
    Base.metadata.create_all(bind=engine)


def dobavi_bazu():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def prikazi_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/zadaci", response_model=ZadatakPrikaz)
def dodaj_zadatak(zadatak: ZadatakUnos, db=Depends(dobavi_bazu)):
    novi_zadatak = Zadatak(naslov=zadatak.naslov)
    db.add(novi_zadatak)
    db.commit()
    db.refresh(novi_zadatak)
    return novi_zadatak


@app.get("/api/zadaci", response_model=list[ZadatakPrikaz])
def svi_zadaci(db=Depends(dobavi_bazu)):
    zadaci = db.query(Zadatak).all()
    return zadaci


@app.put("/api/zadaci/{zadatak_id}", response_model=ZadatakPrikaz)
def azuriraj_zadatak(zadatak_id: int, zadatak: ZadatakUnos, db=Depends(dobavi_bazu)):
    db_zadatak = db.query(Zadatak).filter(Zadatak.id == zadatak_id).first()
    if not db_zadatak:
        raise HTTPException(status_code=404, detail="Zadatak nije pronađen")
    db_zadatak.naslov = zadatak.naslov
    db.commit()
    db.refresh(db_zadatak)
    return db_zadatak

#crfrfrfr


@app.delete("/api/zadaci/{zadatak_id}")
def izbrisi_zadatak(zadatak_id: int, db=Depends(dobavi_bazu)):
    db_zadatak = db.query(Zadatak).filter(Zadatak.id == zadatak_id).first()
    if not db_zadatak:
        raise HTTPException(status_code=404, detail="Zadatak nije pronađen")
    db.delete(db_zadatak)
    db.commit()
    return {"poruka": "Zadatak uspješno obrisan"}