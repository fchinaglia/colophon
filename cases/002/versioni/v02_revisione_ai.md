# v02 — revisione con modifiche marcate

**Convenzioni di lettura**

- `⟦M07⟧ … ⟦/M07⟧` — testo proposto in aggiunta o in sostituzione. Il testo **non marcato è tuo, intatto**.
- `⟦−M12: … ⟧` — testo di cui propongo l'eliminazione.
- `⟦↔M01⟧` — spostamento: il blocco è stato trasferito da un'altra posizione, senza riscrittura sostanziale.
- Le correzioni puramente formali (refusi, accordi, uniformità) sono applicate **senza marcatura** ed elencate in fondo.

Ogni modifica ha un numero: rispondi `M03 sì, M05 no, M07 riformula` e produco la v03.

---

⟦M11⟧
# La frammentazione dei dati: affittare il debito o estinguerlo
⟦/M11⟧

Ecco due situazioni tipiche.

Un'azienda di servizi B2C in fase di scale up attiva in maniera veloce una serie di sistemi e software per automatizzare il ciclo attivo — lead generation, contatto, vendita, pagamento, erogazione del servizio — con una integrazione lasca tra di essi. Al crescere del business i sistemi vengono fatti evolvere in maniera rapida, creando dei silos applicativi, ognuno con i propri dati, e la correlazione tra i dati dei vari silos non è più univoca o garantita, rendendo difficoltosa la governance end-to-end di processo (il pagamento ricevuto via bonifico a quale cliente e a quale lead si riferisce?) e le attività strategiche di evoluzione del business (quella campagna quanto ha generato in termini di incassato?). In questo caso la frammentazione dei dati introduce una inefficienza e può penalizzare la scalabilità dell'azienda.

Un'azienda di servizi consolidata, che eroga importanti volumi di transazioni mission critical B2B verso large account, con livelli di servizio al top del mercato e una infrastruttura importante e strutturata, non è in grado di ricostruire in maniera adeguata — in caso di problemi operativi, di privacy e di sicurezza — l'impatto degli stessi: in termini di attori coinvolti (quanti clienti, quanto personale interno e di partner, e in quale ruolo), di dati (quali dati, in che forma, quali trattamenti) e di processi. Questo perché il numero dei sistemi coinvolti, la loro stratificazione e sovrapposizione ha creato silos di dati, barriere, duplicazioni funzionali, spesso non documentate. Estrarre un elenco di clienti impattati, una mappa degli attori aziendali coinvolti, fare un'analisi analitica dei dati e valutare l'impatto di un problema diventa di per sé un progetto da centinaia di giorni uomo, con risultati, costi e tempi incerti. In questo secondo caso la frammentazione dei dati produce un "passato non dimostrabile": paradossalmente il rischio si accumula all'indietro, e cresce con i volumi. Con l'aumentare delle esigenze di compliance che dai clienti si ripropagano su tutta la catena di fornitura, avere questo tipo di situazioni è una vera e propria bomba a orologeria pronta a esplodere.

⟦↔M01⟧ ⟦M01⟧Sono due facce dello stesso problema, e vale la pena nominarlo. Il "debito tecnologico" — tutte quelle situazioni per cui la propria piattaforma tecnologica è indietro rispetto allo stato dell'arte — è uno dei temi quotidiani di un CTO e di un CIO, e ha nella frammentazione e nella qualità del dato una delle sue componenti più costose. Quello che cambia, tra i due casi, è la valuta in cui lo si paga: nel primo efficienza, nel secondo rischio.⟦/M01⟧

## Il canone invisibile: cosa costa già oggi, e perché ora si vede

La frammentazione dei dati è un costo, spesso invisibile. Aziende in situazioni simili a quelle sopra descritte pagano sicuramente un costo importante per gestire le inefficienze che ne derivano: personale e consulenti dedicati ad attività di riconciliazione manuale, o alla scrittura di procedure software di "integrazione" tra sistemi.

⟦M02⟧È una voce che non compare in nessun cruscotto, perché non è concentrata da nessuna parte: è un po' di tempo di molte persone, in molte funzioni diverse. La mia impressione è che in una struttura ICT corporate valga una quota degli opex a due cifre. Ma è esattamente il punto: nessuno lo sa con precisione, perché nessuno lo misura.⟦/M02⟧

