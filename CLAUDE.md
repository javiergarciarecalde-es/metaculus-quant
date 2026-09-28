# CLAUDE.md — instrucciones permanentes de metaculus-quant

Bot que participa solo (sin intervención humana) en los torneos de pronósticos para bots
de Metaculus (FutureEval / AI Benchmark y MiniBench). No se apuesta dinero: son premios.
Proyecto coordinado por «mando-quant». Qué es y cómo debe ser: `docs/MAESTRO.md`.

Reglas comunes a todos los proyectos: `C:\Users\Administrador\Proyectos\CLAUDE.md` (se cargan solas).
Aquí solo lo propio de este proyecto.

## Protocolo de sesión (matices propios)
- `docs/DECISIONES.md` (documento propio, no está en las comunes §7): solo decisiones del
  USUARIO, con fecha (hora de Madrid).
- `docs/REVISION_SEMANAL.md` (documento propio): ¿qué dijo la revisión automática de este lunes?
  Lo sobrescribe entero cada lunes la rutina de Claude (desde el 05/10/2026); nadie más lo toca.
  El mando lo recoge los lunes. `docs/MARCADOR.md` lo genera el marcador; tampoco se toca a mano.
- `docs/ESTADO.md`: corto y siempre en presente.
- Mensajes de commit en español.
- Si el push a `main` se rechaza, usar una rama y decirlo en ESTADO.

## Reglas duras
1. El sistema nunca mueve dinero, no crea cuentas, no acepta condiciones y no toca credenciales.
   Las claves (token de Metaculus, claves de IA) las pone el usuario como secretos de GitHub;
   nunca se escriben en el código ni en ficheros.
2. Nada se envía a Metaculus sin que el usuario encienda el interruptor `ENVIO_REAL`
   (variable de GitHub). Todo se prueba en modo ensayo (sin enviar) y con respuestas simuladas.
3. No gastar dinero en ninguna API desde las sesiones de desarrollo. Si hace falta una clave
   para probar algo, se deja preparado y anotado.
4. El flujo de GitHub Actions corre cada 20 minutos pero es inofensivo sin secretos: si falta el
   token termina limpio con un aviso (sin error rojo). Envío real apagado hasta que el usuario
   ponga `ENVIO_REAL=true`.
5. **Intervenir a mano en los pronósticos está prohibido** por las reglas del torneo: el bot
   pronostica solo. Nunca editar ni enviar un pronóstico concreto a mano.

## Regla de cambios (normas del torneo; orden 27, aprobada por el usuario el 28/09/2026)
Normas en `docs/FUENTES.md`: se puede actualizar el bot, pero no mirar cómo pronostica preguntas
abiertas o próximas del torneo y ajustarlo según eso, ni relanzarlo porque no guste un pronóstico;
un solo pronóstico por pregunta.
1. Lo que cambie cómo pronostica (textos, modelos, investigación, agregación, límites) se decide
   solo con preguntas **cerradas** del torneo o de **fuera** (zona de pruebas, web principal).
   Nunca se prueba sobre preguntas abiertas del torneo.
2. De las abiertas del torneo solo se mira si las piezas funcionan (estado, errores, tiempo,
   coste); nunca el pronóstico, el razonamiento ni la investigación. De ahí solo salen arreglos.
3. Nunca se relanza el bot sobre una pregunta ya pronosticada ni se toca su pronóstico
   (`bot/normas.py` lo impide). Relanzar el bot entero sí: solo hace las que faltan.
4. Cada cambio importante, a `CHANGELOG.md` con fecha, motivo y **con qué datos se decidió**: para
   cobrar hay que describir el bot con sus actualizaciones importantes y aceptar una inspección.
5. Lo que se sube al repositorio (público) no enseña pronósticos de preguntas abiertas.

## Puerta de la fase 0 (NO CAMBIAR; copia literal en `config/params.yaml`)
Se suma la puntuación de pares de todas las rondas de la fase 0: las MiniBench de octubre a
diciembre de 2026 y la temporada de otoño. El bot sigue solo si supera al mejor bot de Metaculus
del momento Y su proyección cae entre los 20 primeros de la temporada. Si no, se cierra.
(Referencia: 1.º ~3.600 $/temporada, 10.º ~1.700 $, 20.º ~1.000-1.100 $, media tabla ~0.)

