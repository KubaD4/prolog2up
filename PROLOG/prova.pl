% STRESS TEST 4: Ultimate Challenge - Combinazione di Tutti i Fattori
% Combina: Molti oggetti + Azioni split + Precondizioni negative estreme + Multi-step
% Aspettativa: ~6-8 secondi (dovrebbe essere il più lento di tutti)

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Molti cuochi
cuoco(mario).
cuoco(luigi).
cuoco(anna).
cuoco(giuseppe).
cuoco(francesca).
cuoco(marco).

% Molti cibi con ricette complesse
cibo(risotto_milanese).
cibo(ossobuco_gremolata).  
cibo(tiramisù_classico).
cibo(lasagne_bolognese).
cibo(pizza_margherita).

% Molti strumenti specializzati  
strumento(pentola_acciaio).
strumento(pentola_rame).
strumento(padella_ferro).
strumento(padella_antiaderente).
strumento(mixer_planetario).
strumento(forno_statico).
strumento(forno_ventilato).

% Molte stazioni di lavoro
stazione(prep_stazione_1).
stazione(prep_stazione_2).
stazione(cottura_stazione_1).
stazione(cottura_stazione_2).
stazione(finitura_stazione_1).
stazione(finitura_stazione_2).

% Ingredienti per ricette complesse
ingrediente(riso_carnaroli).
ingrediente(brodo_carne).
ingrediente(zafferano).
ingrediente(midollo_osso).
ingrediente(vino_bianco).
ingrediente(mascarpone_fresco).
ingrediente(caffè_espresso).
ingrediente(ragù_bolognese).
ingrediente(besciamella).
ingrediente(mozzarella_bufala).

posizione(pos1).
posizione(pos2).
posizione(pos3).
posizione(pos4).
posizione(pos5).
posizione(pos6).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Tutti i cibi da preparare
  richiesto(risotto_milanese), richiesto(ossobuco_gremolata), richiesto(tiramisù_classico),
  richiesto(lasagne_bolognese), richiesto(pizza_margherita),
  
  % Ingredienti disponibili
  scorta(riso_carnaroli), scorta(brodo_carne), scorta(zafferano), scorta(midollo_osso),
  scorta(vino_bianco), scorta(mascarpone_fresco), scorta(caffè_espresso),
  scorta(ragù_bolognese), scorta(besciamella), scorta(mozzarella_bufala),
  
  % Strumenti disponibili
  disponibile(pentola_acciaio), disponibile(pentola_rame), disponibile(padella_ferro),
  disponibile(padella_antiaderente), disponibile(mixer_planetario), 
  disponibile(forno_statico), disponibile(forno_ventilato),
  
  % Stazioni libere
  stazione_libera(prep_stazione_1), stazione_libera(prep_stazione_2),
  stazione_libera(cottura_stazione_1), stazione_libera(cottura_stazione_2),
  stazione_libera(finitura_stazione_1), stazione_libera(finitura_stazione_2),
  
  % Cuochi affamati e disponibili
  ha_fame(mario), ha_fame(luigi), ha_fame(anna), ha_fame(giuseppe), ha_fame(francesca), ha_fame(marco),
  available(mario), available(luigi), available(anna), available(giuseppe), available(francesca), available(marco),
  cuoco_at(mario, pos1), cuoco_at(luigi, pos2), cuoco_at(anna, pos3),
  cuoco_at(giuseppe, pos4), cuoco_at(francesca, pos5), cuoco_at(marco, pos6),
  
  % Posizioni libere per movimento
  pos_libera(pos5), pos_libera(pos6)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutti i piatti completati e pronti per servire
  pronto_per_servire(risotto_milanese), pronto_per_servire(ossobuco_gremolata),
  pronto_per_servire(tiramisù_classico), pronto_per_servire(lasagne_bolognese),
  pronto_per_servire(pizza_margherita),
  
  % Almeno 4 cuochi soddisfatti
  soddisfatto(mario), soddisfatto(luigi), soddisfatto(anna), soddisfatto(giuseppe),
  
  % Tutte le stazioni pulite e libere
  stazione_libera(prep_stazione_1), stazione_libera(prep_stazione_2),
  stazione_libera(cottura_stazione_1), stazione_libera(cottura_stazione_2)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions - PROCESSO 10-STEP SPLIT CON PRECONDIZIONI NEGATIVE ESTREME
