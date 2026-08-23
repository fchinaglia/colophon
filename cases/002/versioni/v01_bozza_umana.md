Uno dei temi quotidiani per un CTO e per un CIO è come affrontare e gestire il “debito tecnologico”, ovvero tutte quelle situazioni per cui la propria piattaforma tecnologica è “indietro” rispetto allo stato dell’arte. Una componente rilevante del debito tecnologico riguarda la frammentazione e qualità del dato.

Ecco due situazioni tipiche:

Un’azienda di servizi B2C in fase di scale up attiva in maniera veloce una serie di sistemi e software per automatizzare il ciclo attivo, lead generation – contatto – vendita – pagamento – erogazione del servizio, con una integrazione lasca tra di essi. Al crescere del business i sistemi vengono fatti evolvere in maniera rapida, creando dei silos applicativi, ognuno con i propri dati, e la correlazione tra i dati dei vari silos non è più univoca o garantita, rendendo difficoltosa la governance end 2 end di processo (il pagamento ricevuto via bonifico a quale cliente e lead si riferisce?) e le attività strategiche di evoluzione del business (quella campagna quanto ha generato in termini di incassato?).
In questo caso la frammentazione dei dati introduce una inefficienza e può penalizzare la scalabilità dell’azienda..

Un’azienda di servizi consolidata, che eroga importanti volumi di transazioni mission critical B2B verso large account, con livelli di servizio al top del mercato e una infrastruttura importante e strutturata, non è in grado a ricostruire in maniera adeguata, in caso di problemi operativi, di privacy e di sicurezza, l’impatto degli stessi, in termini di attori coinvolti (quanti Clienti, personale interno e di partner coinvolti e in quale ruolo), dati (quali dati, in che forma, quali trattamenti) e processi. Questo perché il numero dei sistemi coinvolti, la loro stratificazione e sovrapposizione ha creato silos di dati, barriere, duplicazioni funzionali, spesso non documentate. Estrarre un elenco di clienti impattati, una mappa degli attori aziendali coinvolti, fare un’analisi analitica dei dati e valutare l’impatto di un problema diventa di per se un progetto da centinaia di giorni uomo, con risultato, costi e temi incerti. In questo secondo caso la frammentazione dei dati produce un “passato non dimostrabile”, paradossalmente il rischio si accumula all’indietro e col crescere dei volumi. Con il crescere delle esigenze di compliance che dai Clienti si ripropagano su tutta la catena di fornitura, avere questo tipo di situazioni è una vera e propria bomba ad orologeria pronta ad esplodere.

## Il canone invisibile: cosa costa già oggi, e perché ora si vede

La frammentazione dei dati è un costo, spesso invisibile. Aziende in situazioni simili a quelle sopra descritte pagano sicuramente un costo importante per gestire le inefficienze generate dalla frammentazione dei dati. Personale e consulenti dedicati ad attività di riconciliazione manuale o alla scrittura di procedure software di “integrazione” tra sistemi. Probabilmente un buon 30% degli opex di una qualsiasi struttura ICT corporate sono dedicate a questo tipo di attività.
Quando questi costi emergono e diventano visibili: un caso tipico in passato era la migrazione ad un nuovo sistema. Attivare un nuovo CRM o un ERP è un caso emblematico, perché costringe a fare ordine nei dati, e di solito almeno il 50% del costo e del tempo è dedicato a quello, una grande, immensa, bonifica.
Un caso “nuovo” è dato dall’uso dell’AI non per risolvere alla fonte la frammentazione dei dati, ma per renderla tollerabile. Al posto di riconciliare a mano, al posto di migrare in sistemi che coprono end 2 end tutti i processi, si costruiscomo una serie di procedure “intelligenti” che riconciliano i dati. In apparenza sembra l’uovo di colombo, l’AI è in grado di gestire anche situazioni nuove, non pienamente definite, sembra fatta apposta per interpretare i disallineamenti tra sistemi.
Questo è vero, è una soluzione efficace ma con due problemi: 1) ha un costo “in tokens” che può diventare importante, se non altro diventa visibile. Il problema è risolto in apparenza, ma nella realtà rimane e genera un costo ricorrente 2) è una soluzione non deterministica, nel senso che può fare errori, e in alcuni contesti l’approssimazione aumenta il rischio.

## Perché nessuno lo risolve: la valle, e la conversazione che si vince solo dopo il danno

Penso che qualsiasi CTO sappia qual è il percorso per arrivare ad avere un modello dati integrato e consistente, con una implementazione performante, resiliente, sicura e scalabile.

