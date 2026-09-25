# Hallazgos (bitácora; solo crece)

## 24/09/2026 — Sesión 1
- Desde el entorno en la nube, metaculus.com no responde (tiempo agotado) y github.com da 403
  al navegar; raw.githubusercontent.com y PyPI sí cargan. Se leen las fuentes de GitHub por ahí.

## 24/09/2026 — Lectura de fuentes (tramo 2)

### Qué se pudo leer
- **metaculus.com está bloqueado** desde el entorno en la nube (y también los espejos: archive.org,
  foros). Lo del anuncio de otoño y el análisis de primavera es de segunda mano (buscador y
  notas de otros bots). Ver `FUENTES.md`.
- Sí se leyó directamente: la plantilla oficial, nostreambot, el código de puntuación de
  Metaculus y la librería forecasting-tools 0.3.1.

### Reglas y calendario (otoño 2026)
| Dato | Valor | Fiabilidad |
|---|---|---|
| Torneo | `fall-futureeval-2026`, id **33121** | verificado en la librería y en notas de nostreambot (leyeron la API el 06/09) |
| Fechas | abre 28/09/2026; últimos pronósticos 06/01/2027; cierre 05/03/2027 | notas de nostreambot |
| Tipo de puntuación | `spot_peer_tournament` («puntuación de pares puntual») | idem |
| Preguntas | 300-500 en la temporada; MiniBench ~60 por ronda cada 2 semanas | buscador |
| Premios | ~50.000 $ temporada + 1.000 $ por MiniBench | buscador / código de la web de Metaculus |
| Tiempo abierta cada pregunta | **~1,5 horas** (a veces 3 h) | notas de otro participante |
| Tipos | binaria (sí/no), numérica (incluida discreta), de opciones. Fechas/condicionales: no vistos en el torneo | segunda mano |
| Comentario obligatorio en cada pronóstico | sí (la librería ya lo publica) | segunda mano |
| Prohibido | humano en el bucle; **previsualizar pronósticos en preguntas del torneo**; repetir porque no gusta el resultado. Probar solo en preguntas cerradas o en la zona de pruebas | segunda mano |
| Créditos | formulario https://forms.gle/aQdYMq9Pisrf1v7d8 ; llegan como **clave de OpenRouter**, solo modelos OpenAI/Anthropic/Google; hay que pedirlos cada temporada | formulario verificado en la plantilla; resto, notas de nostreambot (a ellos les dieron 1.500 $) |
| «De forma selectiva» | no encontrado | — |

### Cómo se puntúa y reparte (código de Metaculus, verificado)
- Puntuación por pregunta (spot peer): `100 · N/(N-1) · ln(p / media geométrica de los demás)`;
  la mitad en numéricas. Cuenta **solo el pronóstico vigente en el momento de puntuar**
  (no hay promedio en el tiempo). Pregunta sin pronóstico = 0.
- Reparto: `parte = max(puntuación total, 0)²`; premio = parte / suma de partes. Puntuación
  negativa = 0 $. Quien quede bajo el mínimo (50 $) se elimina y se reparte de nuevo.
- Consecuencia: **no perderse preguntas** (están abiertas ~1,5 h) y **no dar nunca 0 %/100 %**
  (el logaritmo castiga sin límite). Al ser al cuadrado, ir en cabeza vale mucho más que ir medio.

### Plantilla oficial (metac-bot-template, verificada)
- Clase `ForecastBot` de forecasting-tools: investigación → N pasadas del modelo → mediana → envío.
- Por defecto 5 pasadas del mismo modelo, lector por modelo (cuesta llamadas), ejecución cada
  20 min en GitHub Actions (`cron: 7,27,47 * * * *`), salta preguntas ya pronosticadas.
- Con modelo puntero y mucho razonamiento quedó 18.º de 173 en primavera; con razonamiento
  normal, menos de la mitad de puntuación (segunda mano). Conclusión: **el modelo y el esfuerzo
  de razonamiento pesan más que el prompt**.

### nostreambot (github.com/No-Stream/nostreambot-metaculus-bot, verificado)
- Licencia **MIT** («Copyright (c) 2026 No-Stream»): se puede copiar citando. **No hemos copiado
  código**: solo ideas y parámetros.
