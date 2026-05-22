# Documento tecnico — FSD Esame 2023

Candidato: {COGNOME} {NOME}, reg. {NUMERO_REGISTRO}

---

## Il problema

La prova richiede di costruire una pipeline dati che scarica tre dataset pubblici dal portale datiopen.it riguardanti il settore della pesca in Italia, li carica su un database, colma i buchi temporali tramite interpolazione lineare, calcola cinque serie statistiche aggregate per area geografica e le espone tramite un'API HTTP. Come punto facoltativo è richiesta anche una pagina web che presenta i dati.

---

## Linguaggio e tecnologie scelte

Ho scelto Python perché è il linguaggio più adatto tra quelli affrontati nel corso per questo tipo di lavoro: gestire file CSV, interrogare un database relazionale e costruire un'API web richiede librerie che in Python sono mature e ben documentate.

Per la parte web ho usato FastAPI insieme a Uvicorn. FastAPI genera automaticamente la documentazione Swagger su /docs, comoda sia per testare l'API durante lo sviluppo sia per mostrarla al valutatore senza dover configurare Postman. Gestisce anche la validazione dei parametri di input tramite Pydantic, quindi non ho dovuto scrivere controlli manuali per ogni campo.

Come database ho scelto SQLite perché è un file singolo che non richiede l'installazione di un server, nessuna configurazione, nessuna credenziale. Per i volumi in gioco, venti regioni per una ventina di anni su tre dataset, è più che sufficiente. Ho usato SQLAlchemy come ORM per separare la logica applicativa dal database: se si volesse passare a MySQL o PostgreSQL basterebbe cambiare la stringa di connessione in config.py senza toccare il resto del codice.

Per leggere i CSV ho usato pandas perché gestisce automaticamente l'encoding e permette di provare più separatori senza scrivere codice di parsing manuale.

---

## Struttura del database

Ho creato cinque tabelle. La tabella regioni contiene i nomi canonici delle venti regioni italiane con la rispettiva macro-area geografica e serve da riferimento per le altre tabelle. Le tabelle produttivita_pesca, occupazione_pesca e importanza_pesca contengono i dati grezzi importati dai tre dataset, ognuna con le colonne regione_id, anno, valore e un booleano interpolato che indica se il record è stato aggiunto dalla fase di normalizzazione o era presente nel CSV originale. Questa colonna permette al consumatore dell'API di sapere quali dati sono osservati e quali stimati.

Le cinque serie calcolate condividono un'unica tabella serie_calcolate, distinta dal campo tipo_serie che può valere PROD_AREA, PROD_NAZ, IMP_AREA, OCC_NAZ o OCC_AREA. Le serie nazionali hanno il campo area vuoto, quelle per area lo hanno popolato. Ho preferito una tabella sola a cinque tabelle separate perché la struttura del dato è identica e le query di lettura rimangono semplici.

Su ogni coppia (regione_id, anno) nelle tabelle grezze ho messo un vincolo di unicità a livello di database. Se il CSV contiene duplicati o se la pipeline viene rieseguita, il database garantisce che non vengano inseriti valori contraddittori.

---

## Aggregazione geografica

Le regioni vengono assegnate alle macro-aree secondo la tabella della commessa: Nord-ovest comprende Valle d'Aosta, Piemonte, Liguria e Lombardia; Nord-est comprende Trentino-Alto Adige, Veneto, Friuli-Venezia Giulia ed Emilia-Romagna; Centro comprende Toscana, Umbria, Marche, Lazio e Abruzzo; Sud comprende Molise, Campania, Puglia, Basilicata e Calabria; Isole comprende Sicilia e Sardegna.

Un problema che ho incontrato è che i tre dataset di datiopen.it usano nomi regionali non uniformi tra loro. Ad esempio il Trentino può apparire come "Trentino-Alto Adige", "Trentino Alto Adige" senza trattino, o "Trentino-Alto Adige/Südtirol". Ho costruito una tabella di alias che traduce questi nomi alternativi al nome canonico usato nel database prima di salvare qualsiasi riga.

---

## Normalizzazione dei dati mancanti

Per ogni dataset, per ogni regione, costruisco un dizionario che associa ogni anno al valore osservato. Poi scorro le coppie di anni noti consecutivi: se tra due anni c'è un gap, calcolo il passo come differenza tra i due valori divisa per l'ampiezza del gap e inserisco gli anni intermedi sommando il passo progressivamente. Gli estremi del range non vengono mai estrapolati: se il primo dato di una regione è del 2001 e l'ultimo del 2018, non genero nulla prima del 2001 né dopo il 2018.

