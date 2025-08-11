% Auto-generated from cucinare.pl
% Series: NEG_PRECOND — +2 per azione
% Precondizioni negative false: blocked_i(dummy).

cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).

action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo)],
  [blocked_1(dummy), blocked_2(dummy)],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]).

action(mangia(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona)],
  [blocked_1(dummy), blocked_2(dummy)],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]).

action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [su(_, Strumento), blocked_1(dummy), blocked_2(dummy)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]).

