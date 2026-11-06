# Reporte: capacidad actual de los datos para ANCHOVETA 360

**Fecha:** 6 de noviembre de 2026  
**Proyecto:** ANCHOVETA 360

## 1. Propósito

Este reporte resume qué puede estudiarse actualmente con los datos disponibles y qué significan para la investigación sobre la conectividad entre el océano Austral, el Pacífico Sur, el sistema de Humboldt y la anchoveta peruana (*Engraulis ringens*).

La pregunta general de la investigación es si la variabilidad antártica presenta asociaciones temporales y espaciales con las condiciones del Pacífico Sur y Humboldt, y si esas condiciones se relacionan con la variabilidad de la anchoveta.

## 2. Datos disponibles

### 2.1 Variables ambientales

El proyecto cuenta con un panel mensual de aproximadamente 344 meses con variables procedentes principalmente de CMEMS, NOAA, NASA, NSIDC, IGP/ENFEN y otros productos ambientales. Incluye:

- temperatura y salinidad superficial;
- oxígeno;
- clorofila-a;
- nitrato y fosfato;
- carbono fitoplanctónico;
- Kd490;
- PDO;
- ICEN;
- Niño 1+2;
- extensión del hielo marino antártico;
- índice AAO/SAM;
- productos de viento, circulación y otras variables físicas.

Estos datos tienen una cobertura temporal mucho mayor que las observaciones biológicas. Por ello permiten analizar con bastante detalle la primera parte de la hipótesis:

```text
variabilidad antártica → Pacífico Sur → sistema de Humboldt
```

Se pueden estudiar correlaciones con rezagos, tendencias, cambios de régimen, coherencia temporal y modelos de mediación ambiental.

### 2.2 Biomasa evaluada de RAM Legacy

El pipeline en R incorporó la serie `tb.data` del stock `PANCHPERUNC`, correspondiente a la anchoveta norte-centro del Perú.

La serie contiene 53 años de biomasa total evaluada. Al cruzarla con las variables ambientales disponibles, quedaron 18 años comunes entre 1998 y 2015, de los cuales 17 tienen todos los predictores necesarios para el modelo.

RAM Legacy es una compilación de resultados de evaluaciones de stock. No debe interpretarse como una serie de mediciones acústicas independientes. Su valor principal es proporcionar una respuesta anual de largo plazo para estudiar la relación entre clima, ambiente y biomasa evaluada.

### 2.3 Biomasa desovante histórica

El proyecto cuenta con aproximadamente 96 registros de biomasa desovante entre 1964 y 2020, extraídos de documentación de IMARPE.

Esta serie permite estudiar variabilidad histórica y cambios de régimen, pero debe tratarse con cuidado porque combina diferentes métodos, periodos y tipos de estimación. No debe mezclarse automáticamente con la biomasa total de RAM ni con la biomasa total de cruceros.

### 2.4 Cruceros hidroacústicos

El nuevo archivo [Cruceros_hidroacusticos_1985_2017.csv](../analysis_r/data/raw/Cruceros_hidroacusticos_1985_2017.csv), obtenido de *El libro de la anchoveta*, contiene aproximadamente 70 cruceros hidroacústicos únicos entre 1985 y 2017, con unos 50 cruceros entre 1998 y 2017.

Incluye biomasa, área de distribución y área evaluada. Esto mejora sustancialmente la información biológica disponible frente al panel anterior, que solo utilizaba 9 cruceros con fechas de inicio y fin completas.

El archivo todavía requiere control de calidad porque:

- algunas filas están duplicadas;
- existen identificadores de crucero mal formados;
- los números usan espacios como separadores de miles;
- las unidades deben confirmarse en la fuente original;
- no todas las campañas tienen fechas completas;
- no contiene coordenadas ni NASC por transecto;
- no identifica claramente todos los stocks o regiones.

Una vez depurado, el archivo puede convertirse en el principal panel de biomasa por campaña para los experimentos A, B y C.

### 2.5 Desembarques y manejo pesquero

También existen series mensuales de desembarques, cuotas y temporadas. Estas variables permiten analizar la respuesta de la actividad pesquera, pero los desembarques no son equivalentes a biomasa natural.

Un modelo de desembarques debe incluir esfuerzo, cuota, días de pesca, vedas, temporada y cambios regulatorios. Esta respuesta debe mantenerse separada de los modelos de biomasa.

## 3. Qué puede investigarse actualmente

### 3.1 Conectividad ambiental

Esta es la parte con mejor soporte estadístico actual. Los 344 meses ambientales permiten evaluar si las anomalías antárticas preceden a cambios en el Pacífico Sur y Humboldt.

La secuencia puede analizarse como:

```text
SAM, hielo, SST antártica y circulación
        ↓
temperatura, salinidad y estructura subsuperficial del Pacífico Sur
        ↓
SST, oxígeno, clorofila, nutrientes y surgencia en Humboldt
```

Esto permite probar si existe una asociación ambiental consistente, aunque todavía no demostrar que dicha asociación produzca cambios en la anchoveta.

