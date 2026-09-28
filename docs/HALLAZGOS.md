# Hallazgos (bitácora; solo crece)

> Las entradas del 24/09/2026 (sesión 1 y lectura de fuentes) están en `docs/archivo/HALLAZGOS_2026-09-24.md`.
> Las del 25/09/2026 hasta la orden 14 (sesión 2, esquema mixto, historial reescrito, limpieza de reglas) están en `docs/archivo/HALLAZGOS_2026-09-25.md`.

## 25/09/2026 (tarde) — El código a las reglas comunes (orden 14 del mando)
Decisión del usuario del 25/09: adaptarlo ya, antes del lunes 28/09. Resuelve los cuatro choques de
la entrada anterior. **El bot pronostica exactamente igual**: lo demuestra una prueba nueva
(`tests/test_configuracion_igual.py`) que guarda una «foto» de la configuración efectiva sacada
con el código de ANTES (modelos de cada puesto y su respaldo, esfuerzo, intentos, temperatura,
tiempos, pasadas, límites 2-98 % comprobados agregando pronósticos extremos, 1 % por opción,
investigación con Claude, qué torneos se piden en cada modo, cuántas preguntas se ensayan y los
horarios de los flujos) y la compara después de cada cambio. Salió idéntica en todos.
Además se comprobó aparte que los textos que se mandan a los modelos y el del marcador salen
letra por letra iguales (misma huella antes y después).
- **Python 3.12:** `forecasting-tools` 0.3.1 admite de 3.11 a 3.x; instalado todo desde cero con
  3.12 las pruebas pasan. En GitHub también (flujo de pruebas en verde con 3.12).
- **ruff** (el revisor de estilo): misma configuración y tope de versión que los hermanos. El
  formateo va en un commit aparte (e25b134). Las líneas largas dentro de los textos para los
  modelos no se parten (cambiaría lo que leen): llevan la marca `noqa`. Único cambio que se nota
  fuera de GitHub: la fecha «Today is» de los textos se calcula en UTC (en GitHub ya lo era).
  En el flujo de pruebas, ruff es un trabajo aparte: si falla, pytest se ejecuta igual.
- **Parámetros sin valor por defecto:** lector `bot/params.py` (copia de cripto-quant) que para y
  dice qué falta. Pasaron al YAML, con el mismo valor, los números que estaban en el código:
  intentos por modelo, temperaturas del lector, búsquedas a la vez, letras del informe que se pasan
  al director y a Claude (6.000), recortes del registro, espera del marcador (24 h) y tiempos de
  red. Se quedan en el código, a propósito, los hechos (0,1-99,9 % que acepta Metaculus) y los
  recortes de los mensajes en pantalla. Los intentos del director y del lector siguen siendo los de
  la librería (no son un número nuestro). Prueba nueva: cada parámetro del YAML lo lee alguien
  (`tests/test_params_vivos.py`); la puerta no cuenta como ajuste.
- **Tabla de límites** de los documentos en CLAUDE.md y `tests/test_documentacion.py`.
- **Autor de los commits:** el repositorio firmaba como «Claude <noreply@anthropic.com>»; desde
  esta orden firma con la dirección anónima del usuario (comunes §10), solo en este repositorio.
- Ensayo sin envío ni claves: igual que antes (aviso amarillo «Falta METACULUS_TOKEN», código 0;
  la ejecución programada con el envío apagado no hace nada). 82 pruebas en verde.

## 25/09/2026 — Estudio de bots rivales, datos de los otros proyectos y backtest (25 agentes)
Informe completo en `docs/ESTUDIO_BOTS.md` (4 bots con puesto conocido, descripciones de los mejores
cerrados, criba de ~20 bots más, 5 proyectos del usuario en solo lectura, viabilidad del backtest;
un escéptico por cada mejora candidata). Lo esencial:
- Lo básico ya lo tenemos (3 empresas, mediana, 2-98 %, GPT con razonamiento). Mejora más segura:
  **vigilancia** (alarma si hay preguntas abiertas sin pronóstico; primero lo que cierra antes) y
  **registro completo** (informe de investigación entero, estado de la investigación). Ambas 0 $.
