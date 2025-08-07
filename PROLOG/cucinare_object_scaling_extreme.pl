% EXTREME BENCHMARK 3: Object Scaling EXTREME - Molti più oggetti rispetto all'originale
% Target: Testare il limite di scaling con 3x più oggetti
% Complessità: ESTREMA - Scaling bottleneck massimo

%%%%%%%%%%%%%%%%%%%%%%%
% kb - MASSIVO SCALING
%%%%%%%%%%%%%%%%%%%%%%%

% TEAM ESTESO - 8 cuochi (era ~3)
cuoco(head_chef_mario).
cuoco(sous_chef_luigi).
cuoco(chef_de_partie_anna).
cuoco(commis_chef_paolo).
cuoco(pastry_chef_giulia).
cuoco(sauce_chef_marco).
cuoco(grill_chef_sara).
cuoco(prep_cook_luca).

% MENU ESTESO - 12 piatti (era ~4)
cibo(antipasto_misto).
cibo(carpaccio_manzo).
cibo(risotto_porcini).
cibo(pasta_carbonara).
cibo(lasagne_bolognese).
cibo(osso_buco).
cibo(branzino_crosta).
cibo(agnello_rosmarino).
cibo(contorno_verdure).
cibo(tiramisu_casa).
cibo(panna_cotta).
cibo(gelato_pistacchio).

% STRUMENTI PROFESSIONALI - 20 strumenti (era ~7)
strumento(pentola_acciaio_20l).
strumento(pentola_alluminio_15l).
strumento(padella_antiaderente_28cm).
strumento(padella_ferro_32cm).
strumento(wok_carbonato).
strumento(forno_convezione_grande).
strumento(forno_pizza_pietra).
strumento(forno_vapore).
strumento(mixer_planetario_10l).
strumento(mixer_immersione_prof).
strumento(frullatore_alta_potenza).
strumento(robot_cucina_multifunzione).
strumento(coltello_santoku_18cm).
strumento(coltello_filetto_15cm).
strumento(mandolina_professionale).
strumento(bilancia_precisione_5kg).
strumento(termometro_digitale).
strumento(affettatrice_elettrica).
strumento(tritacarne_elettrico).
strumento(impastatrice_spirale).

% POSTAZIONI LAVORO - 15 postazioni (era ~6)
piano(stazione_antipasti).
piano(stazione_primi).
piano(stazione_secondi).
piano(stazione_contorni).
piano(stazione_dolci).
piano(stazione_preparazione_1).
piano(stazione_preparazione_2).
piano(stazione_preparazione_3).
piano(stazione_cottura_1).
piano(stazione_cottura_2).
piano(stazione_cottura_3).
piano(stazione_forno_1).
piano(stazione_forno_2).
piano(stazione_servizio_1).
piano(stazione_servizio_2).

% INGREDIENTI PREMIUM - 25 ingredienti (era ~10)
ingrediente(farina_manitoba).
ingrediente(farina_00_caputo).
ingrediente(semola_grano_duro).
ingrediente(acqua_san_pellegrino).
ingrediente(sale_rosa_himalaya).
ingrediente(uova_bio_categoria_a).
ingrediente(burro_panna_centrifuga).
ingrediente(parmigiano_24_mesi).
ingrediente(pecorino_romano_dop).
ingrediente(guanciale_amatriciano).
ingrediente(pomodori_san_marzano).
ingrediente(basilico_genovese).
ingrediente(olio_extravergine_taggiasco).
ingrediente(riso_carnaroli_acquerello).
ingrediente(funghi_porcini_secchi).
ingrediente(tartufo_nero_norcia).
ingrediente(manzo_chianina_igp).
ingrediente(agnello_abruzzese).
ingrediente(branzino_mediterraneo).
ingrediente(gamberi_rossi_mazara).
ingrediente(mascarpone_lombardo).
ingrediente(savoiardi_piemonte).
ingrediente(pistacchi_sicilia_dop).
ingrediente(cioccolato_modica_igp).
ingrediente(vino_marsala_dop).

