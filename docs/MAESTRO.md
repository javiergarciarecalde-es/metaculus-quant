# MAESTRO — qué es metaculus-quant y cómo debe ser

Especificación del proyecto. La cambia el usuario, previo acuerdo. Recoge lo que el 25/09/2026
estaba repartido entre `CLAUDE.md`, `docs/ESTADO.md`, `docs/DECISIONES.md` y `config/params.yaml`;
no añade nada nuevo. Dónde estamos hoy: `docs/ESTADO.md`.

## Qué hace
Un bot (programa) que pronostica solo, sin intervención humana, las preguntas de los torneos para
bots de Metaculus: la temporada de otoño 2026 de **FutureEval / AI Benchmark** y las rondas
**MiniBench**. No se apuesta dinero: Metaculus reparte premios entre los mejores.
- Se ejecuta en GitHub Actions (el servicio de GitHub que lanza programas) cada 20 minutos, y a mano
  cuando se quiera. El bot se llama **Kyou-bot** en Metaculus.
- Por cada pregunta: busca noticias, 3 modelos de IA de 3 empresas dan cada uno su probabilidad, y se
  toma la del medio (mediana), sin bajar del 2 % ni subir del 98 %. Además, agentes de Claude Opus 5.5
  investigan en la web y su informe se añade al de noticias (decisión del usuario del 25/09).
- Publica con cada pronóstico un comentario privado con su razonamiento (obligatorio en el torneo).
- Envía de verdad solo si el usuario enciende el interruptor `ENVIO_REAL`; si no, ensaya sin enviar.
- Cada lunes compara lo pronosticado con lo que pasó y la puntuación oficial (`docs/MARCADOR.md`).
- Modelos y números concretos: `config/params.yaml`; su historia, `CHANGELOG.md`.

## Torneos
| Torneo | Qué es |
|---|---|
| Temporada de otoño 2026 (FutureEval) | preguntas desde el 28/09/2026; últimos pronósticos el 06/01/2027 |
| MiniBench | rondas de ~60 preguntas cada 2 semanas, casi todas en los primeros días |
| Zona de pruebas (`bot-testing-area`) | donde se ensaya; nunca se ensaya en preguntas del torneo |

## Normas del torneo que atan al proyecto
- Prohibido pronosticar a mano, retocar el bot mirando preguntas abiertas del torneo o relanzarlo
  porque no guste un resultado.
- Un solo bot con premio por persona. Para cobrar: enseñar el código o una descripción, aceptar una
  inspección y rellenar la encuesta del bot al final de la temporada. La identidad se pide al cobrar.
- Inscribirse y enviar pronósticos equivale a aceptar las normas.

## Fases
**Fase 0: competir de verdad** en las MiniBench de octubre a diciembre de 2026 y en la temporada de
otoño. Es la única fase definida. Lo que venga después lo decide el usuario al pasar la puerta.

### Puerta de la fase 0 (copia literal; NO CAMBIAR; fijada el 24/09/2026)
Se suma la puntuación de pares de todas las rondas de la fase 0: las MiniBench de octubre a
diciembre de 2026 y la temporada de otoño. El bot sigue solo si supera al mejor bot de Metaculus
del momento Y su proyección cae entre los 20 primeros de la temporada. Si no, se cierra.
(Referencia: 1.º ~3.600 $/temporada, 10.º ~1.700 $, 20.º ~1.000-1.100 $, media tabla ~0.)

## Costes (estimados; se cambiarán por lo medido)
| Concepto | Quién paga | Cuánto |
|---|---|---|
| 3 modelos que pronostican + búsqueda de noticias | créditos gratuitos de Metaculus (una clave de OpenRouter, la tienda de modelos de IA); sin créditos, el usuario solo si lo decide | ~0,34 $ por pregunta → ~270 $ hasta enero |
| Investigación con agentes de Opus 5.5 | la suscripción de Claude del usuario | 0 € extra, pero gasta su cupo compartido con los demás proyectos |
| Minutos de GitHub | nadie (repositorio público) | 0 € |
| Capital | — | 0 €: no se arriesga dinero |
Ninguna clave de pago se pone sin decisión del usuario.
