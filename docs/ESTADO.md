# ESTADO (siempre «ahora»)

**Última actualización:** 22/10/2026, 15:40 (hora de Madrid), sesión «Metaculus: revisar el robot
(orden 174)».
**Fase:** **APARCADO Y ARCHIVADO** desde el 22/10/2026 ~15:35 (decisión del usuario, DECISIONES).
Nada corre: ni el bot, ni la vigilancia, ni el marcador, ni las pruebas. No gasta plan de Claude,
ni créditos, ni API, ni minutos de GitHub.
**Rama:** todo está en `main` en GitHub.

## Quién está tocando qué
Nadie. Ninguna sesión trabaja en este proyecto salvo orden expresa del usuario.

## Por qué se aparcó (revisión del 22/10; detalle en HALLAZGOS 22/10)
| Dato | Kyou-bot | Para seguir hacía falta | Valoración |
|---|---|---|---|
| Temporada de otoño | 185.º de 253, 0,5 puntos | entre los 20 primeros (el 20.º: 53) | OJO: muy lejos |
| MiniBench del 05/10 | 83.º de 211, 146 puntos | ganar al mejor bot de Metaculus (505) | OJO: muy lejos |
| Créditos | 39,11 $ gastados de 100 $; Metaculus no da más | llegar al 06/01 | justo, a costa de la temporada |
| Reloj de GitHub | 3-8 lanzamientos al día de 72 desde el 10/10 | 72 | 22 de 81 preguntas perdidas (15-22/10) |

La puerta de la fase 0 (CLAUDE.md) se iba a evaluar en enero; el usuario cerró antes con estos datos.

## Qué está apagado (22/10 ~15:35, comprobado con `gh workflow list --all`)
| Pieza | Estado | Cómo se vuelve a encender |
|---|---|---|
| Flujo «Pronosticar en el torneo» | desactivado (no borrado) | GitHub → Actions → el flujo → «Enable workflow», o `gh workflow enable run_bot_on_tournament.yaml` |
| Flujos «Vigilancia», «Marcador», «Pruebas», «Modelos de la clave» | desactivados (no borrados); la subida del 22/10 15:37 ya no lanzó pruebas | igual, cada uno |
| Variable `ENVIO_REAL` | `false` (antes `true` desde el 27/09) | ponerla en `true` |
| Rutina de revisión de los lunes (`trig_01P1NPoMLt4LgerQFDWu4MZ8`) | apagada desde el 07/10 (comprobado el 22/10) | encenderla |
| Tareas programadas del ordenador | ninguna de este proyecto (comprobado el 22/10) | — |

## Lo que queda tal cual (no se ha borrado nada)
- **Secretos en GitHub:** `METACULUS_TOKEN`, `OPENROUTER_API_KEY` y `CLAUDE_CODE_OAUTH_TOKEN`. Sin
  flujos encendidos no se usan. Borrarlos es opcional y lo haría el usuario (Settings → Secrets).
- **Créditos de OpenRouter:** quedan ~60,89 $ de 100 $ (son de Metaculus; no se pierde dinero tuyo).
- **Bot en Metaculus (Kyou-bot):** sus pronósticos ya enviados siguen contando hasta que resuelvan;
  no se envía ninguno más. Si ganara algún premio, no se cobra hasta que conteste Fremap (comunes §13).
- **Repositorio público** con el código, el marcador y la historia (HALLAZGOS, DECISIONES).
- El marcador quedó en el del 22/10 (`docs/MARCADOR.md`); ya no se actualiza.

## Cosas sueltas para el usuario (ninguna urgente)
1. **AskNews:** si contestan, ya no hace falta poner sus claves.
2. **Archivar la conversación de la nube** «Metaculus: encender el bot con los 100 $ (orden 26)» y esta
   sesión: ya se puede.
3. **Tu correo en el primer commit:** GitHub aún enseña la versión vieja a quien tenga su
   identificador exacto. Para borrarla del todo: soporte de GitHub (opcional).

## Trampas vivas si alguien lo reabre
- Leer CLAUDE.md (reglas duras y regla de cambios del torneo) antes de encender nada.
- El reloj de GitHub lanzaba el bot cada 3-5 h desde el 10/10: sin un lanzador externo se pierden
  preguntas (opciones en HALLAZGOS 22/10).
- La API de Metaculus ya no responde sin token (22/10).
- Con los créditos que quedan, la MiniBench sola (~1 $/día) se comería casi todo; la temporada
  quedaría sin pronósticos.
