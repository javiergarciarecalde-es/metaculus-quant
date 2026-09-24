# CLAUDE.md — instrucciones permanentes de metaculus-quant

Bot que participa solo (sin intervención humana) en los torneos de pronósticos para bots
de Metaculus (FutureEval / AI Benchmark y MiniBench). No se apuesta dinero: son premios.
Proyecto coordinado por «mando-quant».

## Protocolo de sesión
1. Lo PRIMERO: leer `docs/ESTADO.md`.
2. Trabajar por tramos pequeños; al terminar cada tramo: commit (mensaje en español) y push.
   La sesión puede cortarse en cualquier momento: nunca perder más de un tramo.
3. Lo ÚLTIMO: actualizar `docs/ESTADO.md` (corto, siempre en presente: dónde estamos, qué toca,
   qué espera decisión del usuario).
4. `docs/HALLAZGOS.md` es una bitácora que solo crece (se añade al final, con fecha; no se borra).
5. `docs/DECISIONES.md`: solo decisiones del USUARIO, con fecha.
6. `docs/FUENTES.md`: cada fuente marcada «verificado» (leída por nosotros) o «visto en web».
7. Trabajar en `main`. Si el push a main se rechaza, usar una rama y decirlo en ESTADO.

## Cómo hablar al usuario (obligatorio)
El usuario NO programa. Todo lo que él lea (ESTADO, mensajes finales) va en español llano:
palabras sencillas; cada término técnico lleva al lado una aclaración corta, en cada documento
donde salga. Explicar qué se hizo, por qué y qué significa para él (dinero, riesgo, fechas, qué
tiene que hacer). Lo que salga mal, de frente. Cifras en tablas.

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
5. Commit + push tras cada tramo, mensajes en español.
6. No pulir sin fin: cuando se cumple el criterio de terminado, cerrar.
7. **Intervenir a mano en los pronósticos está prohibido** por las reglas del torneo: el bot
   pronostica solo. Nunca editar ni enviar un pronóstico concreto a mano.

## Puerta de la fase 0 (NO CAMBIAR; copia literal en `config/params.yaml`)
Se suma la puntuación de pares de todas las rondas de la fase 0: las MiniBench de octubre a
diciembre de 2026 y la temporada de otoño. El bot sigue solo si supera al mejor bot de Metaculus
del momento Y su proyección cae entre los 20 primeros de la temporada. Si no, se cierra.
(Referencia: 1.º ~3.600 $/temporada, 10.º ~1.700 $, 20.º ~1.000-1.100 $, media tabla ~0.)

## Trampas conocidas
- El usuario trabaja en Windows.
- Windows corta órdenes de más de ~8.000 caracteres: no pasar textos largos por línea de órdenes.
- Las rutas largas de Windows rompen Python: temporales en carpetas cortas (p. ej. `C:\t\`).
- La web de metaculus.com puede estar bloqueada desde el entorno en la nube; GitHub raw sí carga.

## Estructura
- `main.py` — punto de entrada (igual que la plantilla oficial de Metaculus).
- `bot/` — lógica del bot (pronóstico, agregación, registro, interruptores).
- `tests/` — pruebas automáticas (pytest) con API y modelo simulados. `pytest -q` debe dar verde.
- `.github/workflows/` — ejecución cada 20 minutos + manual.
- `config/params.yaml` — parámetros y la puerta.
- `registro/` — registro de pronósticos (se guarda como artefacto de GitHub Actions).