- Resultados: 9.º en otoño 2025, ~10.º-11.º en primavera 2026, 15.º de 277 en verano 2026 (provisional).
- Coste: ~2,60 $ por pregunta (investigación muy pesada).
- Lo que hace y **tomamos**:
  - 3 modelos, uno de cada empresa (OpenAI, Anthropic, Google), una pasada cada uno, con
    razonamiento alto. Recortaron de 6 a 3 sin perder nada medible.
  - **Mediana** para agregar (probaron media, media geométrica de odds, juez: no mejoraron).
  - Límites binaria 2 %-98 %; opciones mínimo 1 % (subir a 5 % costó 3,5 puntos por pregunta).
  - Investigación compartida por todos los modelos (mejor que una por modelo).
- Lo que **descartamos** por ahora: **extremizar** (lo probaron junto a otras calibraciones y lo
  rechazaron: «la pendiente cambia de signo según la época»). Queda en config apagado (factor 1.0).
  Los mercados de predicción, lectura de las fuentes de resolución, curvas PCHIP para numéricas
  y búsquedas de huecos: mejoras grandes, para más adelante (ver «Pendiente»).
- Aviso operativo suyo: el reloj de GitHub Actions solo disparó ~22 % de las veces; ellos
  lanzan el flujo también desde cron-job.org. Con preguntas abiertas ~1,5 h esto importa.
- Su peor fallo: «los tres modelos de acuerdo sobre el mismo informe» (sesgo compartido).

### Decisiones técnicas tomadas (por la sesión, no por el usuario)
1. Base: plantilla oficial + forecasting-tools **0.3.1 fijada** (ya trae el id 33121).
2. 3 modelos de 3 empresas por OpenRouter (la clave de los créditos), mediana, límites 2-98 %,
   sin extremizar. Nombres de modelos tomados de nostreambot (sep. 2026): **sin verificar en vivo**.
3. Lectura de la respuesta con expresiones regulares (gratis) antes que con un modelo.
4. Ensayo SOLO en la zona de pruebas `bot-testing-area`, nunca en preguntas del torneo.
5. Con el envío apagado, las ejecuciones automáticas no hacen nada (no gastan créditos).

### Pendiente / mejoras medibles para después
- Comprobar nombres de modelos y el campo de «esfuerzo» en la primera ejecución de ensayo.
- Disparo externo (cron-job.org) si el reloj de GitHub falla: necesita un token de GitHub del
  usuario → decisión del usuario.
- Numéricas: más percentiles + interpolación suave (idea de nostreambot/Panshul42).
- Añadir precios de mercados de predicción (Polymarket, Manifold) a la investigación.

## 25/09/2026 — Sesión 2 (local, Windows)

### Entorno
- Pruebas: **22 de 22 en verde** en Windows (Python 3.12, entorno en `C:\t\mqv` por las rutas largas).
- Desde local **sí cargan** metaculus.com y la lista pública de modelos de OpenRouter. Se leyeron
  directamente el anuncio de otoño (notebook 45615), el análisis de primavera (45373) y la
  página de recursos (38928). Ver `FUENTES.md`.
- Gancho `post-commit` instalado (sube cada commit a GitHub, igual que cripto-quant y bolsa-quant).
  Vive en `.git/hooks/` (no se versiona); vale también para las sesiones en worktrees.
- La sesión en la nube de esta mañana no subió nada a GitHub (main seguía en 52c900f): la pregunta
  «3 modelos o un Opus» se contesta aquí desde cero.

### Fallo encontrado y arreglado
- `openai/gpt-4o-search-preview` (el modelo de búsqueda de noticias) **ya no existe** en OpenRouter.
  El bot no habría dado error rojo: habría pronosticado **sin noticias**, en silencio. Cambiado a
  `openai/gpt-5.6-sol:online` (búsqueda nativa de OpenAI, la que cubren los créditos según la página
  de recursos de Metaculus) con esfuerzo bajo. Añadido `python -m bot.modelos`: en cada ejecución
  comprueba contra la lista pública de OpenRouter que todos los modelos siguen existiendo y avisa.
- Los tres pronosticadores actuales existen: `gpt-5.6-sol`, `claude-opus-4.8`, `gemini-3.5-flash`.
  Pero ya hay sucesores: `openai/gpt-6-sol` y `anthropic/claude-opus-5.5` (publicados el 22/09/2026).
  nostreambot cambió a esos dos el 22/09 (su `docs/roster_history.md`), con esfuerzo `xhigh`.

