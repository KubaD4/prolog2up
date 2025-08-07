% ULTIMATE STRESS TEST: Combinazione di TUTTI i fattori che rallentano il planner
% - Precondizioni negative complesse con wildcards
% - Processo multi-step con molte fasi sequenziali  
% - Scaling massiccio degli oggetti
% - Interdipendenze complesse tra azioni
% Target: Il file più difficile possibile che il converter possa ancora gestire

%%%%%%%%%%%%%%%%%%%%%%%
% kb - CONFIGURAZIONE ESTREMA
%%%%%%%%%%%%%%%%%%%%%%%

% BRIGADE COMPLETA - 6 cuochi specializzati
cuoco(executive_chef_mario).
cuoco(sous_chef_luigi).
cuoco(chef_de_partie_anna).
cuoco(commis_chef_paolo).
cuoco(pastry_chef_giulia).
cuoco(garde_manger_marco).

% MENU DEGUSTAZIONE - 8 piatti complessi
cibo(amuse_bouche_caviale).
cibo(crudo_ricciola_agrumi).
cibo(tortellini_brodo_cappone).
cibo(rombo_crosta_sale).
cibo(agnello_alle_erbe).
cibo(pre_dessert_sorbetto).
cibo(soufflé_grand_marnier).
cibo(piccola_pasticceria).

% STRUMENTI ALTA GAMMA - 15 strumenti specializzati
strumento(roner_sous_vide).
strumento(abbattitore_temperatura).
strumento(forno_combi_steam).
strumento(planetaria_20l).
strumento(pacojet_gelato).
strumento(gastrovac_concentratore).
strumento(affumicatore_freddo).
strumento(centrifuga_succhi).
strumento(tagliaverdure_robot).
strumento(slicer_professionale).
strumento(bilancia_grammo).
strumento(termocircolatore).
strumento(mixer_ultrasonico).
strumento(pressa_idraulica).
strumento(criocamera_azoto).

% POSTAZIONI SPECIALIZZATE - 12 stazioni
piano(stazione_garde_manger).
piano(stazione_chef_de_partie).
piano(stazione_saucier).
piano(stazione_poissonnier).
piano(stazione_rotisseur).
piano(stazione_patissier).
piano(stazione_plating_1).
piano(stazione_plating_2).
piano(stazione_pass_1).
piano(stazione_pass_2).
piano(stazione_lavaggio).
piano(stazione_expediting).

