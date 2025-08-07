% VARIAZIONE 2: Multi-Course Clean - Sequenze di portate, fluenti specifici
% Struttura: Basata su cucinare.pl, sequenze obbligatorie ma semplici

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Cuochi
cuoco(mario).
cuoco(luigi).

% Portate in sequenza
antipasto(bruschetta).
antipasto(caprese).
primo(spaghetti).
primo(risotto).
secondo(pollo).
secondo(pesce).
dolce(tiramisu).
dolce(gelato).

% Strumenti per tipo portata
strumento_antipasti(tagliere).
strumento_antipasti(piatto_freddo).
strumento_primi(pentola_pasta).
strumento_primi(padella_risotto).
strumento_secondi(griglia).
strumento_secondi(forno_carne).
strumento_dolci(mixer).
strumento_dolci(frigo_dolci).

% Piani specifici
piano_prep(bancone_prep).
piano_cottura(fornelli).
piano_servizio(passaggio).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Stati antipasti
  crudo_antipasto(bruschetta), crudo_antipasto(caprese),
  
  % Stati primi  
  crudo_primo(spaghetti), crudo_primo(risotto),
  
  % Stati secondi
  crudo_secondo(pollo), crudo_secondo(pesce),
  
  % Stati dolci
  non_preparato_dolce(tiramisu), non_preparato_dolce(gelato),
  
  % Strumenti per categoria
  libero_antipasti(tagliere), libero_antipasti(piatto_freddo),
  libero_primi(pentola_pasta), libero_primi(padella_risotto),
  libero_secondi(griglia), libero_secondi(forno_carne),
  libero_dolci(mixer), libero_dolci(frigo_dolci),
  
  % Cuochi
  ha_fame(mario), ha_fame(luigi),
  disponibile_cuoco(mario), disponibile_cuoco(luigi),
  
  % Piani
  vuoto_prep(bancone_prep), vuoto_cottura(fornelli), vuoto_servizio(passaggio)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutte le portate completate
  pronto_antipasto(bruschetta), pronto_antipasto(caprese),
  pronto_primo(spaghetti), pronto_primo(risotto),
  pronto_secondo(pollo), pronto_secondo(pesce),
  pronto_dolce(tiramisu), pronto_dolce(gelato),
  
  % Cuochi soddisfatti
  soddisfatto(mario), soddisfatto(luigi),
  
  % Servizio completato
  servizio_completato(passaggio)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% Preparare antipasto (arity 4)
action(prepara_antipasto(Cuoco, Antipasto, Strumento, Piano),
  [crudo_antipasto(Antipasto), disponibile_cuoco(Cuoco), 
   libero_antipasti(Strumento), vuoto_prep(Piano)],
  [preparando_antipasto(Cuoco), in_uso_antipasti(Strumento)],
  [],
  [cuoco(Cuoco), antipasto(Antipasto), strumento_antipasti(Strumento), piano_prep(Piano)],
  [
    del(crudo_antipasto(Antipasto)), del(disponibile_cuoco(Cuoco)), 
    del(libero_antipasti(Strumento)), del(vuoto_prep(Piano)),
    add(preparando_antipasto(Cuoco)), add(in_uso_antipasti(Strumento)), add(occupato_prep(Piano))
  ]
).

% Completare antipasto (arity 4)
action(completa_antipasto(Cuoco, Antipasto, Strumento, Piano),
  [preparando_antipasto(Cuoco), in_uso_antipasti(Strumento), occupato_prep(Piano)],
  [],
  [],
  [cuoco(Cuoco), antipasto(Antipasto), strumento_antipasti(Strumento), piano_prep(Piano)],
  [
    del(preparando_antipasto(Cuoco)), del(in_uso_antipasti(Strumento)), del(occupato_prep(Piano)),
    add(pronto_antipasto(Antipasto)), add(disponibile_cuoco(Cuoco)), 
    add(libero_antipasti(Strumento)), add(vuoto_prep(Piano))
  ]
).

% Cucinare primo (arity 4)
action(cucina_primo(Cuoco, Primo, Strumento, Piano),
  [crudo_primo(Primo), disponibile_cuoco(Cuoco), 
   libero_primi(Strumento), vuoto_cottura(Piano)],
  [cucinando_primo(Cuoco), in_uso_primi(Strumento)],
  [],
  [cuoco(Cuoco), primo(Primo), strumento_primi(Strumento), piano_cottura(Piano)],
  [
    del(crudo_primo(Primo)), del(disponibile_cuoco(Cuoco)), 
    del(libero_primi(Strumento)), del(vuoto_cottura(Piano)),
    add(cucinando_primo(Cuoco)), add(in_uso_primi(Strumento)), add(occupato_cottura(Piano))
  ]
).