Quando questi costi emergono e diventano visibili? Un caso tipico, in passato, era la migrazione a un nuovo sistema. Attivare un nuovo CRM o un ERP è emblematico, perché costringe a fare ordine nei dati: ⟦M03⟧spesso la parte più costosa e più lunga del progetto non è il software nuovo, è la bonifica di quello vecchio.⟦/M03⟧ Una grande, immensa bonifica.

Un caso "nuovo" è dato dall'uso dell'AI non per risolvere alla fonte la frammentazione dei dati, ma per renderla tollerabile. Al posto di riconciliare a mano, al posto di migrare verso sistemi che coprono end-to-end tutti i processi, si costruiscono una serie di procedure "intelligenti" che riconciliano i dati. In apparenza sembra l'uovo di Colombo: l'AI è in grado di gestire anche situazioni nuove e non pienamente definite, sembra fatta apposta per interpretare i disallineamenti tra sistemi.

Ed è vero, è una soluzione efficace. Ma con due problemi. Primo, ha un costo in token che può diventare importante — e che, se non altro, diventa visibile: il problema è risolto in apparenza, ma nella realtà rimane e genera un costo ricorrente. Secondo, è una soluzione non deterministica, nel senso che può sbagliare, e in alcuni contesti l'approssimazione aumenta il rischio invece di ridurlo.

## Perché nessuno lo risolve: la valle, e la conversazione che si vince solo dopo il danno

Penso che qualsiasi CTO sappia qual è il percorso per arrivare ad avere un modello dati integrato e consistente, con una implementazione performante, resiliente, sicura e scalabile.

Ma come si fa a sostenere questo tipo di progetto di fronte a un CEO, a uno steering committee o a un CDA? I benefici in termini di riduzione del costo e del rischio possono essere importanti, ma in generale si parte da una situazione iniziale in cui il costo operativo è nascosto e l'azienda comunque funziona. Il tema è poi squisitamente tecnico, e impegnare l'azienda per avere un risultato nel medio periodo, passando comunque attraverso la "valle della disperazione" tipica di ogni progetto, è una scelta che rischia di isolare il CTO che la propone.

L'unica situazione in cui tutti gli stakeholder alzano il proprio livello di commitment, paradossalmente, è a fronte di un problema. Se il rischio accumulato a un certo punto "esplode" in un incident, il piano di remediation può diventare il modo per risolvere il debito tecnologico che lo ha causato. ⟦M08⟧Il che significa che il momento in cui il progetto diventa approvabile è esattamente quello in cui ha smesso di essere un investimento ed è diventato una riparazione.⟦/M08⟧

## Cosa si rompe davvero: il debito semantico, la suite come soluzione impacchettata

⟦M05⟧Vale la pena essere precisi su cosa si rompe, perché non è quello che sembra. La difficoltà non è tecnica: formati, protocolli e connettori li risolviamo da vent'anni. La difficoltà è semantica. "Cliente", nel CRM, è un'opportunità che si è chiusa; in fatturazione è un soggetto giuridico con una partita IVA; in assistenza è chi apre il ticket. Sono tre entità con tre cicli di vita diversi, che a volte coincidono e a volte no. Il lead e il cliente nascono con chiavi diverse in sistemi diversi, e il legame tra quelle chiavi è spesso l'unica cosa che nessuno ha progettato, perché al momento sembrava ovvia. Quando quel legame si perde — ed è esattamente ciò che succede nel primo dei due casi — non hai perso un dato: hai perso la possibilità di ricostruire una storia. I progetti di integrazione non falliscono sull'ETL. Falliscono in riunione, quando bisogna decidere quale delle tre definizioni di "cliente" vince.⟦/M05⟧

Il problema della frammentazione dei dati si risolve strutturalmente ricostruendo le correlazioni tra silos applicativi. Se ci pensate, è quello che succede quando un'azienda acquista un CRM o un ERP: alla fine non stai comprando un software, stai comprando un modello dati. È una soluzione impacchettata — per avere il modello devi prendere anche la piattaforma, la migrazione e il lock-in. ⟦M06⟧Ed è una scelta che si giustifica solo se ci sono driver più forti: efficienza operativa, governance dei processi, copertura funzionale. La soluzione della frammentazione arriva come effetto collaterale, non è mai il motivo per cui si firma.⟦/M06⟧

