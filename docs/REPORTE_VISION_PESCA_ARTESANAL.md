# Chaski Polar: propuesta de valor para la pesca artesanal

Fecha: 14 de noviembre de 2026. Documento de producto para el equipo.

Estado: dirección acordada en la conversación y propuesta de alcance. No acredita entrevistas, ventas, ahorro económico ni capacidad predictiva todavía no demostrados.

Documento complementario: [Plan panorámico de evolución de la plataforma](PLAN_EVOLUCION_PLATAFORMA.md).

## 1. Decisión y propuesta de valor

Chaski Polar se enfocará inicialmente en pescadores artesanales del Perú, incluyendo patrones, armadores y organizaciones que acompañan sus faenas. Las grandes empresas pesqueras quedan fuera del mercado inicial.

La propuesta es reunir información del mar, explicar su significado y permitir que el pescador incorpore su propia experiencia. Se ofrecerán tres paquetes: información y aprendizaje; pronóstico ambiental de al menos siete días; y cuentas con bitácoras de pesca y mapas agregados de reportes.

**Promesa inicial:** «Entiende cómo cambia el mar en tu zona, consulta su evolución prevista y registra tus faenas para aprender de ellas».

La experiencia de usuario es parte central del producto: acceso móvil, lenguaje claro, pocas acciones, fechas visibles, gráficos comprensibles y continuidad aunque una fuente falle. El valor puede estar en hacer utilizable información que ya existe, además de producir análisis propios.

## 2. Necesidad real y qué falta validar

