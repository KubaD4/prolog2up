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
  - [Requisiti e Installazione](#requisiti-e-installazione)
    - [Prerequisiti di Sistema](#prerequisiti-di-sistema)
    - [Installazione Virtual Environment](#installazione-virtual-environment)
  - [Utilizzo del Convertitore](#utilizzo-del-convertitore)
    - [Conversione Base](#conversione-base)
    - [Conversione con Pianificazione](#conversione-con-pianificazione)
    - [Output Dettagliato](#output-dettagliato)
    - [Combinazione di Opzioni](#combinazione-di-opzioni)
  - [File di Output](#file-di-output)
    - [Senza flag --solve](#senza-flag---solve)
    - [Con flag --solve](#con-flag---solve)
    - [Descrizione dei File](#descrizione-dei-file)
  - [Gestione dei Risultati](#gestione-dei-risultati)
  - [Esempi di Output](#esempi-di-output)
    - [Output Normale (senza --detailed)](#output-normale-senza---detailed)
    - [Output con --detailed](#output-con---detailed)
  - [Timing delle Performance](#timing-delle-performance)
  - [Workflow Completo di Utilizzo](#workflow-completo-di-utilizzo)
    - [Setup Iniziale (Una volta)](#setup-iniziale-una-volta)

## Struttura del Progetto

La cartella è organizzata come segue:
```
.
├── CONVERTER
│   ├── __pycache__
│   │   ├── kb_to_json.cpython-311.pyc
│   │   ├── prolog_extractor.cpython-311.pyc
│   │   └── prolog2up_V2.cpython-311.pyc
│   ├── from_prolog_to_up.py
│   ├── kb_to_json.py
│   ├── orchestrator.py
│   ├── prolog_extractor.py
│   └── prolog2up_V2.py
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
│   │   └── cucinare_0525_1430          # Cartelle con timestamp
│   │       ├── extracted_knowledge.json
│   │       ├── generated_up.py
│   │       ├── generated_domain.pddl
│   │       ├── generated_problem.pddl
│   │       └── planning_results.txt    # (se usato --solve)
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
Commentare una delle due linee in base a ciò che desideri fare:

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

Permette di trasformare automaticamente file Prolog in rappresentazioni Python utilizzando il framework Unified Planning, generando anche i relativi file PDDL e, opzionalmente, risolvendo i problemi di pianificazione.

## Architettura e Flusso

Il processo di conversione è ora composto da diversi moduli che lavorano insieme:

1. **orchestrator.py**: Coordina l'intero processo di conversione
2. **prolog_extractor.py**: Estrae la conoscenza dai file Prolog
3. **kb_to_json.py**: Converte la conoscenza estratta in formato JSON strutturato
4. **prolog2up_V2.py**: Genera il codice Python Unified Planning dal JSON
5. **generated_up.py**: Il codice Python risultante che crea i file PDDL
6. **run_plan.py**: (Opzionale) Risolve i problemi PDDL generati

Il flusso di conversione è il seguente:
```
File Prolog → Estrazione → JSON → Codice UP → File PDDL → [Pianificazione]
```

## Requisiti e Installazione

### Prerequisiti di Sistema

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **SWI-Prolog** (necessario per PySwip)
   ```bash
   # macOS (usando Homebrew)
   brew install swi-prolog
   
   # Ubuntu/Debian
   sudo apt-get install swi-prolog
   
   # Windows: Scaricare da https://www.swi-prolog.org/download/stable
   ```

3. **Fast Downward** (per la pianificazione PDDL)
   ```bash
   git clone https://github.com/aibasel/downward.git
   cd downward
   ./build.py
   cd ..
   ```

### Installazione Virtual Environment


```bash
# 1. Creare e attivare virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure su Windows: venv\Scripts\activate

# 2. Installare dipendenze Python dal requirements.txt
pip3 install -r requirements.txt

### File requirements.txt

Il file `requirements.txt` contiene tutte le dipendenze Python necessarie:

```bash
# Core dependencies for the PDDL planning system
unified-planning
unified-planning[engines]  # Include all planning engines

# For Prolog extraction
pyswip

# For table formatting and output
prettytable

# Additional planning engines (optional)
pyperplan

# For development and testing
pytest
```

## Utilizzo del Convertitore

### Conversione Base

Per convertire un file Prolog in formato PDDL:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl
```

### Conversione con Pianificazione

Per convertire E risolvere automaticamente il problema di pianificazione:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve
```

### Output Dettagliato

Per un output più dettagliato durante la conversione (messaggi di debug, analisi fluenti, etc.):

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --detailed
```

### Combinazione di Opzioni

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve --detailed
```


## File di Output

Il processo di conversione produce diversi file organizzati in cartelle con timestamp:

### Senza flag --solve
```
RESULTS/CONVERTER/cucinare_0525_1430/
├── extracted_knowledge.json          # Conoscenza strutturata estratta
├── generated_up.py                   # Codice Python UP
├── generated_domain.pddl             # File dominio PDDL
└── generated_problem.pddl            # File problema PDDL
```

### Con flag --solve
```
RESULTS/CONVERTER/cucinare_0525_1430/
├── extracted_knowledge.json          
├── generated_up.py                   
├── generated_domain.pddl             
├── generated_problem.pddl            
└── planning_results.txt              # Risultati di pianificazione unificati
```

### Descrizione dei File

| File | Descrizione |
|------|-------------|
| `extracted_knowledge.json` | Rappresentazione strutturata della conoscenza estratta dal Prolog |
| `generated_up.py` | Codice Python che utilizza il framework Unified Planning |
| `generated_domain.pddl` | File dominio PDDL risultante |
| `generated_problem.pddl` | File problema PDDL risultante |
| `planning_results.txt` | Risultati di pianificazione con tabella comparativa e tutti i piani trovati |

## Gestione dei Risultati

Ogni esecuzione del convertitore crea una cartella con timestamp unico:
- Formato: `{nome_file}_{MMDD_HHMM}`
- Esempio: `cucinare_0525_1430` per il file `cucinare.pl` eseguito il 25 maggio alle 14:30

## Esempi di Output

### Output Normale (senza --detailed)

```
=== Prolog to Unified Planning Conversion Pipeline ===
Input file: PROLOG/cucinare.pl
Output directory: RESULTS/CONVERTER/cucinare_0730_1430
SOLVER: enabled
DETAILS: disabled, use --detailed to enable

Step 1: Extracting knowledge from Prolog file...
  Completed in 0.008 seconds

Step 2: Analyzing fluent signatures...
  Completed in 0.001 seconds

Step 3: Converting knowledge to JSON format...
Step 4: Saving extracted knowledge to JSON...
  - Saved to: RESULTS/CONVERTER/cucinare_0730_1430/extracted_knowledge.json
  Completed in 0.001 seconds

Step 5: Generating Unified Planning code...
  - Generated UP code: RESULTS/CONVERTER/cucinare_0730_1430/generated_up.py
  Completed in 0.495 seconds

Step 6: Executing generated UP code to create PDDL files...
  - Successfully executed generated UP code
  Completed in 0.635 seconds

Step 7: Running PDDL solver...
  - Planning successful! Results saved to planning_results.txt
  - Planning results:
    * fast_downward_lazy_greedy:
      STATUS: Plan found (2 steps)
      Step  1: (cucina mario pasta pentola tavolo)
      Step  2: (mangia mario pasta)

    * fast_downward_astar_ff:
      STATUS: Plan found (2 steps)
      Step  1: (cucina mario pasta pentola tavolo)
      Step  2: (mangia mario pasta)

  Completed in 0.156 seconds

=== Conversion Pipeline Completed Successfully ===
Generated files in: RESULTS/CONVERTER/cucinare_0730_1430
  - JSON knowledge: extracted_knowledge.json
  - UP Python code: generated_up.py
  - PDDL domain: generated_domain.pddl
  - PDDL problem: generated_problem.pddl
  - Planning results: planning_results.txt

Total execution time: 1.29615 seconds
  Step 1 (Extraction): 0.00853s
  Step 2 (Signatures): 0.00015s
  Step 3-4 (JSON): 0.00073s
  Step 5 (UP Code): 0.49463s
  Step 6 (PDDL): 0.63534s
  Step 7 (Planning): 0.15677s
```

### Output con --detailed

Con il flag `--detailed`, l'output includerà informazioni aggiuntive come:
- Messaggi di debug con prefisso "DEBUG:"
- Analisi dettagliata dei fluenti polimorfi
- Vincoli di tipo per ogni azione
- Sincronizzazione dell'uso dei fluenti
- Output completo di tutti i moduli interni

## Timing delle Performance

L'orchestrator fornisce informazioni dettagliate sui tempi di esecuzione per ogni fase, permettendo di identificare colli di bottiglia nel processo di conversione:

```
Total execution time: 1.30857 seconds
  Step 1 (Extraction): 0.00788s     # Estrazione da Prolog
  Step 2 (Signatures): 0.00029s     # Analisi firme fluenti
  Step 3-4 (JSON): 0.00064s         # Conversione JSON
  Step 5 (UP Code): 0.46544s        # Generazione codice UP
  Step 6 (PDDL): 0.63290s           # Creazione file PDDL
  Step 7 (Planning): 0.20131s       # Pianificazione (se --solve)
```

## Workflow Completo di Utilizzo

### Setup Iniziale (Una volta)

```bash
# 1. Clone del repository e navigazione
cd path/to/RoboticsInternship

# 2. Creazione virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Installazione dipendenze Python
pip3 install -r requirements.txt

# 4. Installazione SWI-Prolog (sistema)
brew install swi-prolog  # macOS

# 5. Installazione Fast Downward (opzionale, per planning)
git clone https://github.com/aibasel/downward.git
cd downward && ./build.py && cd ..

# 6. Verifica installazione
python3 -c "import unified_planning; from pyswip import Prolog; print('Setup OK')"
```