Tuttavia l'AI spacchetta il pacchetto: oggi è possibile ricostruire il modello condiviso senza adottare piattaforme trasversali.

## Cosa cambia adesso: l'AI accorcia la valle della disperazione

⟦M04⟧Prima di entrare nel merito, una distinzione che tiene insieme tutto il ragionamento: **l'AI nel percorso di costruzione, non nel percorso di esecuzione.**

Usare un modello per riconciliare i dati a ogni transazione significa metterlo nel percorso di esecuzione: il costo è un canone che cresce con i volumi, l'errore accade in produzione su un dato vero, e l'output è la risposta stessa. Usarlo per progettare il modello, bonificare lo storico e scrivere le procedure di accesso significa metterlo nel percorso di costruzione: il costo è una tantum, l'errore si scopre in revisione, e l'output è deterministico — codice, schemi, migrazioni.

È la stessa tecnologia. Cambia se la compri come investimento o la affitti come servizio.⟦/M04⟧

Al posto di usare l'AI per costruire procedure di integrazione "intelligenti" tra sistemi, è possibile implementare una strategia diversa.

**1) Disegnare un modello dati di riferimento**, ovvero un'architettura di accesso e memorizzazione del dato.

Può essere, nei casi più semplici, un unico database aziendale, opportunamente ridondato e con tutte le misure di sicurezza del caso. Nel caso più generale è un insieme di componenti (database, storage, servizi di accesso, middleware di comunicazione) che garantiscono correttezza, unicità e sicurezza del dato, e lo rendono accessibile dove serve con prestazioni adeguate. La cosa importante è avere una governance unica e un processo chiaro, robusto e veloce per farlo evolvere alla velocità del business. Le stesse applicazioni aziendali sono parte di questo modello: se la fonte certa di un dato — per esempio l'anagrafica clienti — è il CRM aziendale, il modello dati garantirà che ogni copia di quel dato in altri sistemi sia slave della fonte di verità aziendale.

⟦−M12: In una strategia più ampia di adozione dell'AI in azienda, questo modello dei dati analitici di funzionamento dell'azienda è una parte fondamentale del cosiddetto "company brain" aziendale.⟧

**2) Nel breve periodo**, tutte le procedure di integrazione tra sistemi (che sicuramente esistono) vengono disintermediate da procedure di dialogo tra ogni sistema e lo strato di accesso ai dati comune.

**3) Nel medio periodo**, i singoli sistemi usano lo strato di accesso ai dati come riferimento per la gestione di qualsiasi informazione il cui ambito di utilizzo sia più esteso del proprio dominio applicativo.

Ora, questo approccio — oserei dire "classico" — ha un impatto pesante sull'architettura ICT di un'azienda. Ma essendo la difficoltà di tutte queste integrazioni di natura semantica, è proprio il campo dove gli LLM possono dare un contributo determinante. In particolare:

