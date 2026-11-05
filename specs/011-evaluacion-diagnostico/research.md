# Research: Evaluación del diagnóstico con abstención, intervalos e k-fold

## 1. Fundamentos Matemáticos y Estadísticos

### 1.1 Métricas Conjuntas con Abstención
Dado un conjunto de $N$ observaciones $(x_i, y_i)$ con $y_i \in \{0, \dots, K-1\}$ y vector de probabilidades softmax $p_i \in \mathbb{R}^K$:
- **Predicción cruda (argmax)**: $\tilde{y}_i = \operatorname{argmax}_c p_{i, c}$.
- **Confianza máxima**: $c_i = \max_c p_{i, c}$.
- **Abstención con umbral $\theta = 0.80$**:
  $$\hat{y}_i = \begin{cases} \tilde{y}_i & \text{si } c_i \ge \theta \\ \text{UNCERTAIN} & \text{si } c_i < \theta \end{cases}$$

Se definen tres conjuntos disjuntos exhaustivos de muestras:
1. **Aciertos con alta confianza**: $\{i : \hat{y}_i = y_i \land c_i \ge \theta\}$. Proporción: $\text{Acc}_{\text{abst}} = \frac{N_{\text{acierto}}}{N}$.
2. **Abstenciones**: $\{i : c_i < \theta\}$. Proporción: $\text{Tasa}_{\text{abst}} = \frac{N_{\text{abst}}}{N}$.
3. **Errores con alta confianza**: $\{i : \tilde{y}_i \ne y_i \land c_i \ge \theta\}$. Proporción: $\text{Tasa}_{\text{err}} = \frac{N_{\text{err}}}{N}$.

Propiedad matemática fundamental:
$$\text{Acc}_{\text{abst}} + \text{Tasa}_{\text{abst}} + \text{Tasa}_{\text{err}} = 1.0$$
Además, se calcula la **exactitud sobre las muestras decididas**:
$$\text{Acc}_{\text{decididas}} = \frac{N_{\text{acierto}}}{N_{\text{acierto}} + N_{\text{err}}} \quad (\text{si } N_{\text{acierto}} + N_{\text{err}} > 0)$$

---

### 1.2 Intervalos de Confianza de Wilson para Proporciones
El intervalo asintótico estándar de Wald ($p \pm z \sqrt{p(1-p)/n}$) falla gravemente cerca de los límites ($p \to 0$ o $p \to 1$) y en muestras pequeñas, produciendo valores fuera de $[0, 1]$ o intervalos colapsados a ancho cero cuando $k=0$ o $k=n$.

El **intervalo de Wilson score** (Wilson, 1927) invierte la prueba de hipótesis del score y se define como:
$$\hat{p} = \frac{k}{n}, \quad \tilde{p} = \frac{\hat{p} + \frac{z^2}{2n}}{1 + \frac{z^2}{n}}$$
$$\text{SE}_{\text{Wilson}} = \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat{p}(1 - \hat{p})}{n} + \frac{z^2}{4n^2}}$$
$$L = \max\left(0, \tilde{p} - \text{SE}_{\text{Wilson}}\right), \quad U = \min\left(1, \tilde{p} + \text{SE}_{\text{Wilson}}\right)$$
Con $z = 1.95996$ para el 95 % de nivel de confianza.

---

### 1.3 Validación Cruzada Agrupada (Group K-Fold)
En reactores PWR:
- Las corridas de LOCA y LOCAC vienen en pares de igual área de rotura (severidad pareada).
- Los casos de ATWS y TRIP_OK pueden tener gemelos con perturbaciones similares.
- Para evitar fuga entre entrenamiento y validación cruzada, el particionado debe hacerse por **grupos de severidad** (mismo criterio de 004).
- Con $k=5$ folds, cada fold evalúa aproximadamente el 20 % de las corridas, y se calcula la media y desviación estándar de las métricas entre los 5 folds:
$$\mu = \frac{1}{k} \sum_{j=1}^k m_j, \quad s = \sqrt{\frac{1}{k-1} \sum_{j=1}^k (m_j - \mu)^2}$$
Intervalo de confianza al 95 % para la media de la métrica en la población de folds:
$$\mu \pm t_{0.025, k-1} \frac{s}{\sqrt{k}} \quad (\text{para } k=5, t_{0.025, 4} \approx 2.776)$$