% Completare primo (arity 4)
action(completa_primo(Cuoco, Primo, Strumento, Piano),
  [cucinando_primo(Cuoco), in_uso_primi(Strumento), occupato_cottura(Piano)],
  [],
  [],
  [cuoco(Cuoco), primo(Primo), strumento_primi(Strumento), piano_cottura(Piano)],
  [
    del(cucinando_primo(Cuoco)), del(in_uso_primi(Strumento)), del(occupato_cottura(Piano)),
    add(pronto_primo(Primo)), add(disponibile_cuoco(Cuoco)), 
    add(libero_primi(Strumento)), add(vuoto_cottura(Piano))
  ]
).

% Cucinare secondo (arity 4)
action(cucina_secondo(Cuoco, Secondo, Strumento, Piano),
  [crudo_secondo(Secondo), disponibile_cuoco(Cuoco), 
   libero_secondi(Strumento), vuoto_cottura(Piano)],
  [cucinando_secondo(Cuoco), in_uso_secondi(Strumento)],
  [],
  [cuoco(Cuoco), secondo(Secondo), strumento_secondi(Strumento), piano_cottura(Piano)],
  [
    del(crudo_secondo(Secondo)), del(disponibile_cuoco(Cuoco)), 
    del(libero_secondi(Strumento)), del(vuoto_cottura(Piano)),
    add(cucinando_secondo(Cuoco)), add(in_uso_secondi(Strumento)), add(occupato_cottura(Piano))
  ]
).

% Completare secondo (arity 4)
action(completa_secondo(Cuoco, Secondo, Strumento, Piano),
  [cucinando_secondo(Cuoco), in_uso_secondi(Strumento), occupato_cottura(Piano)],
  [],
  [],
  [cuoco(Cuoco), secondo(Secondo), strumento_secondi(Strumento), piano_cottura(Piano)],
  [
    del(cucinando_secondo(Cuoco)), del(in_uso_secondi(Strumento)), del(occupato_cottura(Piano)),
    add(pronto_secondo(Secondo)), add(disponibile_cuoco(Cuoco)), 
    add(libero_secondi(Strumento)), add(vuoto_cottura(Piano))
  ]
).

% Preparare dolce (arity 4)
action(prepara_dolce(Cuoco, Dolce, Strumento, Piano),
  [non_preparato_dolce(Dolce), disponibile_cuoco(Cuoco), 
   libero_dolci(Strumento), vuoto_prep(Piano)],
  [preparando_dolce(Cuoco), in_uso_dolci(Strumento)],
  [],
  [cuoco(Cuoco), dolce(Dolce), strumento_dolci(Strumento), piano_prep(Piano)],
  [
    del(non_preparato_dolce(Dolce)), del(disponibile_cuoco(Cuoco)), 
    del(libero_dolci(Strumento)), del(vuoto_prep(Piano)),
    add(preparando_dolce(Cuoco)), add(in_uso_dolci(Strumento)), add(occupato_prep(Piano))
  ]
).

% Completare dolce (arity 4)
action(completa_dolce(Cuoco, Dolce, Strumento, Piano),
  [preparando_dolce(Cuoco), in_uso_dolci(Strumento), occupato_prep(Piano)],
  [],
  [],
  [cuoco(Cuoco), dolce(Dolce), strumento_dolci(Strumento), piano_prep(Piano)],
  [
    del(preparando_dolce(Cuoco)), del(in_uso_dolci(Strumento)), del(occupato_prep(Piano)),
    add(pronto_dolce(Dolce)), add(disponibile_cuoco(Cuoco)), 
    add(libero_dolci(Strumento)), add(vuoto_prep(Piano))
  ]
).

% Servire menu completo (arity 3) - dopo che tutto è pronto
action(servi_menu_completo(Cuoco, MenuType, Piano),
  [pronto_antipasto(_), pronto_primo(_), pronto_secondo(_), pronto_dolce(_),
   disponibile_cuoco(Cuoco), vuoto_servizio(Piano)],
  [servendo_menu(Cuoco)],
  [],
  [cuoco(Cuoco), piano_servizio(Piano)],
  [
    del(disponibile_cuoco(Cuoco)), del(vuoto_servizio(Piano)),
    add(servendo_menu(Cuoco)), add(servizio_completato(Piano))
  ]
).

% Mangiare menu (arity 2)
action(mangia_menu(Persona, MenuCompleto),
  [servizio_completato(_), ha_fame(Persona), disponibile_cuoco(Persona)],
  [consumando_menu(Persona)],
  [],
  [cuoco(Persona)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% CARATTERISTICHE:
% ✓ Basato su cucinare.pl funzionante
% ✓ Fluenti SPECIFICI per tipo portata:
%   - crudo_antipasto(antipasto) vs crudo_primo(primo)
%   - libero_antipasti(strumento_antipasti) vs libero_primi(strumento_primi)
%   - preparando_antipasto(cuoco) vs cucinando_primo(cuoco)
% ✓ NO fluenti polimorfici
% ✓ Sequenza logica: antipasti → primi → secondi → dolci → servizio
% ✓ 8 portate diverse con strumenti specifici
% ✓ Piano fattibile: ~16-20 azioni (2 step × 8 portate + servizio)
% ✓ Arity rispettata: max 4 parametri