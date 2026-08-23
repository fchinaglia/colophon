#!/usr/bin/env python3
"""Costruisce la versione illustrata dell'articolo a partire da v04.

Non modifica v04 (l'artefatto misurato): inserisce solo blocchi <figure>
dopo ancore testuali esatte. Se un'ancora non si trova, si ferma.
"""
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "../caso001/versioni/v04_articolo_finale.md"
OUT = "articolo_frammentazione_dati_illustrato.md"

FIGURE = [
    ("è una scelta che rischia di isolare il CTO che la propone.",
     "01_valle_disperazione.png",
     "La valle della disperazione. L'ostacolo non è il ritorno dell'investimento, "
     "è il tratto in cui l'azienda sta peggio di prima."),
    ("È la stessa tecnologia. Cambia se la compri come investimento o la affitti come servizio.",
     "03_costruzione_esecuzione.png",
     "Lo stesso modello, due collocazioni diverse: dentro ogni transazione, oppure "
     "a monte a produrre artefatti deterministici."),
    ("è l'insieme delle regole su quale sia la fonte certa di ogni informazione, "
     "come ci si accede, e chi decide quando cambia.",
     "02_architettura.png",
     "Da integrazioni punto a punto a uno strato di accesso comune, governato da "
     "un modello semantico di riferimento."),
    ("Cresce senza segnale e poi si tramuta di colpo in un problema o in una catastrofe.",
     "04_tco_rischio.png",
     "Il costo è misurato e rassicurante; il rischio cresce lo stesso, non osservato. "
     "L'incidente non lo aumenta: lo rende visibile. Il piano di remediation lo abbatte, "
     "ma non tocca il meccanismo che lo genera."),
]


def fig(f, cap):
    return (f'\n\n<figure>\n<img src="immagini/{f}">\n'
            f'<figcaption>{cap}</figcaption>\n</figure>\n')


t = open(SRC, encoding="utf-8").read()
for ancora, f, cap in FIGURE:
    if t.count(ancora) != 1:
        sys.exit(f"ancora non univoca ({t.count(ancora)}x): «{ancora[:50]}…»")
    t = t.replace(ancora, ancora + fig(f, cap))
open(OUT, "w", encoding="utf-8").write(t)
print(f"{OUT} — figure inserite: {len(FIGURE)}")
