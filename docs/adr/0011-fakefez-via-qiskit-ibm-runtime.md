# 0011. FakeFez vía qiskit-ibm-runtime, instalado solo en su extra

## Estado

Aceptada

## Contexto

El extra de ruido de hardware (#12) necesita el modelo de ruido de un backend real de IBM. `FakeFez` está en `qiskit_ibm_runtime.fake_provider`, pero `qiskit-ibm-runtime` no está en nixpkgs: no existe en el rev de `flake.lock` (`0bb82723…`) ni en `master` (404 en `pkgs/development/python-modules/qiskit-ibm-runtime`).

`requirements.txt` es la fuente única de dependencias: `flake.nix` arma el dev shell con `ps.<nombre>` para cada línea, y el check `notebook-deps` compara la **primera** línea `%pip install` del notebook con `requirements.txt`. Agregar el paquete ahí rompería `nix develop` y `nix flake check`.

## Decisión

`qiskit-ibm-runtime==0.47.0` (la versión instalada y probada localmente) **no** va en `requirements.txt` ni en la celda `%pip` principal. Se instala con un `%pip install` propio en la primera celda de código de la sección de #12. El check de Nix sigue pasando, porque solo mira la primera línea `%pip install`.

## Alternativas consideradas

- Agregarlo a `requirements.txt` y a la celda principal: rompe el dev shell de Nix.
- Empaquetarlo en `flake.nix` con `buildPythonPackage` desde PyPI: posible, pero agrega mantenimiento a un extra opcional.
- Exceptuarlo en `flake.nix`: cambia la regla de "fuente única" para todo el equipo.
- No usar FakeFez: se pierde el extra.

## Consecuencias

- En Colab el extra funciona sin pasos manuales.
- Fuera de Colab (incluido el shell de Nix) hay que instalar `qiskit-ibm-runtime` a mano en el entorno antes de correr esa sección; si no, la sección #12 falla y el resto del notebook no se ve afectado hasta ahí.
- Si el equipo decide empaquetarlo en `flake.nix`, se mueve a `requirements.txt` y a la celda principal.

## Referencias

Issue #12; `requirements.txt`; `flake.nix` (check `notebook-deps`); `flake.lock`.