Il modello dati di riferimento può essere molto articolato: alcune scelte dipendono da analisi approfondite dei dati (per esempio eliminare le ridondanze in un'anagrafica clienti) e le procedure di bonifica possono essere molto complesse. La progettazione e la manutenzione del modello possono essere affidate a un set di agenti AI specializzati, che mantengono ed evolvono non solo il modello ma il contesto che ci sta dietro — che è il vero know how aziendale.

Realizzare le procedure di integrazione con i vari sistemi e fornire uno strato di accesso ai dati è un'attività che richiede lo sviluppo di una mole rilevante di codice. Anche in questo caso l'analisi e lo sviluppo possono essere affidati ad agenti AI, ⟦M09⟧con costi e tempi che non sono comparabili a quelli di un team tradizionale⟦/M09⟧.

Gli agenti demandati alla gestione del modello possono poi trovare, realizzare e gestire tutte le ottimizzazioni possibili: ridurre il numero di servizi esposti, migliorare prestazioni, costi di esercizio e sicurezza.

L'evoluzione del modello dati e dello strato di accesso può essere gestita in maniera analoga. Immaginate un team che vuole realizzare una nuova applicazione, che ha necessità di dati aziendali già esistenti e ne aggiunge di nuovi: l'agente architect riceve le specifiche, genera una proposta di soluzione — dati più servizi di accesso — riutilizzando al massimo quanto già disponibile, o attivando un agente developer per realizzare eventuali nuovi componenti.

## Il rovescio: la frattura di velocità, il vibe coding

Pensando ad aziende che decidono di spostare il baricentro sullo sviluppo make di tutta o parte della propria piattaforma applicativa, la frammentazione dei dati è un grandissimo rischio.

Tipicamente, soprattutto nelle aziende piccole in fase di scale up, l'attenzione è focalizzata sulle funzionalità applicative, e i dati vengono clonati o trasportati. In sintesi: la strategia del dato non evolve alla stessa velocità con cui si producono nuove funzionalità, artifact e componenti. È una vera e propria frattura di velocità, e non esistono colpevoli: nessuno decide consapevolmente di frammentare, è che un lato del sistema ha accelerato di dieci volte e l'altro no.

⟦M07⟧I numeri dal software reggono il punto per analogia. Secondo l'analisi di GitClear su 623 milioni di modifiche tra il 2023 e il 2026, la duplicazione di blocchi di codice è cresciuta dell'81%, mentre il refactoring — le righe spostate anziché aggiunte — è passato dal 21% del 2022 al 3,8%. Ma i due indicatori che descrivono meglio quello di cui sto parlando sono altri: la quota di modifiche che tocca codice non aggiornato da oltre un anno è scesa del 74%, e il numero di chiamate con cui il codice nuovo si aggancia a quello esistente è calato del 35%. Tradotto: nessuno torna più indietro a sistemare, e il nuovo nasce già scollegato. È il silo, misurato.

(È l'analisi di un fornitore, non uno studio peer-reviewed, e non dichiara i propri limiti metodologici. La prendo come indizio robusto, non come prova.)⟦/M07⟧

Il vibe coding non ha inventato il problema della frammentazione: ha tolto l'attrito che lo frenava.

Realizzare un modello unico dei dati governato da agenti AI risolve nativamente questo problema. Nello sviluppo in vibe coding si attiva l'architect virtuale in charge del modello dati, che produce quanto necessario all'applicazione. E in questo caso l'AI non bonifica i dati: lavora direttamente sulle procedure di accesso, creazione e modifica. La scelta su come gestire i dati non è dell'applicazione, ma del team agentico che governa il data model.

Questo approccio si può applicare anche ad altri temi architetturali: la frammentazione dei dati è il caso che tratto qui, ma un tema analogo riguarda per esempio la gestione delle identità e le procedure di autenticazione e autorizzazione.

## Il rischio che non si vede: il TCO rassicura, il passato non dimostrabile

Un punto importante riguarda la gestione del rischio. Se pensate ai due esempi iniziali, alla fine la frammentazione dei dati genera costi che sono ormai assorbiti e controllati dall'azienda, e spesso giustificati dalla velocità di implementazione o dalla complessità di gestione. Quindi, pur esistendo aree di miglioramento, dal punto di vista dei costi può anche essere che non ci sia alcun allarme: tutti i cruscotti vanno bene.

Il rischio è una cosa ben diversa. Cresce senza segnale e poi si tramuta di colpo in un problema o in una catastrofe. Penso sia importante, nell'analisi dei propri dati, rilevare questo tipo di informazioni:

- in quanti posti la stessa entità è "masterizzata";
- quanti legami di chiave tra sistemi non sono ricostruibili automaticamente;
- quale quota dei flussi critici attraversa più di N sistemi;
- il costo di riconciliazione per transazione — che ora, in token, si può davvero calcolare.

⟦M10⟧Sono quattro grandezze molto diverse, e non ho una formula da proporre: chiunque ve ne proponga una, a questo stadio, ve la sta vendendo. Quello che si può fare subito è più modesto e più utile. Prendete i tre o quattro flussi che generano più valore e, per ciascuno, contate quanti sistemi attraversa, quanti legami di chiave non sono ricostruibili in automatico, e quanto costa oggi riconciliarli. Sono numeri che si ottengono in qualche giorno e che raramente esistono già da qualche parte. Il primo valore di quell'esercizio non è l'indice: è che per la prima volta qualcuno in azienda ha un numero da mettere accanto a una parola che finora era solo un'impressione.⟦/M10⟧

## Da dove si comincia: il modello to-be come bersaglio e come cancello

La prima cosa da fare è definire — con il supporto dell'AI e usando tutte le informazioni a disposizione dell'azienda — il modello dati to-be e l'architettura dello strato di accesso ai dati.

La realizzazione sarà poi incrementale, e pensando a una progettazione e uno sviluppo in vibe coding è l'approccio migliore. La progressione può seguire due linee guida.

**1) Dare il bersaglio alla bonifica della situazione attuale.** Si identificano tutti i punti dove la correlazione dei dati è problematica, e uno per uno si indirizzano usando il modello dati come strumento di disintermediazione.

**2) Impedire che ogni nuova feature aggiunga debito.** Al posto di realizzare componenti che generano duplicazione di dati e nuovi flussi — e che quindi, paradossalmente, aumentano la frammentazione — gli agenti che gestiscono il nuovo modello dati vengono coinvolti nello sviluppo di ogni nuovo oggetto.

