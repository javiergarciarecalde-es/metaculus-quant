# CHANGELOG — cambios de parámetros

Cada cambio de un número o una elección del bot (modelos, horarios, límites de probabilidad,
topes de tiempo): fecha, motivo, valor anterior y posterior. Los parámetros viven en
`config/params.yaml`; los horarios y el tope de tiempo del flujo, en `.github/workflows/`.
Lo más nuevo, arriba. Las entradas del 24 y 25/09/2026 se han reconstruido del historial de git
(el commit va entre corchetes) y de HALLAZGOS el 25/09/2026.

## 2026-09-28 mañana (decisión del usuario: segundo clasificador en sombra con Opus 5.5 «xhigh»)

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| `clasificador.claude.*` (nuevo) | no existía | Opus 5.5 con esfuerzo `xhigh` (extra alto), plan Max, sin herramientas, 2 turnos, tope 1 $ equivalente, 180 s, 3 a la vez | Decisión del usuario: ver si un modelo más potente clasifica mejor que Gemini 3.8 Flash. Los dos en paralelo y en sombra; no deciden nada |

## 2026-09-28 mañana (decisión del usuario: opción A con Claude Max y clasificador en sombra)

**Cambia la investigación en las preguntas de número par** desde el 28/09/2026 (~08:20 UTC):
la hace Claude Max (plan del usuario) en lugar de la búsqueda de pago.

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| `investigacion.claude_max.sustituye_busqueda` (nuevo) | Claude se sumaba a la búsqueda de pago | `true`: en las preguntas del reparto (pares) Claude busca desde cero y la búsqueda de pago solo entra si Claude falla, no tiene cupo o no hay tiempo | Opción A del usuario: ~20 % menos gasto de créditos (~70 preguntas más), ~10 % del tope semanal de su plan, y deja comparar búsqueda con Max frente a búsqueda de pago |
| `modelos.*.clasificador` (nuevo) | no existía | Gemini 3.8 Flash (en el bloque del intermediario de Metaculus: apagado) | Clasificador en sombra: fácil/normal/difícil antes de investigar; no decide nada |
| `clasificador.tope_segundos` / `max_caracteres` (nuevos) | no existían | 30 s / 3.000 letras | Que nunca retrase la pregunta |

## 2026-09-28 mañana (decisión del usuario: solo Opus 5.5 de Anthropic, GPT-6 Sol/Astra de OpenAI)

**Cambia la investigación** (otro modelo busca las noticias) desde el 28/09/2026 (~07:50 UTC):
para comparar en el marcador, las preguntas anteriores llevan la búsqueda de GPT-5.6 Sol.

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| `modelos.openrouter.investigacion` | `openai/gpt-5.6-sol:online` | `anthropic/claude-opus-5.5:online` | Decisión del usuario: «el de mayor calidad y rigor analítico». Más caro por token (4/20 $ frente a 2/10 $ por millón) |
| `modelos.openrouter.investigacion_respaldo` (nuevo) | no existía (si fallaba, sin noticias) | `openai/gpt-6-sol:online` | Si la búsqueda principal falla o sale vacía, busca otro |
| Respaldo del puesto de OpenAI | `openai/gpt-5.6-sol` | `openai/gpt-6-astra` | De OpenAI solo GPT-6 Sol (uso común) y Astra (razonamiento avanzado) |
| Respaldo del puesto de Anthropic | `anthropic/claude-opus-4.8` | ninguno (Opus 5.5 se reintenta una vez) | De Anthropic solo Opus 5.5 |
| `modelos.openrouter.buscador` (modo ampliada, apagado) | `openai/gpt-5.6-sol:online` | `anthropic/claude-opus-5.5:online` | Igual que la búsqueda |
| Lotes («:batch», más baratos) | — | no se usan | Las preguntas están abiertas ~1,5-3 h y la respuesta por lotes puede tardar horas; la librería no los admite |

## 2026-09-28 mañana (decisión del usuario: Gemini 3.8 Flash)

**Cambia los pronósticos** del puesto de Google desde el 28/09/2026 (~06:50 UTC), el día que abre
la temporada. Para comparar modelos en el marcador, las preguntas de antes de esa hora llevan
Gemini 3.5 Flash.

| Parámetro | Antes | Después | Motivo |
|---|---|---|---|
| `modelos.openrouter.pronostico[2].nombre` | `openrouter/google/gemini-3.5-flash` | `openrouter/google/gemini-3.8-flash` | Decisión del usuario («funciona mejor que el Pro»). Consulta gratuita del 28/09: la clave lo permite y cuesta 0,75/3,75 $ por millón de tokens frente a 1,5/9 $. Respaldo sin cambios (GPT-6) |

## 2026-09-28 (pregunta del usuario: ¿qué modelos deja usar la clave?)

| Pieza | Antes | Después | Motivo |
|---|---|---|---|
| Flujo `modelos_clave.yaml` | no existía | solo a mano; pregunta gratis a OpenRouter qué modelos deja usar la clave | Saber si se podrían usar modelos más baratos (p. ej. chinos) sin gastar nada. No cambia el bot |

## 2026-09-27 noche (decisión del usuario ~22:40: la curva suave entra en las comparaciones)

