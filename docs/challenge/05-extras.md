# 05 · Cosas extra

Nada de esto es obligatorio. Son ideas para quienes tengan tiempo o quieran agregar algo que diferencie su trabajo, y solo se tienen en cuenta si el desafío central está completo.

- **Simulador con ruido:** repetir la curva (o parte de ella) con el modelo de ruido de `ruido.py`, igual para todos: compuertas `cz`, `sx`, `x` y `rz`, qubits conectados en línea, y una probabilidad de error de 0,1 % por `cz` y 0,005 % por compuerta de un qubit.
- **Ruido de hardware real:** repetir un punto estirado con el ruido completo de `FakeFez`.
- **Mitigación de errores:** aplicar técnicas que funcionarían en una computadora real, como *Zero Noise Extrapolation* (ZNE) o corrección de errores de *readout*.
- **Menos qubits:** reducir a 6 qubits o menos usando simetrías y medir cuánto mejora.
- **Precisión química:** lograrla en toda la zona estirada ($d \geq 1{,}8\ \text{Å}$).
- **Comparar ansätze:** probar distintos *ansätze* y comparar precisión, profundidad y costo.
- **VQE vs. SQD:** correr SQD en la zona estirada y compararlo con VQE, o mostrar si las muestras cuánticas le ganan al azar cuando se pone un tope al tamaño del subespacio.
- **Otra geometría:** correr otra forma de $\mathrm{H_4}$ cambiando solo la geometría.

> Nota: `ruido.py` no está incluido en el snapshot de la página (`../source/`). Hay que conseguirlo de los organizadores.