## Trampas conocidas (las de Windows están en las comunes §10)
- La web de metaculus.com puede estar bloqueada desde el entorno en la nube; GitHub raw sí carga.
- La sesión de la nube y la local pueden subir a `main` a la vez: `git fetch` antes de cada push.
- El historial de git se reescribió el 25/09/2026 (quitar el correo del usuario): una copia
  descargada antes de esa fecha hay que volver a descargarla, no juntarla.
- En Windows el reloj avanza a saltos de ~15 ms: una prueba que mida tiempos muy cortos puede dar
  0 y fallar solo aquí.
- El reloj de GitHub Actions no es fiable (a otro participante solo lanzó ~22 % de las veces) y en
  repositorios públicos se apaga tras 60 días sin commits.

- La clave de créditos de Metaculus gasta como «byok»: en OpenRouter `usage` da 0 y lo gastado sale en
  `byok_usage`. Quien mire solo `usage` creerá que no se gasta nada (visto el 27/09/2026).
- La librería no mide el coste de la búsqueda `:online`: cuenta ~60 % de lo gastado. La cifra buena es
  la de la clave (`bot/presupuesto.py`).
- Cambiar un parámetro a propósito hace fallar `tests/test_configuracion_igual.py` (la foto de la
  configuración): se regenera con `python -m tests.test_configuracion_igual` en el mismo commit que
  la entrada de `CHANGELOG.md`. Si falla sin haber cambiado nada, algo cambió el comportamiento.
- La librería da por NO pronosticada una pregunta si Metaculus no manda `my_forecasts.history`
  (falla abierta) y el bot la repetiría cada 20 min: `bot/normas.py` falla cerrada (28/09/2026).
- Una pregunta de la temporada puede seguir abierta más de 10 h (la 45707, ~11 h): «hace más de
  24 h» no prueba que esté cerrada; el marcador mira su hora de cierre.
- El repositorio es público: los registros y artefactos de GitHub del bot (con sus pronósticos)
  los puede ver cualquiera con cuenta de GitHub, también mientras la pregunta está abierta.
- Una rutina de Claude que escribe en una conversación existente deja de funcionar si se archiva esa
  conversación, y su resultado no se ve en la aplicación del usuario (28/09/2026).

## Estructura
- `main.py` — punto de entrada (igual que la plantilla oficial de Metaculus).
- `bot/` — lógica del bot (pronóstico, agregación, registro, interruptores; tope de gasto en
  `presupuesto.py`). Los parámetros se leen con `bot/params.py` (`ajustes.p("seccion.nombre")`), que falla si falta uno: nunca hay valor por defecto.
- `tests/` — pruebas automáticas (pytest) con API y modelo simulados. `pytest -q`, `ruff format --check .` y
  `ruff check .` deben dar verde (Python 3.12).
- `.github/workflows/` — ejecución cada 20 minutos + manual; marcador semanal los lunes.
- `config/params.yaml` — parámetros y la puerta. Sus cambios, en `CHANGELOG.md`.
- `registro/` — registro de pronósticos (se guarda como artefacto de GitHub Actions).

## Límites de tamaño de los documentos (comunes §7)
Las pruebas leen esta tabla (`tests/test_documentacion.py`); si uno se pasa, vale lo de las comunes §7
(el relato va a HALLAZGOS; si aun así no cabe, se sube la cifra aquí con fecha y motivo).
Fijados el 25/09/2026 (orden 14) con margen sobre lo que medían ese día (entre paréntesis).

| Archivo | Tope |
|---|---|
| `CLAUDE.md` | ~120 líneas (78) |
| `ESTADO.md` | ~1.800 palabras (1.355) |
| `FUENTES.md` | ~1.500 palabras (317) |
| `HALLAZGOS.md` | ~500 líneas (366); al pasar de ~400, lo viejo va a `docs/archivo/` |

## Excepciones a las reglas comunes
- **Estructura de carpetas (comunes §6):** el código sigue la estructura de la plantilla oficial
  de Metaculus (`main.py` y `bot/`), no `src/` y `scripts/`; por eso el lector de parámetros es
  `bot/params.py` y no `src/params.py`. Motivo: el bot está construido sobre esa plantilla y conserva
  su forma. Es la única excepción: Python 3.12, ruff y los parámetros sin valor por defecto siguen las
  comunes §6 desde el 25/09/2026 (orden 14).
