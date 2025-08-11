% Auto-generated from cucinare.pl
% Series: ACTIONS — target_actions=12, baseline_actions=3
% Duplicate con vincolo statico sistema_ok(ok).

cuoco(mario).
cibo(pasta).
strumento(pentola).
piano(tavolo).
luce(led).
sistema_ok(ok).

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

action(cucina_alt1(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo), sistema_ok(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]).

action(mangia_alt2(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), sistema_ok(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]).

action(sposta_qualsiasi_alt3(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione), sistema_ok(ok)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]).

action(cucina_alt4(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo), sistema_ok(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]).

action(mangia_alt5(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), sistema_ok(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]).

action(sposta_qualsiasi_alt6(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione), sistema_ok(ok)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]).

action(cucina_alt7(Persona, Cibo, Strumento, Tavolo),
  [crudo(Cibo), disponibile(Strumento), vuoto(Tavolo), sistema_ok(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Tavolo)],
  [
    del(crudo(Cibo)),
    del(vuoto(Tavolo)),
    add(cotto(Cibo)),
    add(pieno(Tavolo))
  ]).

action(mangia_alt8(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), sistema_ok(ok)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]).

action(sposta_qualsiasi_alt9(Persona, Strumento, Destinazione),
  [disponibile(Strumento), vuoto(Destinazione), sistema_ok(ok)],
  [su(_, Strumento)],
  [],
  [cuoco(Persona), piano(Destinazione), strumento(Strumento)],
  [
    del(disponibile(Strumento)),
    del(vuoto(Destinazione)),
    add(su(Destinazione, Strumento))
  ]).

