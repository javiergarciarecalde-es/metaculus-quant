# ESTADO (siempre «ahora»)

**Actualizado:** 25/09/2026 (sesión 2 en Windows + sesión en la nube, integradas).
**Rama:** todo está en `main` en GitHub. Cada commit se sube solo (gancho `post-commit` = una orden
automática que hace git después de guardar).

## Dónde estamos
El bot está **hecho, probado en ensayo y apagado**. No ha enviado nada a Metaculus ni ha gastado
un céntimo: no hay token ni claves puestas.

| Pieza | Estado |
|---|---|
| Pruebas automáticas (programa que comprueba el bot solo) | **42 de 42 en verde** (hoy se encontraron y arreglaron 5 fallos, uno de ellos heredado de la plantilla oficial que habría tumbado la MiniBench) |
| Modelos de IA | **ya cambiados a GPT-6 + Opus 5.5 + Gemini Flash** (la opción recomendada), cada uno con un modelo de respaldo por si falla |
| Fallo arreglado hoy | el modelo que buscaba noticias **había desaparecido**: el bot habría pronosticado sin noticias, sin avisar. Cambiado por uno que existe, y ahora cada ejecución comprueba los nombres y avisa |
| Flujo de GitHub Actions (el «reloj» que lanza el bot cada 20 min) | listo; **apagado** hasta que pongas secretos e interruptor |
| Reglas del torneo | hoy **leídas directamente** en la web de Metaculus (anoche no cargaba) |

## Tu pregunta: ¿3 modelos de 3 empresas o un solo Opus 5.5 con varios agentes?
(«agente» = una copia del modelo haciendo un papel: buscar, pronosticar, criticar…)

**Respuesta corta: mejor seguir con 3 empresas, pero metiendo Opus 5.5 en el puesto de Anthropic.**

Lo que está medido por otros (detalle y cifras en `HALLAZGOS.md`, 25/09):
| Prueba | Qué dice |
|---|---|
| Metaculus, primavera: 65 bots iguales cambiando solo el modelo | GPT-5.1 1.º (11,3 puntos/pregunta), Claude Sonnet 2.º (8,9). Diferencia dentro del azar |
| Encuesta de Metaculus a 58 creadores de bots | usar **GPT** es lo que más se asocia a quedar arriba; usar **Opus, nada** (correlación ~0). Los 10 mejores usaban GPT. Ojo: nada es seguro estadísticamente |
| Metaculus: juntar varios bots | juntar 2-10 bots buenos mejora al mejor bot solo |
| nostreambot (el mejor bot abierto): 262 preguntas | combinar 3 pronósticos con la mediana gana claramente a un modelo solo. Pero **que sean de empresas distintas no añadió nada medible** |
| Opus 5.5 | salió el **22/09** (hace 3 días): **nadie ha medido** cómo pronostica |
| Nuestro código | si falla 1 de 3 modelos, el bot pronostica igual con los otros 2. Con un solo Opus, si Anthropic falla, **se pierde la pregunta** (0 puntos) |

En llano: lo que funciona es **juntar 3 opiniones**. Que sean de 3 empresas no está demostrado que
ayude, pero quitar GPT es quitar el modelo con más pruebas a favor, y depender de una sola empresa
es un riesgo. Tu idea sí tiene sentido en una parte: Opus 5.5 es **más nuevo y un 20 % más barato**
que el Opus 4.8 que usamos ahora. nostreambot hizo justo eso hace 3 días (Opus 5.5 + GPT-6).

