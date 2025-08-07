% EXTREME BENCHMARK 1: Multi-Step Extreme - 50% più step rispetto a multistep originale
% Target: 30 step vs 20 originali
% Complessità: ESTREMA - Processo articolato con più fasi obbligatorie

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Cuochi
cuoco(mario).
cuoco(luigi).
cuoco(chef_anna).

% Cibi che richiedono preparazione super complessa
cibo(pasta_fatta_casa).
cibo(risotto_speciale).
cibo(torta_wedding).
cibo(soufflé).

% Strumenti specializzati + nuovi
strumento(pentola).
strumento(padella).
strumento(forno).
strumento(mixer).
strumento(coltello).
strumento(frullatore).
strumento(bilancia).

% Piani di lavoro estesi
piano(tavolo_prep).
piano(tavolo_cottura).
piano(tavolo_servizio).
piano(tavolo_decorazione).

% Ingredienti base + extra
ingrediente(farina).
ingrediente(acqua).
ingrediente(uova).
ingrediente(riso).
ingrediente(brodo).
ingrediente(burro).
ingrediente(zucchero).
ingrediente(lievito).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Cibi non ancora preparati
  non_preparato(pasta_fatta_casa), non_preparato(risotto_speciale), 
  non_preparato(torta_wedding), non_preparato(soufflé),
  
  % Ingredienti disponibili
  disponibile_ingrediente(farina), disponibile_ingrediente(acqua), 
  disponibile_ingrediente(uova), disponibile_ingrediente(riso), 
  disponibile_ingrediente(brodo), disponibile_ingrediente(burro),
  disponibile_ingrediente(zucchero), disponibile_ingrediente(lievito),
  
  % Strumenti liberi
  disponibile(pentola), disponibile(padella), disponibile(forno), 
  disponibile(mixer), disponibile(coltello), disponibile(frullatore), disponibile(bilancia),
  
  % Cuochi affamati e disponibili
  ha_fame(mario), ha_fame(luigi), ha_fame(chef_anna),
  available(mario), available(luigi), available(chef_anna),
  
  % Piani liberi
  vuoto(tavolo_prep), vuoto(tavolo_cottura), vuoto(tavolo_servizio), vuoto(tavolo_decorazione)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutti i piatti completati e decorati
  servito_decorato(pasta_fatta_casa), servito_decorato(risotto_speciale), 
  servito_decorato(torta_wedding), servito_decorato(soufflé),
  
  % Cuochi soddisfatti
  soddisfatto(mario), soddisfatto(luigi), soddisfatto(chef_anna),
  
  % Strumenti puliti e disponibili
  disponibile(pentola), disponibile(padella), disponibile(forno), disponibile(mixer),
  
  % Tutti i tavoli di servizio pieni
  pieno(tavolo_servizio), pieno(tavolo_decorazione)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions - SEQUENZA OBBLIGATORIA A 6 FASI
%%%%%%%%%%%%%%%%%%%%%%%

% FASE 1: Preparare ingredienti (arity 5)
action(prepara_ingredienti(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [non_preparato(Cibo), disponibile_ingrediente(Ingrediente), available(Cuoco), 
   disponibile(Strumento), vuoto(Piano)],
  [preparando(_, Cibo, _, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(non_preparato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano))
  ]
).

% FASE 2: Finire preparazione - diventa "preparato_base" (arity 5)
action(finisci_preparazione(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano)),
    add(preparato_base(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 3: Impastare/mescolare - diventa "impastato" (arity 4)
action(impasta(Cuoco, Cibo, Strumento, Piano),
  [preparato_base(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [impastando(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(preparato_base(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(impastando(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 4: Finire impasto - diventa "impastato" (arity 4)
action(finisci_impasto(Cuoco, Cibo, Strumento, Piano),
  [impastando(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(impastando(Cuoco, Cibo, Strumento, Piano)),
    add(impastato(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 5: Cucinare vero e proprio - diventa "cotto" (arity 4)
action(cuocere(Cuoco, Cibo, Strumento, Piano),
  [impastato(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [cucinando(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(impastato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(cucinando(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 6: Finire cottura - diventa "cotto" (arity 4)
action(finisci_cottura(Cuoco, Cibo, Strumento, Piano),
  [cucinando(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(cucinando(Cuoco, Cibo, Strumento, Piano)),
    add(cotto(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 7: Iniziare decorazione - diventa "decorando" (arity 3)
action(inizia_decorazione(Cuoco, Cibo, Piano),
  [cotto(Cibo), available(Cuoco), vuoto(Piano)],
  [decorando(_, Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(cotto(Cibo)), del(available(Cuoco)), del(vuoto(Piano)),
    add(decorando(Cuoco, Cibo, Piano))
  ]
).

% FASE 8: Finire decorazione - diventa "decorato" (arity 3)
action(finisci_decorazione(Cuoco, Cibo, Piano),
  [decorando(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(decorando(Cuoco, Cibo, Piano)),
    add(decorato(Cibo)), add(available(Cuoco)), add(pieno(Piano))
  ]
).

% FASE 9: Servire con decorazione finale - diventa "servito_decorato" (arity 3)
action(servi_decorato(Cuoco, Cibo, Piano),
  [decorato(Cibo), available(Cuoco), pieno(Piano)],
  [servendo(_, Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(decorato(Cibo)), del(available(Cuoco)),
    add(servendo(Cuoco, Cibo, Piano))
  ]
).

% FASE 10: Finire servizio finale (arity 3)
action(finisci_servizio(Cuoco, Cibo, Piano),
  [servendo(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(servendo(Cuoco, Cibo, Piano)),
    add(servito_decorato(Cibo)), add(available(Cuoco))
  ]
).

% Mangiare (solo alla fine) (arity 2)
action(mangia(Persona, Cibo),
  [servito_decorato(Cibo), ha_fame(Persona), available(Persona)],
  [cucinando(Persona, _, _, _), preparando(Persona, _, _, _, _), 
   impastando(Persona, _, _, _), decorando(Persona, _, _), servendo(Persona, _, _)],
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
   cucinando(_, _, Strumento, _), impastando(_, _, Strumento, _)],
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
% CARATTERISTICHE EXTREME:
% ✓ 10 FASI SEQUENTIAL OBBLIGATORIE per ogni piatto (vs 6 originali)
% ✓ 4 piatti × 10 fasi = 40 azioni principali + mangiare = ~43+ azioni totali
% ✓ Stati intermedi: preparando → preparato_base → impastando → impastato → cucinando → cotto → decorando → decorato → servendo → servito_decorato
% ✓ Precondizioni negative per evitare conflitti multipli
% ✓ Dipendenze ferree: non puoi saltare nessuna fase
% ✓ Arity rispettata: max 5 parametri
% ✓ TARGET: 30+ step vs 20 del multistep originale (+50%)