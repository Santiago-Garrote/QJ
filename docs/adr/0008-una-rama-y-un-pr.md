# 0008. Una rama y un PR, commits con Refs y no Closes

## Estado

Aceptada

## Contexto

Todas las issues editan el mismo notebook. Con stand-ins, una issue no está completa hasta que lleguen las piezas reales.

## Decisión

Una sola rama (`feat/lruiz49-issues`) y un PR. Los commits usan `Refs #N`, no `Closes #N`.

## Alternativas consideradas

- Una rama por issue: conflictos constantes en el JSON del notebook.
- `Closes`: cerraría issues que dependen de stand-ins.

## Consecuencias

Las issues se cierran a mano cuando se verifican con piezas reales. Seis commits en la integración (a46326e a c1a67dc).

## Referencias

Commits a46326e, 2c78a14, 50faaf5, f82b9db, 5b8e50e, c1a67dc.
