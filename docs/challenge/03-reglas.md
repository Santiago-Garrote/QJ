# 03 · Reglas

- El algoritmo del desafío central es **VQE**. SQD no vale para el desafío central, porque con tan pocos qubits hasta muestras al azar dan la respuesta exacta (pueden usarlo como extra, ver [05 · Cosas extra](05-extras.md)).
- Las energías reportadas tienen que salir de medir circuitos con `EstimatorV2` o `SamplerV2` de `qiskit_aer`, no de leer el estado del simulador.
- Pueden buscar los parámetros como quieran, incluso sin ruido.
- Los métodos clásicos no sirven como resultados: solo para comparar y para elegir puntos de partida.
- En la zona estirada, argumenten por qué su resultado es confiable antes de compararlo con FCI.
