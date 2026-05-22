# Definizione delle 5 tabelle SQLAlchemy del database — settore pesca.
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Regione(Base):
    __tablename__ = "regioni"
    id = Column(Integer, primary_key=True)
    nome = Column(String, unique=True, nullable=False, index=True)
    area = Column(String, nullable=False, index=True)


class Produttivita(Base):
    __tablename__ = "produttivita_pesca"
    __table_args__ = (UniqueConstraint("regione_id", "anno", name="uq_prod_reg_anno"),)
    id = Column(Integer, primary_key=True)
    regione_id = Column(Integer, ForeignKey("regioni.id"), nullable=False, index=True)
    anno = Column(Integer, nullable=False, index=True)
    valore = Column(Float, nullable=False)
    interpolato = Column(Boolean, nullable=False, default=False)
    regione = relationship("Regione")


class Occupazione(Base):
    __tablename__ = "occupazione_pesca"
    __table_args__ = (UniqueConstraint("regione_id", "anno", name="uq_occ_reg_anno"),)
    id = Column(Integer, primary_key=True)
    regione_id = Column(Integer, ForeignKey("regioni.id"), nullable=False, index=True)
    anno = Column(Integer, nullable=False, index=True)
    valore = Column(Float, nullable=False)
    interpolato = Column(Boolean, nullable=False, default=False)
    regione = relationship("Regione")


class Importanza(Base):
    __tablename__ = "importanza_pesca"
    __table_args__ = (UniqueConstraint("regione_id", "anno", name="uq_imp_reg_anno"),)
    id = Column(Integer, primary_key=True)
    regione_id = Column(Integer, ForeignKey("regioni.id"), nullable=False, index=True)
    anno = Column(Integer, nullable=False, index=True)
    valore = Column(Float, nullable=False)
    interpolato = Column(Boolean, nullable=False, default=False)
    regione = relationship("Regione")


class SerieCalcolata(Base):
    __tablename__ = "serie_calcolate"
    __table_args__ = (UniqueConstraint("tipo_serie", "area", "anno", name="uq_serie"),)
    id = Column(Integer, primary_key=True)
    tipo_serie = Column(String, nullable=False, index=True)  # es. PROD_AREA, PROD_NAZ
    area = Column(String, nullable=True, index=True)  # None per serie nazionali
    anno = Column(Integer, nullable=False, index=True)
    valore = Column(Float, nullable=False)
