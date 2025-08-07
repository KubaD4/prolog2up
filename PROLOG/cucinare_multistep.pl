% VARIAZIONE 2: Multi-Step - Processo di cucina articolato
% Complessità: MEDIA - Sequenze obbligatorie di azioni

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Cuochi
cuoco(mario).
cuoco(luigi).

% Cibi che richiedono preparazione complessa
cibo(pasta).
cibo(risotto).
cibo(torta).

% Strumenti specializzati
strumento(pentola).
strumento(padella).
strumento(forno).
strumento(mixer).
strumento(coltello).

% Piani di lavoro
piano(tavolo_prep).
piano(tavolo_cottura).
piano(tavolo_servizio).

% Ingredienti base
ingrediente(farina).
ingrediente(acqua).
ingrediente(uova).
ingrediente(riso).
ingrediente(brodo).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Cibi non ancora preparati
  non_preparato(pasta), non_preparato(risotto), non_preparato(torta),
  
  % Ingredienti disponibili
  disponibile_ingrediente(farina), disponibile_ingrediente(acqua), 
  disponibile_ingrediente(uova), disponibile_ingrediente(riso), disponibile_ingrediente(brodo),
  
  % Strumenti liberi
  disponibile(pentola), disponibile(padella), disponibile(forno), 
  disponibile(mixer), disponibile(coltello),
  
  % Cuochi affamati e disponibili
  ha_fame(mario), ha_fame(luigi),
  available(mario), available(luigi),
  
  % Piani liberi
  vuoto(tavolo_prep), vuoto(tavolo_cottura), vuoto(tavolo_servizio)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutti i piatti completati e serviti
  servito(pasta), servito(risotto), servito(torta),
  
  % Cuochi soddisfatti
  soddisfatto(mario), soddisfatto(luigi),
  
  % Strumenti puliti e disponibili
  disponibile(pentola), disponibile(padella), disponibile(forno),
  
  % Almeno un tavolo di servizio pieno
  pieno(tavolo_servizio)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% FASE 1: Preparare ingredienti (arity 5)
action(prepara_ingredienti(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [non_preparato(Cibo), disponibile_ingrediente(Ingrediente), available(Cuoco), 
   disponibile(Strumento), vuoto(Piano)],
  [preparando(_, Cibo, _, _, _)],  % Solo una persona alla volta per cibo
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(non_preparato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano))
  ]
).

% FASE 2: Finire preparazione (arity 5)
action(finisci_preparazione(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano)),
    add(preparato(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 3: Iniziare cottura (arity 4)
action(inizia_cottura(Cuoco, Cibo, Strumento, Piano),
  [preparato(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [cucinando(_, Cibo, _, _), cucinando(Cuoco, _, _, _)], % Evita conflitti
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(preparato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(cucinando(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 4: Finire cottura (arity 4)  
action(finisci_cottura(Cuoco, Cibo, Strumento, Piano),
  [cucinando(Cuoco, Cibo, Strumento, Piano)],
  [servendo(_, Cibo, _)], % Non servire mentre si cucina
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(cucinando(Cuoco, Cibo, Strumento, Piano)),
    add(cotto(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 5: Servire piatto (arity 3)
action(servi_piatto(Cuoco, Cibo, Piano),
  [cotto(Cibo), available(Cuoco), vuoto(Piano)],
  [servendo(_, Cibo, _), servendo(Cuoco, _, _)], % Una persona, un piatto alla volta
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(cotto(Cibo)), del(available(Cuoco)), del(vuoto(Piano)),
    add(servendo(Cuoco, Cibo, Piano))
  ]
).

% FASE 6: Completare servizio (arity 3)
action(completa_servizio(Cuoco, Cibo, Piano),
  [servendo(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(servendo(Cuoco, Cibo, Piano)),
    add(servito(Cibo)), add(available(Cuoco)), add(pieno(Piano))
  ]
).

% Mangiare piatto servito (arity 2)
action(mangia(Persona, Cibo),
  [servito(Cibo), ha_fame(Persona), available(Persona)],
  [preparando(Persona, _, _, _, _), cucinando(Persona, _, _, _), servendo(Persona, _, _)],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Pulire strumento (arity 2)
action(pulisci_strumento(Cuoco, Strumento),
  [available(Cuoco)],
  [in_uso(Strumento), preparando(_, _, _, Strumento, _), 
   cucinando(_, _, Strumento, _), servendo(Cuoco, _, _)],
  [],
  [cuoco(Cuoco), strumento(Strumento)],
  [
    del(available(Cuoco)),
    add(pulito(Strumento)), add(available(Cuoco))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% CARATTERISTICHE:
% ✓ Processo multi-step obbligatorio: prep → cottura → servizio
% ✓ 6 fasi sequential per ogni piatto
% ✓ Stati intermedi: preparando, cucinando, servendo
% ✓ Precondizioni negative complesse per evitare conflitti
% ✓ Wildcard: preparando(_, Cibo, _, _, _) 
% ✓ Piano minimo: ~21 azioni (7 step × 3 piatti)
% ✓ Arity rispettata: max 5 parametri
% ✓ Dipendenze: non puoi cucinare prima di preparare