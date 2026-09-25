# ESTADO (siempre «ahora»)

**Actualizado:** 25/09/2026 (sesión 2 en Windows, con los cambios de la sesión en la nube integrados).
**Rama:** todo está en `main` en GitHub. Cada commit se sube solo (gancho `post-commit` = una orden
automática que hace git después de guardar).

## Dónde estamos
El bot está **hecho, probado con simulaciones y apagado**. No ha enviado nada a Metaculus ni ha
gastado un céntimo: no hay token ni claves puestas.

| Pieza | Estado |
|---|---|
| Pruebas automáticas (programa que comprueba el bot solo) | **53 de 53 en verde**, también en Windows |
| Modelos que pronostican | **GPT-6 + Opus 5.5 + Gemini Flash** (3 empresas), cada uno con un modelo de respaldo por si falla. Pagan los créditos de Metaculus |
| Investigación con agentes de Opus 5.5 | **construida**; la paga **tu Claude Max**. Se activa sola cuando pongas su secreto (paso 7) |
| Fallos arreglados hoy | el buscador de noticias había desaparecido (el bot habría pronosticado sin noticias, sin avisar); 5 fallos más encontrados en revisión (uno habría tumbado la MiniBench); 1 prueba que fallaba solo en Windows |
| Flujo de GitHub Actions (el «reloj» que lanza el bot cada 20 min) | listo; **apagado** hasta que pongas secretos e interruptor |

## Lo que decidiste hoy
| Decisión | Qué significa |
|---|---|
| **Repositorio público** | minutos de GitHub gratis e ilimitados y **el doble de créditos** de Metaculus por código abierto. Cualquiera verá el código y los registros de cada ejecución; las claves nunca se ven |
| **Esquema mixto** | pronostican 3 modelos de 3 empresas (lo que tiene más pruebas a favor: juntar 3 opiniones, con GPT dentro); tu idea de Opus 5.5 con varios agentes va en la **investigación**, que es donde los agentes sí han demostrado ayudar, y la paga tu Claude Max |

Por qué no «todo con un solo Opus» (resumen; detalle y fuentes en `HALLAZGOS.md`, 25/09): en la
encuesta de Metaculus usar GPT es lo que más se asocia a quedar arriba y usar Opus no se asocia a
nada; Opus 5.5 salió el 22/09 y nadie ha medido cómo pronostica; y con un solo proveedor, si falla,
se pierde la pregunta.

## Dinero y cupo
| Concepto | Quién paga | Cuánto (estimado) |
|---|---|---|
| 3 modelos que pronostican + búsqueda normal | créditos de Metaculus (o tú si no dan) | ~0,34 $ por pregunta → ~270 $ para ~800 preguntas hasta enero |
| Investigación con agentes de Opus 5.5 | tu **Claude Max** (lo que ya pagas) | 0 € extra, pero **gasta tu cupo semanal** |
| Minutos de GitHub | nadie (repositorio público) | 0 € |

- **Créditos:** este otoño dan **~100 $ al empezar** (y puede que nada: son selectivos); más si el
  bot va por encima de la media en la MiniBench, y el doble por código abierto. Con 100 $ llega para
  ~290 preguntas: dependemos de ir bien para que recarguen.
- **Tu cupo de Max:** el bot usa el mismo cupo que tus sesiones de cripto-quant, bolsa-quant, etc.
  Si se agota, el bot sigue pronosticando sin esa investigación (no se pierde la pregunta), pero tus
  sesiones también se quedarían sin cupo hasta que se reinicie. Cada pregunta apunta en el registro
  cuánto habría costado por API: tras la primera semana te digo cuánto cupo gasta de verdad.
- **Riesgo de cuenta:** las condiciones de Max suponen un «uso ordinario e individual». Un bot
  automático 3 meses es zona gris. Si Anthropic lo limitara, afectaría a tu cuenta entera. Para
  quitarlo en cualquier momento: borra el secreto `CLAUDE_CODE_OAUTH_TOKEN` (el bot sigue sin él).

## Lo que tienes que hacer tú (mejor antes del lunes 28/09)
El sistema no crea cuentas, no acepta condiciones ni toca claves: esto lo haces tú.
No hay prisa extrema: las 1-2 primeras semanas salen pocas preguntas y se puede entrar cuando sea
(cada pregunta perdida son 0 puntos, no negativos).

1. **Crear el bot en Metaculus:** entra con tu cuenta en https://www.metaculus.com/futureeval/participate/
   → «Create your first forecasting bot». Queda inscrito solo en el torneo.
2. **Rellenar el formulario de participación** (obligatorio para todos, 3 preguntas) y, en el mismo,
   **pedir los créditos de IA**: https://forms.gle/aQdYMq9Pisrf1v7d8 . Di que el bot es de **código
   abierto** y pon el enlace del repositorio (reciben el doble).
