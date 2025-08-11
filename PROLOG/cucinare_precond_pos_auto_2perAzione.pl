% Auto-generated from cucinare.pl
% Series: POS_PRECOND — +2 per azione
% Precondizioni statiche vere: flag_pos_i(ok).

cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).
flag_pos_1(ok).
flag_pos_2(ok).

action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo), flag_pos_1(ok), flag_pos_2(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]).

action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), flag_pos_1(ok), flag_pos_2(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]).

action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione), flag_pos_1(ok), flag_pos_2(ok)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]).

