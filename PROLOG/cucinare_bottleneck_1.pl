% TEST 1 CORRETTO: Coordinate + Arity ≤ 5
% Versione con arity ridotta per rispettare il limite di 5 parametri

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Posizioni numeriche (raggruppate per ridurre arity)
posizione(pos1).  % Rappresenta (1,1)
posizione(pos2).  % Rappresenta (2,2)  
posizione(pos3).  % Rappresenta (3,3)
posizione(pos10). % Rappresenta (10,10)

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
  
  % Cuochi affamati con posizioni
  ha_fame(mario), cuoco_at(mario, pos1),
  ha_fame(luigi), cuoco_at(luigi, pos2),
  
  % Posizioni libere
  pos_libera(pos3), pos_libera(pos10)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Cibi cotti
  cotto(pasta), cotto(riso),
  
  % Cuochi soddisfatti
  soddisfatto(mario), soddisfatto(luigi),
  
  % Strumenti in posizioni specifiche
  strumento_at(pentola, pos3), strumento_at(padella, pos10)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% Cucinare con coordinate (arity 4) ✓
action(cucina_pos(Persona, Cibo, Strumento, Posizione),
  [crudo(Cibo), disponibile(Strumento), cuoco_at(Persona, Posizione), strumento_at(Strumento, Posizione)],
  [pos_occupata(Posizione)],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), posizione(Posizione)],
  [
    del(crudo(Cibo)), del(pos_libera(Posizione)),
    add(cotto(Cibo)), add(pos_occupata(Posizione))
  ]
).

% Spostare strumento (arity 4) ✓ - RIDOTTO da 6 a 4
action(sposta_strumento(Persona, Strumento, PosDa, PosA),
  [cuoco_at(Persona, PosDa), strumento_at(Strumento, PosDa), pos_libera(PosA)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(strumento_at(Strumento, PosDa)), del(pos_libera(PosA)),
    add(strumento_at(Strumento, PosA)), add(pos_libera(PosDa))
  ]
).

% Spostare persona (arity 3) ✓ - RIDOTTO da 5 a 3
action(muovi_persona(Persona, PosDa, PosA),
  [cuoco_at(Persona, PosDa), pos_libera(PosA)],
  [],
  [],
  [cuoco(Persona), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(cuoco_at(Persona, PosDa)), del(pos_libera(PosA)),
    add(cuoco_at(Persona, PosA)), add(pos_libera(PosDa))
  ]
).

% Mangiare (arity 2) ✓
action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona)],
  [],
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
% ✓ Arity ridotta: tutti predicati ≤ 5 parametri
% ✓ sposta_strumento: 6→4 parametri  
% ✓ muovi_persona: 5→3 parametri
% ✓ Fluenti separati per tipo (no conflitti supertype)
% ✓ pos_occupata definito nelle precondizioni negative
%
% Piano necessario:
% 1. muovi_persona(mario, pos1, pos3)
% 2. sposta_strumento(mario, pentola, pos1, pos3)  
% 3. cucina_pos(mario, pasta, pentola, pos3)
% 4. muovi_persona(luigi, pos2, pos10)
% 5. sposta_strumento(luigi, padella, pos2, pos10)
% 6. cucina_pos(luigi, riso, padella, pos10)
% 7. mangia(mario, pasta)
% 8. mangia(luigi, riso)
%
% Piano minimo: 8 azioni, NESSUNA > arity 5