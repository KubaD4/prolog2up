% EXTREME BENCHMARK 2: Multi-Step MEGA - 100% più step rispetto a multistep originale
% Target: 40+ step vs 20 originali
% Complessità: MASSIMA - Processo super articolato con controllo qualità

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Team di cuochi
cuoco(chef_mario).
cuoco(chef_luigi).
cuoco(sous_chef_anna).
cuoco(commis_paolo).

% Menu super complesso
cibo(lasagne_gourmet).
cibo(risotto_tartufo).
cibo(soufflé_cioccolato).
cibo(wellington_beef).
cibo(tarte_tatin).

% Strumenti professionali
strumento(pentola_chef).
strumento(padella_acciaio).
strumento(forno_convezione).
strumento(mixer_professionale).
strumento(coltello_giapponese).
strumento(frullatore_immersione).
strumento(bilancia_precisione).
strumento(termometro).
strumento(mandolina).

% Stazioni di lavoro
piano(stazione_prep).
piano(stazione_cottura).
piano(stazione_forno).
piano(stazione_servizio).
piano(stazione_decorazione).
piano(stazione_controllo).

% Ingredienti premium
ingrediente(farina_00).
ingrediente(acqua_filtrata).
ingrediente(uova_bio).
ingrediente(riso_carnaroli).
ingrediente(brodo_ossa).
ingrediente(burro_normandia).
ingrediente(zucchero_canna).
ingrediente(lievito_madre).
ingrediente(tartufo_nero).
ingrediente(cioccolato_70).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Menu non ancora iniziato
  non_iniziato(lasagne_gourmet), non_iniziato(risotto_tartufo), 
  non_iniziato(soufflé_cioccolato), non_iniziato(wellington_beef), non_iniziato(tarte_tatin),
  
  % Ingredienti disponibili
  disponibile_ingrediente(farina_00), disponibile_ingrediente(acqua_filtrata), 
  disponibile_ingrediente(uova_bio), disponibile_ingrediente(riso_carnaroli), 
  disponibile_ingrediente(brodo_ossa), disponibile_ingrediente(burro_normandia),
  disponibile_ingrediente(zucchero_canna), disponibile_ingrediente(lievito_madre),
  disponibile_ingrediente(tartufo_nero), disponibile_ingrediente(cioccolato_70),
  
  % Strumenti professionali liberi
  disponibile(pentola_chef), disponibile(padella_acciaio), disponibile(forno_convezione), 
  disponibile(mixer_professionale), disponibile(coltello_giapponese), 
  disponibile(frullatore_immersione), disponibile(bilancia_precisione),
  disponibile(termometro), disponibile(mandolina),
  
  % Team affamato e disponibile
  ha_fame(chef_mario), ha_fame(chef_luigi), ha_fame(sous_chef_anna), ha_fame(commis_paolo),
  available(chef_mario), available(chef_luigi), available(sous_chef_anna), available(commis_paolo),
  
  % Stazioni libere
  vuoto(stazione_prep), vuoto(stazione_cottura), vuoto(stazione_forno), 
  vuoto(stazione_servizio), vuoto(stazione_decorazione), vuoto(stazione_controllo)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Menu completo con certificazione qualità
  certificato_qualita(lasagne_gourmet), certificato_qualita(risotto_tartufo), 
  certificato_qualita(soufflé_cioccolato), certificato_qualita(wellington_beef), 
  certificato_qualita(tarte_tatin),
  
  % Team soddisfatto
  soddisfatto(chef_mario), soddisfatto(chef_luigi), 
  soddisfatto(sous_chef_anna), soddisfatto(commis_paolo),
  
  % Strumenti puliti e pronti
  disponibile(pentola_chef), disponibile(padella_acciaio), disponibile(forno_convezione),
  
  % Tutte le stazioni finali occupate
  pieno(stazione_servizio), pieno(stazione_decorazione), pieno(stazione_controllo)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions - SEQUENZA OBBLIGATORIA A 8 FASI CON CONTROLLI QUALITÀ
%%%%%%%%%%%%%%%%%%%%%%%

