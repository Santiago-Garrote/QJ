# Glosario

Explicado simple. Los términos técnicos quedan como en el enunciado.

## El desafío en una frase

Tenemos 4 átomos de hidrógeno (H₄) en fila, como bolitas en un palito. Los vamos separando de a poco y, a cada distancia $d$, le preguntamos a una computadora cuántica: **¿cuánta energía tiene la molécula ahora?** Cuando los átomos están muy lejos, las computadoras normales se equivocan. Nosotros queremos equivocarnos menos.

## Qué hay que lograr

1. **Dibujar la energía $E(d)$.** Con VQE, calcular la energía en al menos 10 distancias, desde 0,6 hasta 3,0 Å. Cada número va con su $\pm\sigma$, o sea cuánto nos podemos estar equivocando. Después la dibujamos al lado de CCSD y FCI.
2. **$R_e$ y $D_e$.** $R_e$ es la distancia donde la molécula está más cómoda (energía más baja). $D_e$ es cuánta energía cuesta romperla: $D_e = E(3{,}0\ \text{Å}) - E(R_e)$.
3. **Ganarle a CCSD.** Cuando los átomos están lejos ($d \geq 1{,}8$ Å), CCSD se equivoca. Nuestro error, sumándole la $\sigma$, tiene que ser más chico que el de CCSD: $|E_\text{VQE} - E_\text{FCI}| + \sigma < |E_\text{CCSD} - E_\text{FCI}|$.
4. **Precisión química (meta máxima).** Equivocarnos tan poquito que a un químico ya no le importa: menos de 1,6 mHa en esa misma zona lejana.

## Palabras clave

| Término | Qué es |
|---|---|
| **Energía** | Qué tan "cómoda" está la molécula. Menos energía es más cómoda. Se mide en Hartree (Ha); 1 mHa es la milésima parte. |
| **Hamiltoniano** | La receta que dice cuánta energía tiene la molécula. Hay una distinta para cada distancia $d$. |
| **Qubit** | La cajita de información de la computadora cuántica. Acá usamos 8, uno por cada lugar donde puede estar un electrón. |
| **Jordan-Wigner** | El traductor que pasa la receta de la molécula al idioma de los qubits (letras I, X, Y, Z). |
| **VQE** | Un juego de "frío o caliente": probamos un estado, medimos su energía, giramos unas perillas y repetimos hasta encontrar la energía más baja. |
| **Ansatz** | El circuito con perillas (los parámetros) que el VQE va girando. Si es bueno, puede llegar a la respuesta correcta. |
| **Shots** | Cuántas veces medimos. Más shots dan un número más seguro pero tardan más. |
| **σ (barra de error)** | Cuánto puede bailar nuestro número por haber medido pocas veces. |
| **Compuerta cz** | Una operación entre dos qubits. Es la que más falla en una máquina real, así que conviene usar pocas. |
| **Ruido** | Los errores que comete una computadora cuántica de verdad. Más compuertas significa más ruido. |
| **Hartree-Fock (HF)** | Una primera respuesta clásica, rápida y aproximada. Es el punto de partida. |
| **CCSD** | Un método clásico muy bueno cerca del equilibrio, pero que se equivoca cuando estiramos los átomos. Es el rival. |
| **FCI** | La respuesta exacta. Para una molécula chiquita como esta se puede calcular, y la usamos para corregir. |
| **STO-3G** | La versión más simple de cómo describimos los electrones de cada átomo. Por eso alcanzan 8 qubits. |
| **SQD** | Otro método cuántico. Acá no vale para lo principal, solo como extra. |
