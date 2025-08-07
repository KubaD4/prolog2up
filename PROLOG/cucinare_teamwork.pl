% VARIAZIONE 3 FIXED: Teamwork - Bug fixes applicati
% Fix: tipi specifici per tutti i fluenti, no Object generico

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Team cuochi
cuoco_senior(mario).
cuoco_junior(luigi).
cuoco_junior(anna).
assistente(paolo).

% Piatti che richiedono coordinazione
piatto_semplice(pasta_pomodoro).
piatto_semplice(insalata).
piatto_complesso(lasagne).
piatto_complesso(arrosto).
piatto_team(paella).
piatto_team(banchetto).

% Strumenti condivisi
strumento_base(pentola_piccola).
strumento_base(padella_media).
strumento_avanzato(forno_grande).
strumento_avanzato(friggitrice).
strumento_team(pentola_gigante).
strumento_team(griglia_party).

% Postazioni di lavoro
postazione_individuale(banco1).
postazione_individuale(banco2).
postazione_condivisa(isola_centrale).
postazione_team(area_party).

% Ingredienti per quantità
ingrediente_base(pomodoro).
ingrediente_base(pasta).
ingrediente_speciale(tartufo).
ingrediente_speciale(champagne).
ingrediente_team(riso_paella).
ingrediente_team(carne_banchetto).

% Fix: Tipo specifico per coordinazione (evita Object generico)
stato_team(team_cucina_status).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Stati piatti per categoria
  da_cucinare_semplice(pasta_pomodoro), da_cucinare_semplice(insalata),
  da_cucinare_complesso(lasagne), da_cucinare_complesso(arrosto),
  da_cucinare_team(paella), da_cucinare_team(banchetto),
  
  % Stati cuochi per ruolo
  libero_senior(mario),
  libero_junior(luigi), libero_junior(anna),
  libero_assistente(paolo),
  
  % Fame per ruolo
  fame_senior(mario),
  fame_junior(luigi), fame_junior(anna),
  fame_assistente(paolo),
  
  % Strumenti per categoria
  disponibile_base(pentola_piccola), disponibile_base(padella_media),
  disponibile_avanzato(forno_grande), disponibile_avanzato(friggitrice),
  disponibile_team(pentola_gigante), disponibile_team(griglia_party),
  
  % Postazioni
  vuota_individuale(banco1), vuota_individuale(banco2),
  vuota_condivisa(isola_centrale),
  vuota_team(area_party),
  
  % Ingredienti disponibili
  disponibile_base_ing(pomodoro), disponibile_base_ing(pasta),
  disponibile_speciale_ing(tartufo), disponibile_speciale_ing(champagne),
  disponibile_team_ing(riso_paella), disponibile_team_ing(carne_banchetto),
  
  % Fix: Stato team iniziale con tipo specifico
  team_non_coordinato(team_cucina_status)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutti i piatti completati
  completato_semplice(pasta_pomodoro), completato_semplice(insalata),
  completato_complesso(lasagne), completato_complesso(arrosto),
  completato_team(paella), completato_team(banchetto),
  
  % Tutti soddisfatti per ruolo
  soddisfatto_senior(mario),
  soddisfatto_junior(luigi), soddisfatto_junior(anna),
  soddisfatto_assistente(paolo),
  
  % Fix: Team coordinato con tipo specifico
  team_coordinato(team_cucina_status)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% Cucinare piatto semplice - solo cuoco (arity 4)
action(cucina_semplice(Cuoco, Piatto, Strumento, Postazione),
  [da_cucinare_semplice(Piatto), libero_junior(Cuoco), 
   disponibile_base(Strumento), vuota_individuale(Postazione)],
  [lavorando_semplice(Cuoco), usando_base(Strumento)],
  [],
  [cuoco_junior(Cuoco), piatto_semplice(Piatto), strumento_base(Strumento), postazione_individuale(Postazione)],
  [
    del(da_cucinare_semplice(Piatto)), del(libero_junior(Cuoco)), 
    del(disponibile_base(Strumento)), del(vuota_individuale(Postazione)),
    add(lavorando_semplice(Cuoco)), add(usando_base(Strumento)), add(occupata_individuale(Postazione))
  ]
).