% INGREDIENTI PREMIUM - 20 ingredienti selezionati
ingrediente(caviale_ossetra).
ingrediente(ricciola_mediterraneo).
ingrediente(cappone_bresse).
ingrediente(rombo_selvaggio).
ingrediente(agnello_sisteron).
ingrediente(tartufo_alba_bianco).
ingrediente(olio_taggiasca_dop).
ingrediente(sale_guerande).
ingrediente(burro_beurre_échiré).
ingrediente(parmigiano_vacche_rosse).
ingrediente(aceto_balsamico_25anni).
ingrediente(miele_acacia_piemonte).
ingrediente(zafferano_abruzzo).
ingrediente(vaniglia_madagascar).
ingrediente(cioccolato_valrhona_70).
ingrediente(grand_marnier_cordon_rouge).
ingrediente(yuzu_giapponese).
ingrediente(finger_lime_australiano).
ingrediente(alga_kombu_hokkaido).
ingrediente(fleur_de_sel_camargue).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Menu da preparare
  non_iniziato(amuse_bouche_caviale), non_iniziato(crudo_ricciola_agrumi),
  non_iniziato(tortellini_brodo_cappone), non_iniziato(rombo_crosta_sale),
  non_iniziato(agnello_alle_erbe), non_iniziato(pre_dessert_sorbetto),
  non_iniziato(soufflé_grand_marnier), non_iniziato(piccola_pasticceria),
  
  % Ingredienti premium disponibili
  disponibile_ingrediente(caviale_ossetra), disponibile_ingrediente(ricciola_mediterraneo),
  disponibile_ingrediente(cappone_bresse), disponibile_ingrediente(rombo_selvaggio),
  disponibile_ingrediente(agnello_sisteron), disponibile_ingrediente(tartufo_alba_bianco),
  disponibile_ingrediente(olio_taggiasca_dop), disponibile_ingrediente(sale_guerande),
  disponibile_ingrediente(burro_beurre_échiré), disponibile_ingrediente(parmigiano_vacche_rosse),
  disponibile_ingrediente(aceto_balsamico_25anni), disponibile_ingrediente(miele_acacia_piemonte),
  disponibile_ingrediente(zafferano_abruzzo), disponibile_ingrediente(vaniglia_madagascar),
  disponibile_ingrediente(cioccolato_valrhona_70), disponibile_ingrediente(grand_marnier_cordon_rouge),
  disponibile_ingrediente(yuzu_giapponese), disponibile_ingrediente(finger_lime_australiano),
  disponibile_ingrediente(alga_kombu_hokkaido), disponibile_ingrediente(fleur_de_sel_camargue),
  
  % Strumenti haute cuisine disponibili
  disponibile(roner_sous_vide), disponibile(abbattitore_temperatura),
  disponibile(forno_combi_steam), disponibile(planetaria_20l),
  disponibile(pacojet_gelato), disponibile(gastrovac_concentratore),
  disponibile(affumicatore_freddo), disponibile(centrifuga_succhi),
  disponibile(tagliaverdure_robot), disponibile(slicer_professionale),
  disponibile(bilancia_grammo), disponibile(termocircolatore),
  disponibile(mixer_ultrasonico), disponibile(pressa_idraulica), disponibile(criocamera_azoto),
  
  % Brigade affamata e disponibile
  ha_fame(executive_chef_mario), ha_fame(sous_chef_luigi), ha_fame(chef_de_partie_anna),
  ha_fame(commis_chef_paolo), ha_fame(pastry_chef_giulia), ha_fame(garde_manger_marco),
  available(executive_chef_mario), available(sous_chef_luigi), available(chef_de_partie_anna),
  available(commis_chef_paolo), available(pastry_chef_giulia), available(garde_manger_marco),
  
  % Stazioni libere
  vuoto(stazione_garde_manger), vuoto(stazione_chef_de_partie), vuoto(stazione_saucier),
  vuoto(stazione_poissonnier), vuoto(stazione_rotisseur), vuoto(stazione_patissier),
  vuoto(stazione_plating_1), vuoto(stazione_plating_2), vuoto(stazione_pass_1),
  vuoto(stazione_pass_2), vuoto(stazione_lavaggio), vuoto(stazione_expediting)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Menu degustazione completato
  expedited(amuse_bouche_caviale), expedited(crudo_ricciola_agrumi),
  expedited(tortellini_brodo_cappone), expedited(rombo_crosta_sale),
  expedited(agnello_alle_erbe), expedited(pre_dessert_sorbetto),
  expedited(soufflé_grand_marnier), expedited(piccola_pasticceria),
  
  % Brigade soddisfatta
  soddisfatto(executive_chef_mario), soddisfatto(sous_chef_luigi),
  soddisfatto(chef_de_partie_anna), soddisfatto(commis_chef_paolo),
  soddisfatto(pastry_chef_giulia), soddisfatto(garde_manger_marco),
  
  % Stazioni finali operative
  pieno(stazione_pass_1), pieno(stazione_pass_2), pieno(stazione_expediting),
  
  % Strumenti chiave disponibili
  disponibile(roner_sous_vide), disponibile(forno_combi_steam), disponibile(pacojet_gelato)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions - PROCESSO ULTRA-COMPLESSO CON NEGATIVE PRECONDITIONS ESTREME
%%%%%%%%%%%%%%%%%%%%%%%

% FASE 1A: Mise en place (arity 5) + PRECONDIZIONI NEGATIVE COMPLESSE
action(mise_en_place(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [non_iniziato(Cibo), disponibile_ingrediente(Ingrediente), available(Cuoco), 
   disponibile(Strumento), vuoto(Piano)],
  % PRECONDIZIONI NEGATIVE COMPLESSE CON WILDCARD MULTIPLI
  [mise_en_place_in_corso(_, Cibo, _, _, _),              % Solo un chef per piatto
   mise_en_place_in_corso(Cuoco, _, _, _, _),             % Chef non occupato
   strumento_riservato(_, Strumento, _),                  % Strumento non riservato
   stazione_bloccata(_, Piano, _),                        % Stazione non bloccata  
   ingrediente_in_lavorazione(_, Ingrediente, _, _),      % Ingrediente non in uso
   conflitto_timing(Cuoco, _, _),                         % Nessun conflitto timing
   preparazione_simultanea(_, Cibo, _)],                  % No prep simultanee stesso piatto
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(non_iniziato(Cibo)), del(available(Cuoco)), del(disponibile(Strumento)), del(vuoto(Piano)),
    add(mise_en_place_in_corso(Cuoco, Cibo, Ingrediente, Strumento, Piano)),
    add(strumento_riservato(Cuoco, Strumento, Piano)), add(stazione_bloccata(Cuoco, Piano, Cibo))
  ]
).

