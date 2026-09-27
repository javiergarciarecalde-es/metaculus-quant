# CHANGELOG — cambios de parámetros

Cada cambio de un número o una elección del bot (modelos, horarios, límites de probabilidad,
topes de tiempo): fecha, motivo, valor anterior y posterior. Los parámetros viven en
`config/params.yaml`; los horarios y el tope de tiempo del flujo, en `.github/workflows/`.
Lo más nuevo, arriba. Las entradas del 24 y 25/09/2026 se han reconstruido del historial de git
(el commit va entre corchetes) y de HALLAZGOS el 25/09/2026.

## 2026-09-27 (orden 26 del mando: tope de gasto de los 100 $ de créditos)

Motivo: llegó la clave de créditos de Metaculus (100 $ para FutureEval y MiniBench; sube sola si la
MiniBench va por encima de la media). Sin tope, el bot gastaría al ritmo de las preguntas que salgan
(~0,34 $ cada una, ~800 preguntas hasta enero ≈ 270 $) y se quedaría sin dinero a mitad de otoño.
No cambia qué pronostica el bot en cada pregunta: solo cuántas empieza y en qué orden.

| Parámetro o pieza | Antes | Después | Motivo |
|---|---|---|---|
| `presupuesto.total_usd` | no existía | 100 | Correo de Metaculus del 27/09; solo si la clave no trae su propio límite |
| `presupuesto.reserva_usd` | no existía | 3 $ | Por debajo, no se empieza nada (aviso amarillo, sin rojo cada 20 min) |
| `presupuesto.coste_previsto_por_pregunta_usd` | no existía | 0,40 $ | Para contar cuántas preguntas caben; ensayo del 27/09: 0,11-0,23 $ sin la búsqueda de noticias |
| `presupuesto.tope_por_pregunta_usd` | no existía | 1,50 $ | Freno por pregunta (solo lo que la librería sabe medir) |
| `presupuesto.ritmo.*` | no existía | 28/09/2026 → 06/01/2027, colchón 25 % | La temporada va al ritmo de una línea de gasto; la MiniBench, no |
| Orden de los torneos | temporada, luego MiniBench | MiniBench, luego temporada | La MiniBench decide si llega más dinero |
| Preguntas ya enviadas | las quitaba la librería | se quitan antes de contar cuántas caben | Para que no ocupen sitio en el tope |
| `pronostico.max_preguntas_ensayo` (alcance) | 3 preguntas solo en ensayo sin envío; con envío, la zona de pruebas hacía **todas** | 3 también en la zona de pruebas con envío | Visto al encender el envío el 27/09: la prueba gastaba créditos y plan en todas las preguntas de práctica |
| `investigacion.claude_max.una_de_cada` | no existía (Claude investigaba todas) | 2: solo las preguntas de número par | Decisión del usuario del 27/09: gasta la mitad de su plan de Claude y deja un grupo de comparación para medir si ayuda. **Cambia la información que reciben los modelos en la mitad de las preguntas** |

## 2026-09-25 (noche, mejoras A, B y C: decisión del usuario, antes de que abra el torneo)

Motivo: estudio de bots rivales (`docs/ESTUDIO_BOTS.md`). Cambian los textos que reciben los modelos
(C), el orden de las preguntas (B) y lo que se guarda (A). Los límites, modelos y pasadas no cambian.

| Parámetro o pieza | Antes | Después | Motivo |
|---|---|---|---|
| `investigacion.max_enlaces_resolucion` | no existía | 5 | C: enlaces de las condiciones de resolución, «consultar primero» |
| `investigacion.claude_max.minutos_minimos_antes_del_cierre` | no existía | 30 min | B: sin investigación de Claude si la pregunta cierra antes |
| Orden de las preguntas | el que da Metaculus | primero las que cierran antes | B |
| Texto de la búsqueda de noticias | sin enlaces | con enlaces de resolución y «fecha y volumen al citar un mercado» | C (4a, 4b) |
| Texto de Claude | 3 ángulos | «verificar primero» 2-3 datos clave, cita literal de la fuente, fechas | C (5) |
| Textos de los 3 pronosticadores | — | + 3 reglas de lectura (mercados con poco volumen, escaleras de tramos, «RESUELTO») | C (4c) |
| Registro | razonamiento recortado | investigación entera y su estado, criterios, cierre, fecha, razonamiento de cada modelo | A |
| `marcador.comparador.*` | no existía | 3 variantes decididas de antemano (media, sin google, límites 1-99 %), mínimo 150 preguntas, límites alternativos 0,01-0,99 | Comparador de formas de juntar (decisión del usuario); no cambia lo que se envía |

## 2026-09-25 (tarde, orden 14 del mando: el código a las reglas comunes)