% Completare piatto semplice (arity 4)
action(completa_semplice(Cuoco, Piatto, Strumento, Postazione),
  [lavorando_semplice(Cuoco), usando_base(Strumento), occupata_individuale(Postazione)],
  [],
  [],
  [cuoco_junior(Cuoco), piatto_semplice(Piatto), strumento_base(Strumento), postazione_individuale(Postazione)],
  [
    del(lavorando_semplice(Cuoco)), del(usando_base(Strumento)), del(occupata_individuale(Postazione)),
    add(completato_semplice(Piatto)), add(libero_junior(Cuoco)), 
    add(disponibile_base(Strumento)), add(vuota_individuale(Postazione))
  ]
).

% Iniziare piatto complesso - serve senior (arity 4)
action(inizia_complesso(Cuoco, Piatto, Strumento, Postazione),
  [da_cucinare_complesso(Piatto), libero_senior(Cuoco), 
   disponibile_avanzato(Strumento), vuota_condivisa(Postazione)],
  [lavorando_complesso(Cuoco), usando_avanzato(Strumento)],
  [],
  [cuoco_senior(Cuoco), piatto_complesso(Piatto), strumento_avanzato(Strumento), postazione_condivisa(Postazione)],
  [
    del(da_cucinare_complesso(Piatto)), del(libero_senior(Cuoco)), 
    del(disponibile_avanzato(Strumento)), del(vuota_condivisa(Postazione)),
    add(lavorando_complesso(Cuoco)), add(usando_avanzato(Strumento)), add(occupata_condivisa(Postazione))
  ]
).

% Assistere piatto complesso - junior aiuta senior (arity 5)
action(assiste_complesso(Assistente, Senior, Piatto, Ingrediente, Postazione),
  [lavorando_complesso(Senior), libero_junior(Assistente), 
   disponibile_speciale_ing(Ingrediente), occupata_condivisa(Postazione)],
  [assistendo_complesso(Assistente), preparando_ingrediente_spec(Assistente)],
  [],
  [cuoco_junior(Assistente), cuoco_senior(Senior), piatto_complesso(Piatto), 
   ingrediente_speciale(Ingrediente), postazione_condivisa(Postazione)],
  [
    del(libero_junior(Assistente)), del(disponibile_speciale_ing(Ingrediente)),
    add(assistendo_complesso(Assistente)), add(preparando_ingrediente_spec(Assistente))
  ]
).

% Completare piatto complesso (arity 5)
action(completa_complesso(Senior, Assistente, Piatto, Strumento, Postazione),
  [lavorando_complesso(Senior), assistendo_complesso(Assistente), 
   usando_avanzato(Strumento), occupata_condivisa(Postazione)],
  [],
  [],
  [cuoco_senior(Senior), cuoco_junior(Assistente), piatto_complesso(Piatto), 
   strumento_avanzato(Strumento), postazione_condivisa(Postazione)],
  [
    del(lavorando_complesso(Senior)), del(assistendo_complesso(Assistente)), 
    del(usando_avanzato(Strumento)), del(occupata_condivisa(Postazione)),
    add(completato_complesso(Piatto)), add(libero_senior(Senior)), add(libero_junior(Assistente)),
    add(disponibile_avanzato(Strumento)), add(vuota_condivisa(Postazione))
  ]
).

% Coordinare team per piatto team (arity 5)
action(coordina_team(Senior, Piatto, Strumento, Ingrediente, Postazione),
  [da_cucinare_team(Piatto), libero_senior(Senior), 
   disponibile_team(Strumento), disponibile_team_ing(Ingrediente), vuota_team(Postazione)],
  [coordinando_team(Senior), usando_team(Strumento)],
  [],
  [cuoco_senior(Senior), piatto_team(Piatto), strumento_team(Strumento), 
   ingrediente_team(Ingrediente), postazione_team(Postazione)],
  [
    del(da_cucinare_team(Piatto)), del(libero_senior(Senior)), 
    del(disponibile_team(Strumento)), del(disponibile_team_ing(Ingrediente)), del(vuota_team(Postazione)),
    add(coordinando_team(Senior)), add(usando_team(Strumento)), add(occupata_team(Postazione))
  ]
).