%%%%%%%%%%%%%%%%%%%%%%%

% STEP 1A: Iniziare raccolta ingredienti 
action(start_raccolta(Persona, Cibo, Ingrediente, Stazione, Posizione),
  [richiesto(Cibo), scorta(Ingrediente), available(Persona), cuoco_at(Persona, Posizione), stazione_libera(Stazione)],
  % PRECONDIZIONI NEGATIVE ESTREME
  [
    raccogliendo_ingrediente(_, Ingrediente, _, _, _),    % Ingrediente non in uso
    raccogliendo_ingrediente(Persona, _, _, _, _),        % Persona non raccoglie altro
    preparando_mise_en_place(Persona, _, _, _, _),        % Non in altra fase
    cucinando_preliminary(Persona, _, _, _, _),
    assemblando_piatto(Persona, _, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    servendo_clienti(Persona, _, _, _, _),
    occupando_stazione(_, Stazione, _, _),               % Stazione libera
    usando_ingrediente(_, Ingrediente, _, _),            % Ingrediente disponibile
    operazione_complessa(_, Persona, _, _, _)            % Nessuna operazione in corso
  ],
  [],
  [cuoco(Persona), cibo(Cibo), ingrediente(Ingrediente), stazione(Stazione), posizione(Posizione)],
  [
    del(richiesto(Cibo)), del(scorta(Ingrediente)), del(available(Persona)), del(stazione_libera(Stazione)),
    add(raccogliendo_ingrediente(Persona, Cibo, Ingrediente, Stazione, Posizione)),
    add(occupando_stazione(Persona, Stazione, raccolta, Posizione))
  ]
).

% STEP 1B: Finire raccolta ingredienti
action(end_raccolta(Persona, Cibo, Ingrediente, Stazione, Posizione),
  [raccogliendo_ingrediente(Persona, Cibo, Ingrediente, Stazione, Posizione)],
  [
    preparando_mise_en_place(Persona, _, _, _, _),
    operazione_complessa(interruzione, _, _, _, _),
    cambio_stazione(Persona, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), ingrediente(Ingrediente), stazione(Stazione), posizione(Posizione)],
  [
    del(raccogliendo_ingrediente(Persona, Cibo, Ingrediente, Stazione, Posizione)),
    add(ingrediente_raccolto(Cibo, Ingrediente)), add(available(Persona))
  ]
).

% STEP 2A: Iniziare mise en place
action(start_mise_en_place(Persona, Cibo, Ingrediente, Stazione, Strumento),
  [ingrediente_raccolto(Cibo, Ingrediente), available(Persona), stazione_libera(Stazione), disponibile(Strumento)],
  [
    preparando_mise_en_place(_, Ingrediente, _, _, _),
    preparando_mise_en_place(Persona, _, _, _, _),
    cucinando_preliminary(Persona, _, _, _, _),
    assemblando_piatto(Persona, _, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    operazione_complessa(_, Persona, _, _, _),
    occupando_stazione(_, Stazione, _, _),
    usando_strumento(_, Strumento, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), ingrediente(Ingrediente), stazione(Stazione), strumento(Strumento)],
  [
    del(ingrediente_raccolto(Cibo, Ingrediente)), del(available(Persona)), 
    del(stazione_libera(Stazione)), del(disponibile(Strumento)),
    add(preparando_mise_en_place(Persona, Cibo, Ingrediente, Stazione, Strumento)),
    add(occupando_stazione(Persona, Stazione, preparazione, pos1))
  ]
).

% STEP 2B: Finire mise en place
action(end_mise_en_place(Persona, Cibo, Ingrediente, Stazione, Strumento),
  [preparando_mise_en_place(Persona, Cibo, Ingrediente, Stazione, Strumento)],
  [
    cucinando_preliminary(Persona, _, _, _, _),
    operazione_complessa(cambio_fase, _, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), ingrediente(Ingrediente), stazione(Stazione), strumento(Strumento)],
  [
    del(preparando_mise_en_place(Persona, Cibo, Ingrediente, Stazione, Strumento)),
    add(mise_en_place_pronto(Cibo, Ingrediente)), add(available(Persona))
  ]
).

% STEP 3A: Iniziare cottura preliminare
action(start_cottura_preliminary(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [mise_en_place_pronto(Cibo, Ingrediente), available(Persona), disponibile(Strumento), stazione_libera(Stazione)],
  [
    cucinando_preliminary(_, Cibo, _, _, _),
    cucinando_preliminary(Persona, _, _, _, _),
    assemblando_piatto(Persona, _, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    servendo_clienti(Persona, _, _, _, _),
    occupando_stazione(_, Stazione, _, _),
    usando_strumento(_, Strumento, _, _),
    operazione_complessa(_, Persona, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(mise_en_place_pronto(Cibo, Ingrediente)), del(available(Persona)), 
    del(disponibile(Strumento)), del(stazione_libera(Stazione)),
    add(cucinando_preliminary(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    add(usando_strumento(Persona, Strumento, cottura, Stazione))
  ]
).

% STEP 3B: Finire cottura preliminare
action(end_cottura_preliminary(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [cucinando_preliminary(Persona, Cibo, Strumento, Stazione, Ingrediente)],
  [
    assemblando_piatto(Persona, _, _, _, _),
    operazione_complessa(interruzione, _, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(cucinando_preliminary(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    add(cottura_preliminary_completata(Cibo)), add(available(Persona))
  ]
).

% STEP 4A: Iniziare assemblaggio finale
action(start_assemblaggio(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [cottura_preliminary_completata(Cibo), available(Persona), disponibile(Strumento), stazione_libera(Stazione)],
  [
    assemblando_piatto(_, Cibo, _, _, _),
    assemblando_piatto(Persona, _, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    servendo_clienti(Persona, _, _, _, _),
    occupando_stazione(_, Stazione, _, _),
    usando_strumento(_, Strumento, _, _),
    operazione_complessa(_, Persona, _, _, _),
    operazione_complessa(_, _, Strumento, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(cottura_preliminary_completata(Cibo)), del(available(Persona)),
    del(disponibile(Strumento)), del(stazione_libera(Stazione)),
    add(assemblando_piatto(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    add(operazione_complessa(assemblaggio, Persona, Strumento, Stazione, Ingrediente))
  ]
).

% STEP 4B: Finire assemblaggio
action(end_assemblaggio(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [assemblando_piatto(Persona, Cibo, Strumento, Stazione, Ingrediente)],
  [
    finalizzando_ricetta(Persona, _, _, _, _),
    operazione_complessa(cambio_fase, _, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(assemblando_piatto(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    del(operazione_complessa(assemblaggio, Persona, Strumento, Stazione, Ingrediente)),
    add(assemblaggio_completato(Cibo)), add(available(Persona))
  ]
).

% STEP 5A: Iniziare finalizzazione ricetta
action(start_finalizzazione(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [assemblaggio_completato(Cibo), available(Persona), disponibile(Strumento), stazione_libera(Stazione)],
  [
    finalizzando_ricetta(_, Cibo, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    servendo_clienti(Persona, _, _, _, _),
    operazione_complessa(_, Persona, _, _, _),
    occupando_stazione(_, Stazione, _, _),
    usando_strumento(_, Strumento, _, _),
    
    % Pattern complessi con multiple combinazioni
    assemblando_piatto(_, _, Strumento, _, _),
    cucinando_preliminary(_, _, Strumento, _, _),
    raccogliendo_ingrediente(_, _, Ingrediente, _, _),
    preparando_mise_en_place(_, _, Ingrediente, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(assemblaggio_completato(Cibo)), del(available(Persona)),
    del(disponibile(Strumento)), del(stazione_libera(Stazione)),
    add(finalizzando_ricetta(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    add(operazione_complessa(finalizzazione, Persona, Strumento, Stazione, Ingrediente))
  ]
).

% STEP 5B: Finire finalizzazione
action(end_finalizzazione(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [finalizzando_ricetta(Persona, Cibo, Strumento, Stazione, Ingrediente)],
  [
    servendo_clienti(Persona, _, _, _, _),
    operazione_complessa(pulizia, _, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(finalizzando_ricetta(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    del(operazione_complessa(finalizzazione, Persona, Strumento, Stazione, Ingrediente)),
    add(ricetta_finalizzata(Cibo)), add(available(Persona))
  ]
).

% STEP 6A: Iniziare servizio clienti
action(start_servizio(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [ricetta_finalizzata(Cibo), available(Persona), disponibile(Strumento), stazione_libera(Stazione)],
  [
    servendo_clienti(_, Cibo, _, _, _),
    servendo_clienti(Persona, _, _, _, _),
    operazione_complessa(_, Persona, _, _, _),
    occupando_stazione(_, Stazione, _, _),
    usando_strumento(_, Strumento, _, _),
    
    % Controlli di coerenza del processo
    raccogliendo_ingrediente(Persona, _, _, _, _),
    preparando_mise_en_place(Persona, _, _, _, _), 
    cucinando_preliminary(Persona, _, _, _, _),
    assemblando_piatto(Persona, _, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    
    % Controlli risorse condivise
    usando_ingrediente(_, Ingrediente, _, _),
    operazione_complessa(_, _, Strumento, _, _),
    operazione_complessa(_, _, _, Stazione, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(ricetta_finalizzata(Cibo)), del(available(Persona)),
    del(disponibile(Strumento)), del(stazione_libera(Stazione)),
    add(servendo_clienti(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    add(operazione_complessa(servizio, Persona, Strumento, Stazione, Ingrediente))
  ]
).

% STEP 6B: Finire servizio
action(end_servizio(Persona, Cibo, Strumento, Stazione, Ingrediente),
  [servendo_clienti(Persona, Cibo, Strumento, Stazione, Ingrediente)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), stazione(Stazione), ingrediente(Ingrediente)],
  [
    del(servendo_clienti(Persona, Cibo, Strumento, Stazione, Ingrediente)),
    del(operazione_complessa(servizio, Persona, Strumento, Stazione, Ingrediente)),
    add(pronto_per_servire(Cibo)), add(disponibile(Strumento)), 
    add(stazione_libera(Stazione)), add(available(Persona))
  ]
).

% Mangiare finale con controlli estensivi
action(mangia_ultimate(Persona, Cibo),
  [pronto_per_servire(Cibo), ha_fame(Persona), available(Persona)],
  [
    % Controlli che non sia impegnato in nessuna fase
    raccogliendo_ingrediente(Persona, _, _, _, _),
    preparando_mise_en_place(Persona, _, _, _, _),
    cucinando_preliminary(Persona, _, _, _, _),
    assemblando_piatto(Persona, _, _, _, _),
    finalizzando_ricetta(Persona, _, _, _, _),
    servendo_clienti(Persona, _, _, _, _),
    operazione_complessa(_, Persona, _, _, _),
    
    % Altri non stanno usando lo stesso cibo
    servendo_clienti(_, Cibo, _, _, _),
    assemblando_piatto(_, Cibo, _, _, _)
  ],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note di Design
%%%%%%%%%%%%%%%%%%%%%%%
% COMPLESSITÀ MASSIMA COMBINATA:
% ✓ 6 cuochi × 5 cibi × 7 strumenti × 6 stazioni = spazio stati enorme
% ✓ PROCESSO 6-STEP OBBLIGATORIO (ogni step split in start/end) = 12 azioni per piatto
% ✓ 5 piatti × 12 azioni = 60 azioni minime + 4 azioni mangia = 64 azioni totali
% ✓ Ogni azione ha 8-15 precondizioni negative con pattern matching complessi
% ✓ Stati intermedi: raccogliendo_ingrediente, preparando_mise_en_place, 
%   cucinando_preliminary, assemblando_piatto, finalizzando_ricetta, servendo_clienti
% ✓ Fluenti aggiuntivi: operazione_complessa, occupando_stazione, usando_strumento
% ✓ Pattern di wildcard estremamente complessi per evitare conflitti
%
% QUESTO DOVREBBE ESSERE IL FILE PIÙ LENTO:
% ✓ Combinazione di tutti i fattori di complessità identificati
% ✓ Spazio degli stati massimo
% ✓ Piano più lungo possibile (60+ azioni)
% ✓ Pattern matching più complesso possibile
%
% ASPETTATIVA: ~6-8 secondi o più (vs 4.58s di kb_hl.pl)