L'esempio della commessa è quello con il dato del 2001 e del 2004: il passo è (val_2004 - val_2001) diviso 3, il 2002 vale val_2001 più un passo, il 2003 vale val_2001 più due passi.

---

## Calcolo delle cinque serie

Per le cinque serie ho usato due metodi di aggregazione diversi, a seconda della natura del dato.

La produttività è espressa in migliaia di euro, quindi è un valore assoluto. La produttività totale di un'area è la somma di quelle delle regioni che la compongono, non la media: se la Lombardia produce 1000 e la Liguria 100, l'area Nord-ovest produce 1100, non 550. Ho quindi usato la somma per le serie PROD_AREA e PROD_NAZ.

L'importanza economica e la variazione dell'occupazione sono invece percentuali. Come indicato nella nota metodologica della commessa, non avendo le quantità di riferimento per le percentuali si usa il calcolo in modo non proporzionato, cioè la media aritmetica semplice. Questo significa che ogni regione pesa uguale indipendentemente dalla sua dimensione. Ho usato la media per le serie IMP_AREA, OCC_NAZ e OCC_AREA.

---

## API REST

Tutti gli endpoint accettano da_anno e a_anno come parametri obbligatori nella query string. Se a_anno è minore di da_anno, l'API risponde con HTTP 400 e un messaggio di errore. Tre endpoint restituiscono i dati grezzi delle tre tabelle di import, cinque endpoint restituiscono le serie calcolate. La documentazione interattiva è disponibile su /docs generata automaticamente da FastAPI.

---

## Interfaccia web

Come punto facoltativo della commessa ho realizzato una pagina HTML raggiungibile all'indirizzo radice del server. La pagina mostra un grafico a linee interattivo alimentato dalla libreria Chart.js, caricata dal CDN senza dipendenze aggiuntive da installare. L'utente sceglie una delle cinque serie calcolate tramite un menu a tendina, inserisce l'anno di inizio e quello di fine in due campi numerici e preme il pulsante per aggiornare il grafico. La pagina effettua una chiamata fetch all'endpoint corrispondente passando i due anni come parametri, riceve la risposta JSON e costruisce il grafico. Per le serie per area il grafico disegna una linea distinta per ciascuna macro-area, ognuna con il proprio colore; per le serie nazionali disegna una sola linea. Gli errori restituiti dall'API, come il range invertito, vengono mostrati in rosso sopra il grafico. Se il database è ancora vuoto perché la pipeline non è stata eseguita, la pagina lo segnala con un messaggio esplicativo. La comunicazione tra la pagina e il backend avviene interamente tramite l'API, come richiesto dalla commessa.

---

## Scelte non ovvie e assunzioni

Lo script di import è stato scritto in modo che sia rieseguibile senza effetti collaterali: ogni esecuzione cancella i dati precedenti e li reinserisce da capo. Questo evita duplicati e permette di rieseguire la pipeline se i dataset vengono aggiornati.

I dataset di datiopen.it usano il punto e virgola come separatore. Il codice prova prima con il punto e virgola, e se il risultato ha meno di tre colonne riprova con il rilevamento automatico del separatore tramite pandas.

Le colonne del CSV non vengono cercate per nome fisso ma per parola chiave: la colonna della regione è quella il cui nome contiene "regione" o "territorio", quella dell'anno contiene "anno" o "year", quella del valore contiene "valore" o "value". Questo rende il codice più robusto rispetto a piccole variazioni nei nomi delle colonne tra un dataset e l'altro.

Le righe con nomi di regione non riconoscibili vengono scartate silenziosamente durante l'import. Questo riguarda tipicamente righe aggregate come "Italia" o "Nord" che in alcuni CSV compaiono insieme ai dati regionali ma non corrispondono a nessuna delle venti regioni previste. Le righe con valori non convertibili a numero vengono anch'esse scartate.

Durante il download si controlla che la risposta del server sia effettivamente un CSV e non una pagina HTML: datiopen.it a volte risponde con una pagina di errore invece del file richiesto. Se questo accade, il codice segnala il problema con le istruzioni per il download manuale del file da salvare nella cartella data/.

---

## Limiti noti

La media delle percentuali non è ponderata per popolazione o PIL: in un contesto reale si userebbe un peso demografico per regione per ottenere valori più rappresentativi. L'estrapolazione fuori dal range osservato non è implementata per non generare dati privi di basi empiriche. Non è presente nessun meccanismo di autenticazione perché non era richiesto dalla commessa.