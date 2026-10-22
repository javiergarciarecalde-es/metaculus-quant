# Hallazgos (bitácora; solo crece)

> Las entradas del 24/09/2026 (sesión 1 y lectura de fuentes) están en `docs/archivo/HALLAZGOS_2026-09-24.md`.
> Las del 25/09/2026 hasta la orden 14 (sesión 2, esquema mixto, historial reescrito, limpieza de reglas) están en `docs/archivo/HALLAZGOS_2026-09-25.md`.
> Las del 25/09/2026 (tarde) al 27/09/2026 (órdenes 14 y 26: código a las reglas comunes, estudio de bots, mejoras A-C, clave de créditos, tope de gasto y encendido) están en `docs/archivo/HALLAZGOS_2026-09-27.md`.

## 28/09/2026 (tarde) — Orden 27: auditoría de normas del torneo (sesión local)
Normas releídas en la página oficial (docs/FUENTES.md). Lo que se miró y lo que salió:
- **¿Algún cambio desde el 27/09 se decidió viendo pronósticos de preguntas abiertas?** No
  encontrado. Cada cambio tiene su motivo escrito (gasto, preferencia del usuario sobre modelos,
  diseño decidido de antemano, averías) y ninguno cita un pronóstico. La única pregunta del torneo
  pronosticada (45707, del 27/09 19:19 UTC al cierre ~06:00 del 28/09) solo se miró en sus líneas
  de «enviado» (sesión local de la orden 26, buscado en su conversación). La sesión en la nube no se
  puede leer desde aquí: queda como «no encontrado», no como «comprobado».
- **¿Puede la prueba a mano o la vigilancia volver a pronosticar una pregunta?** En la práctica no:
  en modo torneo el bot salta las ya pronosticadas y, tras enviar la 45707, las ejecuciones de
  19:32, 19:51 y 20:18 la vieron abierta y no la tocaron (0 enviados). La zona de pruebas sí repite
  (no puntúa). La vigilancia relanza el bot entero, que solo hace las que faltan: permitido.
- **Dos agujeros encontrados y cerrados, con pruebas** (`bot/normas.py`, `tests/test_normas.py`):
  (1) la librería **falla abierta**: si Metaculus dejara de mandar el historial de nuestros
  pronósticos, daría todas las preguntas por nuevas y el bot las repetiría cada 20 min; ahora esa
  pregunta no se pronostica y la ejecución sale en rojo. (2) Una pregunta que llegara **repetida**
  en la lista se pronosticaba dos veces (la foto de configuración pasó de 12 a 6 envíos con la
  lista duplicada de las pruebas); ahora una vez.
- **Marcador:** subía al repositorio público los pronósticos «de hace más de 24 h» suponiendo que
  la pregunta ya había cerrado; la 45707 siguió abierta ~11 h, así que en la temporada podría no
  bastar. Ahora exige además que su hora de cierre haya pasado. Hasta hoy no se había publicado
  ninguno (marcador del 28/09: 0 cerrados).
- **Riesgos que quedan, para el usuario:** (a) el repositorio es público y los registros de GitHub
  (y los artefactos) muestran investigación y pronósticos mientras la pregunta está abierta: otro
  podría copiarlos. Las normas no lo prohíben; hacerlo privado gastaría minutos de GitHub
  compartidos (el bot y la vigilancia usan ~120 al día). (b) La comprobación programada de las 09:48 UTC (rutina de
  la sesión en la nube) lee el registro de preguntas abiertas: mira estados y costes, que es
  vigilancia, pero con la regla de cambios (CLAUDE.md) no debe mirar pronósticos. (c) La vigilancia
  enseña a Claude líneas de aviso que podrían incluir un trozo de texto de un modelo; sus arreglos
  solo pueden tocar infraestructura, así que no ajusta pronósticos.
- **Otros fallos de método:** 23 commits de la sesión en la nube firmados como «Claude
  <noreply@anthropic.com>» (comunes §10 pide la dirección anónima del usuario; no es su correo
  personal y no se reescribe el historial). La prueba de la curva suave frente a scipy se saltaba
  siempre en GitHub (scipy no estaba instalada): ahora corre y pasa (coincide hasta 1e-12).
- **Regla de cambios** escrita en CLAUDE.md (orden 27, aprobada por el usuario).

