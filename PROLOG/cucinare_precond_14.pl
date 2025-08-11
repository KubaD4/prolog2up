% File sperimentale: cucinare_precond_14.pl
% OBIETTIVO: Testare correlazione pos_precond vs Step 5 (UP Code) e Step 7 (Planning)
% BASELINE: cucinare.pl ha 7 precondizioni positive → questo file ha 14 (doppio)
% MANTIENE: Stesso numero oggetti (4), stesso numero azioni (3), stessa max_arity (4)

% Definizione di oggetti e tipi (INVARIATI)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Stato iniziale (esteso per supportare precondizioni aggiuntive)
init_state([
  % Stati originali
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stati aggiuntivi per precondizioni extra
  pulito(tavolo),
  asciutto(pentola),
  fresco(pasta),
  sicuro(mario),
  accesa(led),
  stabile(tavolo),
  utilizzabile(pentola)
]).

% Stato goal (invariato nella struttura principale)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo)
]).

% AZIONI: Stesso numero (3) ma con PRECONDIZIONI RADDOPPIATE

% Azione 1: cucina - PRECONDIZIONI da 3 a 6
action(cucina(Persona, Cibo, Strumento, Tavolo),
  [
    % Precondizioni originali (3)
    crudo(Cibo), 
    disponibile(Strumento), 
    vuoto(Tavolo),
    
    % Precondizioni aggiuntive (3) - controlli di sicurezza e qualità
    pulito(Tavolo),
    asciutto(Strumento),
    fresco(Cibo)
  ],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    del(pulito(Tavolo)),        % Effetto: il piano si sporca cucinando
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

% Azione 2: mangia - PRECONDIZIONI da 2 a 4  
action(mangia(Persona, Cibo),
  [
    % Precondizioni originali (2)
    cotto(Cibo), 
    ha_fame(Persona),
    
    % Precondizioni aggiuntive (2) - controlli di sicurezza
    sicuro(Persona),
    fresco(Cibo)
  ],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Azione 3: sposta_qualsiasi - PRECONDIZIONI da 2 a 4
action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [
    % Precondizioni originali (2)
    disponibile(Strumento), 
    vuoto(Destinazione),
    
    % Precondizioni aggiuntive (2) - controlli di stabilità e sicurezza
    stabile(Destinazione),
    utilizzabile(Strumento)
  ],
  [su(_, Strumento)],  % Wildcard negativa invariata
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
% - Pos_precond: 7 → 14 (100% aumento) ⭐
% - Neg_precond: 1 → 1 (invariato)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
% - Avg_arity: 3.0 → 3.0 (invariato)
%
% CORRELAZIONI ATTESE dai dati di benchmark:
% - Step 5 (UP Code): dovrebbe aumentare moderatamente (corr: 0.444)
% - Step 7 (Planning): dovrebbe aumentare leggermente (corr: 0.357)
% - Step 6 (PDDL): aumento minimo (correlazione bassa)
%
% LOGICA: Le precondizioni aggiuntive richiedono più controlli nella 
% generazione del codice UP e rendono più complesso il planning, ma non
% cambiano significativamente la struttura PDDL base