**Coste por opción** (estimación propia con precios de hoy; «~800 preguntas» = temporada 300-400 +
MiniBench ~60 cada 2 semanas hasta enero; puede salir hasta el doble si los modelos piensan más):
| Opción | $ por pregunta | ~800 preguntas | Con los ~100 $ de créditos llega para |
|---|---|---|---|
| Actual: GPT-5.6 + Opus 4.8 + Gemini Flash | ~0,38 | ~300 $ | ~260 preguntas |
| **Recomendada: GPT-6 + Opus 5.5 + Gemini Flash** | **~0,34** | **~270 $** | **~290 preguntas** |
| Un Opus 5.5 que pronostica 3 veces | ~0,47 | ~375 $ | ~210 preguntas |
| Un Opus 5.5 una sola vez | ~0,19 | ~150 $ | ~520 preguntas (peor puesto esperado) |
| Opus 5.5 con papeles (investiga, 3 pronostican, 1 critica) | ~0,80 | ~640 $ | ~125 preguntas |

- **Con créditos de Metaculus:** este otoño dan **~100 $ al empezar** (y puede que nada: son
  selectivos). Dan más si el bot va por encima de la media en la MiniBench, y **el doble a los bots
  de código abierto**. Con 100 $ no llega para toda la temporada con ninguna opción buena: dependemos
  de ir bien para que recarguen.
- **Sin créditos:** lo pagas tú: la cifra de «~800 preguntas» más una pequeña comisión de OpenRouter.
- El registro del bot apunta el coste real de cada pregunta: tras la primera prueba cambio estas
  estimaciones por lo medido.

**Ya está aplicada la opción recomendada** (GPT-6 + Opus 5.5 + Gemini Flash). Además:
- Tu idea queda **lista con un solo ajuste**: `modo: "un_modelo"` en `config/params.yaml` hace que
  Opus 5.5 pronostique 3 veces. Si lo prefieres, dímelo y lo cambio.
- Si un modelo falla o contesta vacío, responde un **modelo de respaldo** (el anterior de la misma
  empresa), para no perder la pregunta.
- El registro apunta **lo que dijo cada modelo**, no solo el resultado final: así, con datos reales,
  podremos ver qué funciona mejor.
- Los «agentes» sí tienen sentido en una parte: **investigar** (comprobar los 2-3 datos clave antes
  de pronosticar). Eso está programado y probado, pero **apagado**: con ~100 $ de créditos, primero
  hay que medir cuánto cuesta. Lo que otros probaron y **no** funcionó: agentes que debaten entre sí
  o un «juez» que corrige al grupo.

## Lo que tienes que hacer tú (mejor antes del lunes 28/09)
El sistema no crea cuentas, no acepta condiciones ni toca claves: esto lo haces tú.
No hay prisa extrema: las 1-2 primeras semanas salen pocas preguntas y se puede entrar cuando sea
(cada pregunta perdida son 0 puntos, no negativos).

1. **Crear el bot en Metaculus:** entra con tu cuenta en https://www.metaculus.com/futureeval/participate/
   → «Create your first forecasting bot». Queda inscrito solo en el torneo.
2. **Rellenar el formulario de participación** (obligatorio para todos, 3 preguntas) y, en el mismo,
   **pedir los créditos de IA**: https://forms.gle/aQdYMq9Pisrf1v7d8 . Si decides repositorio público
   (decisión 2), dilo ahí: los bots de código abierto reciben el doble.
3. **Aceptar las condiciones del torneo** en la web y **verificar tu identidad** cuando te lo pida
   (es condición para cobrar). Confirma que participas como aficionado (los bots de empresas no cobran).
4. **Sacar el token** (token = contraseña para programas): en Metaculus, Ajustes → My Forecasting
   Bots → «Show Bot Token».
5. **Ponerlo como secreto de GitHub**: en https://github.com/javiergarciarecalde-es/metaculus-quant
   → **Settings** → **Secrets and variables** → **Actions** → pestaña **Secrets** → **New repository secret**:
   | Nombre (exacto, en mayúsculas) | Valor |
   |---|---|
   | `METACULUS_TOKEN` | el token del paso 4 |
   | `OPENROUTER_API_KEY` | la clave de los créditos (llega por correo) o una tuya |
   Nunca pegues estas claves en ningún fichero ni en un chat.
