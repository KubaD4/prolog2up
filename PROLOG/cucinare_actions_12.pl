% File sperimentale: cucinare_actions_12.pl - VERSIONE FINALE CORRETTA
% OBIETTIVO: Testare correlazione actions vs Step 5 (UP Code Generation) - MASSIMO
% BASELINE: cucinare.pl ha 3 azioni → questo file ha 12 azioni (quadruplo)
% MANTIENE: Stesso numero oggetti (4), stessa struttura logica
% FIX: Usa oggetti "attivo/inattivo" invece di fluenti problematici

% Definizione di oggetti e tipi (ESTESI con stati)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Oggetti per stati sistema
stato(attivo).
stato(inattivo).

% Stato iniziale (esteso per supportare tutte le 12 azioni)
init_state([
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  accesa(led),
  
  % ✅ CORRETTO: Fluenti con oggetti definiti
  temperatura_alta(inattivo),    % Per azioni di controllo temperatura
  timer_attivo(inattivo),        % Per azioni con timer
  modalita_eco(inattivo),        % Per azioni avanzate
  sistema_acceso(attivo)         % Per azioni di sistema
]).

% Stato goal (esteso per dimostrare l'uso di più azioni possibili)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo),
  spenta(led),
  
  % ✅ CORRETTO: Goal con oggetti definiti
  temperatura_alta(attivo),
  timer_attivo(attivo),
  modalita_eco(attivo),
  sistema_acceso(inattivo)
]).

% AZIONI: Quadruplicate da 3 a 12 (4 gruppi da 3 azioni)

% === GRUPPO 1: AZIONI BASE (identiche a cucinare.pl) ===

action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

% === GRUPPO 2: CONTROLLO ILLUMINAZIONE ===

action(accendi_luce(Persona, Illuminazione),
  [spenta(Illuminazione)],
  [],
  [],
  [cuoco(Persona), luce(Illuminazione)],
  [
    del(spenta(Illuminazione)),
    add(accesa(Illuminazione))
  ]
).

action(spegni_luce(Persona, Illuminazione),
  [accesa(Illuminazione)],
  [],
  [],
  [cuoco(Persona), luce(Illuminazione)],
  [
    del(accesa(Illuminazione)),
    add(spenta(Illuminazione))
  ]
).

action(regola_intensita_luce(Persona, Illuminazione),
  [accesa(Illuminazione)],
  [],
  [],
  [cuoco(Persona), luce(Illuminazione)],
  [
    add(intensita_regolata(Illuminazione))
  ]
).

% === GRUPPO 3: CONTROLLO TEMPERATURA ===

action(aumenta_temperatura(Persona, Strumento),
  [disponibile(Strumento), temperatura_alta(inattivo)],  % ✅ CORRETTO
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(temperatura_alta(inattivo)),                      % ✅ CORRETTO
    add(temperatura_alta(attivo))                         % ✅ CORRETTO
  ]
).

action(diminuisci_temperatura(Persona, Strumento),
  [disponibile(Strumento), temperatura_alta(attivo)],    % ✅ CORRETTO
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(temperatura_alta(attivo)),                        % ✅ CORRETTO
    add(temperatura_alta(inattivo))                       % ✅ CORRETTO
  ]
).

action(avvia_timer(Persona, Strumento),
  [disponibile(Strumento), timer_attivo(inattivo)],      % ✅ CORRETTO
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(timer_attivo(inattivo)),                          % ✅ CORRETTO
    add(timer_attivo(attivo))                             % ✅ CORRETTO
  ]
).

% === GRUPPO 4: CONTROLLO SISTEMA AVANZATO ===

action(attiva_modalita_eco(Persona, Strumento),
  [disponibile(Strumento), modalita_eco(inattivo)],      % ✅ CORRETTO
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(modalita_eco(inattivo)),                          % ✅ CORRETTO
    add(modalita_eco(attivo))                             % ✅ CORRETTO
  ]
).

action(disattiva_modalita_eco(Persona, Strumento),
  [disponibile(Strumento), modalita_eco(attivo)],        % ✅ CORRETTO
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(modalita_eco(attivo)),                            % ✅ CORRETTO
    add(modalita_eco(inattivo))                           % ✅ CORRETTO
  ]
).

action(spegni_sistema(Persona, Strumento),
  [disponibile(Strumento), sistema_acceso(attivo)],      % ✅ CORRETTO
  [],
  [],
  [cuoco(Persona), strumento(Strumento)],
  [
    del(sistema_acceso(attivo)),                          % ✅ CORRETTO
    add(sistema_acceso(inattivo))                         % ✅ CORRETTO
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 6 (aggiunto 'attivo' e 'inattivo')
% - Actions: 3 → 12 (quadruplo) ⭐⭐⭐
% - Pos_precond: 7 → ~28 (quadruplo con le nuove azioni)
% - Neg_precond: 1 → 1 (invariato, solo sposta_qualsiasi ha wildcard)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE:
% - Step 5 (UP Code): dovrebbe aumentare molto significativamente
% - Step 7 (Planning): dovrebbe aumentare moderatamente
% - Questo è il test MASSIMO per la correlazione actions vs Step 5

% PIANO DI SOLUZIONE MINIMO (esempi):
% 1. cucina(mario, pasta, pentola, tavolo)
% 2. mangia(mario, pasta)
% 3. spegni_luce(mario, led) 
% 4. aumenta_temperatura(mario, pentola)
% 5. avvia_timer(mario, pentola)
% 6. attiva_modalita_eco(mario, pentola)
% 7. spegni_sistema(mario, pentola)