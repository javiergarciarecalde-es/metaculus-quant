# ESTADO (siempre «ahora»)

**Actualizado:** 24/09/2026 por la noche (sesión 1, sin usuario delante).
**Rama:** todo está en `main` (el push funcionó).

## Dónde estamos
El bot está **hecho y probado en ensayo**, pero **apagado**. No ha enviado nada a Metaculus
ni ha gastado un céntimo: no hay token ni claves puestas.

| Pieza | Estado |
|---|---|
| Protocolo y documentos (CLAUDE.md, este ESTADO, HALLAZGOS, DECISIONES, FUENTES) | hecho |
| Puerta de la fase 0 escrita en `config/params.yaml` | hecho (texto literal, no se toca) |
| Bot (`main.py` + carpeta `bot/`) | hecho, basado en la plantilla oficial de Metaculus |
| Pruebas automáticas (pytest = programa que comprueba el bot solo) | **20 de 20 en verde**, con Metaculus y modelos simulados |
| Flujo de GitHub Actions (el «reloj» que lanza el bot cada 20 min) | listo; **apagado** hasta que tú pongas los secretos y el interruptor |

## Qué hace el bot (en llano)
1. Cada 20 minutos mira si hay preguntas nuevas del torneo de otoño y de la MiniBench.
2. Para cada una busca noticias recientes con un modelo de IA que navega.
3. Pregunta a **3 modelos de IA de 3 empresas distintas** (OpenAI, Anthropic, Google), que
   razonan a fondo y dan su probabilidad.
4. Se queda con el **valor del medio** (mediana) de los tres. Nunca da menos de 2 % ni más de
   98 % (un 0 % equivocado hunde la puntuación sin remedio).
5. Envía el pronóstico con su explicación (obligatoria) y apunta todo en un registro.

Esto copia **lo que está medido** que funciona en el mejor bot abierto (nostreambot, ~10.º de 173
en primavera; licencia MIT, verificada; no se copió código, solo ideas). Lo que ellos probaron y
no funcionó (p. ej. «extremizar» = empujar las probabilidades hacia los extremos), está apagado.

**Honestamente:** esto es un bot «plantilla mejorada». La plantilla sola quedó 18.º de 173; con
esto aspiramos a parecido o algo mejor, **no hay garantía de pasar la puerta**. nostreambot hace
además cosas caras (mercados de apuestas, leer las fuentes oficiales) que quedan para después.

## Lo que tienes que hacer tú antes del lunes 28/09
Todo esto lo tienes que hacer tú: el sistema no crea cuentas, no acepta condiciones ni toca claves.

1. **Crear la cuenta de bot en Metaculus.** Entra en https://www.metaculus.com/futureeval/participate/
   con tu cuenta personal y sigue los pasos para crear el bot. Un solo bot con premio por persona.
2. **Verificar tu identidad** en Metaculus cuando te lo pida (es condición para cobrar).
3. **Aceptar las condiciones del torneo** de otoño 2026 (FutureEval) en esa misma web. Léelas:
   ahí pone lo de entregar el código o una descripción y aceptar inspección.
4. **Pedir los créditos de IA gratis** en este formulario: https://forms.gle/aQdYMq9Pisrf1v7d8 .
   Según otros participantes, te llega una **clave de OpenRouter** (OpenRouter = tienda de modelos
   de IA; la clave es como una tarjeta prepago que paga Metaculus). Hay que pedirlos cada temporada.
5. **Sacar el token de Metaculus** (token = contraseña para programas) en la página del paso 1.
6. **Ponerlo como secreto de GitHub**: en https://github.com/javiergarciarecalde-es/metaculus-quant
   → **Settings** → **Secrets and variables** → **Actions** → pestaña **Secrets** →
   **New repository secret**:
   | Nombre (exacto, en mayúsculas) | Valor |
   |---|---|
   | `METACULUS_TOKEN` | el token del paso 5 |
   | `OPENROUTER_API_KEY` | la clave de los créditos del paso 4 (o una tuya) |
   Nunca pegues estas claves en ningún fichero ni en un chat.
7. **Primera prueba, en ensayo (sin enviar nada):** pestaña **Actions** → «Pronosticar en el
   torneo» → **Run workflow** → modo `test_questions` → botón verde. Pronostica 3 preguntas de la
   **zona de pruebas** de Metaculus (no del torneo: las normas prohíben «previsualizar» preguntas
   del torneo) y no envía nada. Tarda unos minutos. Debe acabar en verde y decir
   «Terminado: 3 pronósticos de ensayo». Si sale un error de modelo (nombre de modelo no
   encontrado), dilo en la próxima sesión: los nombres de modelos no se pudieron comprobar esta noche.