Ma come si fa a sostenere questo tipo di progetto di fronte ad un CEO o ad uno steering committee o un CDA? I benefici in termini di riduzione del costo e del rischio possono essere importanti, ma in generale si parte da una situazione iniziale in cui il costo operativo è nascosto e l’azienda comunque funziona. Il tema è poi squisitamente tecnico, e impegnare l’azienda per avere un risultato nel medio periodo passando comunque attraverso la “valle della disperazione” tipica di ogni progetto è una scelta che rischia di isolare il CTO che la fa.
L’unica situazione in cui tutti gli stakeholder possono alzare il proprio livello di committment paradossalmente è a fronte di un problema. Se il rischio accumulato ad un certo punto “esplode” in un incident, il piano di remediation può essere il modo per risolvere il debito tecnologico che lo ha causato, ma sicuramente sarebbe stato meglio prevenire

## Cosa si rompe davvero: il debito semantico, la suite come soluzione impacchettata

Il problema della frammentazione dei dati si risolve strutturalmente ricostruendo le correlazioni tra silos applicativi. Se ci pensate è quello che succede quando un’azienda acquista un CRM o un ERP. Alla fine non stai comprando un software, stai comprando un modello dati. È una soluzione impacchettata — per avere il modello devi prendere anche la piattaforma, la migrazione e il lock-in. Di certo è una scelta che si giustifica se l’azienda ha un problema più importante di efficienza operativa e governance dei processi, la soluzione del problema della frammentazione dei dati è un side effect, non certo il main driver di questa scelta.
Tuttavia L'AI spacchetta il pacchetto: oggi è possibile ricostruire il modello condiviso senza adottare piattaforme “trasversali”.

## Cosa cambia adesso: l'AI accorcia la valle della disperazione

Al posto di usare l’AI per costruire procedure di integrazione “intelligenti” tra sistemi, è possibile implementare una strategia diversa:

1) Disegno un modello dati di riferimento, ovvero una architettura di accesso e memorizzazione del dato.

Può essere nei casi più semplici un unico database aziendale, opportunamente ridondato e con tutte le misure di sicurezza del caso. Nel caso più generale è un insieme di componenti (database, storage, servizi di accesso, middleware di comunicazione) che garantiscono la correttezza, unicità, sicurezza del dato, e lo rendono accessibile dove serve con prestazioni adeguate. La cosa importante è avere una governance unica ed un processo chiaro, robusto e veloce per farlo evolvere alla velocità del business. Le stesse applicazioni aziendali sono parte di questo modello. Ad esempio se la fonte certa di un dato, ad esempio l’anagrafica Clienti, è il CRM aziendale, il modello dati garantirà che ogni copia di questo dato in altri sistemi sia “slave” della fonte di verità aziendale.

In una strategia più ampia di adozione dell’AI in azienda, questo modello dei dati analitici di funzionamento dell’azienda è una parte fondamentale del cosiddetto “company brain” aziendale.

2) Nel breve periodo tutte le procedure di integrazione tra sistemi (che sicuramente esistono) vengono disintermediate da procedure di dialogo tra ogni sistema e lo strato di accesso ai dati comune.

3) Nel medio periodo i singoli sistemi usano lo strato di accesso ai dati come riferimento per la gestione di qualsiasi tipo di informazione il cui ambito di utilizzo sia più esteso del proprio dominio applicativo

Ora questo approccio oserei dire “classico” ha un impatto pesante sull’architettura ICT di un’azienda. Tuttavia essendo la difficoltà di tutte queste integrazioni di natura semantica, è proprio il campo dove gli LLM possono dare un contributo determinante, in particolare:

Il modello dati di riferimento può essere molto articolato, alcune scelte dipendono da analisi approfondite dei dati (ad esempio eliminare le ridondanze in un’anagrafe Clienti) e le procedure di bonifica possono essere molto complesse. La progettazione e la manutenzione del modello dati possono essere affidate ad un set di agenti AI specializzati che mantengono ed evolvono non solo il modello ma il contesto che ci sta dietro, che è il vero know how aziendale.

Realizzare le procedure di integrazione con i vari sistemi, e fornire uno strato di accesso ai dati è un’attività che richiede lo sviluppo di una mole anche rilevante di codice. Anche in questo caso l’analisi e lo sviluppo può essere affidato ad Agenti AI con costi e tempi sicuramente di ordini di grandezza minori rispetto a team tradizionali.

Gli agenti demandati alla gestione del modello potrebbero poi trovare, realizzare e gestire tutte le ottimizzazioni possibili, sia per ridurre il numero di servizi esposti, sia per migliorare prestazioni, costi di esercizio e sicurezza.

L’evoluzione del modello dati e dello strato di accesso può essere gestito in maniera analoga. Immaginate un team che vuole realizzare una nuova applicazione, che ha necessità di dati aziendali già esistenti e ne aggiunge di nuovi. L’agente architect riceve le specifiche, genera una proposta di soluzione (dati + servizi di accesso) riutilizzando al massimo quanto già disponibile o attivando un agente developer per realizzare eventuali nuovi componenti.

## Il rovescio: la frattura di velocità, il vibe coding