% FASE 1A: Pianificare ricetta (arity 3)
action(pianifica_ricetta(Cuoco, Cibo, Piano),
  [non_iniziato(Cibo), available(Cuoco), vuoto(Piano)],
  [pianificando(_, Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(non_iniziato(Cibo)), del(available(Cuoco)), del(vuoto(Piano)),
    add(pianificando(Cuoco, Cibo, Piano))
  ]
).

% FASE 1B: Finire pianificazione (arity 3)
action(finisci_pianificazione(Cuoco, Cibo, Piano),
  [pianificando(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(pianificando(Cuoco, Cibo, Piano)),
    add(pianificato(Cibo)), add(available(Cuoco)), add(vuoto(Piano))
  ]
).

% FASE 2A: Preparare ingredienti (arity 5)
action(prepara_ingredienti(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [pianificato(Cibo), disponibile_ingrediente(Ingrediente), available(Cuoco), 
   disponibile(Strumento), vuoto(Piano)],
  [preparando(_, Cibo, _, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(pianificato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano))
  ]
).

% FASE 2B: Finire preparazione ingredienti (arity 5)
action(finisci_preparazione(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(preparando(Cuoco, Cibo, Ingrediente, Strumento, Piano)),
    add(ingredienti_pronti(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 3A: Controllo qualità ingredienti (arity 4)
action(controlla_ingredienti(Cuoco, Cibo, Strumento, Piano),
  [ingredienti_pronti(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [controllando_ingredienti(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(ingredienti_pronti(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(controllando_ingredienti(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 3B: Finire controllo ingredienti (arity 4)
action(approva_ingredienti(Cuoco, Cibo, Strumento, Piano),
  [controllando_ingredienti(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(controllando_ingredienti(Cuoco, Cibo, Strumento, Piano)),
    add(ingredienti_approvati(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 4A: Impastare/mescolare (arity 4)
action(impasta(Cuoco, Cibo, Strumento, Piano),
  [ingredienti_approvati(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [impastando(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(ingredienti_approvati(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(impastando(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 4B: Finire impasto (arity 4)
action(finisci_impasto(Cuoco, Cibo, Strumento, Piano),
  [impastando(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(impastando(Cuoco, Cibo, Strumento, Piano)),
    add(impasto_pronto(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 5A: Controllo qualità impasto (arity 4)
action(controlla_impasto(Cuoco, Cibo, Strumento, Piano),
  [impasto_pronto(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [controllando_impasto(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(impasto_pronto(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(controllando_impasto(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 5B: Approvare impasto (arity 4)
action(approva_impasto(Cuoco, Cibo, Strumento, Piano),
  [controllando_impasto(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(controllando_impasto(Cuoco, Cibo, Strumento, Piano)),
    add(impasto_approvato(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 6A: Cucinare (arity 4)
action(cuocere(Cuoco, Cibo, Strumento, Piano),
  [impasto_approvato(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [cucinando(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(impasto_approvato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(cucinando(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 6B: Finire cottura (arity 4)
action(finisci_cottura(Cuoco, Cibo, Strumento, Piano),
  [cucinando(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(cucinando(Cuoco, Cibo, Strumento, Piano)),
    add(cotto_base(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 7A: Controllo cottura (arity 4)
action(controlla_cottura(Cuoco, Cibo, Strumento, Piano),
  [cotto_base(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [controllando_cottura(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(cotto_base(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(controllando_cottura(Cuoco, Cibo, Strumento, Piano))
  ]
).

% FASE 7B: Approvare cottura (arity 4)
action(approva_cottura(Cuoco, Cibo, Strumento, Piano),
  [controllando_cottura(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(controllando_cottura(Cuoco, Cibo, Strumento, Piano)),
    add(cottura_approvata(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 8A: Decorazione finale (arity 3)
action(decora_finale(Cuoco, Cibo, Piano),
  [cottura_approvata(Cibo), available(Cuoco), vuoto(Piano)],
  [decorando_finale(_, Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(cottura_approvata(Cibo)), del(available(Cuoco)), del(vuoto(Piano)),
    add(decorando_finale(Cuoco, Cibo, Piano))
  ]
).

% FASE 8B: Finire decorazione (arity 3)
action(finisci_decorazione_finale(Cuoco, Cibo, Piano),
  [decorando_finale(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(decorando_finale(Cuoco, Cibo, Piano)),
    add(decorato_finale(Cibo)), add(available(Cuoco)), add(pieno(Piano))
  ]
).

% FASE 9A: Controllo qualità finale (arity 3)
action(controllo_qualita_finale(Cuoco, Cibo, Piano),
  [decorato_finale(Cibo), available(Cuoco), pieno(Piano)],
  [controllando_finale(_, Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(decorato_finale(Cibo)), del(available(Cuoco)),
    add(controllando_finale(Cuoco, Cibo, Piano))
  ]
).

% FASE 9B: Certificazione qualità (arity 3)
action(certifica_qualita(Cuoco, Cibo, Piano),
  [controllando_finale(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(controllando_finale(Cuoco, Cibo, Piano)),
    add(certificato_qualita(Cibo)), add(available(Cuoco))
  ]
).

% Mangiare (solo con certificazione) (arity 2)
action(mangia(Persona, Cibo),
  [certificato_qualita(Cibo), ha_fame(Persona), available(Persona)],
  [cucinando(Persona, _, _, _), preparando(Persona, _, _, _, _), 
   impastando(Persona, _, _, _), decorando_finale(Persona, _, _), 
   controllando_ingredienti(Persona, _, _, _), controllando_impasto(Persona, _, _, _),
   controllando_cottura(Persona, _, _, _), controllando_finale(Persona, _, _)],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% CARATTERISTICHE MEGA:
% ✓ 18 FASI (9 fasi × 2 sub-step) per ogni piatto
% ✓ 5 piatti × 18 fasi = 90 azioni principali + mangiare = ~94+ azioni totali  
% ✓ Stati intermedi: non_iniziato → pianificato → ingredienti_pronti → ingredienti_approvati → impasto_pronto → impasto_approvato → cotto_base → cottura_approvata → decorato_finale → certificato_qualita
% ✓ Controlli qualità tripli: ingredienti, impasto, cottura finale
% ✓ TARGET: 40+ step vs 20 del multistep originale (+100%)
% ✓ Ogni fase ha precondizioni negative per evitare conflitti
% ✓ Sistema di certificazione qualità rigoroso