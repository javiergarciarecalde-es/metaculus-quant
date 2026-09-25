# CHANGELOG — cambios de parámetros

Cada cambio de un número o una elección del bot (modelos, horarios, límites de probabilidad,
topes de tiempo): fecha, motivo, valor anterior y posterior. Los parámetros viven en
`config/params.yaml`; los horarios y el tope de tiempo del flujo, en `.github/workflows/`.
Lo más nuevo, arriba. Las entradas del 24 y 25/09/2026 se han reconstruido del historial de git
(el commit va entre corchetes) y de HALLAZGOS el 25/09/2026.

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