Pensando ad Aziende che decidono di spostare il baricentro sullo sviluppo make di tutta o parte della propria piattaforma applicativa, la frammentazione dei dati è un grandissimo rischio.
Tipicamente, soprattutto nelle aziende piccole in fase di scale up, l’attenzione è focalizzata sulle funzionalità applicative, i dati vengono clonati o trasportati. In sintesi, la strategia del dato non evolve alla stessa velocità con cui si producono nuove funzionalità, artifact e componenti.
E’ una vera e propria frattura di velocità, e non esistono colpevoli: nessuno decide consapevolmente di frammentare, è che un lato del sistema ha accelerato di dieci volte e l'altro no.
I numeri dal software reggono il punto per analogia: su 623 milioni di modifiche, churn a due settimane +15%, duplicazione di blocchi +81% rispetto al 2023, e il refactoring crollato dal 21% al 3,8% del codice modificato. (nota: qual è la fonte di questo dato)
Il vibe coding non ha inventato il problema della frammentazione, ha tolto l'attrito che lo frenava.
Ora realizzare un modello unico dei dati governato da agenti AI risolve “nativamente” questo problema. Nello sviluppo in vibe coding si attiva l’Architect virtuale in charge del modello dati, che produce quanto necessario all’applicazione. E in questo caso l’AI non bonifica i dati, lavora direttamente sulle procedure di accesso, creazione e modifica dei dati. La scelta su come gestire i dati non è dell’applicazione ma del team agentico che governa il data model.
Ora questo approccio si può applicare anche ad altri temi architetturale: la frammentazione dei dati è il caso che tratto qui; un tema analogo riguarda per esempio la gestione delle identità e le procedure di autenticazione ed autorizzazione.

## Il rischio che non si vede: il TCO rassicura, il passato non dimostrabile

Un punto importante riguarda la gestione del rischio. Se pensate ai due esempi fatti all’inizio, alla fine la frammentazione dei dati genera costi che comunque sono ormai assorbiti e controllati dall’azienda, e spesso giustificati dalla velocità di implementazione o dalla complessità di gestione.
Quindi pur esistendo aree di miglioramento, dal punto di vista dei costi, può anche essere che non ci sia alcun allarme, “tutti i cruscotti vanno bene”.
Il rischio è una cosa ben diversa. Spesso cresce senza segnale e poi si tramuta di colpo in un problema o in una catastrofe. Penso sia importante, nell’analisi dei propri dati, rilevare questo tipo di informazioni.
- in quanti posti la stessa entità è "masterizzata";
- quanti legami di chiave tra sistemi non sono ricostruibili automaticamente;
- quale quota dei flussi critici attraversa più di N sistemi;
- costo di riconciliazione per transazione — che ora, in token, si può davvero calcolare.

Un kpi composto da una combinazione di questi fattori, che includono anche il costo di riconciliazione, da un indicatore quantitativo del livello di rischio.

## Da dove si comincia: il modello to-be come bersaglio e come cancello

La prima cosa da fare è definire, con il supporto dell’AI e usando tutte le informazioni a disposizione dell’azienda, il modello dati to-be e l’architettura dello strato di accesso ai dati.
La realizzazione del modello sarà poi incrementale, e pensando ad una progettazione e sviluppo in vibe coding, è l’approccio migliore. La progressione dello sviluppo può essere fatta seguendo due linee guida:

1) dare il bersaglio alla bonifica della situazione attuale. Si identificano tutti i punti dove la correlazione dei dati è problematica, e uno per uno si indirizzano usando il modello dati come strumento di disintermediazione

2) impedire che ogni nuova feature aggiunga debito
al posto di realizzare componenti che generano duplicazione di dati, nuovi flussi, e quindi paradossalmente aumentano la frammentazione, gli agenti che gestiscono il nuovo modello dati vengono coinvolti nello sviluppo di ogni nuovo oggetto.

In questo modo si cominciano ad avere risultati anche nel breve termine, e, se vogliamo, è la cosa che rende questo approccio difendibile davanti al CEO, perché produce effetto prima che la bonifica sia finita. Il che, guarda caso, è di nuovo un modo di appiattire la valle.

In estrema sintesi, la frammentazione dei dati non è mai stata un problema di fattibilità tecnica, ma di sostenibilità del progetto. Usare l’AI non serve a rendere il debito più tollerabile: serve a rendere la sua estinzione finalmente proponibile. Chi la userà solo per tollerarlo, lo pagherà a canone, per sempre.

Pensando ai due esempi citati all’inizio:

Una piccola azienda in forte crescita avrebbe un modello dati sviluppato in vibe coding, esattamente come gli altri artefatti. In questo caso però gli obiettivi sono, oltre alla velocità di implementazione, la piena governance, la correttezza e la tempestività di accesso al dato.

Una grande azienda con applicazioni sedimentate potrebbe attivare un processo di evoluzione che potrebbe alimentarsi dalla pura riduzione dei costi operativi, senza generare “traumi” aziendali, con risultati costanti e misurabili. Questo tipo di situazione potrebbe permettere di accelerare e acquisire consenso “dal basso”
