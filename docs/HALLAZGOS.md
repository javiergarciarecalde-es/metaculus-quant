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