3. **Aceptar las condiciones del torneo** y **verificar tu identidad** cuando te lo pida (es condición
   para cobrar). Participas como aficionado (los bots de empresas no cobran).
4. **Hacer público el repositorio:** https://github.com/javiergarciarecalde-es/metaculus-quant →
   **Settings** → abajo del todo, **Danger Zone** → **Change visibility** → **Make public** → confirmar.
   Ojo: el primer commit (el que creaste desde la web de GitHub) muestra tu correo de Gmail. No hay
   ninguna clave en el historial (revisado entero).
5. **Sacar el token de Metaculus** (token = contraseña para programas): en Metaculus, Ajustes →
   My Forecasting Bots → «Show Bot Token».
6. **Ponerlo como secreto de GitHub**: en el repositorio → **Settings** → **Secrets and variables** →
   **Actions** → pestaña **Secrets** → **New repository secret**:
   | Nombre (exacto, en mayúsculas) | Valor |
   |---|---|
   | `METACULUS_TOKEN` | el token del paso 5 |
   | `OPENROUTER_API_KEY` | la clave de los créditos (llega por correo) o una tuya |
   Nunca pegues estas claves en ningún fichero ni en un chat.
7. **Permiso de tu Claude Max para el bot** (para la investigación con agentes):
   - Instala Claude Code en la línea de órdenes (no lo tienes: la app de escritorio no basta). Abre
     **PowerShell** y escribe: `irm https://claude.ai/install.ps1 | iex`
   - Cierra y abre PowerShell, escribe `claude setup-token` y sigue lo que te pida en el navegador.
     Al final te enseña un código largo (es una contraseña de tu cuenta: no lo pegues en ningún chat).
   - Ponlo como secreto de GitHub igual que en el paso 6, con el nombre `CLAUDE_CODE_OAUTH_TOKEN`.
8. **Primera prueba, sin enviar nada:** pestaña **Actions** → «Pronosticar en el torneo» →
   **Run workflow** → modo `test_questions` → botón verde. Pronostica 3 preguntas de la zona de
   pruebas (no del torneo) y no envía. Debe acabar en verde con «Terminado: 3 pronósticos de ensayo».
   Gasta un poco de créditos y de tu cupo de Max. Si sale algo en amarillo o rojo, dímelo.
9. **Encender el envío real**: mismo sitio del paso 6, pestaña **Variables** → **New repository
   variable** → nombre `ENVIO_REAL`, valor `true`. Luego repite el paso 8: ahora sí envía, pero a la
   zona de pruebas; mira el perfil del bot en Metaculus. Desde ahí pronostica solo cada 20 minutos.
10. **Al final de la temporada:** rellenar la encuesta del bot (obligatoria para cobrar). Te lo recordaré.

Para **apagarlo**: borra la variable `ENVIO_REAL` (o ponla en `false`). No toques nunca un
pronóstico a mano ni relances el bot «porque no te gusta»: está prohibido.

## Pendiente de decisión o de datos
1. **Reloj de GitHub poco fiable** (otro participante vio que solo lanzaba ~22 % de las veces):
   lo miramos tras la primera semana con los datos del registro.
2. **Reloj apagado tras 60 días sin cambios** (norma de GitHub en repositorios públicos): mientras
   haya sesiones que guarden algo al menos una vez al mes, no pasa. Si no, añado un guardado mensual.
3. **Opcional, noticias gratis (AskNews):** Metaculus tiene un acuerdo con AskNews (un servicio de
   noticias para bots). Para darte de alta hay que escribirles con tu nombre y LinkedIn; lo harías
   tú. No es necesario para empezar.
4. **Una sola sesión a la vez:** hoy la sesión de la nube y la del ordenador han cambiado el mismo
   código a la vez (se juntó bien, 3 veces). Mejor que trabaje una cada vez.

## Cuánto queda sin verificar (de frente)
- El bot **nunca ha hablado con Metaculus ni con una IA de verdad**: solo con simulaciones. El paso 8
  es la primera prueba real.
- La investigación con Claude Max no se ha probado con tu cuenta (no debo gastar tu cupo desde aquí):
  lo que devuelve Claude Code y el aviso de cupo agotado están tomados de la documentación.
- La búsqueda en internet del modelo (`:online`) tampoco se ha probado de verdad.
- Los costes y el cupo gastado son estimaciones hasta la primera ejecución real.
- Si llegan créditos y cuánto: depende de Metaculus.

## Qué toca en la próxima sesión
- Leer lo que salió del paso 8 y corregir lo que falle; cambiar costes estimados por medidos
  (créditos y cupo de Max).
- Tras la primera semana: ¿el reloj de GitHub lanza de verdad cada 20 min? ¿Cuánto cupo gasta Max?
- Tras las primeras semanas: medir con el registro y la tabla de Metaculus cómo vamos frente a
  la puerta de la fase 0.
