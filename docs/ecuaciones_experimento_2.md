# Ecuaciones Parametrizadas — Experimentos A y B (2)

Documento consolidado de ecuaciones y parámetros estimados para la dinámica poblacional de la anchoveta peruana (*Engraulis ringens*) bajo la influencia de factores abióticos y fitoplancton.

---

# PARTE 1: Experimento A (Línea Base Abiótica — Réplica Castillo et al. 2018)

Evalúa la capacidad explicativa de los parámetros oceanográficos y climáticos locales (*SST, SSS, SSO, dc, ONI 1+2*).

## 1.1 Formulación General GAM Tweedie (Castillo et al., 2018)

$$Y(anch) = \beta_0 + s(SST) + s(SSS) + s(SSO) + s(dc) + s(year) + te(long, lat) + s(ONI_{1+2}) + \epsilon$$

* **Distribución:** Tweedie ($\mathbb{E}[Y] = \mu$, $\text{Var}(Y) = \phi \cdot \mu^p$, con $1 < p < 2$).
* **Capacidad explicativa:** Techo empírico de deviance explicada entre **21.1% y 35.7%**.

---

## 1.2 Ecuación Parametrizada del Experimento A (Ajuste 1998–2024)

$$\begin{aligned}
\mu_t = 879\,817 &+ 95\,974 \cdot z_{SST} - 249\,431 \cdot z_{SST}^2 \\
&+ 17\,098 \cdot z_{SSS} + 23\,934 \cdot z_{SSS}^2 \\
&+ 17\,098 \cdot z_{SSO} + 23\,934 \cdot z_{SSO}^2 \quad \text{[Término $SSO = 6.0\text{ ml/L}$]} \\
&- 309\,272 \cdot z_{dc} + 63\,672 \cdot z_{dc}^2 \\
&- 17\,098 \cdot z_{ONI} + 23\,934 \cdot z_{ONI}^2
\end{aligned}$$

Donde los predictores se normalizan como $z_i = \dfrac{X_i - \bar{X}_i}{\sigma_i}$:
* $z_{SST} = \dfrac{SST - 18.33}{2.01}$
* $z_{SSS} = \dfrac{SSS - 34.83}{0.20}$
* $z_{dc} = \dfrac{dc - 86.22}{12.19}$
* $z_{ONI} = \dfrac{ONI - 0.08}{0.82}$
* Con $SSO = 6.0\text{ ml/L}$ estándar asumido: $z_{SSO} \approx 0.0$.

* **Deviance explicada alcanzada:** **32.89%** ($R^2 = 0.3289$, $AIC = 8427.4$).

---

## 1.3 Índice de Idoneidad de Hábitat Abiótico ($HSI_{\text{abiótico}}$)

$$HSI_{\text{abiótico}} = \Big(S_{SST} \cdot S_{SSS} \cdot S_{O2} \cdot S_{dc}\Big)^{0.25}$$

Asumiendo oxígeno disuelto superficial estándar de $SSO = 6.0\text{ ml/L}$ ($S_{O2} = 1.0$):

$$HSI_{\text{abiótico}} = \Big(S_{SST} \cdot S_{SSS} \cdot 1.0 \cdot S_{dc}\Big)^{0.25} = \Big(S_{SST} \cdot S_{SSS} \cdot S_{dc}\Big)^{0.25}$$

---

# PARTE 2: Experimento B / Experimento 2 (Contribución del Fitoplancton)

Incorpora la clorofila-$a$ y variables de productividad para evaluar la ganancia predictiva sobre la línea base abiótica.

## 2.1 Índice de Idoneidad del Hábitat Trófico ($HSI_B$)

$$HSI = \Big(S_{SST} \cdot S_{SSS} \cdot S_{O2} \cdot S_{dc} \cdot S_{Chl}\Big)^{0.20}$$

Asumiendo oxígeno disuelto superficial estándar de $SSO = 6.0\text{ ml/L}$ ($S_{O2} = 1.0$):

$$HSI = \Big(S_{SST} \cdot S_{SSS} \cdot 1.0 \cdot S_{dc} \cdot S_{Chl}\Big)^{0.20} = \Big(S_{SST} \cdot S_{SSS} \cdot S_{dc} \cdot S_{Chl}\Big)^{0.20}$$

### Funciones de Idoneidad Trapezoidales ($S_k$):

$$S_{SST}(SST) = \begin{cases} 
1.0, & 16.0 \le SST \le 22.0\text{ }^\circ\text{C} \\ 
\max\left(0.0,\; 1.0 - \dfrac{16.0 - SST}{2.5}\right), & SST < 16.0\text{ }^\circ\text{C} \\ 
\max\left(0.0,\; 1.0 - \dfrac{SST - 22.0}{2.5}\right), & SST > 22.0\text{ }^\circ\text{C} 
\end{cases}$$

$$S_{SSS}(SSS) = \begin{cases} 
1.0, & 34.00 \le SSS \le 35.20 \\ 
\max\left(0.0,\; 1.0 - \dfrac{34.00 - SSS}{0.40}\right), & SSS < 34.00 \\ 
\max\left(0.0,\; 1.0 - \dfrac{SSS - 35.20}{0.40}\right), & SSS > 35.20 
\end{cases}$$

