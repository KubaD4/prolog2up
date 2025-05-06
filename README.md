# RoboticsInternship

La cartella è organizzata come segue:
```
.
├── PDDL
│   ├── domain_a_mano.pddl
│   ├── problem_a_mano.pddl
│   └── run_plan.py
├── PROLOG
│   ├── kb_hl.pl
│   └── small_kb_hl.pl
├── UNIFIED_PLANNING
│    ├── blocks_domain.pddl
│    ├── blocks_problem.pddl
│    ├── kb_hl.py
│    └── quickstart.py
├── CONVERTER
│    ├── converter.py
│    └── prolog2up.py
└── RESULTS
    ├── CONVERTER
    │   ├── converter_pddl_result_domain.pddl
    │   └── converter_pddl_result_problem.pddl
    ├── PDDL
    │   └── problem_a_mano_0506_12:16
    │       ├── best_solution_summary.txt
    │       ├── domain_a_mano.pddl
    │       └── problem_a_mano.pddl
    └── UP
        ├── UP_generated_domain.pddl
        └── UP_generated_problem.pddl
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

## Conclusione

Per la realizzazione degli script di risoluzione che vanno a confrontare vari algoritmi ho scelto di aiutarmi tramite l'utilizzo di Claude (a partire da codici scritti a mano) in modo da migliorarli ed avere 
1. output ben formattati
2. script che andassero a combinare tante metologie diverse, senza doverle implementare tutte a mano

Ed infine per riordinare/pulire/simili il codice 

# Convertitore da Prolog a Unified Planning

La sezione del convertitore permette di trasformare automaticamente codice Prolog in rappresentazioni Python utilizzando il framework Unified Planning, generando anche i relativi file PDDL.

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

### Utilizzo del Convertitore

Per avviare il convertitore, eseguire:
```bash
python3 CONVERTER/converter.py
```

Il convertitore:
1. Legge il file Prolog di input (`small_kb_hl.pl` o quello specificato)
2. Converte le definizioni Prolog in costrutti Unified Planning
3. Genera il codice Python equivalente
4. Crea i file PDDL corrispondenti, nella cartella **RESULTS/**:
   - `converter_pddl_result_domain.pddl`
<<<<<<< Updated upstream
   - `converter_pddl_result_problem.pddl`
=======
   - `converter_pddl_result_problem.pddl`
>>>>>>> Stashed changes