### Reglas de otoño leídas en directo (antes eran de segunda mano)
| Dato | Valor |
|---|---|
| Formulario de participación | **obligatorio para todos** (3 preguntas); el mismo sirve para pedir créditos |
| Créditos | más selectivos que antes: **~100 $ iniciales**, más si la MiniBench va por encima de la media; **bots de código abierto: ~el doble** tras un periodo de evaluación. Puede que no den nada |
| Preguntas | temporada **300-400**; MiniBench ~60 cada 2 semanas (casi todas en los primeros días) |
| Fechas | MiniBench de calentamiento desde el 21/09; preguntas de otoño desde el **28/09** (las 1-2 primeras semanas, pocas); se puede entrar en cualquier momento (empieza con 0) |
| Encuesta del bot | obligatoria cada temporada para cobrar |
| Bots comerciales | sin premio salvo que abran el código (un aficionado solo no está afectado) |
| Google | límite compartido de 150 peticiones/min entre todos; Gemini 3.1 Pro mal configurado en los créditos |
| Zona de pruebas | `bot-testing-area` = id 32977 |

### ¿3 modelos de 3 empresas o un solo Opus 5.5 con varios «agentes»? (pregunta del usuario)
Lo medido por otros:
1. **Metaculus, primavera 2026** (65 bots propios con el mismo prompt): GPT-5.1-high 11,3 puntos/pregunta;
   Claude Sonnet 4.5-high 8,9; GPT-5.2-high 8,6 (diferencias dentro del ruido). Más razonamiento
   ganó 8 de 8 comparaciones.
2. **Encuesta a 58 creadores**: usar GPT-5.4 para el pronóstico final = la señal más fuerte
   (correlación 0,42); **usar Opus: correlación ~0**. Los 10 mejores que contestaron usaban todos un
   GPT-5.x en su conjunto. Nada es estadísticamente significativo (33 pruebas).
3. **Metaculus, tamaño de equipo**: juntar los 2-10 mejores bots (~-2) mejoró al mejor bot solo
   (-4,5) frente a los profesionales. Combinar pronosticadores buenos ayuda; añadir malos, no.
4. **nostreambot** (FUTURE.md, banco de agregación del 15/09/2026, n=262): la mediana gana a su miembro
   medio por **+6,3 [+4,7, +7,9]** (log-puntos por pregunta), por «consenso de posición». Pero
   «la diversidad de empresa con 3 miembros» da **delta nulo** en todos los tipos de pregunta.
   Bajaron de 6 modelos a 3 (uno por empresa) sin pérdida medible. Su autor (blog): mejor llamar a
   varios modelos que varias veces al mismo. Nadie ha medido «un modelo × 3» frente al trío.
5. **Opus 5.5 salió el 22/09/2026**: no tiene ningún historial de pronóstico medido.
6. Código (forecasting-tools 0.3.1): hace falta que funcionen al menos la mitad de las pasadas
   (2 de 3). Con 3 empresas, si una cae, se pronostica igual; con un solo Opus, si Anthropic cae (o
   se niega a contestar, como le pasó a nostreambot con fable-5), se pierde la pregunta.
Conclusión: lo medido es que **combinar 3 pronósticos** ayuda; no está medido que las 3 empresas
añadan algo por sí mismas. Pero quitar GPT es quitar el modelo con más evidencia a favor, y un solo
proveedor es un único punto de fallo. Recomendación: seguir con 3 empresas y meter Opus 5.5 en el
hueco de Anthropic (y GPT-6-sol en el de OpenAI). Pendiente del «sí» del usuario.

### Costes (precios en vivo de OpenRouter, 25/09/2026; $ por millón de tokens)
| Modelo | Entrada | Salida |
|---|---|---|
| openai/gpt-6-sol y gpt-5.6-sol | 2 | 10 |
| anthropic/claude-opus-5.5 | 4 | 20 |
| anthropic/claude-opus-4.8 | 5 | 25 |
| google/gemini-3.5-flash | 1,5 | 9 |
| búsqueda web nativa (`:online`) | 0,01 $ por búsqueda | — |

Estimación propia por pregunta (≈5.000 tokens de entrada; 6.000-8.000 de razonamiento+respuesta):
GPT ~0,09 $, Opus 5.5 ~0,14 $, Opus 4.8 ~0,18 $, Gemini Flash ~0,06 $, búsqueda ~0,05 $.
nostreambot midió 0,24-0,27 $ por modelo y pregunta con prompts mucho más largos: es nuestro techo.
El registro guarda `coste_usd` por pregunta: tras la primera ejecución real se cambia por lo medido.