%%%%%%%%%%%%%%%%%%%%%%%
% init - STATO INIZIALE MASSIVO
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Tutti i piatti da preparare
  non_preparato(antipasto_misto), non_preparato(carpaccio_manzo), 
  non_preparato(risotto_porcini), non_preparato(pasta_carbonara),
  non_preparato(lasagne_bolognese), non_preparato(osso_buco),
  non_preparato(branzino_crosta), non_preparato(agnello_rosmarino),
  non_preparato(contorno_verdure), non_preparato(tiramisu_casa),
  non_preparato(panna_cotta), non_preparato(gelato_pistacchio),
  
  % Tutti gli ingredienti disponibili
  disponibile_ingrediente(farina_manitoba), disponibile_ingrediente(farina_00_caputo), 
  disponibile_ingrediente(semola_grano_duro), disponibile_ingrediente(acqua_san_pellegrino),
  disponibile_ingrediente(sale_rosa_himalaya), disponibile_ingrediente(uova_bio_categoria_a),
  disponibile_ingrediente(burro_panna_centrifuga), disponibile_ingrediente(parmigiano_24_mesi),
  disponibile_ingrediente(pecorino_romano_dop), disponibile_ingrediente(guanciale_amatriciano),
  disponibile_ingrediente(pomodori_san_marzano), disponibile_ingrediente(basilico_genovese),
  disponibile_ingrediente(olio_extravergine_taggiasco), disponibile_ingrediente(riso_carnaroli_acquerello),
  disponibile_ingrediente(funghi_porcini_secchi), disponibile_ingrediente(tartufo_nero_norcia),
  disponibile_ingrediente(manzo_chianina_igp), disponibile_ingrediente(agnello_abruzzese),
  disponibile_ingrediente(branzino_mediterraneo), disponibile_ingrediente(gamberi_rossi_mazara),
  disponibile_ingrediente(mascarpone_lombardo), disponibile_ingrediente(savoiardi_piemonte),
  disponibile_ingrediente(pistacchi_sicilia_dop), disponibile_ingrediente(cioccolato_modica_igp),
  disponibile_ingrediente(vino_marsala_dop),
  
  % Tutti gli strumenti disponibili
  disponibile(pentola_acciaio_20l), disponibile(pentola_alluminio_15l),
  disponibile(padella_antiaderente_28cm), disponibile(padella_ferro_32cm),
  disponibile(wok_carbonato), disponibile(forno_convezione_grande),
  disponibile(forno_pizza_pietra), disponibile(forno_vapore),
  disponibile(mixer_planetario_10l), disponibile(mixer_immersione_prof),
  disponibile(frullatore_alta_potenza), disponibile(robot_cucina_multifunzione),
  disponibile(coltello_santoku_18cm), disponibile(coltello_filetto_15cm),
  disponibile(mandolina_professionale), disponibile(bilancia_precisione_5kg),
  disponibile(termometro_digitale), disponibile(affettatrice_elettrica),
  disponibile(tritacarne_elettrico), disponibile(impastatrice_spirale),
  
  % Tutti i cuochi affamati e disponibili
  ha_fame(head_chef_mario), ha_fame(sous_chef_luigi), ha_fame(chef_de_partie_anna), 
  ha_fame(commis_chef_paolo), ha_fame(pastry_chef_giulia), ha_fame(sauce_chef_marco),
  ha_fame(grill_chef_sara), ha_fame(prep_cook_luca),
  available(head_chef_mario), available(sous_chef_luigi), available(chef_de_partie_anna), 
  available(commis_chef_paolo), available(pastry_chef_giulia), available(sauce_chef_marco),
  available(grill_chef_sara), available(prep_cook_luca),
  
  % Tutte le postazioni libere
  vuoto(stazione_antipasti), vuoto(stazione_primi), vuoto(stazione_secondi),
  vuoto(stazione_contorni), vuoto(stazione_dolci), vuoto(stazione_preparazione_1),
  vuoto(stazione_preparazione_2), vuoto(stazione_preparazione_3), vuoto(stazione_cottura_1),
  vuoto(stazione_cottura_2), vuoto(stazione_cottura_3), vuoto(stazione_forno_1),
  vuoto(stazione_forno_2), vuoto(stazione_servizio_1), vuoto(stazione_servizio_2)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal - OBIETTIVI MASSICCI
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutti i 12 piatti completati e serviti
  servito_premium(antipasto_misto), servito_premium(carpaccio_manzo), 
  servito_premium(risotto_porcini), servito_premium(pasta_carbonara),
  servito_premium(lasagne_bolognese), servito_premium(osso_buco),
  servito_premium(branzino_crosta), servito_premium(agnello_rosmarino),
  servito_premium(contorno_verdure), servito_premium(tiramisu_casa),
  servito_premium(panna_cotta), servito_premium(gelato_pistacchio),
  
  % Tutti gli 8 cuochi soddisfatti
  soddisfatto(head_chef_mario), soddisfatto(sous_chef_luigi), 
  soddisfatto(chef_de_partie_anna), soddisfatto(commis_chef_paolo), 
  soddisfatto(pastry_chef_giulia), soddisfatto(sauce_chef_marco),
  soddisfatto(grill_chef_sara), soddisfatto(prep_cook_luca),
  
  % Almeno 10 strumenti tornati disponibili
  disponibile(pentola_acciaio_20l), disponibile(pentola_alluminio_15l),
  disponibile(padella_antiaderente_28cm), disponibile(padella_ferro_32cm),
  disponibile(wok_carbonato), disponibile(forno_convezione_grande),
  disponibile(mixer_planetario_10l), disponibile(robot_cucina_multifunzione),
  disponibile(coltello_santoku_18cm), disponibile(bilancia_precisione_5kg),
  
  % Tutte le stazioni di servizio piene
  pieno(stazione_servizio_1), pieno(stazione_servizio_2),
  pieno(stazione_antipasti), pieno(stazione_primi), pieno(stazione_secondi)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions - PROCESSO SEMPLIFICATO MA CON MASSIVE COMBINAZIONI