8. **Encender el interruptor de envío real**: mismo sitio del paso 6, pero pestaña **Variables**
   → **New repository variable** → nombre `ENVIO_REAL`, valor `true`.
9. **Comprobar el envío de verdad**: repite el paso 7 (modo `test_questions`). Ahora sí envía, pero
   a la zona de pruebas. Mira el perfil de tu bot en Metaculus: deben aparecer los pronósticos.
   Desde ese momento, cada 20 minutos pronostica solo en el torneo y la MiniBench.
10. **Decidir lo de los minutos de GitHub** (ver «Decisiones pendientes», punto 1).

Para **apagarlo**: borra la variable `ENVIO_REAL` (o ponla en `false`). No toques nunca un
pronóstico a mano ni relances el bot «porque no te gusta»: está prohibido.

## Dinero: qué cuesta
No se apuesta nada. Los únicos costes posibles son la IA y los minutos de GitHub.

| Concepto | Con créditos de Metaculus | Sin créditos (pagas tú) |
|---|---|---|
| IA por pregunta (3 modelos + búsqueda) | 0 € | ~1 $ (estimado; nostreambot gasta 2,60 $ con más cosas; el informe dice ~1,40 $ los ganadores) |
| Preguntas hasta diciembre (temporada 300-500 + MiniBench ~60 × 6) | 0 € | ~660-860 preguntas → **~650-900 $** |
| Minutos de GitHub (repositorio privado) | ver decisión 1 | ver decisión 1 |

Si **no dan créditos**: no pongas ninguna clave de pago sin decidirlo antes. Opciones: (a) no
competir esta temporada; (b) pagar tu propia clave de OpenRouter con un tope de gasto; (c) bajar
a modelos más baratos (peor puesto esperado). Es decisión tuya.

## Decisiones pendientes del usuario
1. **Minutos de GitHub.** El repositorio es **privado**. GitHub da gratis ~2.000 minutos al mes en
   privados (plan gratuito). Lanzar el bot cada 20 minutos gasta como mínimo ~2.160 minutos al
   mes (cada lanzamiento cuenta como 1 minuto aunque no haya preguntas), más el tiempo pensando.
   Sin tarjeta, GitHub **no cobra: se para** a mitad de mes, y perderíamos preguntas.
   | Opción | Coste | Riesgo |
   |---|---|---|
   | A. Hacer el repositorio **público** (como la plantilla y nostreambot) | 0 € | tu código lo ve cualquiera (igualmente hay que enseñárselo a Metaculus) |
   | B. Lanzarlo cada 30 min en vez de 20 | 0 € | ~1.500-2.000 min/mes, justo; menos oportunidades (las preguntas están abiertas ~1,5 h) |
   | C. Añadir tarjeta a GitHub | ~0,008 $/min por encima del límite, pocos $ al mes | pagas algo |
   Recomendación: **A**. Mientras esté apagado no gasta nada (las ejecuciones se omiten).
2. **Reloj de GitHub poco fiable.** Otro participante vio que el reloj de GitHub solo lanzó el
   bot ~22 % de las veces y usa un servicio externo gratuito (cron-job.org) para lanzarlo. Eso
   exige crear un token de GitHub: lo tendrías que hacer tú. Proponemos mirarlo tras la primera
   semana, con datos (el registro dirá cuántas preguntas se perdieron).
3. **Si no dan créditos**: ver «Dinero».

## Cuánto quedó sin verificar (de frente)
- **La web de Metaculus estaba bloqueada** desde donde trabajo: no pude leer el anuncio de otoño,
  el análisis de primavera ni la página de participación. Las reglas y fechas vienen de segunda
  mano (buscador, notas de otros participantes) y del código de Metaculus, que sí leí. Léete tú
  las condiciones en el paso 3.
- Sin comprobar: que los créditos sean «selectivos», la encuesta obligatoria, los límites de uso.
- **Nombres de modelos** (`gpt-5.6-sol`, `claude-opus-4.8`, `gemini-3.5-flash`): sacados del código
  de nostreambot de septiembre; no pude ver la lista en vivo. Se confirma en el paso 7.
- El bot **nunca ha hablado con Metaculus ni con una IA de verdad**: solo con simulaciones.
- Cifras de coste: estimaciones.

## Qué toca en la próxima sesión
- Leer lo que salió del paso 7 y corregir nombres de modelos si hace falta.
- Tras las primeras semanas: medir con el registro y la tabla de Metaculus cómo vamos frente a
  la puerta de la fase 0.
- Mejoras con evidencia (ver HALLAZGOS, «Pendiente»).