% FASE 1B: Completare mise en place (arity 5)
action(completa_mise_en_place(Cuoco, Cibo, Ingrediente, Strumento, Piano),
  [mise_en_place_in_corso(Cuoco, Cibo, Ingrediente, Strumento, Piano),
   strumento_riservato(Cuoco, Strumento, Piano), stazione_bloccata(Cuoco, Piano, Cibo)],
  [interruzione_esterna(_, Cuoco, _), emergenza_cucina(_, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), ingrediente(Ingrediente), strumento(Strumento), piano(Piano)],
  [
    del(mise_en_place_in_corso(Cuoco, Cibo, Ingrediente, Strumento, Piano)),
    del(strumento_riservato(Cuoco, Strumento, Piano)), del(stazione_bloccata(Cuoco, Piano, Cibo)),
    add(mise_en_place_completa(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 2A: Preparazione base (arity 4) + PRECONDIZIONI NEGATIVE ESTREME
action(preparazione_base(Cuoco, Cibo, Strumento, Piano),
  [mise_en_place_completa(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  % WILDCARD PATTERNS COMPLESSI
  [preparazione_in_corso(_, Cibo, _, _),                  % Stesso piatto non in prep
   preparazione_in_corso(Cuoco, _, _, _),                 % Chef non occupato
   strumento_occupato(_, Strumento, _, _),                % Strumento libero
   stazione_impegnata(_, Piano, _, _),                    % Stazione libera
   conflitto_chef_stazione(Cuoco, Piano, _, _),          % Nessun conflitto chef-stazione
   timing_overlap(Cuoco, _, _, _),                        % Nessun overlap timing
   cross_contamination_risk(_, Cibo, _, _),               % Nessun rischio contaminazione
   sequenza_interrotta(_, Cibo, _, _)],                   % Sequenza non interrotta
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(mise_en_place_completa(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(preparazione_in_corso(Cuoco, Cibo, Strumento, Piano)),
    add(strumento_occupato(Cuoco, Strumento, Cibo, Piano))
  ]
).

% FASE 2B: Completare preparazione base (arity 4)
action(completa_preparazione_base(Cuoco, Cibo, Strumento, Piano),
  [preparazione_in_corso(Cuoco, Cibo, Strumento, Piano),
   strumento_occupato(Cuoco, Strumento, Cibo, Piano)],
  [interruzione_chef(_, Cuoco, _), strumento_guasto(Strumento, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(preparazione_in_corso(Cuoco, Cibo, Strumento, Piano)),
    del(strumento_occupato(Cuoco, Strumento, Cibo, Piano)),
    add(preparazione_base_completa(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 3A: Cottura specializzata (arity 4) + PRECONDIZIONI CRITICHE
action(cottura_specializzata(Cuoco, Cibo, Strumento, Piano),
  [preparazione_base_completa(Cibo), available(Cuoco), disponibile(Strumento), vuoto(Piano)],
  % PRECONDIZIONI NEGATIVE SUPER COMPLESSE
  [cottura_in_corso(_, Cibo, _, _),                       % Solo una cottura per piatto
   cottura_in_corso(Cuoco, _, _, _),                      % Chef non in cottura
   strumento_surriscaldato(Strumento, _, _),              % Strumento non surriscaldato
   stazione_vapori_attiva(_, Piano, _),                   % Nessun vapore interferente
   temperatura_instabile(_, Strumento, _),                % Temperatura stabile
   ordine_cottura_sbagliato(Cibo, _, _),                  % Ordine cottura corretto
   chef_skills_insufficienti(Cuoco, Cibo, _),            % Skills adeguate
   strumento_incompatibile(Strumento, Cibo, _),          % Strumento compatibile
   timing_service_conflicts(_, Cibo, _, _)],              % Nessun conflitto service
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(preparazione_base_completa(Cibo)), del(available(Cuoco)), 
    del(disponibile(Strumento)), del(vuoto(Piano)),
    add(cottura_in_corso(Cuoco, Cibo, Strumento, Piano)),
    add(stazione_vapori_attiva(Cuoco, Piano, Cibo))
  ]
).

% FASE 3B: Completare cottura specializzata (arity 4)
action(completa_cottura_specializzata(Cuoco, Cibo, Strumento, Piano),
  [cottura_in_corso(Cuoco, Cibo, Strumento, Piano),
   stazione_vapori_attiva(Cuoco, Piano, Cibo)],
  [overcooking_risk(Cibo, _, _), undercooking_detected(Cibo, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(cottura_in_corso(Cuoco, Cibo, Strumento, Piano)),
    del(stazione_vapori_attiva(Cuoco, Piano, Cibo)),
    add(cottura_completata(Cibo)), add(available(Cuoco)), 
    add(disponibile(Strumento)), add(vuoto(Piano))
  ]
).

% FASE 4A: Plating artistico (arity 3) + TIMING CRITICO
action(plating_artistico(Cuoco, Cibo, Piano),
  [cottura_completata(Cibo), available(Cuoco), vuoto(Piano)],
  % PRECONDIZIONI ULTRA-SPECIFICHE
  [plating_in_corso(_, Cibo, _),                          % Solo un plating per piatto
   plating_in_corso(Cuoco, _, _),                         % Chef non in plating
   piatto_temperatura_bassa(Cibo, _, _),                  % Temperatura piatto OK
   sauce_separata(_, Cibo, _),                            % Salsa non separata
   garnish_appassito(_, Cibo, _),                         % Guarnizione fresca
   plate_sporco(_, Piano, _),                             % Piatto pulito
   lighting_inadeguato(Piano, _, _),                      % Illuminazione OK
   hand_tremor_detected(Cuoco, _, _),                     % Mano ferma
   artistic_vision_unclear(Cuoco, Cibo, _)],              % Visione artistica chiara
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(cottura_completata(Cibo)), del(available(Cuoco)), del(vuoto(Piano)),
    add(plating_in_corso(Cuoco, Cibo, Piano)),
    add(piatto_temperatura_bassa(Cibo, Piano, Cuoco))
  ]
).

% FASE 4B: Completare plating (arity 3)
action(completa_plating_artistico(Cuoco, Cibo, Piano),
  [plating_in_corso(Cuoco, Cibo, Piano)],
  [aesthetic_failure(Cibo, _, _), final_touch_missing(Cibo, Cuoco, _)],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(plating_in_corso(Cuoco, Cibo, Piano)),
    add(plating_completato(Cibo)), add(available(Cuoco)), add(pieno(Piano))
  ]
).

% FASE 5A: Expediting finale (arity 3) + CONTROLLI QUALITÀ
action(expediting_finale(Cuoco, Cibo, Piano),
  [plating_completato(Cibo), available(Cuoco), pieno(Piano)],
  % CONTROLLI QUALITÀ ESTREMI
  [expediting_in_corso(_, Cibo, _),                       % Solo un expediting per piatto
   expediting_in_corso(Cuoco, _, _),                      % Chef non in expediting
   quality_standards_unmet(Cibo, _, _),                   % Standard qualità raggiunti
   temperature_out_of_range(Cibo, _, _),                  % Temperatura in range
   visual_defects_detected(Cibo, _, _),                   % Nessun difetto visivo
   service_timing_late(_, Cibo, _),                       % Timing service OK
   customer_allergies_risk(Cibo, _, _),                   % Nessun rischio allergie
   portion_size_incorrect(Cibo, _, _),                    % Porzione corretta
   chef_approval_pending(_, Cibo, _)],                    % Approvazione chef OK
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(plating_completato(Cibo)), del(available(Cuoco)),
    add(expediting_in_corso(Cuoco, Cibo, Piano))
  ]
).

% FASE 5B: Completare expediting (arity 3)
action(completa_expediting_finale(Cuoco, Cibo, Piano),
  [expediting_in_corso(Cuoco, Cibo, Piano)],
  [],
  [],
  [cuoco(Cuoco), cibo(Cibo), piano(Piano)],
  [
    del(expediting_in_corso(Cuoco, Cibo, Piano)),
    add(expedited(Cibo)), add(available(Cuoco))
  ]
).

% Mangiare haute cuisine (arity 2)
action(mangia_haute_cuisine(Chef, Cibo),
  [expedited(Cibo), ha_fame(Chef), available(Chef)],
  % PRECONDIZIONI FINALI ESTREME
  [mise_en_place_in_corso(Chef, _, _, _, _), preparazione_in_corso(Chef, _, _, _),
   cottura_in_corso(Chef, _, _, _), plating_in_corso(Chef, _, _), 
   expediting_in_corso(Chef, _, _), strumento_riservato(Chef, _, _),
   stazione_bloccata(Chef, _, _), conflitto_timing(Chef, _, _)],
  [],
  [cuoco(Chef), cibo(Cibo)],
  [
    del(ha_fame(Chef)),
    add(soddisfatto(Chef))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% ULTIMATE STRESS TEST CHARACTERISTICS:
% ✓ 6 cuochi × 8 piatti × 20 ingredienti × 15 strumenti × 12 stazioni = COMBINAZIONI MASSIVE
% ✓ 10 FASI PER PIATTO (5 fasi × 2 sub-step) con precondizioni negative ESTREME
% ✓ 60+ PRECONDIZIONI NEGATIVE UNICHE con pattern wildcard complessi
% ✓ 8 piatti × 10 fasi = 80+ azioni principali + mangiare = 86+ step totali
% ✓ Wildcard patterns: _, Cuoco, Cibo, Strumento, Piano in ogni combinazione
% ✓ Pattern matching INTENSIVO su stati intermedi complessi
% ✓ Controlli qualità, timing, skills, compatibilità, rischi, standard
% ✓ Stati intermedi: 25+ fluenti intermedi diversi
% ✓ TARGET: File più difficile possibile mantenendo solvibilità
% ✓ Combina: scaling oggetti + multi-step + negative preconditions complesse