% File sperimentale: cucinare_arity_6.pl
% OBIETTIVO: Testare correlazione max_arity vs Step 7 (Planning)
% BASELINE: cucinare.pl ha max_arity=4 → questo file ha max_arity=6
% MANTIENE: Stesso numero oggetti (4), stesso numero azioni (3)

% Definizione di oggetti e tipi (INVARIATI)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Aggiunta di fluenti per supportare azioni con arietà più alta
temperatura(alta).
temperatura(bassa).

% Stato iniziale (esteso per supportare nuovi parametri)
init_state([
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  temperatura_ambiente(bassa)  % Nuovo stato per azioni con più parametri
]).

% Stato goal (esteso)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  temperatura_ambiente(alta)   % Goal che richiede azioni con arietà più alta
]).

% AZIONI: Stesso numero (3) ma con ARIETÀ AUMENTATA

% Azione 1: cucina_avanzata - ARIETÀ 6 (vs 4 originale)
% Aggiunge parametri per temperatura e controllo qualità
action(cucina_avanzata(Persona, Cibo, Strumento, Tavolo, Temp_iniziale, Temp_finale),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo), temperatura_ambiente(Temp_iniziale)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo), temperatura(Temp_iniziale), temperatura(Temp_finale)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    del(temperatura_ambiente(Temp_iniziale)),
    add(cotto(Cibo)),
    add(pieno(Tavolo)),
    add(temperatura_ambiente(Temp_finale))
  ]
).

% Azione 2: mangia_controllato - ARIETÀ 4 (mantenuta dal baseline per variazione)
action(mangia_controllato(Persona, Cibo, Luogo, Illuminazione),
  [cotto(Cibo), ha_fame(Persona), pieno(Luogo)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), piano(Luogo), luce(Illuminazione)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Azione 3: sposta_complesso - ARIETÀ 6 (vs arietà 3 della baseline)
% Versione più complessa di sposta_qualsiasi con controllo temperatura
action(sposta_complesso(Persona, Strumento, Origine, Destinazione, Temp_richiesta, Illuminazione),
  [disponibile(Strumento), vuoto(Destinazione), temperatura_ambiente(Temp_richiesta)],
  [su(_, Strumento)],  % Mantiene wildcard della baseline
  [],
  [cuoco(Persona), strumento(Strumento), piano(Origine), piano(Destinazione), temperatura(Temp_richiesta), luce(Illuminazione)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 4 (invariato)
% - Actions: 3 → 3 (invariato)
% - Pos_precond: 7 → ~10 (leggero aumento per controlli aggiuntivi)
% - Neg_precond: 1 → 1 (invariato, stesso wildcard)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 6 (aumento del 50%)
% - Avg_arity: 3.0 → ~5.3 (aumento significativo)
%
% CORRELAZIONI ATTESE dai dati di benchmark:
% - Step 7 (Planning): dovrebbe aumentare moderatamente (corr: 0.495)
% - Step 6 (PDDL): dovrebbe aumentare leggermente (corr: 0.338)
% - Step 5 (UP Code): dovrebbe aumentare leggermente (corr: 0.379)
% - Aumento della complessità del planning per via dei parametri extra

% NOTA TECNICA: L'aumento dell'arietà significa che il planner deve
% considerare più combinazioni di parametri, aumentando lo spazio di ricerca
% Questo dovrebbe essere evidente soprattutto nel Step 7 (Planning time)