Motivo: la curva suave (PCHIP) es la única variante con una medición a favor en otro bot, y sin
estar «decidida de antemano» nunca se podría adoptar. Se cambia ANTES de ver ningún resultado.

| Parámetro o pieza | Antes | Después | Motivo |
|---|---|---|---|
| `marcador.comparador.preregistradas` | media, sin google, límites 1%-99% | media, sin google, **curva suave (PCHIP)** | «Límites 1 %-99 %» sigue calculándose como exploratoria |
| Comparador en numéricas | no entraban | la curva suave frente a la enviada (cuenta la mitad, como en Metaculus) | Puntuar lo que se guarda en sombra |
| Piezas de los flujos de GitHub | checkout v4, setup-python v5, setup-node v4, upload-artifact v4 | v5, v6, v5, v6 | GitHub quitó Node 20 el 23/09/2026 |

## 2026-09-27 noche (decisión del usuario ~22:40: lista semanal de preguntas perdidas)

Motivo: comprobar con datos reales que la vigilancia no deja escapar preguntas (mejora 1c de
docs/ESTUDIO_BOTS.md). No cambia qué pronostica el bot.

| Parámetro o pieza | Antes | Después | Motivo |
|---|---|---|---|
| `marcador.dias_preguntas_perdidas` | no existía | 7 | El marcador de los lunes lista las preguntas cerradas esa semana sin pronóstico nuestro |
| Registro de las preguntas que deja el tope | solo un aviso | además una línea «dejadas» en `presupuesto_*.jsonl` | Para separar las perdidas a propósito (tope de gasto) de las perdidas sin explicar |

## 2026-09-27 noche (orden 26 del mando: curva numérica suave en sombra)

Motivo: decisión del usuario del 27/09 (~21:55); mejora 3 de docs/ESTUDIO_BOTS.md. **No cambia lo
que se envía**: la curva suave solo se guarda. Sin parámetros nuevos.

| Pieza | Antes | Después | Motivo |
|---|---|---|---|
| `sombra_pchip` en cada numérica del registro | no existía | curva enviada (rectas) y curva PCHIP (suave), 201 puntos cada una | Poder comparar gratis con preguntas resueltas; se activaría solo con ≥150 resueltas y ganando en las dos mitades |

## 2026-09-27 noche (orden 26 del mando: medir en qué se va el dinero)

Motivo: decisión del usuario del 27/09 (~21:55): estirar los 100 $ midiendo primero. No cambia qué
pronostica el bot ni los modelos (el cambio de modelos se propone con datos tras la primera semana).

| Parámetro o pieza | Antes | Después | Motivo |
|---|---|---|---|
| `coste_partes` en cada línea del registro | no existía | coste de cada parte según la librería (búsqueda, cada modelo, lector) | Saber qué parte pesa; la búsqueda «:online» sale ~0 porque la librería no la mide |
| `marcador.dias_resumen_gasto` | no existía | 7 | El marcador de cada lunes resume el gasto de la semana: clave frente a librería y frente a la línea de ritmo |

## 2026-09-27 noche (orden 26 del mando: vigilancia que reacciona sola)

Motivo: decisión del usuario del 27/09 (~21:55): si el bot se calla o falla, que algo automático lo
relance y, si no basta, despierte a Claude; sin avisarle a él. No cambia qué pronostica el bot.

| Parámetro o pieza | Antes | Después | Motivo |
|---|---|---|---|
| Flujo `vigilancia.yaml` | no existía | a :13 y :43 de cada hora, solo con `ENVIO_REAL=true` | Dos veces por hora: el reloj de GitHub no es fiable |
| `vigilancia.minutos_sin_ejecucion_buena` | no existía | 45 | El bot sale cada 20 min: 45 = dos salidas perdidas |
| `vigilancia.minutos_margen_pregunta_nueva` | no existía | 60 | Una pregunta recién abierta aún no es «olvidada» |
| `vigilancia.ventana_horas_relanzamientos` / `relanzamientos_antes_de_claude` | no existían | 3 h / 2 | Dos relanzamientos sin arreglo en 3 h = nivel 2 (Claude) |
| `vigilancia.horas_entre_claude` | no existía | 12 | Como mucho un despertar de Claude cada 12 h (cuida el plan) |
| `vigilancia.claude.*` | no existía | Opus 5.5, 40 turnos, 5 $ equivalentes, 20 min | Topes de Claude Code al diagnosticar |
| `vigilancia.flujo_bot`, `ejecuciones_a_mirar`, `max_caracteres_errores` | no existían | el flujo del bot, 30, 20.000 | Qué mira y cuánto registro de errores le enseña a Claude |
| Título de cada ejecución del bot (`run-name`) | «Pronosticar en el torneo» | lleva el modo y cómo se lanzó | Para distinguir las de torneo de las pruebas a mano |

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
| `investigacion.claude_max.pausada_hasta_utc` | no existía | 28/09/2026 09:00 UTC (11:00 de Madrid); luego vuelve sola | Decisión del usuario del 27/09 (21:25): su tope semanal de Claude estaba al 92 % y la temporada abre de madrugada |
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
