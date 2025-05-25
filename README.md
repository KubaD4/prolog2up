# RoboticsInternship

## Indice
- [RoboticsInternship](#roboticsinternship)
  - [Indice](#indice)
  - [Struttura del Progetto](#struttura-del-progetto)
- [Prolog, PDDL e Unified Planning](#prolog-pddl-e-unified-planning)
  - [Requisiti](#requisiti)
    - [Requisiti Generali](#requisiti-generali)
    - [Requisiti per la Sezione PDDL](#requisiti-per-la-sezione-pddl)
    - [Requisiti per Unified Planning](#requisiti-per-unified-planning)
    - [Requisiti per Prolog](#requisiti-per-prolog)
    - [Requisiti per il Convertitore](#requisiti-per-il-convertitore)
  - [Utilizzo](#utilizzo)
    - [Sezione PDDL](#sezione-pddl)
    - [Sezione Unified Planning](#sezione-unified-planning)
    - [Sezione Prolog](#sezione-prolog)
- [Convertitore da Prolog a Unified Planning](#convertitore-da-prolog-a-unified-planning)
  - [Architettura e Flusso](#architettura-e-flusso)
  - [Utilizzo del Convertitore](#utilizzo-del-convertitore)
  - [File di Output](#file-di-output)
  - [Troubleshooting](#troubleshooting)

## Struttura del Progetto

La cartella è organizzata come segue:
```
.
├── CONVERTER
│   ├── **pycache**
│   │   ├── kb_to_json.cpython-311.pyc
│   │   ├── prolog_extractor.cpython-311.pyc
│   │   └── prolog2up_V2.cpython-311.pyc
│   ├── from_prolog_to_up.py
│   ├── kb_to_json.py
│   ├── orchestrator.py
│   ├── prolog_extractor.py
│   └── prolog2up_V2.py
├── extracted_knowledge.json
├── GENERATED_BY_CONVERTED
│   └── generated_up.py
├── PDDL
│   ├── domain_a_mano.pddl
│   ├── problem_a_mano.pddl
│   └── run_plan.py
├── PROLOG
│   ├── cucinare.pl
│   ├── entrare.pl
│   ├── kb_hl.pl
│   ├── medic.pl
│   └── small_kb_hl.pl
├── README.md
├── RESULTS
│   ├── CONVERTER
│   ├── PDDL
│   │   └── problem_a_mano_0506_12:16
│   │       ├── best_solution_summary.txt
│   │       ├── comparison_report.txt
│   │       ├── comparison_results.csv
│   │       ├── detailed_results.json
│   │       ├── domain_a_mano.pddl
│   │       ├── fd_astar_ff_output.txt
│   │       ├── fd_astar_ff_plan.txt
│   │       ├── fd_lazy_greedy_output.txt
│   │       ├── fd_lazy_greedy_plan.txt
│   │       └── problem_a_mano.pddl
│   ├── RESULTS
│   │   └── PDDL
│   │       └── converter_pddl_result_problem_0517_1851
│   │           ├── comparison_report.txt
│   │           ├── comparison_results.csv
│   │           ├── converter_pddl_result_domain.pddl
│   │           ├── converter_pddl_result_problem.pddl
│   │           ├── detailed_results.json
│   │           ├── fd_astar_ff_output.txt
│   │           └── fd_lazy_greedy_output.txt
│   └── UP
└── UNIFIED_PLANNING
    ├── blocks_domain.pddl
    ├── blocks_problem.pddl
    ├── cucinare.py
    ├── kb_hl_old.py
    ├── kb_hl.py
    ├── quickstart.py
    └── test.py
```

# Prolog, PDDL e Unified Planning

## Requisiti

### Requisiti Generali

1. **Python 3.8+**
   ```bash
   # Verifica la tua versione di Python
   python3 --version
   ```

2. **Visual Studio Code**
   - Come IDE ho scelto Visual Studio Code
   - Estensioni consigliate:
     - Estensione Python 
     - Estensione Prolog (se si vuole usare il Prolog)
     - PDDL https://marketplace.visualstudio.com/items?itemName=jan-dolejsi.pddl

### Requisiti per la Sezione PDDL

1. **Dipendenze Python**
   ```bash
   pip3 install prettytable
   ```

2. **Pianificatore PyPerplan** 
   ```bash
   pip3 install pyperplan
   ```

3. **Pianificatore Fast Downward** (più avanzato)
   ```bash
   # Clona il repository Fast Downward
   git clone https://github.com/aibasel/downward.git
   cd downward
   ./build.py
   cd ..
   ```

### Requisiti per Unified Planning

[Documentazione Unified Planning](https://unified-planning.readthedocs.io/en/latest/getting_started.html)

1. **Installa il pacchetto unified_planning**
   ```bash
   pip3 install unified-planning
   ```

2. **Installa i motori di pianificazione**
   ```bash
   # Installa *tutti* i motori di base
   pip3 install unified-planning[engines]
   
   # Oppure installa motori specifici, ad esempio:
   pip3 install unified-planning[pyperplan]
   pip3 install unified-planning[tamer]
   pip3 install unified-planning[enhsp]
   ```
   
   - [elenco completo dei motori disponibili per Unified Planning](https://unified-planning.readthedocs.io/en/latest/engines/01_available_engines.html)


### Requisiti per Prolog

Per la sezione Prolog, fare riferimento al [repository PLANTOR](https://github.com/idra-lab/PLANTOR) per istruzioni dettagliate sull'installazione. Come minimo, servirà:

1. **SWI-Prolog**
   ```bash
   # Per macOS (usando Homebrew)
   brew install swi-prolog
   
   # Per Ubuntu/Debian
   sudo apt-get install swi-prolog
   ```

### Requisiti per il Convertitore

1. **Python 3.8+**
   ```bash
   # Verifica la tua versione di Python
   python3 --version
   ```

2. **Unified Planning**
   ```bash
   pip3 install unified-planning
   pip3 install unified-planning[engines]
   ```

3. **Pyswip** (interfaccia Python per SWI-Prolog)
   ```bash
   pip3 install pyswip
   ```

4. **SWI-Prolog** (come indicato nella sezione Prolog)

## Utilizzo

### Sezione PDDL

La sezione PDDL contiene file di dominio e problema scritti manualmente insieme a uno script Python per trovare piani.

1. **Esecuzione con algoritmo di ricerca predefinito**
   ```bash
   python3 PDDL/run_plan.py PDDL/domain_a_mano.pddl PDDL/problem_a_mano.pddl
   ```

2. **Esecuzione con algoritmi di ricerca specifici**
   ```bash
   # python3 PDDL/run_plan.py PDDL/domain_a_mano.pddl PDDL/problem_a_mano.pddl --searches algoritmo1 algoritmo2...
   python3 PDDL/run_plan.py PDDL/domain_a_mano.pddl PDDL/problem_a_mano.pddl --searches lazy_greedy eager_greedy astar_ff astar_lmcount wastar astar_blind astar_lmcut lazy_wastar
   ```

Lo script creerà una directory con i risultati, incluso il piano trovato, le statistiche di esecuzione e i rapporti di confronto tra diversi algoritmi di ricerca.

### Sezione Unified Planning

Questa sezione utilizza il framework Unified Planning per creare e risolvere problemi di pianificazione e generare file PDDL. 

1. **Esecuzione dell'esempio dei blocchi**
   ```bash
   python3 UNIFIED_PLANNING/kb_hl.py
   ```
   Questo script:
   - Definisce un problema del mondo dei blocchi
   - Genera file PDDL (blocks_domain.pddl e blocks_problem.pddl)
   - Utilizza un motore appropriato (scelto automaticamente dal framework) per trovare una soluzione

2. **Esecuzione dell'esempio quickstart**

    Un piccolo esempio creato a partire dal tutorial seguito dalla documentazione ufficiale.
   ```bash
   python3 UNIFIED_PLANNING/quickstart.py
   ```

Il framework Unified Planning seleziona automaticamente un motore di pianificazione appropriato in base alle caratteristiche del problema, ma si può anche specificare quale motore utilizzare.

**Importante**: Alla fine del file kb_hl.py ci sono due chiamate di funzione:
```python
export_to_pddl()  # Genera i file PDDL
solve_problem()   # Risolve il problema
```
Cmmentare una delle due linee in base a ciò che desideri fare:

- Generare i file PDDL senza risolvere il problema, commentare solve_problem()
- Risolvere il problema senza generare i file PDDL, commentare export_to_pddl()
- O lasciare entrambi scommentati 

### Sezione Prolog

La sezione Prolog contiene un file di knowledge base preso dal progetto PLANTOR.

Per istruzioni dettagliate su come utilizzare questo file con il framework PLANTOR, fare riferimento al [repository PLANTOR](https://github.com/idra-lab/PLANTOR).

```bash
prolog_planner % swipl -l planner.pl -t "plan(4)."
```

# Convertitore da Prolog a Unified Planning

La sezione del convertitore è stata aggiornata con una nuova struttura modulare che permette di trasformare automaticamente file Prolog in rappresentazioni Python utilizzando il framework Unified Planning, generando anche i relativi file PDDL.

## Architettura e Flusso

Il processo di conversione è ora composto da diversi moduli che lavorano insieme:

1. **orchestrator.py**: Coordina l'intero processo di conversione
2. **prolog_extractor.py**: Estrae la conoscenza dai file Prolog
3. **kb_to_json.py**: Converte la conoscenza estratta in formato JSON strutturato
4. **prolog2up_V2.py**: Genera il codice Python Unified Planning dal JSON
5. **generated_up.py**: Il codice Python risultante che crea i file PDDL

Il flusso di conversione è il seguente:
```
File Prolog → Estrazione della Conoscenza → JSON → Codice Unified Planning → File PDDL
```

## Utilizzo del Convertitore

Per avviare il convertitore con la nuova struttura, eseguire lo script orchestrator seguito dal percorso del file Prolog che si desidera convertire:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl
```

Per un output più dettagliato, utilizzare il flag --verbose:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --verbose
```

Dopo il completamento del processo di conversione, otterrai diversi file di output. Per garantire che i file PDDL vengano generati correttamente, potrebbe essere necessario eseguire direttamente il codice Python generato:

```bash
python3 GENERATED_BY_CONVERTED/generated_up.py
```

## File di Output

Il processo di conversione produce diversi file:

1. **extracted_knowledge.json**: Rappresentazione strutturata della conoscenza estratta dal file Prolog
2. **generated_up.py**: Codice Python che utilizza il framework Unified Planning
3. **generated_domain.pddl**: Il file di dominio PDDL risultante
4. **generated_problem.pddl**: Il file di problema PDDL risultante

Questi file vengono memorizzati nelle seguenti posizioni:
- File JSON: Nella directory principale
- Codice Python Unified Planning: Nella directory `GENERATED_BY_CONVERTED/`
- File PDDL: Nella directory `GENERATED_BY_CONVERTED/`

## Troubleshooting

Se riscontri errori durante il processo di conversione, ecco alcune soluzioni comuni:

1. **Problemi con i percorsi dei file**: Assicurati di eseguire i comandi dalla directory principale del progetto
2. **File PDDL mancanti**: Se i file PDDL non vengono generati automaticamente, esegui manualmente lo script generated_up.py
3. **Errori di PySwip**: Assicurati che SWI-Prolog sia installato e configurato correttamente per PySwip
.