6. **Primera prueba, sin enviar nada:** pestaña **Actions** → «Pronosticar en el torneo» →
   **Run workflow** → modo `test_questions` → botón verde. Pronostica 3 preguntas de la zona de
   pruebas (no del torneo) y no envía. Debe acabar en verde con «Terminado: 3 pronósticos de ensayo».
   Si sale algo en amarillo o rojo, dímelo en la próxima sesión.
7. **Decidir lo de los minutos de GitHub** (decisión 2) **antes** del paso 8.
8. **Encender el envío real**: mismo sitio del paso 5, pestaña **Variables** → **New repository
   variable** → nombre `ENVIO_REAL`, valor `true`. Luego repite el paso 6: ahora sí envía, pero a la
   zona de pruebas; mira el perfil del bot en Metaculus. Desde ahí pronostica solo cada 20 minutos.
9. **Al final de la temporada:** rellenar la encuesta del bot (obligatoria para cobrar). Te lo recordaré.

Para **apagarlo**: borra la variable `ENVIO_REAL` (o ponla en `false`). No toques nunca un
pronóstico a mano ni relances el bot «porque no te gusta»: está prohibido.

## Decisiones pendientes del usuario
1. **Modelos:** puesto GPT-6 + Opus 5.5 + Gemini Flash (recomendado). ¿Te vale, o prefieres
   `un_modelo` (Opus 5.5 tres veces, ~0,47 $/pregunta en vez de ~0,34 $)? Mejor decidirlo antes
   del paso 8: cambiar a mitad de temporada mezcla resultados.
2. **Minutos de GitHub (repositorio público o privado).** Ahora es **privado**.
   | Opción | Coste | A favor | En contra |
   |---|---|---|---|
   | **A. Hacerlo público** (recomendada) | 0 € | minutos gratis e ilimitados; **créditos dobles** por código abierto; así están la plantilla oficial y nostreambot | cualquiera ve el código y los registros de cada ejecución (incluidos los pronósticos mientras la pregunta está abierta, ~1,5 h). Las claves nunca se ven |
   | B. Privado y cada 30 min | 0 € | nadie lo ve | no llega: ~2.000-4.000 min/mes contra 2.000 gratis; sin tarjeta **GitHub lo para** a mitad de mes y se pierden preguntas |
   | C. Privado con tarjeta en GitHub | ~6-27 $/mes (0,006 $/min por encima de 2.000) | nadie lo ve | pagas; pierdes el doble de créditos |
   Cómo se hace A (lo haces tú): repositorio → **Settings** → abajo del todo, **Danger Zone** →
   **Change visibility** → **Make public** → confirmar. Mientras el envío esté apagado no gasta nada.
3. **Reloj de GitHub poco fiable** (otro participante vio que solo lanzaba ~22 % de las veces):
   lo miramos tras la primera semana con los datos del registro.
4. **Opcional, noticias gratis (AskNews):** Metaculus tiene un acuerdo con AskNews (un servicio de
   noticias para bots). Para darte de alta hay que escribirles con tu nombre y LinkedIn; lo harías
   tú. No es necesario para empezar.

## Cuánto queda sin verificar (de frente)
- El bot **nunca ha hablado con Metaculus ni con una IA de verdad**: solo con simulaciones. El paso 6
  es la primera prueba real.
- El modo «búsqueda en internet» del modelo (`:online`) no se ha probado de verdad (hace falta clave).
- Los costes son estimaciones hasta la primera ejecución real.
- Si llegan créditos y cuánto: depende de Metaculus.

## Qué toca en la próxima sesión
- Tras la primera ejecución real: medir el coste de la «investigación ampliada» y decidir si se enciende.
- Aplicar lo que decidas en 1 y 2.
- Leer lo que salió del paso 6 y corregir lo que falle; cambiar costes estimados por medidos.
- Tras las primeras semanas: medir con el registro y la tabla de Metaculus cómo vamos frente a
  la puerta de la fase 0.
