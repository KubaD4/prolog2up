% TEST 3 CORRETTO: Precondizioni Negative Complesse + Arity ≤ 5
% Versione con arity ridotta e tutti i fluenti definiti

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Posizioni semplificate
posizione(pos1).  % (1,1)
posizione(pos2).  % (2,2)
posizione(pos3).  % (3,3)
posizione(pos10). % (10,10)

% Oggetti base
cuoco(mario).
cuoco(luigi).
cibo(pasta).
cibo(riso).
strumento(pentola).
strumento(padella).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Cibi crudi
  crudo(pasta), crudo(riso),
  
  % Strumenti disponibili con posizioni
  disponibile(pentola), strumento_at(pentola, pos1),
  disponibile(padella), strumento_at(padella, pos2),
  
  % Cuochi affamati e disponibili con posizioni
  ha_fame(mario), cuoco_at(mario, pos1), available(mario),
  ha_fame(luigi), cuoco_at(luigi, pos2), available(luigi),
  
  % Posizioni libere
  pos_libera(pos3), pos_libera(pos10)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Cibi cotti
  cotto(pasta), cotto(riso),
  
  % Cuochi soddisfatti e disponibili
  soddisfatto(mario), soddisfatto(luigi),
  available(mario), available(luigi),
  
  % Strumenti in posizioni specifiche e disponibili
  strumento_at(pentola, pos3), strumento_at(padella, pos10),
  disponibile(pentola), disponibile(padella)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% AZIONE SPLIT 1A: Iniziare a cucinare (arity 4 + precondizioni negative complesse) ✓
action(cucina_start(Persona, Cibo, Strumento, Posizione),
  [crudo(Cibo), disponibile(Strumento), available(Persona), cuoco_at(Persona, Posizione), strumento_at(Strumento, Posizione)],
  % PRECONDIZIONI NEGATIVE COMPLESSE (come kb_hl.pl)
  [cucinando(_, Cibo, _, _),              % Nessun altro sta cucinando questo cibo
   cucinando(Persona, _, _, _),           % Questa persona non sta già cucinando
   spostando_strumento(_, Strumento, _, _), % Strumento non viene spostato
   muovendo_persona(Persona, _, _),       % Persona non si sta muovendo
   pos_occupata(Posizione)],              % Posizione non occupata
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), posizione(Posizione)],
  [
    del(crudo(Cibo)), del(disponibile(Strumento)), del(available(Persona)),
    add(cucinando(Persona, Cibo, Strumento, Posizione))
  ]
).

% AZIONE SPLIT 1B: Finire di cucinare (arity 4 + precondizioni negative) ✓
action(cucina_end(Persona, Cibo, Strumento, Posizione),
  [cucinando(Persona, Cibo, Strumento, Posizione)],
  % Nessun altro sta interferendo
  [spostando_strumento(_, Strumento, _, _),
   muovendo_persona(Persona, _, _)],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), posizione(Posizione)],
  [
    del(cucinando(Persona, Cibo, Strumento, Posizione)),
    add(cotto(Cibo)), add(disponibile(Strumento)), add(available(Persona))
  ]
).

% AZIONE SPLIT 2A: Iniziare a spostare strumento (arity 4 + precondizioni negative complesse) ✓
action(sposta_strumento_start(Persona, Strumento, PosDa, PosA),
  [cuoco_at(Persona, PosDa), strumento_at(Strumento, PosDa), available(Persona), pos_libera(PosA)],
  % PRECONDIZIONI NEGATIVE COMPLESSE
  [spostando_strumento(_, Strumento, _, _),    % Strumento non già in movimento
   spostando_strumento(Persona, _, _, _),      % Persona non sposta altro
   cucinando(_, _, Strumento, _),              % Strumento non in uso per cucinare
   cucinando(Persona, _, _, _),                % Persona non sta cucinando
   muovendo_persona(Persona, _, _),            % Persona non si sta muovendo
   pos_occupata(PosA)],                        % Destinazione libera
  [],
  [cuoco(Persona), strumento(Strumento), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(strumento_at(Strumento, PosDa)), del(available(Persona)), del(pos_libera(PosA)),
    add(spostando_strumento(Persona, Strumento, PosDa, PosA))
  ]
).