- Única mejora de pronóstico medida (débil): curva numérica PCHIP (+2,39 [+0,21, +4,59] en 97 preguntas
  de edisonymy, elegida entre 13 variantes) → proponer solo «en sombra».
- Revisor/juez/debate/Delphi: sin efecto donde se midió (joy-void: 0 cambios en 72 sesiones, ~2,7 $/pregunta).
- Otros proyectos: ningún dato reutilizable tal cual; solo fuentes públicas (FRED, Yahoo, CBOE, BCE,
  DefiLlama); Binance/Bybit bloquean los servidores de EE. UU. de GitHub. Esperar 2 semanas y contar.
- Backtest con preguntas antiguas: **no** (no podemos leer sus resoluciones; la búsqueda filtra la
  respuesta en el 71-81 % de casos; ~90 $). Sí: comparar gratis combinaciones de los 3 miembros ya
  registrados; hacen falta ~125 preguntas pareadas para ver +3 puntos.

## 25/09/2026 (noche) — Mejoras A, B, C y comparador (decisión del usuario)
- A: el registro guarda la investigación entera (búsqueda y Claude por separado) con su estado
  (ok / vacía / fallo / tiempo; Claude: ok / sin_secreto / sin_cupo / fallo / tiempo /
  saltada_poco_tiempo), criterios, letra pequeña, cierre, fecha dada a los modelos y el razonamiento
  completo de cada modelo. El marcador pasa ese texto largo a `datos/detalle/` (un fichero por pregunta).
- B: preguntas ordenadas por hora de cierre; sin Claude si cierran en menos de 30 min.
- C: enlaces de las condiciones de resolución (hasta 5) en la búsqueda y en Claude; «fecha y volumen al
  citar un mercado»; Claude «verifica primero» 2-3 datos clave; 3 reglas de lectura en los prompts.
- Comparador (`bot/comparador.py`): cambio de puntuación ≈ 100·ln(p_variante/p_enviada) por pregunta
  (sí/no y opciones). Control: la variante «mediana (la actual)» da 0. Decididas de antemano: media,
  sin google, límites 1-99 %. Regla: ≥150 resueltas y ganar en las dos mitades.
- 98 pruebas en verde; ruff limpio.

## 27/09/2026 — Orden 26: clave de créditos, tope de gasto y encendido
- **Clave:** el secreto `OPENROUTER_API_KEY` existe (comprobado solo el nombre). Ensayo sin envío
  lanzado a mano: **verde, «Terminado: 3 pronósticos de ensayo»** (ejecuciones 36338357573 y
  36339352166). Un fallo pasajero de Gemini (503) lo cubrió su respaldo.
- **La clave de Metaculus gasta como «byok»:** en la consulta real `usage` = 0 y lo gastado va en
  `byok_usage`, que cuenta en el límite. Límite **100 $**, sin renovación. Si el código hubiera
  mirado solo `usage`, habría creído que nunca gastaba. Se suma `usage` + `byok_usage`; lo que queda
  se toma de `limit_remaining`.
- **Coste real:** el primer ensayo (3 preguntas) costó **0,91 $** según la clave, es decir **~0,30 $ por
  pregunta**. La librería solo contó 0,55 $ porque no mide la búsqueda `:online`. 100 $ ≈ 330
  preguntas; hasta enero salen ~420 de MiniBench y 300-400 de la temporada.
- **Tope de gasto** (`bot/presupuesto.py`): antes de cada torneo pregunta a la clave cuánto queda.
  La reserva es de 3 $. La MiniBench va primero y solo la para la reserva. La temporada va al ritmo
  de una línea: 25 % desde el primer día y el resto repartido por igual hasta el 06/01. Previsión
  de 0,40 $ por pregunta para contar cuántas caben, y freno de 1,50 $ por pregunta (solo de lo que
  mide la librería). Sin dinero: aviso amarillo, sin rojo. Si OpenRouter contesta 402 a mitad, no
  cuenta como fallo. Con estos números la temporada tendrá pocas preguntas hasta que llegue más
  dinero: la MiniBench (~18 $ por ronda) va por delante de la línea desde la 2.ª ronda.