$$S_{dc}(dc) = \max\left(0.0,\; 1.0 - \frac{dc}{150.0}\right), \quad dc \text{ en millas náuticas}$$

$$S_{Chl}(Chl_a) = \begin{cases} 
1.0, & 2.50 \le Chl_a \le 8.00\text{ mg/m}^3 \\ 
\max\left(0.0,\; 1.0 - \dfrac{2.50 - Chl_a}{1.50}\right), & Chl_a < 2.50\text{ mg/m}^3 \\ 
\max\left(0.0,\; 1.0 - \dfrac{Chl_a - 8.00}{1.50}\right), & Chl_a > 8.00\text{ mg/m}^3 
\end{cases}$$

$$S_{O2}(SSO = 6.0) = 1.0$$

---

## 2.2 Capacidad de Carga Ambiental Dinámica $K(SST, Chl_a)$

$$K(SST, Chl_a) = 1.15 \times 10^6 \cdot \left(\frac{Chl_a}{3.70}\right)^{0.050} \cdot \exp\Big(-0.1419 \cdot \max(0,\; SST - 19.0)^2\Big)\quad \text{[toneladas / mes]}$$

En escala anualizada:

$$K_{\text{anual}}(SST, Chl_a) = 1.38 \times 10^7 \cdot \left(\frac{Chl_a}{3.70}\right)^{0.050} \cdot \exp\Big(-0.1419 \cdot \max(0,\; SST - 19.0)^2\Big)\quad \text{[toneladas / año]}$$

---

## 2.3 Modelo Dinámico de Biomasa Acoplada (Schaefer–NPZ)

$$\frac{dB}{dt} = 1.010 \cdot B \cdot \left(1 - \frac{B}{12 \cdot K(SST, Chl_a)}\right) - C_t$$

Donde:
* $B$: Biomasa total de anchoveta en toneladas.
* $r = 1.010$: Tasa intrínseca neta de crecimiento poblacional.
* $C_t$: Desembarque o captura mensual en toneladas.

---

## 2.4 Modelo Aditivo Generalizado (GAM con Fitoplancton y Tweedie $p=1.950$)

$$\mathbb{E}[Y_t] = \mu_t, \quad \text{Var}(Y_t) = \phi \cdot \mu_t^{1.950}$$

Con los predictores estandarizados $z_i = \dfrac{X_i - \bar{X}_i}{\sigma_i}$:

$$\begin{aligned}
\mu_t = 724\,396 &- 18\,743 \cdot z_{SST} - 316\,865 \cdot z_{SST}^2 \\
&+ 170\,502 \cdot z_{SSS} - 141\,150 \cdot z_{SSS}^2 \\
&+ 0.0 \quad \text{[Término $SSO = 6.0\text{ ml/L}$]} \\
&- 638\,774 \cdot z_{dc} + 356\,293 \cdot z_{dc}^2 \\
&- 170\,502 \cdot z_{ONI} - 141\,150 \cdot z_{ONI}^2 \\
&- 239\,791 \cdot z_{Chl} + 212\,742 \cdot z_{Chl}^2
\end{aligned}$$

Donde los parámetros de estandarización $(\bar{X}, \sigma)$ son:
* $z_{SST} = \dfrac{SST - 18.33}{2.01}$
* $z_{SSS} = \dfrac{SSS - 34.83}{0.20}$
* $z_{dc} = \dfrac{dc - 86.22}{12.19}$
* $z_{ONI} = \dfrac{ONI - 0.08}{0.82}$
* $z_{Chl} = \dfrac{Chl_a - 3.70}{1.47}$

* **Deviance explicada alcanzada:** **41.96%** ($R^2 = 0.4196$, $AIC = 8388.4$).
* **Ganancia científica frente a Exp. A:** $+9.07\%$ de deviance ($F = 24.697$, $p = 1.08 \times 10^{-10}$).

---

## 2.5 Sistema EDO de Cadena Trófica Diaria (Pino & Salazar 2022)

Para la interacción en escala diaria entre Fitoplancton ($F$), Zooplancton ($Z$) y Anchoveta ($A$):

$$\frac{dF}{dt} = 1.20 \cdot F \left(1 - \frac{F}{0.60}\right) - \frac{2.00 \cdot F \cdot Z}{0.80 + F} - \frac{0.70 \cdot F \cdot A}{0.80 + F} - 0.02 \cdot F$$

$$\frac{dZ}{dt} = \frac{1.55 \cdot F \cdot Z}{0.80 + F} - \frac{0.90 \cdot Z \cdot A}{0.80 + F} - 0.03 \cdot Z$$

$$\frac{dA}{dt} = \frac{0.50 \cdot F \cdot A}{0.80 + F} + \frac{0.70 \cdot Z \cdot A}{0.80 + Z} - 0.25 \cdot A$$

---

