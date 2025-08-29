# Prolog2UP: Prolog to Unified Planning Converter

An automated pipeline for translating Prolog knowledge bases to Unified Planning models with PDDL export capabilities. This name-agnostic translation framework implements a three-phase pipeline (extraction, JSON intermediate representation, UP code generation) for converting logic programming knowledge bases into solver-agnostic planning models.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Configuration](#configuration)
- [Examples](#examples)
- [Project Structure](#project-structure)

## Overview

**Prolog2UP** bridges the gap between logic programming (Prolog) and modern automated planning by providing:

- **Name-agnostic translation**: No hard-coded predicate/action names or domain-specific rules
- **Lossless intermediate representation**: JSON format preserves structural information
- **Solver-agnostic output**: Generates both Unified Planning models and PDDL files
- **Deterministic code generation**: Identical inputs produce identical outputs
- **Performance monitoring**: Detailed timing analysis for each pipeline stage
- **Extensible architecture**: JSON layer enables future back-ends without modifying extraction

## Architecture

The conversion pipeline consists of 7 steps:

```
Prolog File → Extraction → JSON → UP Code → PDDL Files → [Planning]
```

1. **Extraction**: Parse Prolog knowledge base structure
2. **Signature Analysis**: Analyze fluent signatures and types  
3. **JSON Conversion**: Create intermediate representation
4. **JSON Storage**: Save structured knowledge
5. **UP Code Generation**: Generate Python Unified Planning code
6. **PDDL Export**: Execute generated code to create PDDL files
7. **Planning** (optional): Solve generated planning problems

## Installation

### Prerequisites

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **SWI-Prolog** (required for PySwip)
   ```bash
   # macOS (using Homebrew)
   brew install swi-prolog
   
   # Ubuntu/Debian  
   sudo apt-get install swi-prolog
   
   # Windows: Download from https://www.swi-prolog.org/download/stable
   ```

3. **Fast Downward** (optional, for enhanced planning)
   ```bash
   git clone https://github.com/aibasel/downward.git
   cd downward
   ./build.py
   cd ..
   ```

### Setup

```bash
# 1. Clone and navigate to repository
cd path/to/prolog2up

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r CONVERTER/requirements.txt

# 4. Verify installation
python3 -c "import unified_planning; from pyswip import Prolog; print('Setup successful!')"
```

### Dependencies

Core dependencies (from `requirements.txt`):
```
unified-planning[engines]  # Planning framework and engines
pyswip                     # Python-SWI-Prolog interface  
prettytable               # Output formatting
```

## Usage

### Basic Conversion

Convert a Prolog knowledge base to PDDL format:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl
```

### Conversion with Planning

Convert and automatically solve the planning problem:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve
```

### Detailed Output

Get verbose debug information and detailed analysis:

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --detailed
```

### Plan Display Options

Control how planning results are shown:

```bash
# Show complete plans (all steps)
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve --show-full-plans

# Hide plan steps (only status and timing)  
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve --hide-plans
```

### Combined Options

```bash
python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve --detailed --show-full-plans
```

## Output Structure

Each run creates a timestamped directory in `RESULTS/CONVERTER/`:

```
RESULTS/CONVERTER/cucinare_0830_1430/
├── extracted_knowledge.json     # Structured knowledge representation
├── generated_up.py              # Python Unified Planning code  
├── generated_domain.pddl        # PDDL domain file
├── generated_problem.pddl       # PDDL problem file
└── planning_results.txt         # Planning results (if --solve used)
```

### File Descriptions

| File | Purpose |
|------|---------|
| `extracted_knowledge.json` | Intermediate representation of Prolog KB structure |
| `generated_up.py` | Self-contained Python script using Unified Planning API |
| `generated_domain.pddl` | Standard PDDL domain compatible with external planners |
| `generated_problem.pddl` | PDDL problem instance with objects, initial state, goals |
| `planning_results.txt` | Comprehensive planning results with timing and comparison |

## Configuration

### Algorithm Sets

The system supports multiple planning algorithm configurations via `CONVERTER/planner_config.py`:

- **basic**: `lazy_greedy`, `astar_ff` (fast, reliable)
- **fast**: Adds `eager_greedy`, `wastar` (balanced speed/quality)  
- **comprehensive**: Full algorithm suite (thorough evaluation)
- **research**: Extended set including experimental algorithms
- **debug**: Minimal set for testing

### Timing and Performance

The orchestrator provides detailed performance analysis:

```
Total execution time: 1.296 seconds
  Step 1 (Extraction): 0.009s
  Step 2 (Signatures): 0.000s  
  Step 3-4 (JSON): 0.001s
  Step 5 (UP Code): 0.495s
  Step 6 (PDDL): 0.635s
  Step 7 (Planning): 0.157s
```

## Examples

### Sample Output

```bash
$ python3 CONVERTER/orchestrator.py PROLOG/cucinare.pl --solve

=== Prolog to Unified Planning Conversion Pipeline ===
Input file: PROLOG/cucinare.pl
Output directory: RESULTS/CONVERTER/cucinare_0830_1430
SOLVER: enabled
DETAILS: disabled, use --detailed to enable

Step 1: Extracting knowledge from Prolog file...
  Completed in 0.008 seconds

Step 2: Analyzing fluent signatures...  
  Completed in 0.001 seconds

[... additional steps ...]

Step 7: Running PDDL solver...
  - Planning successful! Results saved to planning_results.txt
  - Planning results:
    * fast_downward_lazy_greedy:
      STATUS: Plan found (2 steps)
      Step  1: (cucina mario pasta pentola tavolo)
      Step  2: (mangia mario pasta)

=== Conversion Pipeline Completed Successfully ===
Total execution time: 1.296 seconds
```

### Prolog Knowledge Base Format

The system expects Prolog files with the following structure:

```prolog
% Objects and types
object(mario, person).
object(pasta, food).
object(pentola, utensil).

% Initial state facts  
at_initial_state(hungry(mario)).
at_initial_state(available(pasta)).

% Goal specification
goal(satisfied(mario)).

% Action definitions
action(cucina(Person, Food, Utensil, Place),
       [hungry(Person), available(Food), clean(Utensil)],  % Preconditions
       [cooked(Food), dirty(Utensil)],                     % Add effects
       [available(Food), clean(Utensil)]).                 % Delete effects
```

## Project Structure

```
.
├── CONVERTER/                    # Main conversion system
│   ├── orchestrator.py          # Main entry point and coordination
│   ├── prolog_extractor.py      # Prolog knowledge extraction
│   ├── kb_to_json.py            # JSON intermediate conversion
│   ├── prolog2up_V2.py          # UP code generation
│   ├── planner_config.py        # Algorithm configuration
│   └── requirements.txt         # Python dependencies
├── PROLOG/                      # Sample Prolog knowledge bases
│   ├── cucinare.pl             # Cooking domain example
│   ├── entrare.pl              # Room entry example  
│   └── medic.pl                # Medical domain example
├── PDDL/                       # Legacy PDDL utilities
│   └── run_plan.py             # PDDL solver wrapper
├── UNIFIED_PLANNING/           # UP framework examples
├── RESULTS/                    # Generated outputs
│   └── CONVERTER/              # Timestamped conversion results
└── README.md                   # This file
```

## Advanced Usage

### Working with Complex Domains

For knowledge bases with complex structure, use detailed mode to inspect the conversion process:

```bash
python3 CONVERTER/orchestrator.py PROLOG/complex_domain.pl --detailed --solve
```

### Batch Processing

Process multiple knowledge bases:

```bash
for kb in PROLOG/*.pl; do
    echo "Processing $kb..."
    python3 CONVERTER/orchestrator.py "$kb" --solve
done
```

### Integration with External Tools

The generated PDDL files are compatible with standard planners:

```bash
# Use with external planner
./external_planner generated_domain.pddl generated_problem.pddl

# Import generated UP code in Python
from generated_up import create_problem, solve_problem
problem = create_problem()
result = solve_problem(problem)
```

## Troubleshooting

### Common Issues

1. **SWI-Prolog not found**: Ensure SWI-Prolog is installed and in PATH
2. **Import errors**: Verify all dependencies are installed in virtual environment
3. **Planning failures**: Check PDDL files are valid using `--detailed` flag
4. **Timeout errors**: Large problems may need increased timeout settings

### Debug Mode

Use `--detailed` flag for comprehensive debugging information:

```bash
python3 CONVERTER/orchestrator.py PROLOG/problem.pl --detailed --solve
```

This provides:
- Step-by-step progress with DEBUG messages
- Detailed fluent analysis
- Type constraint validation  
- Complete planner output
- Performance bottleneck identification

---

**Repository**: https://github.com/KubaD4/prolog2up  
**License**: Apache 2.0  
**Requirements**: Python 3.8+, SWI-Prolog, Unified Planning framework
