# 01 · Motivación

Más o menos la mitad de la comida del mundo depende de fertilizantes hechos con amoníaco, y el amoníaco se fabrica con el proceso Haber-Bosch: se rompen moléculas de nitrógeno a unos 450 °C y a cientos de atmósferas de presión. Solo ese proceso se lleva cerca del 1-2 % de toda la energía que consume la humanidad. Mientras tanto, unas bacterias que viven en las raíces de la soja hacen lo mismo a temperatura ambiente, gracias a una enzima (la nitrogenasa). Si entendiéramos exactamente cómo lo logran, podríamos diseñar catalizadores que hagan fertilizante gastando una fracción de esa energía.

¿Por qué no lo sabemos todavía? Porque para eso hay que calcular con mucha precisión la energía de los electrones mientras se rompe un enlace, y justamente ahí es donde las computadoras clásicas no dan abasto. El mismo problema aparece al diseñar baterías para celulares y autos eléctricos o al predecir cómo un medicamento se une a una proteína. Es uno de los casos de uso más prometedores de las computadoras cuánticas.

Obviamente, en esta Jam no vamos a resolver la nitrogenasa. Pero la pregunta de fondo es la misma, y la podemos atacar con una molécula de juguete: cuatro hidrógenos en fila.

## La energía de una molécula

Casi toda la química se reduce a una pregunta: ¿cuál es la energía más baja que puede tener una molécula para una cierta disposición de sus núcleos? Si acercamos demasiado los núcleos, sus cargas positivas se repelen y la energía sube. Si los alejamos demasiado, la molécula deja de existir. En el medio hay una distancia en la que la energía es mínima: la **distancia de equilibrio** $R_e$. La diferencia entre la energía de los átomos separados y ese mínimo es la **energía de disociación** $D_e$, es decir, lo que cuesta romper la molécula.

Para cada distancia, esa energía mínima es el autovalor más chico $E_0$ del hamiltoniano electrónico $\hat H$ de la molécula. El problema es que la dimensión de $\hat H$ crece exponencialmente con el tamaño del sistema, y por eso los métodos clásicos exactos (como FCI) dejan de ser viables muy rápido. Los métodos clásicos aproximados (como CCSD) funcionan muy bien cerca del equilibrio, pero acumulan cada vez más error a medida que se estiran los enlaces.

## De la molécula a los qubits

El camino tiene dos partes:

1. **Obtener el hamiltoniano:** como $\hat H$ es distinto para cada distancia internuclear, hay que construirlo una vez por punto de la curva. Con Hartree-Fock se definen los orbitales moleculares (espín-orbitales) y se escribe $\hat H$ con operadores de creación y aniquilación fermiónicos:

   $$\hat H = \sum_{pq} h_{pq}\, a_p^\dagger a_q + \frac{1}{2} \sum_{pqrs} h_{pqrs}\, a_p^\dagger a_q^\dagger a_r a_s.$$

   Luego una transformación como la de Jordan-Wigner reescribe esos operadores con matrices de Pauli, y el hamiltoniano queda como una suma de cadenas de Pauli que se pueden medir en un circuito cuántico:

   $$\hat H = \sum_k c_k P_k, \qquad P_k \in \{I, X, Y, Z\}^{\otimes n}.$$

2. **Encontrar su estado fundamental:** el *Variational Quantum Eigensolver* (VQE) propone un estado de prueba $|\psi(\boldsymbol\theta)\rangle$ preparado por un circuito parametrizado (el *ansatz*), mide su energía en la computadora cuántica y usa un optimizador clásico para ajustar los parámetros $\boldsymbol\theta$. El principio variacional garantiza que

   $$E(\boldsymbol\theta) = \left\langle \psi(\boldsymbol\theta) \,\middle|\, \hat H \,\middle|\, \psi(\boldsymbol\theta) \right\rangle \geq E_0,$$

   así que minimizar $E(\boldsymbol\theta)$ nos acerca a $E_0$ desde arriba.

## El ruido

En 2017, IBM calculó con VQE las curvas de energía de $\mathrm{H_2}$, $\mathrm{LiH}$ y $\mathrm{BeH_2}$ en un procesador de 6 qubits (Kandala et al., *Nature* 549, 242). El gran obstáculo era, y sigue siendo, el ruido. Cada compuerta tiene una probabilidad de fallar, y un circuito con muchas compuertas termina devolviendo basura. Por eso, en este desafío no alcanza con llegar al número correcto: importa **cómo** se llega, con cuántas compuertas y con cuántas mediciones.
