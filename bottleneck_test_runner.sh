#!/bin/bash
# Script per testare progressivamente i bottleneck
# Esegue i 4 test in sequenza e misura i tempi

echo "🔍 ANALISI BOTTLENECK: cucinare.pl vs kb_hl.pl"
echo "=============================================="
echo

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzione per misurare tempo e successo
run_test() {
    local test_name="$1"
    local test_file="$2"
    local description="$3"
    
    echo -e "${BLUE}TEST: $test_name${NC}"
    echo "File: $test_file"
    echo "Descrizione: $description"
    echo "----------------------------------------"
    
    # Controlla se il file esiste
    if [[ ! -f "$test_file" ]]; then
        echo -e "${RED}❌ File non trovato: $test_file${NC}"
        echo
        return 1
    fi
    
    # Misura tempo di esecuzione
    start_time=$(date +%s.%N)
    
    # Esegui conversione con timeout
    timeout 300 python3 CONVERTER/orchestrator.py "$test_file" --solve --verbose > "test_output_${test_name}.log" 2>&1
    exit_code=$?
    
    end_time=$(date +%s.%N)
    execution_time=$(echo "$end_time - $start_time" | bc)
    
    # Analizza risultato
    if [[ $exit_code -eq 0 ]]; then
        echo -e "${GREEN}✅ SUCCESSO${NC}"
        
        # Estrai timing dal log se disponibile
        if grep -q "Total execution time:" "test_output_${test_name}.log"; then
            detailed_time=$(grep "Total execution time:" "test_output_${test_name}.log" | awk '{print $4}')
            echo -e "⏱️  Tempo dettagliato: ${GREEN}${detailed_time}${NC}"
        fi
        
        # Verifica se ha trovato una soluzione
        if grep -q "Planning successful" "test_output_${test_name}.log"; then
            echo -e "🎯 Pianificazione: ${GREEN}SUCCESSO${NC}"
        else
            echo -e "🎯 Pianificazione: ${YELLOW}N/A o FALLITA${NC}"
        fi
        
    elif [[ $exit_code -eq 124 ]]; then
        echo -e "${RED}⏰ TIMEOUT (>300s)${NC}"
    else
        echo -e "${RED}❌ FALLITO (exit code: $exit_code)${NC}"
        
        # Mostra errori se presenti
        if [[ -f "test_output_${test_name}.log" ]]; then
            echo "Ultimi errori:"
            tail -n 5 "test_output_${test_name}.log" | sed 's/^/  /'
        fi
    fi
    
    echo -e "⏱️  Tempo totale: ${YELLOW}${execution_time}s${NC}"
    echo
    
    # Salva risultato per confronto finale
    echo "$test_name,$execution_time,$exit_code" >> bottleneck_results.csv
}

# Inizializza file risultati
echo "test_name,execution_time,exit_code" > bottleneck_results.csv

echo "Iniziando test progressivi dei bottleneck..."
echo "Ogni test introduce nuovi elementi che potrebbero rallentare il sistema."
echo

# TEST BASELINE: cucinare.pl originale
run_test "baseline" "PROLOG/cucinare.pl" "File originale semplice (2 azioni, nessuna coordinata)"

# TEST 1: Coordinate numeriche
run_test "coordinates" "PROLOG/cucinare_bottleneck_1.pl" "Aggiunge coordinate numeriche at_pos(obj,X,Y)"

# TEST 2: Azioni split + stati intermedi  
run_test "split_actions" "PROLOG/cucinare_bottleneck_2.pl" "Aggiunge azioni start/end + stati intermedi"

# TEST 3: Precondizioni negative complesse
run_test "complex_negatives" "PROLOG/cucinare_bottleneck_3.pl" "Aggiunge precondizioni negative complesse"

# TEST FINALE: kb_hl.pl originale
run_test "kb_hl_original" "PROLOG/kb_hl.pl" "File originale kb_hl.pl (mondo dei blocchi completo)"

echo "=============================================="
echo -e "${BLUE}📊 RIASSUNTO RISULTATI${NC}"
echo "=============================================="

# Analizza risultati
if [[ -f "bottleneck_results.csv" ]]; then
    echo "Test completati. Analisi tempi:"
    echo
    
    # Header tabella
    printf "%-20s %-15s %-10s\n" "TEST" "TEMPO (s)" "STATUS"
    printf "%-20s %-15s %-10s\n" "----" "--------" "------" 
    
    # Leggi risultati
    while IFS=',' read -r test_name execution_time exit_code; do
        if [[ "$test_name" != "test_name" ]]; then  # Skip header
            
            # Status
            if [[ $exit_code -eq 0 ]]; then
                status="${GREEN}OK${NC}"
            elif [[ $exit_code -eq 124 ]]; then
                status="${RED}TIMEOUT${NC}"
                execution_time=">300"
            else
                status="${RED}FAILED${NC}"
            fi
            
            # Formato tempo
            if [[ "$execution_time" =~ ^[0-9]+\.?[0-9]*$ ]] && [[ $(echo "$execution_time > 60" | bc -l) -eq 1 ]]; then
                time_color="${RED}"
            elif [[ "$execution_time" =~ ^[0-9]+\.?[0-9]*$ ]] && [[ $(echo "$execution_time > 10" | bc -l) -eq 1 ]]; then
                time_color="${YELLOW}"
            else
                time_color="${GREEN}"
            fi
            
            printf "%-20s ${time_color}%-15s${NC} %-20s\n" "$test_name" "$execution_time" "$status"
        fi
    done < bottleneck_results.csv
    
    echo
    echo -e "${YELLOW}💡 INTERPRETAZIONE RISULTATI:${NC}"
    echo
    echo "• Se 'coordinates' >> 'baseline': Le coordinate numeriche sono il bottleneck"
    echo "• Se 'split_actions' >> 'coordinates': Le azioni split sono il bottleneck"  
    echo "• Se 'complex_negatives' >> 'split_actions': Le precondizioni negative sono il bottleneck"
    echo "• 'kb_hl_original' dovrebbe essere il più lento di tutti"
    echo
    echo -e "${BLUE}📁 File di log salvati:${NC}"
    ls -la test_output_*.log 2>/dev/null || echo "Nessun file di log generato"
    
else
    echo -e "${RED}❌ Errore: file risultati non generato${NC}"
fi

echo
echo -e "${GREEN}✅ Analisi bottleneck completata!${NC}"
echo "Controlla i file di log per dettagli specifici su eventuali errori."