In questo modo si cominciano ad avere risultati anche nel breve termine. Ed è la cosa che rende questo approccio difendibile davanti al CEO, perché produce effetto prima che la bonifica sia finita. Il che, guarda caso, è di nuovo un modo di appiattire la valle.

⟦↔M13⟧ Pensando ai due esempi citati all'inizio.

⟦M13⟧L'azienda cresciuta in fretta costruirebbe il proprio modello dati con gli stessi strumenti con cui costruisce tutto il resto — in vibe coding — ma con obiettivi diversi dalla sola velocità: governance piena, correttezza, tempestività di accesso al dato. Non un progetto separato: una regola su come si sviluppa.

L'azienda consolidata può partire dalla sola riduzione dei costi operativi, senza generare traumi organizzativi e con risultati costanti e misurabili a ogni passo. E proprio per questo costruire il consenso dal basso, invece di doverlo chiedere dall'alto. Che è, di nuovo, un modo di attraversare la valle senza scenderci dentro.⟦/M13⟧

⟦↔M14⟧ In estrema sintesi: la frammentazione dei dati non è mai stata un problema di fattibilità tecnica, ma di sostenibilità del progetto. Usare l'AI non serve a rendere il debito più tollerabile: serve a rendere la sua estinzione finalmente proponibile. Chi la userà solo per tollerarlo, lo pagherà a canone, per sempre.

---

# Indice delle modifiche