## 28/09/2026 (tarde) — Orden 27: lo que gasta el bot del plan de Claude y su tope
- **Medido de verdad** (las 11 investigaciones del 27/09 en la zona de pruebas, registro de GitHub):
  10 salieron bien, entre 1,54 y 2,76 $ equivalentes (media 2,07 $); una se cortó a los 300 s sin
  decir cuánto gastó. El tope semanal se movió 5-6,6 $ por punto (cota baja: otras sesiones
  gastaban a la vez). **Sin medir aún:** el clasificador con Opus «xhigh» (se añadió el 28/09 a las
  08:30 UTC y desde entonces no ha habido preguntas; estimación 0,05-0,3 $ por pregunta), la
  vigilancia despertando a Claude (nunca ha hecho falta; freno 5 $) y la revisión de los lunes (aún
  no ha corrido; reserva de 5 $).
- **Previsión por semana** (20-30 preguntas por semana mientras solo haya 100 $ de créditos; la mitad,
  pares): investigación 20-30 $, clasificador con Opus 1-9 $, vigilancia 0 (máximo 10 $), revisión
  ~5 $: **~5-9 % del tope semanal** en una semana normal; en una semana de ronda de MiniBench con
  muchas preguntas, el tope del 15 % frena primero a Opus y luego a la investigación.
- **La comprobación encadenada de la nube** (cada 4 h hasta el 05/10, despertando una conversación
  muy larga) podía gastar más que todo el bot junto: apagada con el «sí» del usuario (12:07).
- **Tope puesto** (`bot/plan_claude.py`): 15 % del tope semanal = 70 $ equivalentes por semana del
  plan (5 $ por punto, menos 5 $ de reserva para la revisión). Al 80 % (56 $) se apaga el
  clasificador con Opus; al 100 %, la investigación con Claude y los despertares de la vigilancia.
  La vigilancia, además, como mucho 2 despertares por semana. Cada uso apunta su coste en un
  artefacto `plan-claude-<id>` (orden de la lista de artefactos de GitHub: de más nuevo a más viejo,
  visto en la respuesta real del 28/09). Si la cuenta no se puede leer, solo se apaga Opus.
- **Regla escrita antes de ver resultados (experimento par/impar):** las preguntas pares que se
  queden sin Claude por el tope (`claude_estado` = «tope_plan») se quitan de la comparación, igual
  que las de la pausa; las impares no se tocan.
- **Calibrar el «5 $ por punto»:** con la tarjeta de uso de la aplicación (el % semanal) y la tabla
  «Plan de Claude» del marcador de los lunes. Si sale otra cifra, se cambia en `config/params.yaml`
  con su entrada en CHANGELOG.

## 28/09/2026 (tarde) — Orden 27: lo que quedaba sin verificar y la revisión semanal
- **Relanzamiento de la vigilancia, comprobado en GitHub de verdad** (sin preguntas abiertas, así
  que sin pronosticar nada): (1) con el botón de prueba nuevo (vigilancia 36409654631 → bot
  36409737166, lanzado por «github-actions[bot]», que es como la vigilancia reconoce los suyos);
  (2) **sola**, a las 10:31 UTC (vigilancia 36410150135 → bot 36410250191), porque la ejecución
  anterior había fallado. Ninguna despertó a Claude (hacen falta 2 relanzamientos en 3 h sin arreglo).
- **Fallo encontrado por el camino:** esas dos ejecuciones relanzadas salieron en rojo al instalar
  las piezas: pypi.org no contestaba a las máquinas de GitHub (5 esperas de 15 s agotadas en
  `python-dateutil`) y pip acabó diciendo «ResolutionImpossible». No era el código (las pruebas de
  un minuto antes instalaron lo mismo). Arreglo: la instalación de bot, vigilancia y marcador
  reintenta 10 veces con 60 s de espera y, si aun así falla, otra vez al minuto (prueba en
  `tests/test_flujos.py`). Una ejecución a mano a las 10:37 (0 preguntas abiertas, 0 enviados)
  salió en verde, así que la vigilancia no llegó a despertar a Claude por un corte ya pasado.
- **Sin poder verificar todavía** (no hay preguntas en ningún torneo desde las ~06:00 UTC): la
  vuelta de la investigación tras la pausa, la opción A, los clasificadores y el tope de gasto con
  una ronda de MiniBench. La página de la MiniBench da 403 desde aquí (fecha de la próxima ronda
  desconocida).