### Minutos de GitHub (documentación de GitHub, leída hoy)
- Plan gratuito: 2.000 min/mes en privados; **públicos gratis**; exceso Linux **0,006 $/min**; sin
  tarjeta, se **bloquea** al agotarlos. Cada trabajo redondea al minuto.
- Con el envío encendido: 72 lanzamientos/día × ~1,5-3 min (instalar + mirar preguntas) ≈
  3.000-6.500 min/mes → privado con tarjeta ≈ 6-27 $/mes.
- Riesgo de hacerlo público: los registros de las ejecuciones (y el artefacto `registro/`) los
  puede ver cualquiera, con los pronósticos mientras la pregunta está abierta (~1,5 h). Mismo caso
  que nostreambot y la plantilla. Los secretos no se ven nunca.

## 25/09/2026 — Sesión en la nube: «3 modelos o un Opus con agentes» (estudio con agentes) y cambios
Se estudió con un equipo de 9 agentes (2 recogen pruebas, 3 diseñan, 3 critican, 1 juez). Coincide
con la sesión 2. Datos nuevos verificados en los documentos de nostreambot:
- Probabilidad extrema dada por **un solo** modelo sin que otro lo acompañe: acertó **4 de 9**;
  con otro modelo de acuerdo: **21 de 23** (performance_analysis.md). La pregunta q44874, publicada
  con un solo modelo (0,03), sacó −105 puntos. Desde entonces limitan a 5-95 % si publica uno solo.
- Probaron y **rechazaron** agentes que debaten, juez, combinador y que cada pronosticador investigue
  por su cuenta con agentes (FUTURE.md). Los agentes que SÍ usan están en la **investigación
  compartida** («búsqueda de huecos»: comprobar los 2-3 datos clave), porque sus peores fallos
  vienen de un dato erróneo que se creen todos los modelos (q44267, −95,66 puntos).
- Diseños evaluados (coste estimado por pregunta): Opus con 8-12 papeles ~1,65-3 $ (**descartado**:
  no cabe en los créditos, un solo proveedor, sin evidencia de mejora); híbrido completo ~1-2,4 $
  (descartado por calendario y coste); cambio mínimo + opciones configurables (**elegido**).

Cambios hechos (código probado con modelos simulados; 35 pruebas en verde):
1. Modelos por defecto: **gpt-6-sol + claude-opus-5.5 + gemini-3.5-flash** (la opción que
   recomiendan las dos sesiones). Cada puesto tiene un **respaldo** (el modelo anterior de la
   misma empresa) que responde si el principal falla o contesta vacío.
2. `pronostico.modo`: `tres_empresas` (por defecto) o `un_modelo` (3 pasadas de Opus 5.5, la idea
   del usuario). Se cambia con una línea de `config/params.yaml`.
3. El registro guarda **cada pronóstico individual** (modelo y valor), no solo la mediana: sin eso
   nunca se podrá medir qué modo va mejor.
4. `investigacion.modo: ampliada` (APAGADA): un director (Opus 5.5) elige hasta 2 datos clave y
   2 buscadores los comprueban a la vez; lo encontrado se AÑADE al final del informe, con tope de
   240 s; si algo falla, se sigue con el informe normal. Coste extra estimado: +0,05-0,35 $/pregunta.
5. El comprobador de modelos (`python -m bot.modelos`) revisa también respaldos, director y buscador.

## 25/09/2026 — Sesión 2 (cont.): la sesión de la nube y la local trabajaron a la vez
- La sesión de la nube subió 4 commits a `main` (05:24-05:26 UTC) mientras la local trabajaba;
  la local los integró sin conflictos (mezcla limpia, **35 de 35 pruebas en verde** en Windows).
  La nota «gpt-6-sol y claude-opus-5.5 NO comprobados» de `params.yaml` estaba desfasada: la
  sesión local los comprobó en vivo el 25/09. Corregida.

