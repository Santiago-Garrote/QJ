# 0004. Registrar decisiones con ADRs

## Estado

Aceptada

## Contexto

El notebook `notebooks/h4_vqe.ipynb` lo editan varias personas y varias issues a la vez. Muchas decisiones (qué medir, con qué, qué descartar) quedan en chats y commits y se pierden.

## Decisión

Cada decisión de arquitectura o método se registra como un ADR corto en `docs/adr/`, estilo MADR, en español, numerado y con estado. Un ADR aceptado no se reescribe: se agrega otro que lo reemplace.

## Alternativas consideradas

- Solo la celda final del notebook 'Qué decidimos, por qué y qué no funcionó' (no cubre decisiones fuera del notebook).
- Mensajes de commit (difíciles de encontrar y sin alternativas).

## Consecuencias

Las decisiones y sus cifras quedan junto al código. Cuesta unos minutos por decisión.

## Referencias

docs/adr/README.md