% AZIONE SPLIT 2B: Finire di spostare strumento (arity 4) ✓
action(sposta_strumento_end(Persona, Strumento, PosDa, PosA),
  [spostando_strumento(Persona, Strumento, PosDa, PosA)],
  % Nessuna interferenza
  [muovendo_persona(Persona, _, _),
   cucinando(Persona, _, _, _)],
  [],
  [cuoco(Persona), strumento(Strumento), posizione(PosDa), posizione(PosA)],
  [
    del(spostando_strumento(Persona, Strumento, PosDa, PosA)),
    add(strumento_at(Strumento, PosA)), add(available(Persona)), add(pos_libera(PosDa))
  ]
).

% AZIONE SPLIT 3A: Iniziare a muovere persona (arity 3 + precondizioni negative complesse) ✓
action(muovi_persona_start(Persona, PosDa, PosA),
  [cuoco_at(Persona, PosDa), available(Persona), pos_libera(PosA)],
  % PRECONDIZIONI NEGATIVE COMPLESSE
  [muovendo_persona(Persona, _, _),           % Non già in movimento
   cucinando(Persona, _, _, _),               % Non sta cucinando
   spostando_strumento(Persona, _, _, _),     % Non sposta strumenti
   pos_occupata(PosA)],                       % Destinazione libera
  [],
  [cuoco(Persona), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(cuoco_at(Persona, PosDa)), del(available(Persona)), del(pos_libera(PosA)),
    add(muovendo_persona(Persona, PosDa, PosA))
  ]
).

% AZIONE SPLIT 3B: Finire di muovere persona (arity 3) ✓
action(muovi_persona_end(Persona, PosDa, PosA),
  [muovendo_persona(Persona, PosDa, PosA)],
  % Nessuna interferenza  
  [cucinando(Persona, _, _, _),
   spostando_strumento(Persona, _, _, _)],
  [],
  [cuoco(Persona), posizione(PosDa), posizione(PosA)],
  [
    del(muovendo_persona(Persona, PosDa, PosA)),
    add(cuoco_at(Persona, PosA)), add(available(Persona)), add(pos_libera(PosDa))
  ]
).

% Mangiare (arity 2 + precondizioni negative) ✓
action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), available(Persona)],
  % Non può mangiare se sta facendo altro
  [cucinando(Persona, _, _, _),
   muovendo_persona(Persona, _, _),
   spostando_strumento(Persona, _, _, _)],
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
% CORREZIONI APPLICATE:
% ✓ Coordinate semplificate: (X,Y) → posizione(pos1)
% ✓ Arity ridotta: TUTTE le azioni ≤ 5 parametri
% ✓ spostando_strumento: 6→4 parametri
% ✓ muovendo_persona: 5→3 parametri
% ✓ cucinando: 5→4 parametri
% ✓ Fluenti separati per tipo
% ✓ PRECONDIZIONI NEGATIVE COMPLESSE con pattern matching:
%   - cucinando(_, Cibo, _, _)     → wildcard matching (arity 4)
%   - spostando_strumento(Persona, _, _, _) → parametro + wildcard (arity 4)
%   - pos_occupata(Posizione) → fluent nelle precondizioni negative (arity 1)
%   - Combinazioni multiple di precondizioni negative
%
% ASPETTATIVA: Se le precondizioni negative complesse sono il bottleneck,
% questo file dovrebbe essere MOLTO più lento del Test 2
%
% Il planner deve verificare per ogni azione che:
% - Nessun altro oggetto sia in conflitto
% - Nessuna azione interferente sia in corso  
% - Tutti i pattern di wildcard siano soddisfatti
%
% Questo richiede PATTERN MATCHING ELABORATO su tutti gli stati possibili!
%
% Piano necessario: identico al Test 2 (14 azioni)
% ma ogni azione richiede verifiche molto più complesse
%
% FLUENTI CHE DEVONO ESSERE DEFINITI (inclusi quelli solo in neg_preconditions):
% ✓ pos_occupata (solo in precondizioni negative)
% ✓ cucinando (stati intermedi)
% ✓ spostando_strumento (stati intermedi)
% ✓ muovendo_persona (stati intermedi)
% ✓ pos_libera, cuoco_at, strumento_at (stati normali)