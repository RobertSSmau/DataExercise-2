# Percorsi del database e URL di download dei 3 dataset pubblici (pesca).
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Settings:
    db_url: str = f"sqlite:///{ROOT / 'data' / 'esame.db'}"
    data_dir: Path = ROOT / "data"

    url_produttivita: str = (
        "http://www.datiopen.it/export/csv/"
        "Produttivita-del-settore-della-pesca-per-regione.csv"
    )
    url_occupazione: str = (
        "http://www.datiopen.it/export/csv/"
        "Andamento-dell-occupazione-nel-settore-della-pesca-per-regione.csv"
    )
    url_importanza: str = (
        "http://www.datiopen.it/export/csv/"
        "Importanza-economica-del-settore-della-pesca-per-regione.csv"
    )


settings = Settings()