## 2.6 Mapeo de Variables y Fuentes de Datos

### Variables por Ecuación

| Ecuación | Variable | Descripción | Unidades | Disponibilidad |
|----------|----------|-------------|----------|----------------|
| **2.1 HSI_B** | SST | Temperatura superficial del mar | °C | anchoveta.py (simulado) |
| | SSS | Salinidad superficial | PSU | anchoveta.py (simulado) |
| | SSO | Oxígeno disuelto superficial | ml/L | anchoveta.py (simulado, constante 6.0) |
| | dc | Distancia a la costa | millas náuticas | anchoveta.py (simulado) |
| | Chl_a | Clorofila-a | mg/m³ | experimentob.py (OC-CCI), anchoveta.py (simulado) |
| **2.2 K(SST, Chl_a)** | SST | Temperatura superficial del mar | °C | anchoveta.py (simulado) |
| | Chl_a | Clorofila-a | mg/m³ | experimentob.py (OC-CCI), anchoveta.py (simulado) |
| **2.3 Schaefer–NPZ** | B | Biomasa total de anchoveta | toneladas | anchoveta.py (simulado desde FAO) |
| | K(SST, Chl_a) | Capacidad de carga | toneladas/mes | Calculado con SST y Chl_a |
| | C_t | Captura mensual | toneladas | anchoveta.py (simulado desde FAO) |
| **2.4 GAM** | z_SST | SST estandarizado | adimensional | anchoveta.py (simulado) |
| | z_SSS | SSS estandarizado | adimensional | anchoveta.py (simulado) |
| | z_dc | dc estandarizado | adimensional | anchoveta.py (simulado) |
| | z_ONI | ONI estandarizado | adimensional | anchoveta.py (simulado) |
| | z_Chl | Chl_a estandarizado | adimensional | experimentob.py (OC-CCI), anchoveta.py (simulado) |
| **2.5 EDO Trófica** | F | Fitoplancton | mg C/m³ | experimentob.py (carbono fitoplancton) |
| | Z | Zooplancton | mg C/m³ | Pendiente (IMARPE) |
| | A | Anchoveta | toneladas | anchoveta.py (simulado) |

### Fuentes de Datos en el Código

#### experimentob.py (datos satelitales)
- **PDO NOAA**: Índice PDO mensual vía ERDDAP/PSL
- **Nutrientes WOA 2023**: Nitrato, fosfato, silicato (climatología mensual, sin variación interanual)
- **Clorofila OC-CCI**: Serie mensual 1998-2022 (ESA Ocean Colour CCI v6)
- **Fracciones de tamaño Brewin**: Pico, nano, micro desde clorofila (Brewin et al. 2010)
- **Carbono fitoplancton**: Conversión Chl:C con ratio constante (0.02)

#### anchoveta.py (datos simulados/estimados)
- **SST**: Temperatura superficial con estacionalidad y anomalías ENSO
- **SSS**: Salinidad superficial correlacionada con ENSO
- **SSO**: Oxígeno superficial correlacionado con ENSO
- **dc**: Distancia a la costa con variación ENSO
- **ONI**: Índice Niño 1+2 (anomalías históricas aproximadas)
- **Chl_a**: Clorofila-a con estacionalidad y respuesta ENSO
- **Biomasa (y_t)**: Estimada desde desembarques FAO con ratio stock/captura
- **Captura (C_t)**: Desembarques FAO distribuidos mensualmente

### Parámetros de Estandarización (GAM)

| Variable | Media (μ) | Desviación (σ) | Fórmula z-score |
|----------|-----------|----------------|-----------------|
| SST | 18.33 °C | 2.01 | z = (SST - 18.33) / 2.01 |
| SSS | 34.83 | 0.20 | z = (SSS - 34.83) / 0.20 |
| dc | 86.22 nm | 12.19 | z = (dc - 86.22) / 12.19 |
| ONI | 0.08 | 0.82 | z = (ONI - 0.08) / 0.82 |
| Chl_a | 3.70 mg/m³ | 1.47 | z = (Chl_a - 3.70) / 1.47 |

### Notas sobre Datos Simulados vs Satelitales

1. **Datos satelitales (experimentob.py)**: Representan observaciones reales del océano vía sensores remotos. Son más confiables para análisis espacial y temporal pero tienen limitaciones (nubes, resolución costera).

2. **Datos simulados (anchoveta.py)**: Son aproximaciones basadas en patrones climáticos conocidos y datos históricos de desembarques. Útiles para pruebas de concepto y desarrollo de modelos, pero no deben usarse para resultados científicos finales sin validación.

3. **Nutrientes WOA**: La climatología WOA23 no tiene variación interanual. Para series temporales de nutrientes se recomienda usar reanálisis CMEMS (módulo `nutrientes.py`).

4. **Zooplancton**: Pendiente de implementación (datos IMARPE). Necesario para el modelo EDO trófico (2.5).

5. **PDO**: Disponible en experimentob.py pero no usado directamente en las ecuaciones del Experimento B. Puede ser útil como covariable adicional en análisis extendidos.