- **Revisión semanal rehecha** (sí del usuario, 12:07): rutina nueva `trig_01P1NPoMLt4LgerQFDWu4MZ8`
  («metaculus-quant: revisión semanal (lunes, escribe en el repo)»), lunes 09:12 de Madrid, Sonnet 5
  (más barato para el plan; la tarea es leer el marcador y aplicar reglas ya escritas), memoria
  limpia en cada vuelta, sin conectores (se le quitaron Gmail, Drive y Calendar, que se añadían
  solos), firma los commits con la dirección anónima del usuario, no arregla ni cambia nada y
  sobrescribe `docs/REVISION_SEMANAL.md`. Apagadas (no borradas) las tres rutinas que vivían en la
  conversación de la nube: `trig_01Jpv6Pfyp3yo3SxcknZAs4f` (revisión vieja),
  `trig_01X5xNNWkveFfeTSNe6no1xy` (ya había corrido) y `trig_01392sLyrpnQiigTnsHXj3Qx` (la
  encadenada cada 4 h). Esa conversación ya se puede archivar.

## 07-08/10/2026 — Orden 82: el bot sale del plan de Claude del usuario (cambio con fecha anunciada)
- **Corte antes/después:** commit `d66176f` en `main`, 07/10/2026 ~21:05 UTC (23:05 Madrid). Primera
  ejecución del bot con el cambio: `37685740188` era la última sin él (20:55 UTC); todas las de
  `d66176f` en adelante van sin Claude. Cambio de configuración decidido por el usuario por consumo
  del plan (ver DECISIONES), **sin mirar ninguna pregunta abierta ni ningún pronóstico**; no se
  relanzó nada por un resultado. Para comparar antes/después, cortar por esa hora.
- **Experimento pares/impares: se corta.** Desde el corte, pares e impares van igual (búsqueda de
  pago, Opus 5.5 `:online`). Las pares con Claude Max van del 28/09 ~09:00 UTC al corte; con 0
  resueltas al corte, no llegará a 150 por grupo: queda sin conclusión salvo que se reactive.
  El clasificador con Opus deja de producir filas; el de Gemini sigue.
- **Piezas que gastaban el plan y cómo se apagaron** (gasto: marcador 05/10, semana 28/09-05/10):
  | Pieza | Dónde se encendía | Gasto medido | Ahora | Para reactivar |
  |---|---|---|---|---|
  | Investigación Claude Max (pares) | `investigacion.modo` = `claude_max` | 27,19 $ eq./semana (~2,07 $/pregunta) | `basica` | `claude_max` |
  | Clasificador en sombra Opus xhigh | `clasificador.claude.activo` | 0,64 $ eq./semana | `false` | `true` |
  | Vigilancia nivel 2 (despierta a Claude) | `vigilancia.claude.activo` (nuevo; antes siempre) | 0 (nunca hizo falta) | `false` | `true` |
  | Revisión semanal de los lunes (rutina en la nube, Sonnet 5.5) | rutina `trig_01P1NPoMLt4LgerQFDWu4MZ8` | 1 vuelta (05/10), sin medir; reserva 5 $ | apagada, no borrada | encenderla (RemoteTrigger `update` `enabled: true`) |
  | Instalar Claude Code y pasar `CLAUDE_CODE_OAUTH_TOKEN` al bot | `run_bot_on_tournament.yaml` | 0 (no gasta, pero lo hacía posible) | solo si `python -m bot.plan_claude` da `usa=si` | automático al encender cualquiera de las 3 primeras |
  Total medido 27,83 $ eq./semana ≈ 5,6 puntos del tope semanal. Rutinas de Metaculus encendidas
  tras el cambio: ninguna (lista de RemoteTrigger del 07/10 ~21:00 UTC).
- **Verificado en real:** ejecución `37744871699` (08/10 07:40 UTC, `d66176f`, en verde): el paso
  nuevo escribe «Plan de Claude del usuario: no lo usa ninguna pieza del bot»; `setup-node` e
  «Instalar Claude Code» salen *skipped*; el bot recibe `CLAUDE_CODE_OAUTH_TOKEN` vacío. 15
  ejecuciones del bot y la vigilancia de `d66176f` hasta las 07:40 UTC, todas en verde. Sin
  preguntas nuevas desde el corte hasta el 08/10 07:40 UTC: el coste por pregunta con todo por la
  búsqueda de pago aún no está medido.
