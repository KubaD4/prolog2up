% Auto-generated from cucinare.pl
% Series: OBJECTS — target_total=16, baseline_total=5
% Azioni invariate.

cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).
cuoco(cuoco_2).
cibo(cibo_2).
strumento(strumento_2).
piano(piano_2).
luce(luce_2).
cuoco(cuoco_3).
cibo(cibo_3).
strumento(strumento_3).
piano(piano_3).
luce(luce_3).
cuoco(cuoco_4).

action(cucina(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]
).

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

action(sposta_qualsiasi(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]
).

