# Come verificare questo registro

Il file `events.jsonl` contiene il registro degli interventi fatti mentre scrivevo
*Come rendere trasparente il tuo uso dell'AI quando scrivi un contenuto*.
Ogni riga è un evento, e ogni evento contiene l'impronta di quello precedente: la sequenza
è una catena, e **alterare un evento passato invalida tutti gli hash successivi**.

Accanto al registro trovate i file che permettono di verificarlo senza credermi sulla parola.

## 1. La catena non è stata alterata

```bash
python3 record.py --verify
```

Ricalcola l'intera catena e segnala il primo anello rotto. Deve rispondere `chain intact`,
con la radice corrente.

## 2. Il registro è mio

La firma è Ed25519, staccata, nel file `events.jsonl.sig`. La mia chiave pubblica è
pubblicata qui: **https://github.com/fchinaglia/colophon/blob/main/cases/001/colophon.pub**
In forma scaricabile: `https://raw.githubusercontent.com/fchinaglia/colophon/main/cases/001/colophon.pub`

```bash
echo 'f.chinaglia@gmail.com namespaces="colophon" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFBuJGGXqAqAZ0PqK6Fd5743SwJIJhrYd/S2S5tHZUg1 colophon' > allowed_signers
ssh-keygen -Y verify -f allowed_signers -I f.chinaglia@gmail.com \
           -n colophon -s events.jsonl.sig < events.jsonl
```

Deve rispondere `Good "colophon" signature`.

## 3. Il registro esisteva già a quella data

Due marche temporali indipendenti, per non dipendere da un solo garante.

**RFC 3161** — `events.jsonl.tsr`:

```bash
openssl ts -reply -in events.jsonl.tsr -text | grep "Time stamp"
```

**OpenTimestamps** — `events.jsonl.ots`, ancorato alla blockchain Bitcoin:

```bash
pip install opentimestamps-client
ots verify events.jsonl.ots
```

Questa non richiede di fidarsi di nessuna autorità.

## 4. Il testo corrisponde all'annotazione

```bash
python3 measure.py
```

Deve dire `reconstruction: OK`: gli span annotati, concatenati, riproducono esattamente il
testo pubblicato. Nessun intervento è attribuito a un testo che non esiste, e nessun testo
è rimasto senza attribuzione.

Il controllo di copertura segnala alcuni orfani, ed è atteso: sono le cancellazioni, che per
definizione non hanno uno span nel testo finale, le correzioni ai blocchi esclusi dal
conteggio, e i blocchi toccati da più di una correzione, perché il formato accetta un solo
riferimento a evento per span. Ogni orfano è spiegato in un evento `register_note`.

## 5. Gli artefatti sono quelli firmati

L'ultimo evento del registro contiene il digest SHA-256 di ogni file del caso: il testo
finale, l'annotazione, la misurazione, l'icona, la pagina di verifica e il PDF. Ricalcolateli
e confrontateli.

```bash
shasum -a 256 versions/v21_final.txt annotation.json kpi.json spans.json icon.svg
```

Il PDF pubblicato riporta la radice della catena **al momento in cui è stato prodotto**, che
è l'evento immediatamente precedente al manifest. È l'ordine corretto: prima il documento,
poi il registro che lo impronta, poi la firma che chiude tutto.

---

## Cosa tutto questo dimostra, e cosa no

**Dimostra** che il registro esisteva in quella forma a quella data, che non è stato alterato
da allora, e che è stato prodotto da chi possiede quella chiave.

**Non dimostra che il registro sia completo.** Nessun sistema volontario può dimostrarlo:
posso registrare tutto fedelmente oppure omettere, e la crittografia non distingue i due casi.
Il registro è inoltre compilato dal modello linguistico su sé stesso.

Lo dico per primo perché è la critica più solida che si possa fare a una dichiarazione
volontaria, ed è giusta: **il valore di questo registro non sta nella prova, sta nella
responsabilità che mi assumo pubblicandolo e nel fatto che sia ispezionabile.**

Un'ultima cosa, dichiarata e non nascosta: durante la lavorazione il modello ha distrutto
un file di versione con una scrittura sbagliata, e il controllo di ricostruzione è passato
lo stesso perché confrontava due testi entrambi vuoti. A trovarlo è stato il controllo di
copertura. L'incidente è nel registro, con la diagnosi e il recupero.

Se trovate un'incoerenza, scrivetemi: **f.chinaglia@gmail.com**

---

*MIT License — Copyright (c) 2026 Fabio Chinaglia.*
