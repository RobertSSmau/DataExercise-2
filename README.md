## Settore pesca Italia

Applicazione per la raccolta e analisi dei dati sul settore della pesca in Italia.
Scarica 3 dataset pubblici da datiopen.it, normalizza i dati mancanti con interpolazione lineare e calcola 5 serie statistiche aggregate per area geografica. Tutto viene esposto tramite API REST.

## Come si avvia

Prima di tutto crea e attiva un ambiente virtuale:

```
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Poi esegui i 3 passaggi di pipeline nell'ordine, ognuno dipende dal precedente:

```
python -c "from app.services.importer import run_import; run_import()"
python -c "from app.services.normalizer import run_normalize; run_normalize()"
python -c "from app.services.calculator import run_calculate; run_calculate()"
```

Infine avvia il server:

```
python run.py
```

L'API è disponibile su http://127.0.0.1:8000 e la documentazione Swagger su http://127.0.0.1:8000/docs.

## Note

Il database è un file SQLite in data/esame.db, non serve configurare niente. Se il download automatico da datiopen.it non funziona, scarica manualmente i CSV e salvali in data/ come produttivita.csv, occupazione.csv e importanza.csv.