Hay evidencia de problemas de planificación y exposición económica. El estudio de SPDA de 2024 documenta costos de operación y financiación mediante ahorros, entidades financieras o comerciantes. En este último caso puede existir obligación de vender al financiador. Esto hace relevante entender el costo y el resultado de una salida, pero no demuestra demanda pagada por Chaski Polar. [SPDA, estudio de costo-beneficio](https://spda.org.pe/wp-content/uploads/2026/01/Formalizacion-de-la-pesca-en-el-Peru_Estudio-de-costo-beneficio-2024.pdf).

PescApp, una investigación aplicada en Matarani, combinó estimación de costos, GPS y evaluación posterior de rentabilidad. Su prueba con 14 pescadores evaluó principalmente usabilidad y experiencia; constituye un antecedente de interés, no una demostración de rentabilidad ni de adopción masiva. [Artículo de PescApp](https://proceedings.laccei.org/index.php/laccei/article/view/5112).

| Elemento | Estado | Consecuencia para el proyecto |
| --- | --- | --- |
| Necesidad de comprender condiciones y planificar faenas | Respaldada como problema general por fuentes y antecedentes | Diseñar para una decisión concreta y comprobarla en una caleta |
| Mejor interfaz que las alternativas actuales | Hipótesis de valor elegida por el equipo | Medir comprensión, tiempo de consulta y uso repetido |
| Problemas de INFOMAR | Observación reportada por el usuario; comprobación externa parcial | Evitar depender de su interfaz; probar los recorridos relevantes antes de publicar comparaciones |
| Interés por un pronóstico ambiental semanal | Hipótesis plausible | Preguntar qué variable, horizonte y precisión cambian una decisión real |
| Disposición a compartir posiciones y capturas | Sin validar | Diseñar privacidad y beneficios individuales desde el inicio |
| Disposición a pagar | Sin validar | Probar alternativas individuales, organizacionales y patrocinadas |
| Optimizar profundidad de pesca y número de lanchas | Sin validación biológica u operativa propia | Mantener como investigación futura, sin prometerla en los primeros paquetes |

**Sobre INFOMAR:** en la revisión del 14/11/2026 fue posible recuperar su portada y una página de especies. Los enlaces «Ingresar», «Mareas» y «Oleajes» recuperados por la herramienta remitían a la portada. No se verificó de extremo a extremo el funcionamiento de consultas dinámicas en un navegador. Se conserva el reporte del usuario sin convertirlo en una afirmación de caída total o permanente. [Portada](https://infomar.imarpe.gob.pe/), [especies](https://infomar.imarpe.gob.pe/newHome/especies).

## 3. Público, usuario y posible comprador

La pesca artesanal no constituye un solo perfil. El primer piloto debe elegir una combinación de caleta, especie o pesquería, arte de pesca y duración de faena. La disponibilidad actual de datos de anchoveta no demuestra que sea la mejor pesquería para captar usuarios.

| Perfil | Decisiones que interesa acompañar | Papel propuesto |
| --- | --- | --- |
| Pescador o patrón | Interpretar condiciones, preparar la faena y registrar lo ocurrido | Usuario cotidiano y participante en el diseño |
| Armador artesanal | Financiar, equipar y revisar resultados de sus embarcaciones | Usuario y posible comprador |
| Cooperativa o asociación | Acompañar socios y comparar información compartida | Posible comprador colectivo y aliado de distribución |
| Extensionista u organización de apoyo | Explicar cambios ambientales y enseñar herramientas | Facilitador, posible financiador y usuario de formación |

El alquiler de botes no se asume como práctica dominante. Debe comprobarse quién contrata embarcaciones, con qué frecuencia y bajo qué condiciones. Empresas de excursiones de pesca deportiva son otro segmento: no se mezclará su demanda de reservas con las necesidades de faenas artesanales comerciales.

## 4. Tecnología y alternativas existentes

| Alternativa | Evidencia disponible | Oportunidad para Chaski Polar |
| --- | --- | --- |
| GPS, radios y ecosondas | ENEPA IV 2022–23 documenta equipos y diferencias regionales; FONDEPES continúa realizando capacitación | Complementar navegación y observación a bordo con lectura ambiental accesible |
| SOSMAP de IMARPE | Publica variables oceanográficas y describe productos históricos y pronósticos | Diferenciarse mediante comprensión, integración y experiencia móvil |
| INFOMAR | Publica una oferta de reportes; el usuario informa fallas | Ofrecer acceso resistente a fallos, mostrando procedencia y vigencia |
| TrazApp | Registro de zarpes, tripulaciones y desembarques, orientado a trazabilidad | Dar valor analítico a los registros y explorar interoperabilidad |
| APPescar | Registra faenas, estadísticas y conexión con compradores | Evitar duplicar sin necesidad; investigar intercambio autorizado de registros |
| CATSAT | Oferta comercial de oceanografía para operaciones pesqueras en CLS Perú | La diferenciación inicial será accesibilidad y adecuación artesanal, no la novedad de usar satélites |

Fuentes: [ENEPA IV](https://repositorio.imarpe.gob.pe/server/api/core/bitstreams/0df4ea93-17e7-4c24-a8bf-701efdb2ae0d/content), [FONDEPES](https://www.gob.pe/institucion/fondepes/noticias/1370315-moquegua-fondepes-capacito-en-el-uso-de-equipos-electronicos-para-pesca-y-navegacion-a-pescadores-artesanales-de-ilo), [SOSMAP](https://www.gob.pe/institucion/imarpe/noticias/566413-imarpe-pone-al-servicio-de-la-comunidad-pesquera-y-ciudadania-renovado-portal-del-sistema-de-observacion-satelital-del-mar-peruano), [TrazApp](https://www.trazapp.org/), [APPescar](https://www.prodelphinusperu.org/appescar-es), [CLS Perú](https://peru.groupcls.com/aplicaciones/monitoreo-sostenible-de-pesca/?tab=1&tabs=categories).

Estos antecedentes no cuantifican el uso actual de cada herramienta en la caleta que se elija. Tener una web pública tampoco acredita facilidad de uso o disponibilidad continua. La investigación de campo debe observar qué consulta realmente el usuario y cómo interpreta la información.

## 5. Paquete 1: información, API y aprendizaje

**Entrega:** información ambiental mediante gráficos y mapas en la página, y una API para integraciones; Cardumen como demostración, aprendizaje y simulación educativa.

| Componente | Alcance propuesto |
| --- | --- |
| Consulta por zona | Elegir caleta o área, variable y fecha; consultar condiciones disponibles y contexto histórico |
| Interpretación | Explicar unidades, desviaciones respecto de lo habitual y relaciones investigadas |
| Transparencia | Distinguir observación, reanálisis, pronóstico, reporte de usuario y simulación; mostrar antigüedad y cobertura |
| API | Contrato documentado y versionado de las mismas series que consume la web; comenzar con lectura ambiental |
| Aprendizaje | Tutorial breve con los mismos controles del monitor y misiones opcionales de Cardumen |
| Tendencias | Mantener serie temporal, tasa de cambio, significancia y sensibilidad al periodo |

El aprendizaje será opcional: el pescador no tendrá que jugar para consultar información. El simulador podrá explicar decisiones y sus supuestos; sus resultados ilustrativos no se presentarán como predicciones de captura o rentabilidad.

**Factibilidad:** alta para una versión histórica y educativa con lo disponible; media para un servicio actualizado continuamente, porque requiere adquisición automática, operación y seguimiento de fallos. «Último disponible» no significa «estado del mar de hoy».

## 6. Paquete 2: pronóstico ambiental de siete días

**Entrega objetivo:** evolución diaria prevista durante al menos una semana, inicialmente para temperatura del mar y, después de evaluar fuentes, corrientes y salinidad. Viento y oleaje requieren sus propios productos. Clorofila y carbono son variables biológicas; se tratarán como una ampliación diferenciada.

### Estrategia de modelado

1. Integrar un pronóstico operativo basado en física como referencia inicial. Copernicus Marine ofrece un producto físico global con horizonte de diez días y actualización diaria; su resolución aproximada de 1/12° obliga a evaluar el desempeño costero. No sería un modelo creado por Chaski Polar. [Producto físico oficial](https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/description).
2. Evaluar ecuaciones propias sencillas: persistencia, climatología y modelos autorregresivos o de espacio de estados, incluyendo corrección estadística del pronóstico externo si hay datos adecuados.
3. Probar aprendizaje automático si las alternativas anteriores no alcanzan el desempeño requerido y existe suficiente información diaria. Elegirlo por validación, costo y mantenimiento; no por complejidad.

No se plantea resolver desde cero un océano tridimensional durante el hackathon. La integración de un modelo físico operativo permite ofrecer un primer servicio mientras se investiga una mejora local.

### Condiciones para ofrecerlo

- Tener entradas diarias u horarias y conocer cuándo estuvieron realmente disponibles. Las correlaciones mensuales existentes no se convierten en un pronóstico diario interpolando la serie.
- Archivar cada emisión con fecha de generación, fecha válida, horizonte, fuente, versión y ubicación.
- Evaluar por separado los días +1 a +7 frente a persistencia y climatología, con periodos futuros reservados y sin información posterior al momento de emisión.
- Publicar error histórico y, cuando se hayan calibrado, intervalos de predicción. Si no existen intervalos válidos, indicarlo sin inventar porcentajes de confianza.
- Si la fuente falla, conservar la última emisión con su antigüedad; no prolongar artificialmente su horizonte. Un producto que no cubre siete días debe indicarlo.

La biogeoquímica operativa también tiene productos de pronóstico, pero su resolución y habilidad local deben evaluarse por separado. [Producto biogeoquímico oficial](https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_BGC_001_028/description).

**Factibilidad:** media para integrar un producto existente; incierta para demostrar superioridad de un modelo propio. El objetivo de siete días es una meta de servicio, no una precisión ya conseguida.

## 7. Paquete 3: cuentas, embarcaciones y bitácoras propias

**Entrega:** cuentas para pescadores y organizaciones, registro por embarcación y expedición, historial individual y mapas agregados construidos a partir de los reportes autorizados.

Cada expedición tendrá identificador, embarcación, salida y regreso, especie objetivo, arte de pesca y resultado. Podrá contener varios lances o eventos de pesca, cada uno con tiempo y posición; el puerto de desembarque no se usará como ubicación de captura.

El mínimo de datos debe equilibrar utilidad y esfuerzo: captura por especie y unidad, duración de pesca, resultado cero o desconocido, ubicación o zona y método. Costos, combustible, profundidad de operación y número de anzuelos u otras medidas de esfuerzo se incorporarán según la pesquería. El reporte exacto de posición puede ser privado y opcional.

### Mapas de calor: qué mostrarían realmente

| Capa | Qué permite interpretar |
| --- | --- |
| Número de reportes | Cobertura y actividad reportada |
| Captura declarada | Volumen registrado, afectado por esfuerzo y participación |
| Captura por unidad de esfuerzo, cuando sea comparable | Rendimiento observado de una pesquería y periodo definidos |
| Antigüedad y embarcaciones participantes | Vigencia y soporte de cada celda |

Más capturas en una celda pueden significar más barcos o más horas. Cero captura es distinto de no tener reportes. La CPUE deberá definirse por especie y arte; no se mezclarán denominadores incompatibles ni se interpretará como biomasa del stock.

**Independencia buscada:** construir una fuente propia de actividad y resultados reportados, sin depender del IMARPE para cada registro. La colaboración con fuentes oceanográficas y validaciones externas sigue siendo útil. Una muestra voluntaria no sustituye un censo ni cubre automáticamente todo el litoral.

### Confianza para compartir

Los registros individuales serán privados por defecto. El usuario podrá consultar y exportar sus datos; el acceso del armador o de la cooperativa dependerá de permisos explícitos. Para mapas compartidos se propondrán celdas espaciales, retraso temporal y mínimos de contribuyentes distintos, con supresión de celdas escasas. Los parámetros se definirán con el piloto y se evaluará el riesgo de reidentificación; agregar datos no garantiza anonimato.

**Factibilidad:** media para cuentas y registros; condicionada a participación, calidad y esfuerzo registrado para mapas útiles. La captura de datos debe empezar temprano, aunque las visualizaciones compartidas lleguen después.

## 8. Cómo se relacionan los paquetes

Los paquetes expresan capacidades del producto, no precios o contratos definidos. Se podrán comercializar juntos o por separado después de validar el mercado.

| Paquete | Valor inmediato | Qué habilita después |
| --- | --- | --- |
| 1. Información y aprendizaje | Entender el mar y usar la plataforma | Adopción y confianza |
| 2. Pronóstico | Consultar evolución ambiental prevista | Comparar previsión y observación |
| 3. Bitácora y comunidad | Aprender de las propias faenas | Datos locales para evaluar ambiente y rendimiento |

El paquete 3 no necesita esperar un modelo propio del paquete 2. Primero puede ofrecer historial privado; los mapas colectivos se habilitan al existir cobertura suficiente. Una futura recomendación de zona, profundidad o despliegue de embarcaciones dependerá de esa validación pesquera y económica.

## 9. Qué resultados científicos se pueden aprovechar

La fuente interna principal es el [reporte consolidado del 14/11/2026](../../data_treatment/docs/pruebas_pendientes/REPORTE_CONSOLIDADO_RESULTADOS.md), que actualiza documentos previos.

| Resultado | Uso apropiado |
| --- | --- |
| Niño 1+2 y carbono fitoplanctónico peruano: r parcial −0,537; q = 1,34 × 10⁻⁷ | Contexto ambiental; el carbono proviene de CMEMS y es modelado |
| Niño 1+2 y clorofila OC-CCI de Chimbote/Callao: r parcial −0,406/−0,388 | Comparaciones regionales y educación; pigmento no equivale a captura |
| Asociaciones históricas con temperatura, nivel del mar, oxígeno y fosfato | Explicar variabilidad y diferencias verticales, conservando sus límites |
| Mezcla y carbono en Bellingshausen/Pacífico Sur | Contenido comparativo y educativo, sin extrapolar la relación a toda la costa |
| Carbono antártico frente a peruano: 0 de 12 contrastes supera FDR | Resultado negativo que impide presentar una conexión directa como demostrada |

Las mejoras de RMSE de la ronda ecológica con predictor contemporáneo conocido no son un pronóstico operativo. Las asociaciones entre campos del mismo modelo tampoco son validaciones observacionales independientes. La selección del pronóstico semanal requerirá datos y evaluación propios.

## 10. Validación del producto y siguiente decisión

Primer piloto propuesto: una caleta y una pesquería, con 5–10 participantes de perfiles diferentes. Estos tamaños son metas de exploración cualitativa, no muestras representativas del sector.

1. Reconstruir una faena reciente: decisión, fuentes consultadas, financiación, costos, búsqueda y resultado.
2. Observar cómo consulta una variable en sus herramientas actuales y en un prototipo de Chaski Polar.
3. Identificar qué horizonte y variable cambiarían una decisión; distinguir información interesante de información accionable.
4. Pedir un registro real y evaluar si puede completarlo sin ayuda. Investigar objeciones a compartir posiciones.
5. Probar continuidad de uso y una propuesta concreta de pago individual, colectivo o patrocinado, sin dar por confirmada la monetización.

Medir tiempo de consulta, comprensión de dato/pronóstico, repetición de uso, porcentaje de bitácoras completas y correcciones necesarias. El ahorro de combustible, mayor captura o rentabilidad requerirán un estudio posterior que controle diferencias de esfuerzo, precios y condiciones.

Para Space Apps, la demostración debe conservar el análisis histórico de variables NASA, región, tasa de cambio y significancia. Los paquetes de pronóstico y comunidad son evolución del producto; no sustituyen ese núcleo del desafío. [Desafío oficial](https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/).
