# Decisiones del usuario

Solo decisiones tomadas por el usuario, con fecha (hora de Madrid).

| Fecha | Decisión |
|---|---|
| 24/09/2026 22:35 | Aprobado el proyecto metaculus-quant y la orden nº 3 del mando (montar el bot, probarlo en ensayo, dejar GitHub Actions listo pero apagado). Puerta de la fase 0 fijada (ver `config/params.yaml`). |
| 25/09/2026 | **Repositorio público** (opción A de los minutos de GitHub: minutos gratis, créditos dobles por código abierto). El cambio de visibilidad lo hace el usuario en GitHub. |
| 25/09/2026 | **Modelos: esquema mixto.** Pronostican 3 modelos de 3 empresas (GPT-6 + Opus 5.5 + Gemini Flash) pagados con los créditos; la **investigación con agentes de Opus 5.5** se paga con la suscripción **Claude Max** del usuario (Claude Code en GitHub Actions). Elegido tras conocer los riesgos (cupo compartido con sus otros proyectos, «uso ordinario» de las condiciones de Max, sin GPT si fuese solo Opus). Primero había respondido «Opus 5.5 ultracode con mi cuenta de Claude Max». |
| 25/09/2026 | **Quitar su correo de Gmail del primer commit** reescribiendo el historial y sustituyéndolo a la fuerza en GitHub, tras conocer que el correo ya estuvo público y que GitHub puede guardar la versión vieja. |
| 25/09/2026 | **Adaptar ya el código a las reglas comunes** (Python 3.12, revisor ruff, parámetros sin valor por defecto) y añadir la tabla de límites de los documentos, antes del lunes 28/09 (orden 14 del mando), sin cambiar qué pronostica el bot. |
| 25/09/2026 | **No usar la cuenta de Google** (suscripción AI Pro ni sus créditos de Cloud) en el bot: no hay una vía viable clara. Se deja la investigación parada. |
| 25/09/2026 | **Mejoras A, B y C antes del 28/09** («vamos a hacer las tres»): registro completo, primero lo que cierra antes y sin Claude si cierra pronto, textos mejores para la investigación y los modelos. Y **comparar gratis con lo que guarda el bot las formas de juntar los 3 modelos** para ver cuál es mejor. |
| 27/09/2026 ~20:20 | **Encender el envío real** (`ENVIO_REAL` = `true`), tras la prueba sin envío en verde y con el tope de gasto de los 100 $ puesto (orden 26 del mando). |
| 27/09/2026 ~20:25 | **Investigación con Claude en una de cada dos preguntas** (las de número par), en vez de en todas: gasta la mitad de su plan y sirve para medir si ayuda. Lo pidió al saber que la mejora es una suposición sin datos. |
| 27/09/2026 ~21:25 | **Pausar la investigación con Claude hasta el 28/09 a las 11:00** (cuando se renueva su tope semanal, que estaba al 92 %), para que la apertura de la temporada no deje sin Claude a sus otros proyectos. Vuelve sola a «una de cada dos». |
| 27/09/2026 ~21:55 | **Hacer ya, antes de que abra la temporada y en la nube, tres mejoras:** (1) vigilancia que **no le avise a él**: si el bot se calla o falla, que un proceso automático lo relance solo, y si no basta, que despierte a Claude para que reaccione; (2) medir en qué se va el dinero para estirar los 100 $ (el cambio de modelos, si lo hay, se decide después con datos); (3) curva numérica suave «en sombra» (se guarda, no se envía). |