- **Plan de Claude (investigación con agentes):** entre 2,2 y 2,8 $ equivalentes por pregunta. Una
  tanda de 3 preguntas movió ~9-11 puntos la ventana de 5 horas (medido con la sesión de desarrollo
  también en marcha, así que es una cota alta) y ~1 punto el tope semanal (88 → 89 → 90 %). Una de 3
  investigaciones se pasó de los 300 s.
- **Experimento «Claude sí / Claude no»** (decisión del usuario del 27/09; reglas escritas ANTES de ver
  resultados, regla común 3): Claude investiga solo las preguntas de **número par**; las impares son
  el grupo de comparación. Cómo se mide: la puntuación de pares media por pregunta resuelta en cada
  grupo, con los números del marcador. Solo se decide con **≥150 preguntas resueltas en total**. Se
  da por bueno que Claude ayuda si su grupo gana **en las dos mitades** (ordenadas por fecha de
  cierre), la misma regla que el comparador. Hasta enero solo se verían diferencias grandes, de unos
  5-10 puntos.
- **Envío encendido** (27/09, 21:04, con el «sí» del usuario). Prueba a mano en la zona de pruebas:
  **8 pronósticos enviados** («Posted prediction» de Metaculus, cada uno con su comentario privado).
  Fallo encontrado: con el envío encendido, la zona de pruebas **no se limitaba a 3 preguntas** y hacía
  todas, gastando créditos y plan en preguntas de práctica. Se paró a los 14 min y se corrigió (3
  preguntas también con envío, con su prueba). El reparto par/impar funcionó: 5 con Claude y 3 sin.
- Plan de Claude en esa prueba: 1,7-2,1 $ equivalentes por investigación. La ventana de 5 h pasó de
  11 a 30 % con ~6 investigaciones y esta sesión en marcha: **~3 puntos por investigación** (cota
  alta). El tope semanal pasó de 90 a 92 %.
- **Primera ejecución automática en torneo** (19:18 UTC): verde, **1 pronóstico enviado en la
  temporada** (pregunta 45707); la MiniBench no tenía preguntas abiertas. El tope decía «llevamos
  5,36 $ de 25,00 $ permitidos». Coste medio hasta aquí: ~0,35 $ por pregunta (5,36 $ entre ~15).
- **Pausa de Claude hasta el 28/09 a las 11:00** (decisión del usuario): el tope semanal estaba al
  92 %. Para el experimento par/impar, **las preguntas pronosticadas durante la pausa se quitan de
  los dos grupos** (escrito antes de ver resultados).
- **Tres mejoras antes de que abra la temporada** (27/09 noche, decisión del usuario, orden 26):
  (1) **vigilancia que reacciona sola** (`vigilancia.yaml`, a :13 y :43): si el bot se calla más de
  45 min, si su última ejecución falla o si hay preguntas abiertas hace más de 1 h sin pronóstico que
  el tope sí permitiría, lo relanza; tras 2 relanzamientos en 3 h sin arreglo, despierta a Claude
  (40 turnos, 5 $ equivalentes, una vez cada 12 h como mucho, respetando la pausa del plan). Claude
  solo ve líneas de error, no puede subir nada: un paso aparte comprueba que su arreglo no toca lo
  prohibido y lo deja en una rama `vigilancia/…` más un issue. 40 pruebas con fallos simulados.
  (2) **coste por parte** en cada pregunta (`coste_partes`) y resumen semanal del gasto en el
  marcador (clave frente a librería y frente a la línea). La medida por parte suma exactamente el
  total de la librería (probado). (3) **curva PCHIP en sombra** en las numéricas (`sombra_pchip`):
  misma construcción que la librería (mismos puntos y escala), solo cambia rectas por curva suave;
  coincide con la de scipy hasta 1e-12. Ninguna cambia lo que se envía.
