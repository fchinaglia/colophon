# Come verificare questo registro

Il file `eventi.jsonl` contiene il registro degli interventi durante la scrittura di
**«Frammentazione dei dati: usare l'AI per affittare il debito tecnologico o estinguerlo»**,
tracciato con il metodo [Colophon](https://github.com/fchinaglia/colophon).

Ogni riga è un evento; ogni evento contiene l'impronta del precedente, quindi la sequenza
è una catena: **modificare un evento passato invalida tutti gli hash successivi**.

Accanto al registro trovate i file che permettono di verificarlo senza fidarvi di me.

## 1. La catena non è stata alterata

```bash
python3 registra.py --verifica
```

Ricalcola l'intera catena e segnala il primo anello rotto. Deve rispondere
`catena integra`, con la radice corrente.

## 2. Il registro è mio

La firma è Ed25519, staccata, nel file `eventi.jsonl.sig`. La mia chiave pubblica è
pubblicata qui: https://raw.githubusercontent.com/fchinaglia/colophon/main/cases/001/colophon.pub

```bash
echo 'f.chinaglia@gmail.com namespaces="colophon" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFBuJGGXqAqAZ0PqK6Fd5743SwJIJhrYd/S2S5tHZUg1 colophon' > allowed_signers
ssh-keygen -Y verify -f allowed_signers -I f.chinaglia@gmail.com \
           -n colophon -s eventi.jsonl.sig < eventi.jsonl
```

Deve rispondere `Good "colophon" signature`.

## 3. Il registro esisteva già a quella data

Due marche indipendenti, per non dipendere da un solo garante.

**RFC 3161** — `eventi.jsonl.tsr`:

```bash
openssl ts -reply -in eventi.jsonl.tsr -text | grep "Time stamp"
```

**OpenTimestamps** — `eventi.jsonl.ots`, ancorato alla blockchain di Bitcoin:

```bash
pip install opentimestamps-client
ots verify eventi.jsonl.ots
```

Non richiede di fidarsi di nessuna autorità.

## 4. Il testo corrisponde all'annotazione

```bash
python3 misura.py
```

Deve dire `ricostruzione: OK`. Significa che gli span annotati, concatenati, riproducono
esattamente il testo pubblicato: nessun passaggio è stato attribuito a un pezzo di testo
che non esiste, e nessun pezzo di testo è rimasto senza attribuzione.

Il secondo controllo, la **copertura**, verifica che ogni modifica dichiarata nel registro
compaia in almeno uno span. Le modifiche elencate come orfane sono quelle sostituite da un
intervento successivo o diffuse su più span, e sono attese.

---

## Cosa tutto questo dimostra, e cosa no

**Dimostra** che il registro esisteva in quella forma a quella data, che non è stato
alterato da allora, e che è stato prodotto da chi detiene quella chiave.

**Non dimostra** che il registro sia **completo**. Nessun sistema volontario può
dimostrarlo: posso registrare fedelmente tutto, oppure omettere, e la crittografia non
distingue i due casi. Il registro è inoltre compilato dal modello linguistico su sé stesso.

Lo dico per primo perché è la critica più solida che si può muovere a una dichiarazione
volontaria, ed è giusta: **il valore di questo registro non sta nella prova, sta nella
responsabilità che mi assumo pubblicandolo e nel fatto che sia ispezionabile.**

Un'ultima avvertenza specifica di questo caso: le percentuali si riferiscono al **testo
italiano**, l'unico su cui la misura è stata presa. La versione inglese è una traduzione
prodotta dal modello, e sull'asse lessicale non è descritta da quei numeri.

Se trovate un'incoerenza, scrivetemi: f.chinaglia@gmail.com

---

*Licenza MIT — Copyright (c) 2026 Fabio Chinaglia.*
