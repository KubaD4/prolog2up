% VARIAZIONE 1: Extended Clean - Più oggetti, fluenti specifici per tipo
% Struttura: Basata su cucinare.pl funzionante, NO supertypes

%%%%%%%%%%%%%%%%%%%%%%%
% kb
%%%%%%%%%%%%%%%%%%%%%%%
% Più cuochi
cuoco(mario).
cuoco(luigi).
cuoco(anna).

% Più cibi
cibo(pasta).
cibo(riso).
cibo(pizza).
cibo(minestrone).

% Più strumenti
strumento(pentola).
strumento(padella).
strumento(forno).
strumento(casseruola).

% Più piani
piano(tavolo1).
piano(tavolo2).
piano(bancone).
piano(isola).

%%%%%%%%%%%%%%%%%%%%%%%
% init
%%%%%%%%%%%%%%%%%%%%%%%
init_state([
  % Stati cibi (solo cibo)
  crudo(pasta), crudo(riso), crudo(pizza), crudo(minestrone),
  
  % Stati strumenti (solo strumento)  
  disponibile_strumento(pentola), disponibile_strumento(padella), 
  disponibile_strumento(forno), disponibile_strumento(casseruola),
  
  % Stati cuochi (solo cuoco)
  ha_fame(mario), ha_fame(luigi), ha_fame(anna),
  libero_cuoco(mario), libero_cuoco(luigi), libero_cuoco(anna),
  
  % Stati piani (solo piano)
  vuoto_piano(tavolo1), vuoto_piano(tavolo2), vuoto_piano(bancone), vuoto_piano(isola)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% goal
%%%%%%%%%%%%%%%%%%%%%%%
goal_state([
  % Tutti i cibi cotti
  cotto(pasta), cotto(riso), cotto(pizza), cotto(minestrone),
  
  % Tutti soddisfatti  
  soddisfatto(mario), soddisfatto(luigi), soddisfatto(anna),
  
  % Almeno due piani occupati
  pieno_piano(tavolo1), pieno_piano(tavolo2),
  
  % Strumenti tornati disponibili
  disponibile_strumento(pentola), disponibile_strumento(padella)
]).

%%%%%%%%%%%%%%%%%%%%%%%
% actions
%%%%%%%%%%%%%%%%%%%%%%%

% Cucinare con più controlli (arity 4)
action(cucina_extended(Persona, Cibo, Strumento, Piano),
  [crudo(Cibo), disponibile_strumento(Strumento), libero_cuoco(Persona), vuoto_piano(Piano)],
  [occupato_piano(Piano), strumento_in_uso(Strumento)],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(crudo(Cibo)), del(disponibile_strumento(Strumento)), 
    del(libero_cuoco(Persona)), del(vuoto_piano(Piano)),
    add(cotto(Cibo)), add(strumento_in_uso(Strumento)), 
    add(cuoco_impegnato(Persona)), add(pieno_piano(Piano))
  ]
).

% Finire cucina e liberare risorse (arity 4)
action(finisci_cucina(Persona, Cibo, Strumento, Piano),
  [cotto(Cibo), strumento_in_uso(Strumento), cuoco_impegnato(Persona), pieno_piano(Piano)],
  [],
  [],
  [cuoco(Persona), cibo(Cibo), strumento(Strumento), piano(Piano)],
  [
    del(strumento_in_uso(Strumento)), del(cuoco_impegnato(Persona)),
    add(disponibile_strumento(Strumento)), add(libero_cuoco(Persona))
  ]
).

% Mangiare (arity 2)
action(mangia_extended(Persona, Cibo),
  [cotto(Cibo), ha_fame(Persona), libero_cuoco(Persona)],
  [mangiando(Persona)],
  [],
  [cuoco(Persona), cibo(Cibo)],
  [
    del(ha_fame(Persona)),
    add(soddisfatto(Persona))
  ]
).

% Spostare strumento tra piani (arity 3)
action(sposta_strumento_piano(Strumento, PianoDa, PianoA),
  [disponibile_strumento(Strumento), pieno_piano(PianoDa), vuoto_piano(PianoA)],
  [strumento_in_movimento(Strumento)],
  [],
  [strumento(Strumento), piano(PianoDa), piano(PianoA), PianoDa \= PianoA],
  [
    del(pieno_piano(PianoDa)), del(vuoto_piano(PianoA)),
    add(vuoto_piano(PianoDa)), add(pieno_piano(PianoA))
  ]
).

% Preparare workspace (arity 3)
action(prepara_workspace(Persona, Piano, Strumento),
  [libero_cuoco(Persona), vuoto_piano(Piano), disponibile_strumento(Strumento)],
  [workspace_in_prep(Piano)],
  [],
  [cuoco(Persona), piano(Piano), strumento(Strumento)],
  [
    del(libero_cuoco(Persona)), del(vuoto_piano(Piano)), del(disponibile_strumento(Strumento)),
    add(cuoco_impegnato(Persona)), add(workspace_pronto(Piano)), add(strumento_riservato(Strumento))
  ]
).

% Liberare workspace (arity 3)
action(libera_workspace(Persona, Piano, Strumento),
  [cuoco_impegnato(Persona), workspace_pronto(Piano), strumento_riservato(Strumento)],
  [],
  [],
  [cuoco(Persona), piano(Piano), strumento(Strumento)],
  [
    del(cuoco_impegnato(Persona)), del(workspace_pronto(Piano)), del(strumento_riservato(Strumento)),
    add(libero_cuoco(Persona)), add(vuoto_piano(Piano)), add(disponibile_strumento(Strumento))
  ]
).

%%%%%%%%%%%%%%%%%%%%%%%
% Note
%%%%%%%%%%%%%%%%%%%%%%%
% CARATTERISTICHE:
% ✓ Basato su cucinare.pl funzionante
% ✓ Fluenti SPECIFICI per tipo:
%   - disponibile_strumento(strumento) vs libero_cuoco(cuoco)
%   - vuoto_piano(piano) vs pieno_piano(piano)
%   - strumento_in_uso(strumento) vs cuoco_impegnato(cuoco)
% ✓ NO fluenti polimorfici che causano supertypes
% ✓ Più oggetti: 3 cuochi, 4 cibi, 4 strumenti, 4 piani
% ✓ Azioni aggiuntive ma logica semplice
% ✓ Piano fattibile: ~12-15 azioni
% ✓ Arity rispettata: max 4 parametri