%%%%%%%%%%%%%%%%%%%%%%%

% Preparare piatto specializzato (arity 5)
action(prepara_piatto_specializzato(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [non_preparato(Cibo), disponibile_ingrediente(Ingrediente), available(Cuoco), 
   disponibile(Strumento), vuoto(Piano)],
  [preparando_specializzato(_, Cibo, _, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(non_preparato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(preparando_specializzato(Cuoco, Cibo, Ingrediente, Strumento, Piano))
  ]
).

% Finire preparazione specializzata (arity 5)
action(finisci_preparazione_specializzata(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [preparando_specializzato(Cuoco, Cibo, Ingrediente, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(preparando_specializzato(Cuoco, Cibo, Ingrediente, Strumento, Piano)),
    add(preparato_specializzato(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% Cucinare premium (arity 4)
action(cucina_premium(Cuoco, Cibo, Strumento, Piano),
  [preparato_specializzato(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  [cucinando_premium(_, Cibo, _, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(preparato_specializzato(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(cucinando_premium(Cuoco, Cibo, Strumento, Piano))
  ]
).

% Finire cottura premium (arity 4)
action(finisci_cottura_premium(Cuoco, Cibo, Strumento, Piano),
  [cucinando_premium(Cuoco, Cibo, Strumento, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(cucinando_premium(Cuoco, Cibo, Strumento, Piano)),
    add(cotto_premium(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% Servire premium (arity 3)
action(servi_premium(Cuoco, Cibo, Piano),
  [cotto_premium(Cibo), available(Cuoco), vuoto(Piano)],
  [servendo_premium(_, Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(cotto_premium(Cibo)), del(available(Cuoco)), del(vuoto(Piano)),
    add(servendo_premium(Cuoco, Cibo, Piano))
  ]
).

% Finire servizio premium (arity 3)
action(finisci_servizio_premium(Cuoco, Cibo, Piano),
  [servendo_premium(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(servendo_premium(Cuoco, Cibo, Piano)),
    add(servito_premium(Cibo)), add(available(Cuoco)), add(pieno(Piano))
  ]
).

% Mangiare premium (arity 2)
action(mangia_premium(Persona, Cibo),
  [servito_premium(Cibo), ha_fame(Persona), available(Persona)],
  [preparando_specializzato(Persona, _, _, _, _), cucinando_premium(Persona, _, _, _), 
   servendo_premium(Persona, _, _)],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Pulire strumento professionale (arity 2)
action(pulisci_strumento_professionale(Cuoco, Strumento),
  [available(Cuoco)],
  [in_uso_professionale(Strumento), preparando_specializzato(_, _, _, Strumento, _), 
   cucinando_premium(_, _, Strumento, _)],
  [],
  [cuoco(Cuoco), strumento(Strumento)],
  [
    del(available(Cuoco)),
    add(pulito_professionale(Strumento)), add(available(Cuoco))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% CARATTERISTICHE EXTREME SCALING:
% ✓ 8 cuochi (vs ~3 originali) = +167% objects
% ✓ 12 piatti (vs ~4 originali) = +200% cibo objects  
% ✓ 20 strumenti (vs ~7 originali) = +186% strumento objects
% ✓ 15 postazioni (vs ~6 originali) = +150% piano objects
% ✓ 25 ingredienti (vs ~10 originali) = +150% ingrediente objects
% ✓ TOTALE: ~80 objects vs ~30 originali = +167% SCALING TOTALE
% ✓ Processo: 6 fasi per piatto × 12 piatti = 72+ azioni principali
% ✓ Combinazioni: 8×12×25×20×15 = 72,000,000 possibili combinazioni iniziali
% ✓ TARGET: Stressare il limite di scaling degli oggetti per pianificazione
% ✓ Piano minimo stimato: ~60+ step (5 step × 12 piatti)
% ✓ Ogni oggetto ha più interdipendenze e vincoli