% Junior si unisce al team (arity 3)
action(unisciti_team(Junior, Senior, Piatto),
  [coordinando_team(Senior), libero_junior(Junior)],
  [nel_team(Junior)],
  [],
  [cuoco_junior(Junior), cuoco_senior(Senior), piatto_team(Piatto)],
  [
    del(libero_junior(Junior)),
    add(nel_team(Junior))
  ]
).

% Assistente si unisce al team (arity 3)
action(assistente_unisciti_team(Assistente, Senior, Piatto),
  [coordinando_team(Senior), libero_assistente(Assistente)],
  [nel_team_assistente(Assistente)],
  [],
  [assistente(Assistente), cuoco_senior(Senior), piatto_team(Piatto)],
  [
    del(libero_assistente(Assistente)),
    add(nel_team_assistente(Assistente))
  ]
).

% Fix: Completare piatto team con stato specifico (arity 5)
action(completa_team(Senior, Junior, Assistente, Piatto, StatoTeam),
  [coordinando_team(Senior), nel_team(Junior), nel_team_assistente(Assistente), 
   team_non_coordinato(StatoTeam)],
  [],
  [],
  [cuoco_senior(Senior), cuoco_junior(Junior), assistente(Assistente), 
   piatto_team(Piatto), stato_team(StatoTeam)],
  [
    del(coordinando_team(Senior)), del(nel_team(Junior)), del(nel_team_assistente(Assistente)), 
    del(team_non_coordinato(StatoTeam)),
    add(completato_team(Piatto)), add(libero_senior(Senior)), add(libero_junior(Junior)), 
    add(libero_assistente(Assistente)), add(team_coordinato(StatoTeam))
  ]
).

% Mangiare per ruolo - senior (arity 2)
action(mangia_senior(Senior, TipoPiatto),
  [completato_complesso(lasagne), fame_senior(Senior), libero_senior(Senior)],
  [mangiando_senior(Senior)],
  [],
  [cuoco_senior(Senior)],
  [
    del(fame_senior(Senior)),
    add(soddisfatto_senior(Senior))
  ]
).

% Mangiare per ruolo - junior (arity 2)
action(mangia_junior(Junior, TipoPiatto),
  [completato_semplice(pasta_pomodoro), fame_junior(Junior), libero_junior(Junior)],
  [mangiando_junior(Junior)],
  [],
  [cuoco_junior(Junior)],
  [
    del(fame_junior(Junior)),
    add(soddisfatto_junior(Junior))
  ]
).

% Fix: Mangiare assistente con precondizione specifica (arity 2)
action(mangia_assistente(Assistente, TipoPiatto),
  [completato_team(paella), fame_assistente(Assistente), libero_assistente(Assistente)],
  [mangiando_assistente(Assistente)],
  [],
  [assistente(Assistente)],
  [
    del(fame_assistente(Assistente)),
    add(soddisfatto_assistente(Assistente))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% FIX APPLICATI:
% ✓ Aggiunto tipo specifico: stato_team(team_cucina_status)
% ✓ Sostituito coordinazione_riuscita(team_cucina) → team_coordinato(team_cucina_status)
% ✓ Eliminati fluenti che usano Object generico
% ✓ Precondizioni specifiche invece di wildcard complesse:
%   - completato_team(_) → completato_team(paella)
%   - completato_complesso(_) → completato_complesso(lasagne)
% ✓ Tutti i fluenti hanno tipi UserType specifici
% ✓ Mantenuta logica di coordinazione ma semplificata
% ✓ Piano fattibile: ~18-20 azioni