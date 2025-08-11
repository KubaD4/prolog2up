% File sperimentale: cucinare_negprecond_8.pl
% OBIETTIVO: Testare correlazione neg_precond vs Step 5 - MASSIMO
% BASELINE: cucinare.pl ha 1 precondizione negativa → questo file ha 8
% NOTA: Correlazione NEGATIVA (-0.283) - più neg_precond = meno tempo Step 5

% Definizione di oggetti e tipi (INVARIATI)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Stato iniziale (esteso per supportare molte precondizioni negative)
init_state([
  % Stati originali
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stati per supportare precondizioni negative multiple
  spento(led)
]).

% Stato goal (invariato)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo)
]).

% AZIONI: Stesso numero (3) ma con MOLTE PRECONDIZIONI NEGATIVE

% Azione 1: cucina - PRECONDIZIONI NEGATIVE da 0 a 3
action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo)],
  [
    % Precondizioni negative: NESSUNO di questi deve essere vero
    fumo(Tavolo),              % Non deve esserci fumo
    rotto(Strumento),          % Strumento non deve essere rotto
    occupato(Persona)          % Persona non deve essere occupata
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

% Azione 2: mangia - PRECONDIZIONI NEGATIVE da 0 a 3
action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona)],
  [
    % Precondizioni negative multiple
    distratto(Persona),        % Non deve essere distratto
    guasto(Cibo),              % Cibo non deve essere guasto
    disturbato(Persona)        % Non deve essere disturbato
  ],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Azione 3: sposta_qualsiasi - PRECONDIZIONI NEGATIVE da 1 a 2
% (Mantiene la wildcard originale + aggiunge altra)
action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [
    % Precondizioni negative originale + nuove
    su(_, Strumento),          % Wildcard originale
    bloccato(Destinazione)     % Destinazione non deve essere bloccata
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
% - Neg_precond: 1 → 8 (700% aumento) ⭐⭐⭐
% - Wildcards: 1 → 1 (ma ci sono più wildcards nelle neg_precond)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE (CONTROINTUITIVE!):
% - Step 5 (UP Code): potrebbe DIMINUIRE ulteriormente (corr: -0.283) 🤔
% - Step 7 (Planning): dovrebbe rimanere simile (corr: -0.086)
% - Step 6 (PDDL): dovrebbe rimanere simile (corr: -0.113)
%
% IPOTESI INTERESSANTE: Più precondizioni negative = più vincoli = 
% meno combinazioni da controllare = codice UP più semplice!
% Questo potrebbe spiegare la correlazione negativa controintuitiva.