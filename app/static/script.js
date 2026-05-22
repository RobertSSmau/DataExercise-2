let grafico = null;

const COLORI = ['#2563eb', '#dc2626', '#16a34a', '#d97706', '#7c3aed'];

async function carica() {
    const endpoint = document.getElementById('serie').value;
    const da = document.getElementById('da_anno').value;
    const a = document.getElementById('a_anno').value;
    const errDiv = document.getElementById('errore');
    errDiv.textContent = '';

    let risposta;
    try {
        const r = await fetch(`${endpoint}?da_anno=${da}&a_anno=${a}`);
        if (!r.ok) {
            const err = await r.json();
            errDiv.textContent = err.detail || 'Errore nella richiesta.';
            return;
        }
        risposta = await r.json();
    } catch (e) {
        errDiv.textContent = 'Impossibile contattare il server.';
        return;
    }

    if (!risposta.length) {
        errDiv.textContent = 'Nessun dato per il periodo selezionato. Esegui prima la pipeline di import.';
        return;
    }

    const haArea = 'area' in risposta[0];

    let datasets;
    if (haArea) {
        const aree = [...new Set(risposta.map(r => r.area))].sort();
        datasets = aree.map((area, i) => ({
            label: area,
            data: risposta.filter(r => r.area === area).map(r => ({ x: r.anno, y: r.valore })),
            borderColor: COLORI[i % COLORI.length],
            backgroundColor: 'transparent',
            tension: 0.3
        }));
    } else {
        datasets = [{
            label: 'Nazionale',
            data: risposta.map(r => ({ x: r.anno, y: r.valore })),
            borderColor: COLORI[0],
            backgroundColor: 'transparent',
            tension: 0.3
        }];
    }

    if (grafico) grafico.destroy();
    grafico = new Chart(document.getElementById('grafico'), {
        type: 'line',
        data: { datasets },
        options: {
            parsing: false,
            scales: {
                x: { type: 'linear', title: { display: true, text: 'Anno' } },
                y: { title: { display: true, text: 'Valore' } }
            },
            plugins: { legend: { position: 'bottom' } }
        }
    });
}
