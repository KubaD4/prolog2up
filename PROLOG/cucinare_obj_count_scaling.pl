% STRESS TEST 1: Object Count Scaling
% Testa il scaling lineare con molti più oggetti dello stesso tipo


%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Molti più oggetti di ogni tipo
cuoco(mario).
cuoco(luigi).
cuoco(anna).
cuoco(giuseppe).
cuoco(francesca).
cuoco(marco).
cuoco(sofia).
cuoco(alessandro).

cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(minestrone).
cibo(lasagne).
cibo(polenta).
cibo(risotto).
cibo(gnocchi).
cibo(carbonara).
cibo(amatriciana).

strumento(pentola1).
strumento(pentola2).
strumento(padella1).
strumento(padella2).
strumento(forno1).
strumento(forno2).
strumento(casseruola1).
strumento(casseruola2).
strumento(wok).
strumento(tegame).

posizione(pos1).
posizione(pos2).
posizione(pos3).
posizione(pos4).
posizione(pos5).
posizione(pos6).
posizione(pos7).
posizione(pos8).
posizione(pos9).
posizione(pos10).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Tutti i cibi crudi
  crudo(pasta), crudo(riso), crudo(pizza), crudo(minestrone), crudo(lasagne),
  crudo(polenta), crudo(risotto), crudo(gnocchi), crudo(carbonara), crudo(amatriciana),
  
  % Tutti gli strumenti disponibili
  disponibile(pentola1), disponibile(pentola2), disponibile(padella1), disponibile(padella2),
  disponibile(forno1), disponibile(forno2), disponibile(casseruola1), disponibile(casseruola2),
  disponibile(wok), disponibile(tegame),
  
  % Tutti i cuochi affamati e disponibili
  ha_fame(mario), ha_fame(luigi), ha_fame(anna), ha_fame(giuseppe),
  ha_fame(francesca), ha_fame(marco), ha_fame(sofia), ha_fame(alessandro),
  available(mario), available(luigi), available(anna), available(giuseppe),
  available(francesca), available(marco), available(sofia), available(alessandro),
  
  % Posizioni dei cuochi
  cuoco_at(mario, pos1), cuoco_at(luigi, pos2), cuoco_at(anna, pos3), cuoco_at(giuseppe, pos4),
  cuoco_at(francesca, pos5), cuoco_at(marco, pos6), cuoco_at(sofia, pos7), cuoco_at(alessandro, pos8),
  
  % Posizioni degli strumenti
  strumento_at(pentola1, pos1), strumento_at(pentola2, pos2), strumento_at(padella1, pos3),
  strumento_at(padella2, pos4), strumento_at(forno1, pos5), strumento_at(forno2, pos6),
  strumento_at(casseruola1, pos7), strumento_at(casseruola2, pos8), strumento_at(wok, pos9),
  strumento_at(tegame, pos10),
  
  % Posizioni libere
  pos_libera(pos9), pos_libera(pos10)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Almeno la metà dei cibi cotti
  cotto(pasta), cotto(riso), cotto(pizza), cotto(minestrone), cotto(lasagne),
  
  % Almeno la metà dei cuochi soddisfatti
  soddisfatto(mario), soddisfatto(luigi), soddisfatto(anna), soddisfatto(giuseppe),
  
  % Tutti i cuochi disponibili
  available(mario), available(luigi), available(anna), available(giuseppe),
  available(francesca), available(marco), available(sofia), available(alessandro),
  
  % Alcuni strumenti riposizionati
  strumento_at(pentola1, pos9), strumento_at(padella1, pos10)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% Cucinare (arity 4) - azione base semplice
action(cucina(Persona, Cibo, Strumento, Posizione),
  [crudo(Cibo), disponibile(Strumento), available(Persona), 
   cuoco_at(Persona, Posizione), strumento_at(Strumento, Posizione)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), posizione(Posizione)],
  [
    del(crudo(Cibo)), del(disponibile(Strumento)), del(available(Persona)),
    add(cotto(Cibo)), add(disponibile(Strumento)), add(available(Persona))
  ]
).

% Spostare strumento (arity 4)
action(sposta_strumento(Persona, Strumento, PosDa, PosA),
  [cuoco_at(Persona, PosDa), strumento_at(Strumento, PosDa), available(Persona), pos_libera(PosA)],
  [],
  [],
  [cuoco(Persona), strumento(Strumento), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(strumento_at(Strumento, PosDa)), del(available(Persona)), del(pos_libera(PosA)),
    add(strumento_at(Strumento, PosA)), add(available(Persona)), add(pos_libera(PosDa))
  ]
).

% Muovere persona (arity 3)
action(muovi_persona(Persona, PosDa, PosA),
  [cuoco_at(Persona, PosDa), available(Persona), pos_libera(PosA)],
  [],
  [],
  [cuoco(Persona), posizione(PosDa), posizione(PosA), PosDa \= PosA],
  [
    del(cuoco_at(Persona, PosDa)), del(available(Persona)), del(pos_libera(PosA)),
    add(cuoco_at(Persona, PosA)), add(available(Persona)), add(pos_libera(PosDa))
  ]
).

% Mangiare (arity 2)
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
% Note di Design
%%%%%%%%%%%%%%%%%%%%%%%
% COMPLESSITÀ INTRODOTTA:
% ✓ 8 cuochi (vs 2 del base)
% ✓ 10 cibi (vs 2 del base)  
% ✓ 10 strumenti (vs 2 del base)
% ✓ 10 posizioni (vs 4 del base)
% ✓ Piano richiede 5 azioni cucina + 4 azioni mangia + spostamenti
% ✓ Spazio degli stati: 8×10×10×10 = 8,000 combinazioni possibili
% 
% ASPETTATIVA: Scaling lineare del numero di oggetti
% dovrebbe portare a ~2-3 secondi vs 1.6s del file base