% Definizione di oggetti e tipi
block(b1).
block(b2).
pos(1,1).
pos(2,2).
agent(a1).
mela(m1).
vegetale(carota1).
% Stato iniziale
init_state([
  ontable(b1), ontable(b2),
  at(b1,1,1), at(b2,2,2),
  clear(b1), clear(b2),
  available(a1),
  intera(m1),
  cruda(carota1)
]).

% Stato goal
goal_state([
  ontable(b2),
  on(b1, b2),
  at(b1,2,2), at(b2,2,2),
  clear(b1),
  available(a1),
  morsa(m1),
  cotta(carota1)
]).

% Definizione delle azioni
action(move_table_to_block_start(Agent, Block1, Block2, X1, Y1, X2, Y2),
  [available(Agent), ontable(Block1), at(Block1, X1, Y1), at(Block2, X2, Y2), clear(Block2), clear(Block1)],
  [on(_, Block1), on(Block1, _), moving_table_to_block(_, Block1, _, _, _, _, _)],
  [],
  [agent(Agent), pos(X1, Y1), pos(X2, Y2), block(Block1), block(Block2), Block1 \= Block2],
  [
    del(available(Agent)), del(clear(Block1)), del(ontable(Block1)), del(at(Block1, X1, Y1)),
    add(moving_table_to_block(Agent, Block1, Block2, X1, Y1, X2, Y2))
  ]
).

action(move_table_to_block_end(Agent, Block1, Block2, X1, Y1, X2, Y2),
  [moving_table_to_block(Agent, Block1, Block2, X1, Y1, X2, Y2), clear(Block2)],
  [],
  [],
  [agent(Agent)],
  [
    del(clear(Block2)), del(moving_table_to_block(Agent, Block1, Block2, X1, Y1, X2, Y2)),
    add(on(Block1, Block2)), add(at(Block1, X2, Y2)), add(clear(Block1)), add(available(Agent))
  ]
).

action(mangia_mela(Agent, Mela),
  [intera(Mela), available(Agent)],
  [],
  [],
  [agent(Agent), mela(Mela)],
  [
    del(intera(Mela)), del(available(Agent)),
    add(morsa(Mela))
  ]
).

action(cuoci(Agente, Verdura),
  [available(Agente), cruda(Verdura)],
  [],
  [],
  [agent(Agente), vegetale(Verdura)],
  [
    del(cruda(Verdura)),
    add(cotta(Verdura))
  ]
).