- **Pruebas:** 276 en verde (`tests/test_orden82.py` nuevo). Las pruebas de las piezas de Claude se
  conservan con el fixture `claude_encendido` (conftest): siguen probando que funcionan si se
  reactivan. En `construir_bot` con modelos simulados el clasificador con Opus ahora respeta
  `clasificador.claude.activo`, como fuera de las pruebas.
- **Créditos de OpenRouter hasta el 06/01/2027** (punto 4 de la orden): lo que queda según la clave
  (líneas «Quedan …» del registro): 05/10 04:21 UTC 90,55 $; 05/10 21:19 85,23 $; 06/10 05:36
  83,53 $; 07/10 06:24 82,03 $; 07/10 20:55 **80,79 $**. Del 05/10 04:21 al 07/10 21:00: 9,76 $ en
  51 pronósticos enviados (~0,19 $/pregunta, con las pares sin búsqueda de pago). Desde el 28/09
  ~13:00 (5,36 $ gastados) hasta el 07/10 21:00: 13,85 $ en ~9,6 días = 1,44 $/día. Para llegar al
  06/01 (90 días desde el 08/10) haría falta ≤0,90 $/día. Proyección de agotamiento sin el freno de
  ritmo: 1,44 $/día → ~02/12; con las pares pagando búsqueda (+25 % supuesto, sin medir) 1,80 $/día →
  ~21/11; ritmo del 05-07/10 (3,63 $/día) → ~30/10; ritmo flojo (5 preguntas/día × 0,19) → ~01/01.
  **No llega al 06/01 salvo con el ritmo más flojo.** El freno de ritmo (`presupuesto.ritmo`) frena
  la temporada para estirar el dinero; la MiniBench va primero y solo la para la reserva de 3 $.
  Tope de gasto de la orden: 0 €; no se puso dinero ni claves.
- **Fallo de método (08/10):** al leer el final del registro de la ejecución `37685740188` para
  buscar la línea del gasto, salieron en pantalla las probabilidades por opción de una pregunta aún
  abierta. No se usaron para nada ni se copiaron; desde entonces solo se filtran las líneas
  «Quedan …» y «Terminado: N pronósticos ENVIADOS». Para mirar el gasto en un registro: `grep` de
  esas dos líneas, nunca `tail` del paso del bot.

## 18/10/2026 — Metaculus no da créditos extra a Kyou-bot (ronda incremental)
- **Fuente:** correo de ben@metaculus.com, «Incremental credit round», 18/10/2026 06:42 UTC (.eml
  pasado por el usuario; SPF/DKIM/DMARC de metaculus.com en «pass»). Fila en FUENTES.
- **Qué dice:** ronda de créditos extra basada en el rendimiento en la MiniBench 2026-10-05; a
  Kyou-bot no le amplían créditos («factors we evaluated and the available budget», sin cifras ni
  puesto). Sigue con derecho a premios en los torneos.
- **Qué invalida:** la vía «sube sola si la MiniBench va por encima de la media, hasta ~775 $» (correo
  del 27/09, FUENTES) queda descartada en esta ronda; la opción (b) «pedir más créditos» de ESTADO
  (08/10) pierde casi todo su valor. No se sabe si habrá más rondas. No implica por sí solo que el bot
  esté bajo la media: el motivo no se da y el marcador del 12/10 tenía 0 preguntas resueltas.
- **Saldo al 18/10:** registro de la ejecución `39086870846` (18/10 01:32 UTC), línea «Temporada:
  llevamos 27.12 $ de 40.05 $ permitidos a esta fecha; caben 32 preguntas» → quedan ~72,88 $ de 100 $.
  Marcador del 12/10 06:55 UTC: 21,96 $. Ritmo 12/10→18/10: 5,16 $ en 5,8 días = **0,89 $/día**;
  para llegar al 06/01/2027 (80 días) hace falta ≤0,91 $/día → **hoy llega, justo**. Ese ritmo es bajo
  en parte porque el reloj de GitHub lanzó el bot solo 5-16 veces al día del 12 al 17/10 (de 72
  posibles; trampa conocida), y con menos preguntas. Si el ritmo vuelve al de 05-07/10 (3,63 $/día),
  el freno de ritmo dejará preguntas de la temporada sin pronóstico.
