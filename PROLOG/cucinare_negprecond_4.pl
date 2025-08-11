% File sperimentale: cucinare_negprecond_4.pl
% OBIETTIVO: Testare correlazione neg_precond vs Step 5 e Step 7
% BASELINE: cucinare.pl ha 1 precondizione negativa → questo file ha 4
% MANTIENE: Stesso numero oggetti (4), stesso numero azioni (3), stessa max_arity (4)
% NOTA: Dai dati, neg_precond ha correlazione NEGATIVA con Step 5 (-0.283) - interessante!

% Definizione di oggetti e tipi (INVARIATI)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Stato iniziale (esteso per supportare precondizioni negative aggiuntive)
init_state([
  % Stati originali
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stati per supportare precondizioni negative aggiuntive
  % (Questi predicati NON dovranno essere veri per alcune azioni)
  spento(led)
]).

% Stato goal (invariato)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo)
]).

% AZIONI: Stesso numero (3) ma con PRECONDIZIONI NEGATIVE AGGIUNTIVE

% Azione 1: cucina - PRECONDIZIONI NEGATIVE da 0 a 1
action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo)],
  [
    % Nuova precondizione negativa: non deve esserci fumo 
    fumo(Tavolo)  
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

% Azione 2: mangia - PRECONDIZIONI NEGATIVE da 0 a 1
action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona)],
  [
    % Nuova precondizione negativa: non deve essere distratto
    distratto(Persona)
  ],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Azione 3: sposta_qualsiasi - PRECONDIZIONI NEGATIVE da 1 a 2
action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [
    % Precondizione negativa originale (wildcard)
    su(_, Strumento),
    
    % Nuova precondizione negativa: non deve essere occupato
    occupato(Destinazione)
  ],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

% RISULTATO ATTESO:
% - Objects: 4 → 4 (invariato)
% - Actions: 3 → 3 (invariato)
% - Pos_precond: 7 → 7 (invariato)
% - Neg_precond: 1 → 4 (quadruplicato) ⭐
% - Wildcards: 1 → 1 (invariato, ma ci sono wildcards aggiuntive nelle neg_precond)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE dai dati di benchmark (CONTROINTUITIVE):
% - Step 5 (UP Code): potrebbe DIMINUIRE o aumentare poco (corr: -0.283) 🤔
% - Step 7 (Planning): dovrebbe rimanere simile (corr: -0.086)
% - Step 6 (PDDL): dovrebbe rimanere simile (corr: -0.113)
%
% IPOTESI: Le precondizioni negative potrebbero SEMPLIFICARE il planning
% perché riducono lo spazio di ricerca eliminando azioni inapplicabili.
% Questo potrebbe spiegare la correlazione negativa controintuitiva.
%
% LOGICA: Più precondizioni negative = più vincoli = meno combinazioni
% da esplorare nel planning = tempi potenzialmente più bassi