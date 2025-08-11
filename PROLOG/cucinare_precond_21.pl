% File sperimentale: cucinare_precond_21.pl
% OBIETTIVO: Testare correlazione pos_precond vs Step 5 (UP Code) - TRIPLO
% BASELINE: cucinare.pl ha 7 precondizioni positive → questo file ha 21 (triplo)
% MANTIENE: Stesso numero oggetti (4), stesso numero azioni (3), stessa max_arity (4)

% Definizione di oggetti e tipi (INVARIATI)
cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

% Stato iniziale (esteso per supportare precondizioni molto estese)
init_state([
  % Stati originali
  crudo(pasta),
  disponibile(pentola),
  ha_fame(mario),
  vuoto(tavolo),
  
  % Stati aggiuntivi per precondizioni extra (MOLTI controlli)
  pulito(tavolo),
  asciutto(pentola),
  fresco(pasta),
  sicuro(mario),
  accesa(led),
  stabile(tavolo),
  utilizzabile(pentola),
  
  % Controlli di qualità aggiuntivi
  temperatura_ok(tavolo),
  pressione_ok(pentola),
  umidita_ok(pasta),
  energia_ok(mario),
  luminosita_ok(led),
  livello_ok(tavolo),
  calibrato(pentola)
]).

% Stato goal (invariato nella struttura principale)
goal_state([
  cotto(pasta),
  soddisfatto(mario),
  pieno(tavolo)
]).

% AZIONI: Stesso numero (3) ma con PRECONDIZIONI TRIPLICATE

% Azione 1: cucina - PRECONDIZIONI da 3 a 9
action(cucina(Persona, Cibo, Strumento, Tavolo),
  [
    % Precondizioni originali (3)
    crudo(Cibo), 
    disponibile(Strumento), 
    vuoto(Tavolo),
    
    % Precondizioni aggiuntive gruppo 1 (3) - sicurezza base
    pulito(Tavolo),
    asciutto(Strumento),
    fresco(Cibo),
    
    % Precondizioni aggiuntive gruppo 2 (3) - controlli avanzati
    temperatura_ok(Tavolo),
    pressione_ok(Strumento),
    energia_ok(Persona)
  ],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    del(pulito(Tavolo)),        % Il piano si sporca cucinando
    del(asciutto(Strumento)),   % Lo strumento si bagna
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

% Azione 2: mangia - PRECONDIZIONI da 2 a 6  
action(mangia(Persona, Cibo),
  [
    % Precondizioni originali (2)
    cotto(Cibo), 
    ha_fame(Persona),
    
    % Precondizioni aggiuntive gruppo 1 (2) - sicurezza
    sicuro(Persona),
    fresco(Cibo),
    
    % Precondizioni aggiuntive gruppo 2 (2) - controlli qualità
    umidita_ok(Cibo),
    energia_ok(Persona)
  ],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Azione 3: sposta_qualsiasi - PRECONDIZIONI da 2 a 6
action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [
    % Precondizioni originali (2)
    disponibile(Strumento), 
    vuoto(Destinazione),
    
    % Precondizioni aggiuntive gruppo 1 (2) - stabilità
    stabile(Destinazione),
    utilizzabile(Strumento),
    
    % Precondizioni aggiuntive gruppo 2 (2) - controlli sistema
    livello_ok(Destinazione),
    calibrato(Strumento)
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
% - Pos_precond: 7 → 21 (200% aumento) ⭐⭐⭐
% - Neg_precond: 1 → 1 (invariato)
% - Wildcards: 1 → 1 (invariato)
% - Max_arity: 4 → 4 (invariato)
%
% CORRELAZIONI ATTESE dai dati di benchmark:
% - Step 5 (UP Code): dovrebbe aumentare significativamente vs precond_14
% - Step 7 (Planning): dovrebbe aumentare moderatamente
% - Molti più controlli nella generazione UP code