- **Método:** del registro solo se filtraron las líneas de gasto («Quedan …» no sale en las
  ejecuciones de la temporada; la línea es «Temporada: llevamos …»; trampa de CLAUDE.md ampliada).
  No se vio ningún pronóstico.

## 22/10/2026 — Orden 174: el reloj de GitHub lanza el bot en tandas cada 3-5 h desde el 10/10
- **Crudo:** `gh run list -w {run_bot_on_tournament,vigilancia}.yaml --created ">=2026-10-09"`
  (169 y 106 ejecuciones) y líneas de gasto de 104 registros del bot desde el 11/10 (`grep` de
  «Quedan …», «Temporada: llevamos …», «Terminado: N»). Sin ver pronósticos de preguntas abiertas.
- **Corte:** 09/10 = 55 lanzamientos del reloj (normal). Desde 09/10 18:42 UTC, 3-8 al día.
  | Día (UTC) | Bot reloj (de 72) | Bot a mano | Mayor hueco (h) | Vigilancia reloj (de 48) | Enviados | Gastado acumulado ($) |
  |---|---|---|---|---|---|---|
  | 10/10 | 5 | 4 | 6,4 | 5 | — | — |
  | 11/10 | 5 | 5 | 6,9 | 5 | 2 | 21,96 |
  | 12/10 | 3 | 2 | 9,9 | 3 | 2 | 22,11 |
  | 13/10 | 4 | 3 | 8,0 | 4 | 4 | 23,34 |
  | 14/10 | 6 | 5 | 5,0 | 5 | 6 | 24,55 |
  | 15/10 | 6 | 6 | 4,3 | 6 | 4 | 25,27 |
  | 16/10 | 7 | 1 | 4,6 | 6 | 3 | 26,06 |
  | 17/10 | 8 | 8 | 3,5 | 8 | 3 | 26,87 |
  | 18/10 | 7 | 1 | 5,1 | 7 | 3 | 27,49 |
  | 19/10 | 5 | 4 | 4,7 | 4 | 29 | 34,85 |
  | 20/10 | 6 | 1 | 5,0 | 6 | 14 | 35,41 |
  | 21/10 | 6 | 1 | 5,7 | 6 | 2 | 38,16 |
  | 22/10 (hasta 12:30) | 3 | 1 | 5,0 | 2 | 4 | 39,11 |
  «Mayor hueco» del 10-14/10: entre lanzamientos del reloj (`medir.py`); del 15/10: `bot/lanzamientos.py`
  contra la API real. «Gastado» = último valor del día leído de la clave (lag de OpenRouter de horas).
- **Mecanismo (inferido de los datos):** los dos flujos se lanzan en el mismo minuto aunque sus
  `cron` difieran (p. ej. 18/10 01:32, 06:36, 11:44 ambos; bot `7,27,47`, vigilancia `13,43`): GitHub
  procesa el reloj del repositorio en tandas y cada tanda da una ejecución por flujo; los ticks
  intermedios se pierden. Cambiar los minutos del `cron` o añadir más líneas no lo arregla (no hay
  probabilidad por tick que subir). docs.github.com solo dice «may be delayed… may be dropped»
  (FUENTES 22/10). Lo mismo en otros proyectos de la cuenta desde el 10/10 (PANEL del mando).
  Los `workflow_dispatch` sí llegan al momento (la vigilancia relanza en <1 min).
- **La vigilancia no compensa:** va en la misma tanda que el bot; su relanzamiento por «silencio»
  sale justo después del bot (duplicado, 0 enviados). No acorta ningún hueco.
- **Pregunta 45956 (temporada, cierre 11/10 06:00 UTC):** ejecuciones del bot 11/10 02:13
  (`38104425749`, «Terminado: 0 pronósticos ENVIADOS» → aún no estaba abierta o no visible) y la
  siguiente 07:05 (`38120190714`). Hueco de 4,9 h sin lanzamientos; abrió y cerró dentro. Causa:
  reloj de GitHub. Sigue viva.
- **Las 6 del marcador del 19/10:** 46005 (hueco 9,9 h), 45960 (5,4), 45964 (4,0), 46056 (4,6),
  46127 (3,6): misma causa. 46128 (MiniBench, cierre 19/10 05:21): la ejecución `39204044175` la
  empezó a las 05:20, pagó investigación y modelos y al enviar a las 05:22 Metaculus contestó 405
  (ya cerrada); gasto perdido (~0,23 $). Marcador 12/10: 63 de 64 cerradas con pronóstico; 19/10:
  37 de 43.