## 25/09/2026 — Respuesta del usuario: «Opus 5.5 ultracode con mi cuenta de Claude Max»
Qué dicen las fuentes oficiales (leídas hoy; «ultracode» = modo de Claude Code que reparte el
trabajo entre muchos agentes):
| Punto | Fuente oficial | Qué dice |
|---|---|---|
| ¿Se puede usar la suscripción en GitHub Actions? | code.claude.com/docs/en/github-actions | **Sí**: secreto `CLAUDE_CODE_OAUTH_TOKEN` (lo genera el usuario con `claude setup-token`); «runs use your Claude subscription instead of API billing». Vale también en ejecución programada |
| ¿De qué cupo tira? | support.claude.com, artículo 15036540 | `claude -p`, Agent SDK y **GitHub Actions gastan el mismo cupo de la suscripción** que claude.ai y Claude Code interactivo. Anthropic anunció un crédito aparte (100-200 $/mes en Max) para el 15/06/2026 y lo **pausó**: puede cambiar en cualquier momento |
| Límites de Max | support.claude.com, artículo 11049741 | límite por sesión de 5 h y **límite semanal** para todos los modelos; se reinicia a una hora fija por semana |
| Condiciones | code.claude.com/docs/en/legal-and-compliance | Max va con las Condiciones de consumidor. El inicio de sesión con suscripción es para el «uso ordinario» de Claude Code; «los límites anunciados de Pro y Max suponen un uso ordinario, individual». Lo prohibido expresamente es que terceros enruten peticiones de otros por credenciales de Max; el uso propio del titular no está prohibido expresamente. Anthropic se reserva actuar «sin previo aviso» |
| Coste de «ultracode» | code.claude.com/docs/en/workflows (vía agente) | «un flujo lanza muchos agentes, así que puede gastar bastante más» que hacerlo en una conversación |

Consecuencias para metaculus-quant:
- **Dinero:** 0 € extra si el usuario ya paga Max: elimina la dependencia de los ~100 $ de créditos.
- **Cupo compartido:** el bot competiría por el mismo cupo semanal que usan cripto-quant,
  bolsa-quant, mando-quant y estas sesiones. Las rondas de MiniBench sacan ~60 preguntas en pocos
  días: en esos picos el bot (o las sesiones del usuario) podría quedarse sin cupo. Pregunta sin
  pronóstico = 0 puntos.
- **Uso automático cada 20 min durante 3 meses** no es claramente «uso ordinario individual»: zona
  gris. Riesgo: que Anthropic limite la cuenta, que es la que usa el usuario para todo lo demás.
- **Evidencia de acierto:** no cambia: solo Opus = sin GPT (la señal más fuerte de la encuesta) y
  un solo proveedor. «Ultracode» con agentes que debaten o juzgan es justo lo que nostreambot probó
  y rechazó; donde los agentes sí ayudan es en la **investigación** compartida.
- Técnicamente factible: instalar Claude Code en el ejecutor de GitHub y llamarlo con `claude -p`
  desde el bot. No construido: espera la confirmación del usuario tras conocer estos riesgos.

## 25/09/2026 — GitHub público: el reloj se apaga tras 60 días sin actividad
- Documentación de GitHub (citada en la página oficial de Claude Code GitHub Actions): en
  repositorios públicos, **GitHub desactiva el reloj tras 60 días sin actividad** en el repositorio.
  La temporada dura hasta el 06/01/2027 (~100 días). Mientras haya sesiones con commits al menos
  una vez al mes no pasa; si no, hay que añadir un commit automático mensual. Anotado en «Pendiente».
- Al hacerlo público, el primer commit (creado desde la web de GitHub) deja ver el correo personal
  del usuario. No hay claves en ningún commit (revisado todo el historial).

### 25/09/2026 — Revisión con agentes del cambio anterior: 5 fallos confirmados, arreglados
| Fallo | Qué habría pasado | Arreglo |
|---|---|---|
| Turno de investigación compartido entre tandas (viene de la plantilla oficial) | la **MiniBench entera** (segunda tanda de cada ejecución) podía fallar con «bound to a different event loop» | un turno nuevo por tanda; prueba nueva |
| Modelos repartidos con una rueda común a todas las preguntas | sin clave de OpenRouter, si un modelo del proxy caía, se perdía 1 de cada 2 preguntas | la pasada n de cada pregunta usa el puesto n; respaldo también en el proxy |
| Modelo colgado: 2 intentos × 10 min, y después el respaldo | una sola pregunta podía pasar de los 40 min del flujo y **cortar la ejecución** | 1 intento si hay respaldo; tope de 15 min por pasada; búsqueda 3 min; no se empiezan preguntas tras 28 min |
| Registro solo al final de la tanda | si se cortaba, no quedaba nada apuntado | se apunta cada pregunta en cuanto termina |
| Subpreguntas de un grupo con la misma dirección web | el registro por modelo se mezclaba | clave = id de la pregunta |
Pruebas: **42 de 42 en verde**.

