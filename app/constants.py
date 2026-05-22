# Associa ogni regione alla sua area geografica, con gli alias per i nomi alternativi nei CSV.

REGIONE_AREA: dict[str, str] = {
    "Valle d'Aosta": "Nord-ovest",
    "Valle d'Aosta/Vallée d'Aoste": "Nord-ovest",
    "Piemonte": "Nord-ovest",
    "Liguria": "Nord-ovest",
    "Lombardia": "Nord-ovest",
    "Trentino-Alto Adige": "Nord-est",
    "Trentino Alto Adige": "Nord-est",
    "Trentino-Alto Adige/Südtirol": "Nord-est",
    "Veneto": "Nord-est",
    "Friuli-Venezia Giulia": "Nord-est",
    "Friuli Venezia Giulia": "Nord-est",
    "Emilia-Romagna": "Nord-est",
    "Emilia Romagna": "Nord-est",
    "Toscana": "Centro",
    "Umbria": "Centro",
    "Marche": "Centro",
    "Lazio": "Centro",
    "Abruzzo": "Centro",
    "Molise": "Sud",
    "Campania": "Sud",
    "Puglia": "Sud",
    "Basilicata": "Sud",
    "Calabria": "Sud",
    "Sicilia": "Isole",
    "Sardegna": "Isole",
}

AREE = ("Nord-ovest", "Nord-est", "Centro", "Sud", "Isole")

# I dataset usano nomi non standard; qui li normalizziamo al nome canonico del DB.
ALIAS_TO_CANONICAL: dict[str, str] = {
    "Valle d'Aosta/Vallée d'Aoste": "Valle d'Aosta",
    "Trentino Alto Adige": "Trentino-Alto Adige",
    "Trentino-Alto Adige/Südtirol": "Trentino-Alto Adige",
    "Friuli Venezia Giulia": "Friuli-Venezia Giulia",
    "Emilia Romagna": "Emilia-Romagna",
}
