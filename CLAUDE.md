# CLAUDE.md — instrucciones permanentes de metaculus-quant

Bot que participa solo (sin intervención humana) en los torneos de pronósticos para bots
de Metaculus (FutureEval / AI Benchmark y MiniBench). No se apuesta dinero: son premios.
Proyecto coordinado por «mando-quant». Qué es y cómo debe ser: `docs/MAESTRO.md`.

Reglas comunes a todos los proyectos: `C:\Users\Administrador\Proyectos\CLAUDE.md` (se cargan solas).
Aquí solo lo propio de este proyecto.

## Protocolo de sesión (matices propios)
- `docs/DECISIONES.md` (documento propio, no está en las comunes §7): solo decisiones del
  USUARIO, con fecha (hora de Madrid).
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

## Estructura
- `main.py` — punto de entrada (igual que la plantilla oficial de Metaculus).
- `bot/` — lógica del bot (pronóstico, agregación, registro, interruptores).
- `tests/` — pruebas automáticas (pytest) con API y modelo simulados. `pytest -q` debe dar verde.
- `.github/workflows/` — ejecución cada 20 minutos + manual; marcador semanal los lunes.
- `config/params.yaml` — parámetros y la puerta. Sus cambios, en `CHANGELOG.md`.
- `registro/` — registro de pronósticos (se guarda como artefacto de GitHub Actions).

## Excepciones a las reglas comunes
- **Estructura de carpetas (comunes §6):** el código sigue la estructura de la plantilla oficial
  de Metaculus (`main.py` y `bot/`), no `src/` y `scripts/`. Motivo: el bot está construido sobre esa
  plantilla y conserva su forma.