- **Arreglo aplicado (commit `6468245`):** el marcador de los lunes enseña lanzamientos por día del
  bot y la vigilancia y, por pregunta perdida, el último lanzamiento antes del cierre y el primero
  después (`bot/lanzamientos.py`, `vigilancia.Github.ejecuciones_desde`, GH_TOKEN en
  `marcador.yaml`). No cambia ni gasto ni pronósticos. Probado contra la API real de GitHub.
- **Arreglo del reloj: no aplicado, decide el usuario** (todas exigen salir de GitHub o un riesgo
  de cuenta): (A) seguir igual, (B) Programador de tareas de Windows con `gh workflow run
  run_bot_on_tournament.yaml -f modo=tournament` cada 20 min (0 $, 0 minutos: repo público; solo con
  el PC encendido; los huecos de las perdidas caen 00-09 UTC), (C) servicio de cron externo gratis
  llamando a `POST /repos/{o}/{r}/actions/workflows/run_bot_on_tournament.yaml/dispatches` (body
  `{"ref":"main","inputs":{"modo":"tournament"}}`, mismo que `vigilancia.Github.relanzar`) con un
  token de grano fino solo de este repositorio y permiso Actions: escritura (cuenta y token, del
  usuario), (D) trabajo «metrónomo» dentro de Actions que duerme y se relanza (riesgo con las
  condiciones de uso de Actions para toda la cuenta; descartado).
- **Gasto (clave, no librería):** 11/10 21,96 $ → 22/10 39,11 $ = 17,15 $ en ~11 días ≈ **1,56 $/día**,
  ~0,23 $/pregunta (76 enviadas). 18/10→22/10: 27,12 → 39,11 = ~2,7 $/día por la ronda de MiniBench
  del 19/10 (29 + 14 enviadas). Línea de ritmo (`presupuesto.ritmo`, colchón 25 %): pendiente
  0,75 $/día, 43,39 $ el 22/10 (margen 4,28 $). La MiniBench no tiene freno de ritmo: si cada ronda
  (cada 2 semanas) cuesta ~10-14 $ (0,7-1,0 $/día), por sí sola ocupa casi toda la pendiente y el
  freno retendrá casi todas las preguntas de la temporada hasta el 06/01. Lanzar más (B/C) añade
  ≤ ~0,1 $/día de MiniBench (~2 perdidas/semana) y nada neto en la temporada (la frena la línea).
- **Visto de paso (no arreglado):** en el marcador del 19/10 «medido por la librería» = 0,0 $ en
  todas las partes (antes medía ~40 %): la librería ya no mide el coste de los modelos. No afecta al
  tope (usa la clave). Gemini 3.8 Flash dio `RateLimitError` de OpenRouter en `39204044175`.

## 22/10/2026 (tarde) — Orden 174: marcador a mano en GitHub; 22 perdidas de 81 en 7 días
- **Crudo:** ejecución `39783847831` de `marcador.yaml` (lanzada a mano 13:05 UTC, en verde; commit
  `e12230f` con `docs/MARCADOR.md`). La sección nueva sale bien en Actions (GH_TOKEN funciona).
- **Perdidas sin explicar 15-22/10:** 22 de 81 cerradas (27 %): 17 MiniBench (ronda del 19/10:
  46127-46178) y 5 temporada (46056, 46066, 46069, 46191, 46193). Todas con hueco de 2,5-5,0 h sin
  lanzamientos alrededor del cierre: las ventanas de la MiniBench son más cortas que los huecos.
  Corrige la cifra de la entrada anterior (6 de 43 era la semana al 19/10).
- **Gasto con el arreglo del reloj (B/C):** ronda MiniBench ≈ 60 preguntas × 0,23 $ ≈ 14 $ cada 14
  días ≈ 1,0 $/día (hoy ~0,72: se pescan ~43 de 60). La línea de ritmo sube 0,75 $/día y la
  MiniBench no tiene freno: con el arreglo, MiniBench sola > línea → el dinero útil (57,89 $ =
  60,89 − 3 de reserva) se acaba hacia el **19/12/2026** y la temporada no recibe nada salvo el margen
  actual (4,28 $). Sin el arreglo: llega al 06/01 pero pierde ~17 MiniBench por ronda y la
  temporada también recibe ~0. Lo decide el usuario (no se aplica nada que cambie el gasto).
