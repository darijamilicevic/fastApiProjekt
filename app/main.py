from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "lozinka")
DB_NAME = os.environ.get("DB_NAME", "todo_baza")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


app = FastAPI()


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




@app.post("/zadaci", response_model=ZadatakPrikaz)
def dodaj_zadatak(zadatak: ZadatakUnos, db=Depends(dobavi_bazu)):
    novi_zadatak = Zadatak(naslov=zadatak.naslov)
    db.add(novi_zadatak)
    db.commit()
    db.refresh(novi_zadatak)
    return novi_zadatak


@app.get("/zadaci", response_model=list[ZadatakPrikaz])
def svi_zadaci(db=Depends(dobavi_bazu)):
    zadaci = db.query(Zadatak).all()
    return zadaci


@app.put("/zadaci/{zadatak_id}", response_model=ZadatakPrikaz)
def azuriraj_zadatak(zadatak_id: int, podaci: ZadatakUnos, db=Depends(dobavi_bazu)):
    zadatak = db.query(Zadatak).filter(Zadatak.id == zadatak_id).first()
    if not zadatak:
        raise HTTPException(status_code=404, detail="Zadatak nije pronađen")
    zadatak.naslov = podaci.naslov
    db.commit()
    db.refresh(zadatak)
    return zadatak


@app.delete("/zadaci/{zadatak_id}")
def izbrisi_zadatak(zadatak_id: int, db=Depends(dobavi_bazu)):
    zadatak = db.query(Zadatak).filter(Zadatak.id == zadatak_id).first()
    if not zadatak:
        raise HTTPException(status_code=404, detail="Zadatak nije pronađen")
    db.delete(zadatak)
    db.commit()
    return {"poruka": "Zadatak uspješno obrisan"}
