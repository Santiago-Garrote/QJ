# 02 · El desafío

Calcular con VQE la curva de energía de una cadena de cuatro hidrógenos ($\mathrm{H_4}$) mientras se separan sus átomos, y ganarle a CCSD en la zona donde ese método clásico falla. La cadena es recta, con los átomos separados por la misma distancia $d$, en la base STO-3G.

1. **Curva de energía:** calculen $E(d)$ con al menos 10 distancias entre $0{,}6\ \text{Å}$ y $3{,}0\ \text{Å}$, cada energía con su barra de error $\pm\sigma$ (la incertidumbre estadística de la estimación), y compárenla con CCSD y con la energía exacta (FCI).

2. **Equilibrio y disociación:** obtengan la distancia de equilibrio $R_e$ y la energía de disociación, definida como

   $$D_e = E\big(3{,}0\ \text{Å}\big) - E(R_e),$$

   ya que a $3{,}0\ \text{Å}$ los átomos se consideran separados.

3. **Ganarle a CCSD:** desde $1{,}8\ \text{Å}$ en adelante, logren un error menor que el suyo contando la barra de error:

   $$\left|E_{\mathrm{VQE}} - E_{\mathrm{FCI}}\right| + \sigma < \left|E_{\mathrm{CCSD}} - E_{\mathrm{FCI}}\right| \quad \text{para } d \geq 1{,}8\ \text{Å}.$$

4. **Meta máxima:** lleguen a precisión química en esa zona:

   $$\left|E_{\mathrm{VQE}} - E_{\mathrm{FCI}}\right| < 1{,}6\ \text{mHa}.$$