### 3.2 Relación entre ambiente local y anchoveta

Después de limpiar el nuevo archivo de cruceros, se podrá analizar:

```text
SST, salinidad, oxígeno, productividad y surgencia
        ↓
biomasa hidroacústica por crucero
```

Con aproximadamente 50 campañas comparables entre 1998 y 2017 sería posible ajustar modelos exploratorios y algunos GAM/GAMM reducidos, siempre que se utilicen pocos predictores preseleccionados.

El nuevo archivo permite estudiar mejor la relación local entre hábitat y anchoveta que la serie RAM, porque está más directamente asociada a campañas hidroacústicas.

### 3.3 Relación temporal entre clima y biomasa

La serie RAM permite una primera prueba anual de la hipótesis antártica. El modelo realizado en R comparó:

```text
M0 = condiciones locales + ENSO + PDO + tendencia
M1 = M0 + hielo antártico rezagado + AAO/SAM rezagado
```

El contraste conjunto obtuvo:

```text
p = 0.114958
```

La decisión fue no rechazar H0 al 5 %. Esto no demuestra que no exista relación. Significa que, con 17 años completos, dos indicadores antárticos, resolución anual y el conjunto de controles utilizado, no se obtuvo evidencia suficiente para rechazar la hipótesis nula.

Además, esa prueba no incluyó todavía SST antártica, ACC, AAIW, oxígeno subsuperficial ni un indicador explícito de conectividad del Pacífico Sur.

## 4. Qué no puede afirmarse todavía

Con los datos actuales no es científicamente defendible afirmar que:

- la variabilidad antártica causa cambios en la anchoveta;
- la Corriente Circumpolar Antártica se convierte directamente en la Corriente de Humboldt;
- una anomalía de hielo marino determina por sí sola la biomasa peruana;
- la biomasa interpolada mensual es una observación;
- los desembarques representan directamente el tamaño del stock;
- una mejora de predicción demuestra causalidad;
- un único valor significativo de un modelo confirma la hipótesis general.

La hipótesis debe evaluarse como una cadena de asociaciones físicas, ambientales y biológicas.

## 5. Interpretación científica de los datos

Los datos actuales permiten separar la investigación en tres niveles:

### Nivel 1: conectividad oceanográfica

Puede estudiarse ahora con buena cobertura temporal. La pregunta es si las señales antárticas preceden a cambios en el Pacífico Sur y Humboldt.

### Nivel 2: respuesta ambiental del hábitat

Puede estudiarse con las variables locales de temperatura, oxígeno, salinidad, clorofila, nutrientes, viento y surgencia.

### Nivel 3: respuesta poblacional de anchoveta

Puede estudiarse utilizando RAM, biomasa desovante y cruceros hidroacústicos, pero cada fuente debe modelarse por separado debido a sus diferentes definiciones y escalas.

## 6. Diseño recomendado

El análisis debe organizarse en tres experimentos acumulativos:

```text
A: variables oceanográficas locales
B: A + productividad y biogeoquímica
C: B + conectividad antártica y del Pacífico Sur
```

Para cada experimento se deben conservar:

- respuesta utilizada;
- stock;
- fuente;
- unidad;
- periodo;
- tipo de observación;
- datos faltantes;
- variables interpoladas o modeladas;
- producto ambiental utilizado.

El nuevo archivo de cruceros debe incorporarse primero a un panel de campaña. No debe agregarse directamente al panel mensual ni combinarse con la biomasa RAM sin una decisión metodológica explícita.

## 7. Conclusión

La disponibilidad de datos es actualmente suficiente para avanzar hacia una investigación estadística real, no solo hacia un monitor descriptivo.

La principal mejora reciente es el archivo hidroacústico de *El libro de la anchoveta*, que puede aportar aproximadamente 70 cruceros únicos y alrededor de 50 campañas durante 1998–2017. Esto permite construir un análisis de biomasa por campaña mucho más informativo que el panel anterior de 9 observaciones.

La evidencia ambiental es suficientemente amplia para estudiar la conectividad Antártida–Pacífico Sur–Humboldt. La evidencia biológica permite analizar la respuesta de la anchoveta mediante RAM, biomasa desovante y cruceros, pero esas fuentes deben mantenerse separadas y armonizarse cuidadosamente.

La conclusión actual sobre las hipótesis debe expresarse así:

> Los datos disponibles permiten evaluar de manera exploratoria y reproducible las asociaciones entre variabilidad antártica, condiciones del Pacífico Sur, ambiente de Humboldt y biomasa de anchoveta. La primera prueba anual realizada con RAM no rechazó H0, pero no evaluó todavía la cadena antártica completa. La incorporación depurada de los cruceros hidroacústicos puede aumentar sustancialmente la capacidad estadística del estudio, aunque todavía faltan coordenadas, variables subsuperficiales y una armonización completa de stocks y métodos para sostener una conclusión causal o espacial fuerte.
