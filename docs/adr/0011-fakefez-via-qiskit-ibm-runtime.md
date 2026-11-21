# 0011. FakeFez vía qiskit-ibm-runtime

## Estado

Aceptada

## Contexto

El extra de ruido de hardware necesita un backend fake de 156 qubits.

## Decisión

Se usa `FakeFez` de `qiskit_ibm_runtime.fake_provider`. Se agregó `qiskit-ibm-runtime==0.47.0` a `requirements.txt` y al `%pip` del notebook, con el mismo pin. 0.47.0 es la versión instalada local; el paquete no está en nixpkgs para el rev de `flake.lock` (0bb82723..., 404 en el directorio y sin entrada en python-packages.nix), así que la versión de nixpkgs queda SIN VERIFICAR.

## Alternativas consideradas

- Buscar otros revs de nixpkgs.
- No usar FakeFez.

## Consecuencias

`nix flake check` no pasa tal cual: hace falta empaquetar la dependencia en `flake.nix` o una excepción explícita.

## Referencias

Issue #12; requirements.txt; flake.lock.