## 25/09/2026 — Sesión 2 (cont.): esquema mixto construido (investigación con Claude Max)
Decisión del usuario (DECISIONES 25/09): 3 empresas con créditos + investigación con agentes de
Opus 5.5 pagada con su Claude Max. Construido en `bot/claude_max.py`:
- `investigacion.modo: claude_max` (por defecto ya). Tras la búsqueda normal, el bot llama a
  Claude Code (`claude -p`, modelo `claude-opus-5-5`), que lanza hasta 3 investigadores en paralelo
  (fuente de resolución, últimas noticias, tasas base) con búsqueda web y lectura de páginas. Sus
  notas se **añaden** al final del informe con la cabecera «Investigación con agentes».
- Seguridad: no puede ejecutar órdenes ni tocar ficheros (`--disallowedTools Bash Edit Write`);
  corre en una carpeta vacía (no lee el CLAUDE.md del repositorio); no recibe las otras claves
  (token de Metaculus, OpenRouter); el texto va por la entrada estándar (no por la línea de órdenes).
- Topes: 300 s por pregunta, 30 turnos, 3 preguntas a la vez, freno de 3 $ equivalentes por pregunta
  (`--max-budget-usd`). Si el cupo de Max se agota, deja de llamar el resto de la ejecución.
- Sin el secreto `CLAUDE_CODE_OAUTH_TOKEN`, sin el programa, con error o sin tiempo: sigue con el
  informe normal (nunca bloquea un pronóstico). El flujo instala Claude Code solo si está el secreto.
- El registro guarda `claude_max_usd_equivalente` por pregunta (lo que costaría por API): así se mide
  cuánto cupo de Max gasta el bot.
- No se usa el modo «ultracode» (decenas de agentes): gastaría el cupo de Max muy deprisa. Si con
  los datos del registro sobra cupo, se puede subir `agentes`.
- Flujo de GitHub: límite de 60 min (antes 40) por la investigación extra; Node 22 para Claude Code.
- Arreglada una prueba de la nube que fallaba solo en Windows (el reloj avanza a saltos de ~15 ms y
  «más de 0 min» salía falso). **53 de 53 pruebas en verde** en Windows.

Sin verificar (hace falta el secreto real; se verá en el primer ensayo):
- Que `claude -p --output-format json` devuelva los campos `result`, `is_error` y `total_cost_usd`
  (así los usa el Agent SDK; si cambian, el bot sigue sin esta investigación y se ve en el registro).
- Que `--max-budget-usd` se aplique con suscripción, y el texto exacto del aviso de cupo agotado.
- Cuánto cupo semanal de Max gasta cada pregunta.
- **Sesiones a la vez:** hoy la sesión de la nube y la local han subido a `main` al mismo tiempo
  (3 veces hubo que juntar cambios). Funciona, pero conviene que trabaje una sola sesión cada vez.

## 25/09/2026 — Puesta en marcha hecha por el usuario con Claude Cowork (informe de Cowork)
Hecho por el usuario: bot creado en Metaculus (**Kyou-bot**); formulario de participación y créditos
enviado (aficionado, código abierto, se piden 270 $); repositorio **público**; secretos
`METACULUS_TOKEN` y `CLAUDE_CODE_OAUTH_TOKEN` puestos (comprobado con `gh secret list`). Falta
`OPENROUTER_API_KEY` (la clave de créditos aún no ha llegado; Metaculus avisa de que suele caer en spam).

