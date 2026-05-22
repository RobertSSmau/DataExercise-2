# Scarica i 3 CSV da datiopen.it (o li legge da cache locale) e popola il database.
from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

from app.config import settings
from app.constants import ALIAS_TO_CANONICAL, REGIONE_AREA
from app.database import Base, SessionLocal, engine
from app.models import Importanza, Occupazione, Produttivita, Regione

DATASETS = {
    "produttivita.csv": (settings.url_produttivita, Produttivita),
    "occupazione.csv": (settings.url_occupazione, Occupazione),
    "importanza.csv": (settings.url_importanza, Importanza),
}

REGIONI_CANONICHE = [
    ("Valle d'Aosta", "Nord-ovest"),
    ("Piemonte", "Nord-ovest"),
    ("Liguria", "Nord-ovest"),
    ("Lombardia", "Nord-ovest"),
    ("Trentino-Alto Adige", "Nord-est"),
    ("Veneto", "Nord-est"),
    ("Friuli-Venezia Giulia", "Nord-est"),
    ("Emilia-Romagna", "Nord-est"),
    ("Toscana", "Centro"),
    ("Umbria", "Centro"),
    ("Marche", "Centro"),
    ("Lazio", "Centro"),
    ("Abruzzo", "Centro"),
    ("Molise", "Sud"),
    ("Campania", "Sud"),
    ("Puglia", "Sud"),
    ("Basilicata", "Sud"),
    ("Calabria", "Sud"),
    ("Sicilia", "Isole"),
    ("Sardegna", "Isole"),
]


def download_if_missing(filename: str, url: str) -> Path:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    dest = settings.data_dir / filename
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  cache HIT: {dest.name}")
        return dest
    print(f"  download: {url}")
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        content = resp.content
        # datiopen.it a volte restituisce una pagina HTML invece del CSV
        if content.lstrip()[:15].lower().startswith(b"<!doctype") or b"<html" in content[:200].lower():
            raise RuntimeError(
                f"L'URL ha restituito una pagina HTML invece di un CSV.\n"
                f"datiopen.it potrebbe aver cambiato gli URL di download.\n"
                f"Scarica manualmente il CSV dalla pagina del dataset e salvalo in data/{filename}"
            )
        dest.write_bytes(content)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"Download fallito per {filename}: {e}\n"
            f"Scarica manualmente il CSV e salvalo in data/{filename}"
        )
    return dest


def seed_regioni(db) -> dict[str, int]:
    if db.query(Regione).count() == 0:
        db.add_all([Regione(nome=n, area=a) for n, a in REGIONI_CANONICHE])
        db.commit()
    return {r.nome: r.id for r in db.query(Regione).all()}


def _nome_canonico(raw: str) -> str | None:
    s = str(raw).strip()
    s = ALIAS_TO_CANONICAL.get(s, s)
    if s in REGIONE_AREA:
        return s
    return None


def _detect_columns(df: pd.DataFrame) -> tuple[str, str, str]:
    # i CSV di datiopen.it non hanno nomi colonna uniformi, si cerca per keyword
    lower = {c.lower().strip(): c for c in df.columns}
    col_reg = next(
        (lower[k] for k in lower if "regione" in k or "territorio" in k or "region" in k),
        None,
    )
    col_anno = next(
        (lower[k] for k in lower if k in ("anno", "year", "time", "tempo") or "anno" in k),
        None,
    )
    col_val = next(
        (
            lower[k]
            for k in lower
            if k in ("valore", "value", "dato") or "valore" in k or "value" in k
        ),
        None,
    )
    if not (col_reg and col_anno and col_val):
        raise RuntimeError(
            f"Colonne non rilevate automaticamente. Disponibili: {list(df.columns)}\n"
            f"Trovate -> regione={col_reg}, anno={col_anno}, valore={col_val}"
        )
    return col_reg, col_anno, col_val


def import_csv(path: Path, ModelCls, regione_id_by_nome: dict[str, int], db) -> int:
    # prova sep=';' (formato datiopen.it), fallback su rilevamento automatico
    try:
        df = pd.read_csv(path, sep=";", encoding="utf-8")
        if len(df.columns) < 3:
            raise ValueError("troppo poche colonne con ';'")
    except Exception:
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8")

    col_reg, col_anno, col_val = _detect_columns(df)

    rows = []
    skipped = 0
    for _, r in df.iterrows():
        nome = _nome_canonico(r[col_reg])
        if not nome or nome not in regione_id_by_nome:
            skipped += 1
            continue
        try:
            anno = int(r[col_anno])
            valore = float(str(r[col_val]).replace(",", ".").strip())
        except (TypeError, ValueError):
            skipped += 1
            continue
        rows.append(
            ModelCls(
                regione_id=regione_id_by_nome[nome],
                anno=anno,
                valore=valore,
                interpolato=False,
            )
        )

    # cancella e reinserisci per garantire idempotenza (script rieseguibile)
    db.query(ModelCls).delete()
    db.add_all(rows)
    db.commit()
    if skipped:
        print(f"   (righe scartate: {skipped})")
    return len(rows)


def run_import() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        print("Popolamento tabella regioni...")
        regione_id_by_nome = seed_regioni(db)
        for filename, (url, ModelCls) in DATASETS.items():
            print(f"-> {filename}")
            path = download_if_missing(filename, url)
            n = import_csv(path, ModelCls, regione_id_by_nome, db)
            print(f"   inserite {n} righe in {ModelCls.__tablename__}")