- **Sacado de ESTADO el 27/09 (22:45) por su tope de palabras:** la tabla «Lo último que se hizo
  (orden 26)» (clave comprobada por su nombre; prueba sin envío en verde dos veces; 0,91 $ las 3
  primeras preguntas; tope con 31 pruebas; 8 enviados en la zona de pruebas; 1.ª ejecución en torneo
  verde con 1 enviado en la temporada, pregunta 45707; la zona de pruebas con envío hacía todas las
  preguntas y se limitó a 3) y la nota de que la carpeta vieja `stoic-burnell-55dfc1` y las ramas
  `elastic-maxwell`, `lucid-dewdney` y `stoic-burnell` ya estaban fusionadas en `main`.
- **Más mejoras gratuitas** (27/09 noche, «adelante» del usuario): lista semanal de preguntas
  perdidas en el marcador (el bot apunta ahora las que deja el tope, línea «dejadas»); piezas de
  GitHub sobre Node 24 (checkout v5, setup-python v6, setup-node v5, upload-artifact v6; Node 20 se
  quitó el 23/09); la curva suave pasa a ser una de las 3 comparaciones decididas de antemano (antes
  de ver resultados) y el comparador la puntúa frente a la enviada (50 · ln del cociente del tramo).
  AskNews: hace falta que el usuario cree su cuenta en my.asknews.app y escriba a rob@asknews.app
  (fuente: plantilla oficial de Metaculus, leída con una búsqueda web el 27/09); ~3.000 consultas al
  mes por bot. El Gmail conectado a la sesión en la nube era otra cuenta: no se usó.
- **Qué modelos deja usar la clave de créditos** (28/09, 05:09 UTC, flujo «Modelos de la clave»,
  consulta gratuita `GET /api/v1/models/user`): **156 de 458** modelos públicos, solo de **OpenAI
  (89), Anthropic (25) y Google (24)**, más alias «~…-latest» de esas tres y 7 enrutadores
  (`openrouter/auto`, `openrouter/free`…, `typesafe/jev-router`). **Ningún modelo chino** (DeepSeek,
  Qwen, Kimi…): confirmado lo que decían las notas de nostreambot. Nuestros modelos, todos
  permitidos. Si se quiere abaratar con los créditos, la vía es un modelo barato de esas tres
  empresas (se propone tras la 1.ª semana, con el gasto por partes).
- **Precios y cambio a Gemini 3.8 Flash** (28/09, consulta gratuita de la clave): Google permitidos
  incluyen `gemini-3.8-flash` (0,75/3,75 $ por millón de tokens de entrada/salida) y `3.5-flash` (el
  que usábamos: 1,5/9 $). Los nuestros: GPT-6 y GPT-5.6 2/10 $, Opus 5.5 4/20 $, Opus 4.8 5/25 $,
  lector gpt-4o-mini 0,15/0,6 $. El usuario decidió pasar a 3.8 Flash (~06:50 UTC): en el marcador,
  las preguntas anteriores llevan 3.5 Flash.
- **Modelos elegidos por el usuario** (28/09 ~07:50 UTC): búsqueda con Opus 5.5 `:online` (antes
  GPT-5.6 Sol), nuevo respaldo de la búsqueda GPT-6 Sol `:online`, respaldo de OpenAI GPT-6 Astra,
  Anthropic sin respaldo. **Sin verificar en vivo:** que `claude-opus-5.5:online` funcione con la
  clave de créditos y cuánto cuesta su búsqueda web; si falla, entra el respaldo y el registro lo
  dice (`base_estado` = «respaldo»). Riesgo anotado: Opus 5.5 busca y también pronostica, así que
  su visión entra dos veces (el texto de la búsqueda le prohíbe dar pronósticos). Los «:batch» (por
  lotes, más baratos) no sirven: preguntas abiertas ~1,5-3 h.