Ningún valor cambia: son números que estaban escritos dentro del código y pasan al fichero de
parámetros con el mismo valor. Lo demuestra la prueba `tests/test_configuracion_igual.py`.

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| `modelos.intentos.*` | fijos en `main.py`: 1 (principal con respaldo), 2 (sin respaldo), 2 (respaldo), 1 (búsqueda) | los mismos, en el fichero | Reglas comunes §6: ningún número elegido escondido en el código |
| `modelos.temperatura_lector` / `temperatura_resumidor` / `lector_validaciones` | fijos en `main.py`: 0,0 / 0,3 / 2 | los mismos | Idem (valores de la plantilla oficial) |
| `modelos.proxy_metaculus.investigacion_esfuerzo` | faltaba (el código lo daba por vacío) | `null` (vacío) | Idem: sin valores por defecto |
| `investigacion.busquedas_a_la_vez` / `max_caracteres_informe` | fijos en el código: 1 / 6.000 letras | los mismos | Idem |
| `registro.max_caracteres_razonamiento` / `max_caracteres_error` | fijos: 600 / 300 letras | los mismos | Idem |
| `marcador.horas_de_espera` / `pausa_entre_preguntas_segundos` | fijos: 24 h / 0,5 s | los mismos | Idem |
| `red.tiempo_espera_segundos` | fijo: 30 s | el mismo | Idem |
| Flujos de GitHub: versión de Python | 3.11 | 3.12 | Reglas comunes §6 (decisión del usuario del 25/09) |

## 2026-09-25

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| Flujo «Marcador»: horario | no existía | lunes 06:30 UTC (`30 6 * * 1`) | Marcador semanal nuevo [3b13d98] |
| `investigacion.modo` | `basica` | `claude_max` | Decisión del usuario del 25/09 (esquema mixto: investigación con agentes de Opus 5.5 pagada con su suscripción de Claude) [1605cd4] |
| `investigacion.claude_max.*` | no existía | modelo `claude-opus-5-5`; 3 agentes; 30 turnos; 300 s por pregunta; 3 preguntas a la vez; freno de 3 $ equivalentes por pregunta | Topes para que no bloquee pronósticos ni agote el cupo (HALLAZGOS 25/09, «esquema mixto construido») [1605cd4] |
| Flujo del bot: tope de tiempo (`timeout-minutes`) | 40 min | 60 min | La investigación con Claude suma hasta 5 min por tanda [1605cd4] |
| `tiempos.*` | no existía | 900 s por pasada; 180 s de búsqueda; no empezar preguntas tras 28 min | Un modelo colgado podía cortar la ejecución entera (HALLAZGOS 25/09, revisión con agentes: 5 fallos) [e34210c] |
| `modelos.proxy_metaculus.pronostico` (respaldos) | sin respaldo | gpt-5 ↔ claude-sonnet-4-5, uno de respaldo del otro | Misma revisión: si un modelo caía se perdía 1 de cada 2 preguntas [e34210c] |
| `modelos.openrouter.buscador` | `openai/gpt-4o-search-preview` | `openai/gpt-5.6-sol:online` | Ese modelo ya no existe en OpenRouter (comprobado en vivo el 25/09) [2958420] |
| `modelos.openrouter.pronostico` | gpt-5.6-sol (high) + claude-opus-4.8 (high) + gemini-3.5-flash | gpt-6-sol (high) + claude-opus-5.5 (high) + gemini-3.5-flash, cada uno con respaldo (gpt-5.6-sol, claude-opus-4.8, gpt-6-sol) | Modelos al día; tres empresas recomendado (HALLAZGOS 25/09, «¿3 modelos o un solo Opus?»); confirmado por la decisión del usuario del 25/09 [4ef3e8c] |
| `pronostico.modo` | no existía | `tres_empresas` (alternativa `un_modelo`: Opus 5.5 ×3) | Idea del usuario hecha configurable; nadie ha medido cuál gana [4ef3e8c] |
| `modelos.*.director` y `buscador`; `investigacion.modo` | no existían | director claude-opus-5.5 (proxy: claude-sonnet-4-5); `investigacion.modo: basica`; 2 datos clave; 240 s en total | Investigación ampliada preparada pero apagada hasta medir su coste [4ef3e8c] |
| `modelos.openrouter.investigacion` | `openai/gpt-4o-search-preview` | `openai/gpt-5.6-sol:online`, esfuerzo `low` | Ese modelo ya no existe en OpenRouter [100b81e] |

## 2026-09-24

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| Modelos que pronostican (con clave) | claude-sonnet-4.5, gpt-5, o3 | gpt-5.6-sol (high), claude-opus-4.8 (high), gemini-3.5-flash | Ajuste a lo medido por nostreambot: 3 modelos de 3 empresas, una pasada cada uno (HALLAZGOS 24/09) [3d7c484] |
| Modelos que pronostican (proxy de Metaculus) | claude-sonnet-4-5, gpt-5, o3 | gpt-5 (high), claude-sonnet-4-5 | Idem [3d7c484] |
| `pronostico.pasadas_por_pregunta` | 5 | 3 | Una pasada por modelo [3d7c484] |
| `pronostico.factor_extremizar` | 1.15 | 1.0 (apagado) | nostreambot lo probó y lo descartó [3d7c484] |
| `modelos.temperatura` | 0.3 | `null` (la del modelo) | Lo recomendado en modelos que razonan [3d7c484] |
| `modelos.tiempo_max_segundos` | 180 | 600 | Motivo no escrito; va en el mismo cambio que el paso a modelos con razonamiento alto [3d7c484] |
| Flujo del bot: horario y tope | no existía | minutos 7, 27 y 47 de cada hora (cada 20 min); tope 40 min | Horario de la plantilla oficial [e207d3a] |
| Valores iniciales | — | límites de probabilidad 2 %-98 %; mínimo 1 % por opción; 1 búsqueda por pregunta; 3 preguntas en ensayo | Primer borrador; los límites, iguales que nostreambot [5e0c8de] |