| # | Tipo | Cosa | Perché |
|---|---|---|---|
| **M01** | spostamento + riscrittura | Il paragrafo di definizione del debito tecnologico passa dall'apertura a **ponte dopo le due situazioni**, e acquisisce la frase sulla "valuta" (efficienza / rischio) | L'apertura definitoria abbassa l'energia e mette una barriera davanti al materiale più forte. Come ponte, invece, fa un lavoro in più: introduce l'asse costo/rischio che regge la seconda metà dell'articolo |
| **M02** | sostituzione | Via il «30% degli opex», al suo posto la constatazione che il costo è distribuito e non misurato, con la stima dichiarata come impressione personale | Numero non sostenibile in un articolo che argomenta sul misurare. Trasformato da debolezza in argomento |
| **M03** | sostituzione | Via «almeno il 50% del costo e del tempo» → «spesso la parte più costosa e più lunga non è il software nuovo, è la bonifica di quello vecchio» | Stessa ragione. La versione qualitativa è più forte e infalsificabile senza essere disonesta |
| **M04** | aggiunta | Nuovo blocco in apertura della sezione 4: **l'AI nel percorso di costruzione, non nel percorso di esecuzione**, con i tre criteri (costo una tantum vs canone; errore in revisione vs in produzione; output deterministico vs risposta) | Risolve la contraddizione apparente tra sezione 1 e sezione 4, e dà al lettore il criterio operativo da portarsi via. È la modifica che secondo me vale di più |
| **M05** | aggiunta | Nuovo paragrafo di apertura della sezione 3: la dimostrazione che il debito è semantico — le tre definizioni di "cliente", il legame di chiave che nessuno ha progettato, «non hai perso un dato, hai perso la possibilità di ricostruire una storia» | Il titolo prometteva "debito semantico" e la sezione non lo dimostrava; la sezione 4 poi lo dava per acquisito. Aggancia esplicitamente il primo dei due casi |
| **M06** | riscrittura | Il periodo sul CRM/ERP come scelta giustificata da altri driver | Il periodo originale era sintatticamente aggrovigliato e l'argomento si perdeva |
| **M07** | riscrittura + correzione | I dati GitClear: baseline corrette (refactoring 21% è **2022**), attribuzione esplicita della fonte, sostituiti churn e duplicazione con **Long-term Update −74%** e **Function Connectivity −35%**, più la nota sui limiti della fonte | Il refactoring aveva la baseline sbagliata; e i due nuovi indicatori dicono la tua tesi molto meglio: "nessuno torna indietro a sistemare" e "il nuovo nasce già scollegato". La nota sui limiti rafforza la tua credibilità invece di indebolirla |
| **M08** | sostituzione | Via «sarebbe stato meglio prevenire» → «il momento in cui il progetto diventa approvabile è esattamente quello in cui ha smesso di essere un investimento ed è diventato una riparazione» | La chiusura originale era una banalità dopo un paragrafo acuto |
| **M09** | attenuazione | «ordini di grandezza minori rispetto a team tradizionali» → «costi e tempi che non sono comparabili a quelli di un team tradizionale» | Terza quantificazione non sostenuta. Dice la stessa cosa senza esporre il fianco |
| **M10** | sostituzione | Via «un kpi composto da una combinazione di questi fattori dà un indicatore quantitativo», al suo posto: nessuna formula, ma un esercizio concreto e fattibile in pochi giorni sui tre-quattro flussi principali | Era l'unico punto in cui l'articolo prometteva una misura e consegnava un gesto — proprio ciò che critica negli altri. Ora consegna qualcosa di più piccolo ma vero |
| **M11** | aggiunta | Titolo: *La frammentazione dei dati: affittare il debito o estinguerlo*. Alternative: *Il debito che si paga a canone* · *La frammentazione dei dati non è mai stata un problema tecnico* · *Affittare o comprare: l'AI e il debito sui dati* | Mancava |
| **M12** | eliminazione proposta | Il riferimento al "company brain" | Compare una volta, non spiegato, e suona come buzzword in un pezzo altrimenti asciutto. Se ci tieni, va sviluppato in due righe invece che nominato |
| **M13** | riscrittura | I due paragrafi di chiusura sugli esempi: tolti i tre «potrebbe» in due frasi, aggiunte «non un progetto separato: una regola su come si sviluppa» e «attraversare la valle senza scenderci dentro» | Era l'ultima cosa che il lettore leggeva prima della tesi, ed era la più sfocata. Il richiamo alla valle chiude la cornice |
| **M14** | spostamento | La tesi («in estrema sintesi…») passa da **prima** dei due esempi a **dopo**, come ultimo paragrafo | È la frase più forte del pezzo: l'ultima cosa che si legge è quella che resta |

## Correzioni formali applicate senza marcatura

`si costruiscomo` → si costruiscono · `non è in grado a ricostruire` → di ricostruire · `costi e temi incerti` → costi e tempi incerti · `altri temi architetturale` → altri temi architetturali · `de per se` → di per sé · `Tuttavia L'AI` → Tuttavia l'AI · `da un indicatore` → dà un indicatore · `bomba ad orologeria` → bomba a orologeria · `committment` → commitment · doppio punto in `scalabilità dell'azienda..` · punti finali mancanti in due paragrafi · uniformato `end 2 end` → end-to-end · uniformato `Clienti/Aziende/Agenti` → minuscolo · uniformate le virgolette · sciolte alcune enumerazioni in linea (1)…2)…) in elenchi puntati o in periodi separati, dove la leggibilità lo richiedeva.

## Cosa non ho toccato, e perché

- **La tua voce.** Le scelte lessicali, gli anglicismi (`make`, `in charge`, `large account`, `slave`), il registro colloquiale in prima persona («se ci pensate», «immaginate un team») sono tuoi e funzionano: sono il segnale che chi scrive lavora davvero in quel mondo.
- **La struttura delle sezioni.** L'ordine dei sette blocchi è quello che avevi.
- **L'architettura in tre passi** della sezione 4 e l'idea del team agentico che governa il data model: è la parte originale dell'articolo, e non ho aggiunto né tolto nulla.
- **I due casi.** Solo pulizia sintattica, nessun cambiamento di contenuto o di livello di dettaglio.