Lo que Cowork leyó en Metaculus (anuncio 45615, recursos 38928, /tournament-rules) y matiza lo anterior:
| Punto | Qué dice |
|---|---|
| Aceptar condiciones | no hay botón: inscribirse o enviar pronósticos equivale a aceptarlas |
| Identidad | se pide al cobrar, no ahora. Pago por Ramp (comprobar que admite España/EUR), documentos de identidad y formulario W-8BEN; impuestos a cargo del ganador; pago ~1-2 meses tras resolverse |
| Token | el botón se llama «Copiar token de API» (no «Show Bot Token») |
| Créditos dobles por código abierto | llegan **tras un periodo de evaluación**, no desde el principio; «puede cambiar» |
| Comentarios | obligatorios, deben reflejar el razonamiento real y ser **notas privadas**; comentarios largos sin valor = spam (puede desactivar la cuenta); privados aceptados «dentro de límites razonables». Comprobado en forecasting-tools 0.3.1: `post_question_comment` publica con `is_private=True` por defecto; el texto es el de la plantilla (resumen + investigación + razonamientos, tope 150.000 caracteres) |
| Comentarios archivados | >30 días y >1.000 caracteres: el listado da 200 caracteres; texto completo con api/comments/[id]/ (8 llamadas / 10 s). No nos afecta: el bot no lee sus comentarios |
| Para cobrar | código o descripción (y cambios importantes), aceptar inspección (enseñar código, demostración, preguntas), encuesta |
| Un bot con premio por persona | los secundarios llevan «v2» y se vinculan en Ajustes |
Otras notas: `claude` no quedó en la lista de carpetas de Windows tras instalarlo (se usó la ruta
`%USERPROFILE%\.local\bin\claude.exe`); el formulario de créditos es «solo para humanos» y se declaró
que lo rellenó el usuario con ayuda de IA; Metaculus pide que las IAs no les escriban sin guía humana.
Pedido por el usuario: quitar su correo de Gmail del primer commit (repositorio ya público).

## 25/09/2026 — Primer ensayo real en GitHub Actions (ejecución 36118516529, sin envío)
- Lanzado con `gh workflow run` (modo test_questions, zona de pruebas). Secretos presentes:
  METACULUS_TOKEN y CLAUDE_CODE_OAUTH_TOKEN; sin OPENROUTER_API_KEY.
- Instalación bien: Claude Code 2.1.282 con Node 22; comprobador de modelos: todos existen.
- Sin clave de OpenRouter el bot usa el bloque `proxy_metaculus`: Metaculus contestó
  «You don't have an allowance for model <gpt-5>», «<claude-sonnet-4-5>» y «<gpt-4o-search-preview>»
  (sin cupo), y una vez «Cannot authenticate user» (página HTML) en la ruta de Anthropic.
  Resultado: **0 de 3 pronósticos**. Sin la clave de créditos el bot no puede pronosticar.
- La investigación con Claude Max no dio error (hubo ~2 min entre la búsqueda y los pronósticos),
  pero su texto no se registraba en ningún sitio y las preguntas fallaron: sin confirmar.
- **Fallo de diseño:** el flujo acabó en VERDE con 0 pronósticos. Arreglado: fallo total → rojo
  (`::error::`, código 1); fallo parcial → amarillo; aviso si falta OPENROUTER_API_KEY. Las preguntas
  que se dejan por falta de tiempo no cuentan como fallo. La investigación con Claude Max apunta
  en el registro de la ejecución su longitud, su coste equivalente y el principio del texto.
  **55 de 55 pruebas en verde.**

## 25/09/2026 — Historial reescrito para quitar el correo del usuario (decisión del usuario)
- Copia de seguridad previa: `C:/t/mq-respaldo-antes-de-reescribir.bundle` (todas las ramas; comprobada).
- `git filter-branch --env-filter` en un clon limpio: el autor del primer commit pasa de su Gmail a
  `327065986+javiergarciarecalde-es@users.noreply.github.com` (la dirección anónima de GitHub).
  Contenido idéntico (sin diferencias de ficheros); cambian los identificadores de los 23 commits.
- Subido con `--force-with-lease` a `main` y a `claude/elastic-maxwell-4718c9`: nuevo `main` = cf8c20e.
  Copias locales (principal y worktree) puestas al día; estaban limpias.
- **Límite:** GitHub sigue sirviendo el commit viejo 4bc7453 si se pide por su identificador exacto
  (comprobado con la API). Solo el soporte de GitHub puede purgarlo del todo (lo tendría que pedir el
  usuario). Las ejecuciones antiguas de Actions apuntan a commits viejos.
- **Aviso a la sesión de la nube:** su copia tiene el historial viejo. Antes de trabajar debe
  descargar de nuevo (`git fetch` + `git reset --hard origin/main` si no tiene cambios propios); si
  sube el historial viejo, el correo volvería.
