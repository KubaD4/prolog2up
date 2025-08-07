% TEST 2 CORRETTO: Azioni Split + Arity ≤ 5
% Versione con arity ridotta e fluenti completi

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

% AZIONE SPLIT 1A: Iniziare a cucinare (arity 4) ✓
action(cucina_start(Persona, Cibo, Strumento, Posizione),
  [crudo(Cibo), disponibile(Strumento), available(Persona), cuoco_at(Persona, Posizione), strumento_at(Strumento, Posizione)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), posizione(Posizione)],
  [
    del(crudo(Cibo)), del(disponibile(Strumento)), del(available(Persona)),
    add(cucinando(Persona, Cibo, Strumento, Posizione))  % STATO INTERMEDIO (arity 4)
  ]
).

% AZIONE SPLIT 1B: Finire di cucinare (arity 4) ✓
action(cucina_end(Persona, Cibo, Strumento, Posizione),
  [cucinando(Persona, Cibo, Strumento, Posizione)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), posizione(Posizione)],
  [
    del(cucinando(Persona, Cibo, Strumento, Posizione)),
    add(cotto(Cibo)), add(disponibile(Strumento)), add(available(Persona))
  ]
).

% AZIONE SPLIT 2A: Iniziare a spostare strumento (arity 4) ✓ - RIDOTTO da 6
action(sposta_strumento_start(Persona, Strumento, PosDa, PosA),
  [cuoco_at(Persona, PosDa), strumento_at(Strumento, PosDa), available(Persona), pos_libera(PosA)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(strumento_at(Strumento, PosDa)), del(available(Persona)), del(pos_libera(PosA)),
    add(spostando_strumento(Persona, Strumento, PosDa, PosA))  % STATO INTERMEDIO (arity 4)
  ]
).

% AZIONE SPLIT 2B: Finire di spostare strumento (arity 4) ✓
action(sposta_strumento_end(Persona, Strumento, PosDa, PosA),
  [spostando_strumento(Persona, Strumento, PosDa, PosA)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento), posizione(PosDa), posizione(PosA)],
  [
    del(spostando_strumento(Persona, Strumento, PosDa, PosA)),
    add(strumento_at(Strumento, PosA)), add(available(Persona)), add(pos_libera(PosDa))
  ]
).

% AZIONE SPLIT 3A: Iniziare a muovere persona (arity 3) ✓ - RIDOTTO da 5  
action(muovi_persona_start(Persona, PosDa, PosA),
  [cuoco_at(Persona, PosDa), available(Persona), pos_libera(PosA)],
  [],
  [],
  [cuoco(Persona), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(cuoco_at(Persona, PosDa)), del(available(Persona)), del(pos_libera(PosA)),
    add(muovendo_persona(Persona, PosDa, PosA))  % STATO INTERMEDIO (arity 3)
  ]
).

% AZIONE SPLIT 3B: Finire di muovere persona (arity 3) ✓
action(muovi_persona_end(Persona, PosDa, PosA),
  [muovendo_persona(Persona, PosDa, PosA)],
  [],
  [],
  [cuoco(Persona), posizione(PosDa), posizione(PosA)],
  [
    del(muovendo_persona(Persona, PosDa, PosA)),
    add(cuoco_at(Persona, PosA)), add(available(Persona)), add(pos_libera(PosDa))
  ]
).

% Mangiare (arity 2) ✓
action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), available(Persona)],
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
% ✓ Arity ridotta: TUTTE le azioni ≤ 5 parametri
% ✓ spostando_strumento: 6→4 parametri
% ✓ muovendo_persona: 5→3 parametri  
% ✓ cucinando: 5→4 parametri
% ✓ Fluenti separati per tipo
% ✓ Stati intermedi ben definiti
%
% Piano necessario (RADDOPPIATO ma arity corretta):
% 1. muovi_persona_start(mario, pos1, pos3)
% 2. muovi_persona_end(mario, pos1, pos3)
% 3. sposta_strumento_start(mario, pentola, pos1, pos3)
% 4. sposta_strumento_end(mario, pentola, pos1, pos3)
% 5. cucina_start(mario, pasta, pentola, pos3)
% 6. cucina_end(mario, pasta, pentola, pos3)
% 7. muovi_persona_start(luigi, pos2, pos10)
% 8. muovi_persona_end(luigi, pos2, pos10)
% 9. sposta_strumento_start(luigi, padella, pos2, pos10)
% 10. sposta_strumento_end(luigi, padella, pos2, pos10)
% 11. cucina_start(luigi, riso, padella, pos10)
% 12. cucina_end(luigi, riso, padella, pos10)
% 13. mangia(mario, pasta)
% 14. mangia(luigi, riso)
%
% Piano minimo: 14 azioni, TUTTE ≤ arity 5