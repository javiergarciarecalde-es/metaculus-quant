# Informe: qué copiar de otros bots, qué datos de tus proyectos sirven y si merece la pena un backtest

*25/09/2026. Para el dueño de metaculus-quant (el bot se llama Kyou-bot). Cuando digo «medido» significa que el autor lo comprobó con preguntas ya resueltas. «Creencia» significa que el autor piensa que ayuda, pero no lo comprobó.*

## Resumen en pocas líneas

- **Tu bot ya hace bien lo básico que hacen los mejores:** usa 3 empresas de IA distintas, toma la mediana (el valor del medio de los tres), no «exagera» los números y usa GPT con razonamiento alto. Al revisar varias ideas ajenas, resultó que la mayoría ya estaban en el bot. La «puerta 2 de 3» (no enviar si fallan dos de los tres modelos) y la «mediana de curvas» ya las hace la librería que usamos.
- **La mejora con más valor seguro no es de pronóstico, es de vigilancia.** Un día con el bot parado sin que nadie se entere cuesta unos 120 puntos (estimación mía), y dos bots rivales perdieron preguntas así. Se arregla gratis.
- **Solo una mejora de pronóstico tiene medición a favor, y es débil:** suavizar la curva de las preguntas numéricas (técnica PCHIP, explicada abajo). La propongo solo «en sombra»: se calcula y se guarda, pero no se envía hasta que nuestros propios datos la confirmen.
- **Tus otros proyectos no tienen datos que se puedan reutilizar tal cual.** Solo aportan direcciones públicas y gratuitas de internet (precios, tipos de interés), y nadie ha medido que ayuden a pronosticar. No compensa ahora.
- **Backtest** (probar el bot con preguntas del pasado): no merece la pena con preguntas antiguas. Saldría caro, haría trampa sin querer y ni siquiera podemos leer esas preguntas. Sí merece la pena, y es gratis, guardar desde ya todo lo necesario para comparar versiones más adelante con nuestras propias preguntas.

---

## 1) Mejoras recomendadas para nuestro bot

Ordenadas por prioridad. «Pregunta» es cada pregunta del torneo. «Punto» es un punto de la puntuación de pares («spot peer», nuestra nota frente a los demás bots en cada pregunta). Un bot de media tabla alta saca unos +12 a +17 por pregunta.

| # | Nombre | Qué hace (en llano) | De qué bot sale | Pruebas a favor | Coste por pregunta | Dificultad | Veredicto del escéptico |
|---|---|---|---|---|---|---|---|
| 1 | **Red de seguridad**: alarma de silencio + primero lo que cierra antes + sin Claude Max si quedan menos de 30 min + lista de preguntas perdidas | Una vez por hora, un programa aparte mira si hay preguntas abiertas en las que Kyou-bot no ha pronosticado. Si las hay, abre un aviso en GitHub y te llega un correo. Además, el bot atiende primero las preguntas que cierran antes. Si queda poco tiempo, se salta la investigación lenta de Claude Max. Y cada semana saca la lista de preguntas cerradas sin pronóstico nuestro, que valen 0 puntos | edisonymy (alarma; licencia MIT solo en versiones antiguas: copiamos la idea, no el código) y nostreambot (licencia MIT: se puede copiar con mención) | **El problema está medido; el remedio no.** edisonymy estuvo 1 día callado (01/08) y perdió 6 preguntas, unos 70-100 puntos. Otra vez pasó 2,5 h «en verde» sin pronosticar nada. nostreambot perdió 6-7 preguntas en verano por retrasos y cortes del reloj de GitHub | 0 $ | Baja-media: casi todo es configuración de GitHub y un programa pequeño | **Merece la pena.** Cuidado: la alarma de edisonymy falló en silencio dos veces antes de funcionar. Hay que probarla simulando fallos. El reloj desfasado (:07/:27/:47) ya lo tenemos |
| 2 | **Registro completo** (para poder comparar más adelante) + estado de la investigación | Guardar por cada pregunta: el informe de investigación entero (el normal y el de Claude Max por separado), el texto y las condiciones de la pregunta en ese momento, la fecha que se dio a los modelos, qué modelo contestó de verdad (el principal o el de reserva), y su razonamiento completo. Y además, si la investigación funcionó, falló, se quedó sin cupo o tardó demasiado | nostreambot (MIT) y joy-void (MIT) | joy-void lo **midió**: 5 pronósticos en los que la herramienta de búsqueda falló sin avisar sacaron de media **-40 puntos**, frente a **+11,6** de los otros 40 (muestra muy pequeña, n=5). Hoy nuestro bot, si la investigación falla, sigue adelante sin decirlo (bot/claude_max.py y bot/investigacion.py) | 0 $ | Baja | **Merece la pena.** Sin esto no se puede probar nada más adelante. Hoy los registros caducan a los 90 días y guardan el razonamiento recortado |
| 3 | **Curva numérica suavizada (PCHIP), solo «en sombra»** | En las preguntas de «¿qué valor tendrá X?» el bot entrega una curva de probabilidades. Hoy une los puntos que da cada modelo con líneas rectas, lo que deja escalones. PCHIP (un tipo de curva suave que nunca baja) los une con una curva sin escalones. La propuesta es calcularla y guardarla junto a lo que se envía, sin enviarla todavía | edisonymy (medición) y nostreambot (MIT, código de ejemplo) | **Medido, pero débil.** edisonymy rehízo sus preguntas numéricas ya resueltas y ganó **+2,39 puntos por pregunta** (rango probable +0,21 a +4,59, 97 preguntas). No estaba planificado de antemano, fue la mejor de 13 variantes probadas y en una de las tres tandas casi no ganó. Su bot era de un solo modelo y con curvas demasiado estrechas: para nosotros espero menos, quizá +0,5 a +2 | 0 $ | Baja-media | **Quizá.** Solo el cambio de curva, manteniendo lo demás igual. **No** pedir percentiles extremos (1 % y 99 %) a los modelos: nadie lo ha medido y puede adelgazar las colas justo donde están los desastres de unos -200 puntos. Activarla solo si nuestros datos lo confirman |
| 4 | **Instrucciones baratas a la investigación** | (a) Sacar automáticamente los enlaces que aparecen en las condiciones de resolución y dárselos a la búsqueda y a Claude Max con la orden «consulta estos primero». (b) Pedir que, si citan un precio de un mercado de apuestas (Polymarket, Kalshi…), pongan la fecha en que lo vieron y cuánto dinero mueve. (c) Tres reglas de lectura para los modelos: si el mercado mueve poco dinero, no copiar su precio; una escalera de tramos (por ejemplo «entre 100 y 110», «entre 110 y 120») se lee entera, como una distribución; y «RESUELTO» es un resultado, no un pronóstico | nostreambot (MIT); GreeneiBot2, el 1.º de primavera (solo la idea) | **Creencia.** Encuesta de Metaculus: «lee las fuentes» se asocia con +0,33 y «mira mercados» con +0,34 (correlaciones; ninguna aguanta la corrección estadística). El único caso documentado va en contra: nostreambot perdió -26,77 puntos por leer mal una escalera de Kalshi | ~0 $ | Baja (cambiar textos) | **Quizá.** Barato. **No** prohibir citar precios de mercado, que es lo que hace nostreambot: ellos tienen precios en vivo aparte y nosotros no, así que perderíamos la única señal de mercado que tenemos |
| 5 | **Claude Max: «verificar primero»** | Cambiar solo las instrucciones de los 3 ayudantes de Claude Max. Que comprueben en fuentes originales las 2-3 afirmaciones del informe de GPT en las que más se apoya el pronóstico, que citen la frase exacta que decide la pregunta y la fecha de cada cosa, y que avisen de lo que pasó antes de que la pregunta se abriera | nostreambot (MIT) | **Casi todo creencia.** Su «auditoría» dice que los peores fallos venían de datos viejos o inventados en el informe, pero sin cifras publicadas. Su medición (+7,18 puntos en 36 casos) mide al investigador solo, no al bot entero | 0 $ (gasta cupo de tu Claude Max) | Baja | **Quizá.** Sin la parte de «pronóstico fantasma»: Opus también es uno de los 3 que pronostican, y si su opinión se cuela en el informe, la mediana cuenta dos veces la misma voz. Nuestras instrucciones ya dicen «no pronostiques» a propósito |
| 6 | **Marcador ampliado** | Al informe semanal que ya existe (docs/MARCADOR.md) añadirle: nota por tipo de pregunta, si en las numéricas el resultado cayó dentro del rango del 50 % y del 90 %, y el porcentaje de investigaciones fallidas | geemus y joy-void (MIT) | Creencia (herramienta de trabajo, no de pronóstico) | 0 $ | Baja | **Quizá.** Útil para cazar fallos grandes. No sirve para afinar: con pocas preguntas, las diferencias pequeñas son ruido |
| 7 | **Reglas de razonamiento concretas** (solo 2) | (a) «Algo que pasó antes de publicarse la pregunta solo cuenta si las condiciones lo dicen expresamente». (b) «Un objetivo anunciado que nadie está obligado a cumplir no significa que se vaya a cumplir: mira cuántas veces se ha retrasado antes» | nostreambot (MIT), joy-void (MIT) | **El fallo está medido; la regla no.** En nostreambot las preguntas con ese patrón puntuaron 18,7 peor. Pero la única prueba real de reglas parecidas (edisonymy, 69 preguntas) dio **cero efecto**, y en las preguntas que quería arreglar salió algo peor | ~0,003 $ | Baja | **Quizá, baja prioridad.** Ganancia máxima realista: 0,2-0,5 puntos por pregunta, imposible de distinguir del ruido. Si se hace, que sea antes del 28/09 |

**Aviso sobre un error en los datos recibidos:** un informe decía que nuestro bot «mezcla mal» las curvas numéricas (percentil a percentil). No es así. Esa función (`agregar_percentiles`) no se usa. El envío real lo hace la librería forecasting-tools, que ya toma la mediana de las curvas completas, que es lo correcto según la medición de nostreambot (-7,4 puntos por pregunta si se hace de la otra forma).

### Descartadas y por qué

| Idea | Por qué no |
|---|---|
| «No enviar si fallan 2 de 3 modelos» + margen 5-95 % con un solo modelo | Lo primero **ya lo hacemos** (la librería lo exige y hay una prueba automática). Lo segundo nunca llegaría a usarse, porque con un solo modelo no enviamos. Además, su beneficio medido viene de **una sola pregunta** |
| Colas numéricas declaradas + ensanchar la curva (×1,15) | Arreglaba un fallo de la herramienta de edisonymy que la nuestra no tiene. La versión parecida a la nuestra da un resultado que puede ser cero (+3,14, rango −1,18 a +8,32). Ensanchar solo las colas fue claramente malo (hasta −240 puntos) |
| Pedir percentiles extremos 1/5/95/99 | Sin medir (7 frente a 5 percentiles: rango que incluye cero). Riesgo de colas demasiado finas |
| Revisor que aprueba o rechaza, juez, debate, ronda Delphi (los modelos corrigen tras leerse entre sí) | joy-void: cambió la probabilidad **0 veces** en 72 sesiones, con un coste de ~2,7 $ por pregunta. nostreambot lo rechazó con datos. geemus lo usa y quedó ~114.º |
| Varias pasadas por modelo | 3 veces el coste. edisonymy midió que no mejora (−0,0059, rango que incluye cero). No cabe en 100 $ |
| Exagerar los números o recalibrarlos después (Platt) | En la encuesta, exagerar va con peor resultado (−0,30). Platt empeoró en la prueba de edisonymy. nostreambot vio que el efecto cambia de signo de una temporada a otra |
| Buscador completo de mercados (Kalshi + Polymarket + Manifold con clasificador) | Unos 350 KB de código. **Nunca se ha medido** que acierte más. Solo 9 de 711 filas guardadas eran de verdad la misma pregunta. Se puede reconsiderar como «cuarto ayudante» de Claude Max si los registros muestran que aparecen mercados a menudo |
| Descargador completo de la fuente de resolución (navegador automático, archivo web) | Nadie lo ha medido. nostreambot necesitó ~150 KB de código y aún tiene errores abiertos. Si una lectura sale mal, engaña a los 3 modelos a la vez. Antes, probar la versión barata (mejora 4a) y mirar los registros |
| AskNews en dos fases | La propia auditoría de nostreambot: solo un 16 % de contenido que no traen otras búsquedas |
| Segunda búsqueda de ~0,75 $ por pregunta (gap-fill v1 de nostreambot) | Más que el doble de todo nuestro coste por pregunta |
| Dar más peso a GPT dentro de la mediana | Solo hay una correlación de encuesta (+0,42). No hay ninguna prueba |
| Dos bots en paralelo con cuentas distintas (5cast) | Las normas permiten un solo bot con premio por persona |
| Límites muy amplios (0,1-99,9 %) | Los propios datos de joy-void apoyan nuestro 2-98 % |
| Anotar en HALLAZGOS la lista de «no construir» tal como llegó | Tiene errores de etiqueta: la cifra del revisor no está en el fichero citado, «3 investigaciones» sí ayudó en numéricas y «research v2» no fue nulo. Si se anota, en la versión corregida de esta tabla y como «no se ha visto que ayude», no como «probado inútil» |

---

## 2) Datos de tus otros proyectos que podrían servir

Primero, la conclusión: **ninguno de tus proyectos guarda datos que el bot pueda usar tal cual.** Sus archivos están en tu PC o en repositorios privados que GitHub no puede leer, y el bot no debe depender de ellos ni tocarlos. Lo que sí aportan es una lista de **direcciones públicas y gratuitas** ya comprobadas, a las que el bot podría llamar por su cuenta. Nadie ha medido que ayuden a pronosticar mejor. Una pista en contra: el «ancla de series» de nostreambot (precios y datos macro automáticos) se activó en solo **5 de 322** preguntas y en **0 de las 30** más recientes.

| Fuente | Proyecto | Qué preguntas ayudaría | Esfuerzo | Pegas |
|---|---|---|---|---|
| FRED (datos económicos de la Reserva Federal de San Luis, sin clave) | bolsa-quant, _investigacion_ideas | Inflación, paro, empleo, tipos de interés, petróleo de EE. UU. | Bajo | Publica horas después que la fuente oficial y los datos se corrigen luego. Solo se ha comprobado una serie |
| Yahoo Finance (precios diarios, no oficial) | bolsa-quant | «¿Cerrará la acción, índice, oro o bitcoin por encima de X?» | Bajo | Puede bloquear los ordenadores de GitHub (sin comprobar). Las condiciones de uso no son claras. La pregunta puede resolverse con otra fuente |
| CBOE (índice del miedo VIX y S&P 500) | bolsa-quant | Preguntas sobre el VIX. Da la anchura razonable para preguntas del S&P 500 | Bajo | No tiene datos dentro del día |
| BCE (Banco Central Europeo) y Fed de Nueva York (tipos de interés a un día) | bolsa-quant, cripto-quant | Euro/dólar, decisiones del BCE, tipo de la Fed | Bajo | Pocas preguntas de este tipo. Dan el valor de hoy, no lo que espera el mercado |
| DefiLlama (precios de criptomonedas, sin clave) | cripto-quant | Precios de criptos para calcular cuánto suelen moverse | Bajo | Precio agregado, no el cierre de un mercado concreto. Binance y Bybit **no sirven**: bloquean los ordenadores de EE. UU., donde corre GitHub |
| API de Wikipedia | bolsa-quant, quiniela-quant | Preguntas que se resuelven «según Wikipedia» (cargos, resultados, listas) | Bajo-medio | Cualquiera puede editarla. El código de tus proyectos solo sirve para sus tablas concretas |
| The Odds API (cuotas de casas de apuestas) | quiniela-quant, betfair-quant | Deportes: quién gana un partido o una liga | Medio | **Habría que abrir una cuenta nueva (la abrirías tú)**. Nunca usar las claves de quiniela o betfair: les gastarías el cupo. Hay pocas preguntas de deporte |
| football-data.co.uk (histórico de fútbol) | quiniela-quant | Probabilidades de partida («base rates») en preguntas de fútbol | Bajo | Solo fútbol, y hay pocas preguntas |
| Kalshi, ForecastEx y Deribit (mercados y opciones) | solo en _investigacion_ideas | Fed, datos macro, bitcoin | Medio | Sin código hecho. Emparejar el mercado con la pregunta es lo difícil |
| Betfair.es, SELAE, EduardoLosilla, BetExplorer, cadenas de bloques | betfair-quant, quiniela-quant, cripto-quant | Ninguna | Alto | Descartados: bloqueo geográfico, credenciales personales o descarga de páginas sin permiso |

**Veredicto:** no compensa ahora. Lo sensato es esperar 2 semanas y contar en el registro cuántas preguntas son de precios o datos macro. Si son muchas (por ejemplo, más de 1 de cada 5), montar una «ficha de datos» pequeña con FRED + Yahoo + VIX, escrita de nuevo en nuestro repositorio, que añada al informe el último valor y cuánto suele moverse. Ojo: **el repositorio es público**, así que copiar código de tus proyectos privados lo publicaría.

---

## 3) Backtest (probar el bot con preguntas del pasado)

**¿Merece la pena?**

| Tipo | Veredicto | Motivo |
|---|---|---|
| Con preguntas antiguas de torneos | **No** | Metaculus no nos deja leer su resolución: solo vemos las preguntas en las que hemos pronosticado (comprobado: la web devuelve «solo para usuarios autenticados»). Además, la búsqueda en internet encontraría la respuesta: en un estudio, el 71-81 % de las preguntas se filtraban aunque se usara filtro de fechas. Y saldría por ~90 $, casi todo el crédito |
| Guardar ya todo lo necesario (mejora 2) y comparar gratis con lo registrado | **Sí, ya** | 0 $ |
| Repetir solo la parte de pronóstico con la investigación guardada | **Más adelante** (nov-dic), con 150-300 preguntas nuestras resueltas y con tu permiso para gastar | De pago |

**El diseño honesto, en 4 capas (de más barata a más cara):**

1. **Capa 0, ahora, 0 $.** Registro completo (mejora 2), guardado fuera de la caducidad de 90 días. Se escribe solo cuando la pregunta ya ha cerrado, para no publicar nada de preguntas abiertas.
2. **Capa 1, gratis, en cuanto se resuelvan preguntas.** Con los 3 pronósticos guardados de cada pregunta se puede calcular sin gastar qué habría pasado con otra forma de juntarlos: media en vez de mediana, sin Gemini, márgenes 1-99 %, y la curva PCHIP guardada «en sombra». Esto es posible porque cambiar solo nuestro número cambia la nota en una cantidad exacta y fácil de calcular (100 × logaritmo del cociente de probabilidades; la mitad en numéricas). Decidir de antemano como mucho 3 comparaciones, y adoptar un cambio solo si gana con 150 o más preguntas resueltas **y** en las dos mitades (octubre y noviembre).
3. **Capa 2, de pago y con tu permiso.** Repetir un solo modelo con la investigación guardada, y solo en preguntas abiertas después del corte de conocimiento de todos los modelos. Hoy eso es a partir de ~julio de 2026, porque Opus 5.5 sabe hasta junio. El «grupo de control» (la versión sin cambio) se ejecuta a la vez que la variante.
4. **Capa 3, solo hacia delante.** Los cambios en la investigación no se pueden repetir sin trampas. Se juzgan con un cambio anunciado en una fecha fija (por ejemplo, entre dos rondas de MiniBench) y solo se verán efectos grandes (5-10 puntos).

**Cuántas preguntas hacen falta para ver una mejora** (80 % de probabilidad de detectarla; fuente: dispersiones medidas por nostreambot):

| Tipo de comparación | Mejora de 2 puntos | Mejora de 3 | Mejora de 5 |
|---|--:|--:|--:|
| Mismas preguntas, cambio en el paso de pronóstico | ~280 | ~125 | ~45 |
| Mismas preguntas, cambio en la investigación | 780-1.225 | 350-545 | 125-196 |
| Preguntas distintas (antes y después) | ~4.800 | ~2.130 | ~770 |

Con unas 300-500 preguntas resueltas a principios de enero, se podrá ver como mucho una mejora de ~2 puntos en el paso de pronóstico, o de ~4-5 en investigación.

**Coste:**

| Opción | Coste (estimado) |
|---|---|
| Comparaciones con lo ya registrado | 0 $ |
| Repetir 1 modelo en 300 preguntas | 18-42 $ por versión (×2 con el control) |
| Repetir los 3 modelos en 300 preguntas, 2 versiones | ~175 $ (no hay dinero para esto) |
| Segunda versión completa del bot en paralelo sin enviar | ~100 $ (todo el crédito) |
| Probar variantes de Claude a través de tu Claude Max | 0 $, pero gasta tu cupo y solo compara Claude con Claude |

Recuerda: 800 preguntas × 0,34 $ son ~272 $, y hoy solo se esperan ~100 $ (has pedido 270 $). Cada dólar gastado en pruebas son ~3 pronósticos reales menos, y una pregunta sin pronóstico vale 0.

**Lo que NO hay que hacer:**
- Leer como real la nota de un backtest con búsqueda en directo sobre preguntas ya resueltas.
- Usar un modelo con preguntas resueltas antes de su corte de conocimiento.
- Llamar mejora a 1-3 puntos de diferencia comparando preguntas distintas.
- Probar 10 variantes y quedarse con la ganadora sin una mitad de datos reservada para confirmar.
- Retocar el bot mirando preguntas abiertas del torneo (lo prohíben las normas), o cambiar algo por una sola pregunta.
- Gastar crédito donado en pruebas sin tu decisión expresa.
- Copiar código de Metaculus/aib-analysis (no tiene licencia).

---

## 4) Plan de trabajo para las próximas 2 semanas

El torneo abre el **lunes 28/09**. La clave de créditos aún no ha llegado. Regla general: **todo lo que cambie qué pronostica el bot se hace antes del 28/09, o se deja para una fecha anunciada.** Así la temporada no queda partida en dos épocas que luego no se pueden comparar.

| Cuándo | Qué | Cambia los pronósticos | Coste |
|---|---|---|---|
| Vie 25 - dom 27/09 | Tramo A: registro completo + estado de la investigación (mejora 2) | No | 0 $ |
| Vie 25 - dom 27/09 | Tramo B: primero lo que cierra antes + sin Claude Max si quedan menos de 30 min + aviso si la investigación falla (mejora 1, parte b) | Apenas (solo el orden y el tiempo) | 0 $ |
| Vie 25 - dom 27/09 | Tramo C, opcional si da tiempo: instrucciones baratas (mejora 4) y «verificar primero» en Claude Max (mejora 5). Si no llega a tiempo, se deja para después de la 1.ª ronda de MiniBench, en fecha anunciada | Sí (se describe en DECISIONES) | ~0 $ |
| Semana del 28/09 | Tramo D: alarma de silencio con aviso por correo, probada con fallos simulados (mejora 1a) + lista semanal de preguntas perdidas (1c) | No | 0 $ |
| Semana del 28/09 | Tramo E: curva PCHIP **en sombra** (se calcula y se guarda, no se envía) con pruebas automáticas | No | 0 $ |
| Semana del 05/10 | Primera revisión de registros: cuántas preguntas llegaron, cuántas se perdieron, fallos de investigación, cupo de Max usado y qué parte son de precios o macro. Con eso se decide lo de la ficha de datos (sección 2) | No | 0 $ |
| Semana del 05/10 | Marcador ampliado (mejora 6) + preparar por escrito las 3 comparaciones de la Capa 1 | No | 0 $ |

**Lo que te toca a ti:**
1. Vigilar el correo por la clave de créditos y ponerla como secreto `OPENROUTER_API_KEY`.
2. Si no llega pronto, decidir entre esperar, pagar una clave tuya con tope de gasto, o no competir esta temporada.
3. Ojo: cada prueba sin envío **con** la clave también gasta créditos (unos 0,34 $ por pregunta), así que haremos pocas.
4. Opcional: pedir a Metaculus el «nivel de acceso para pruebas de bots» (unas 250 preguntas abiertas con la opinión media de la comunidad). Es un formulario que solo puedes rellenar tú, y solo sirve para comprobar que todo funciona, no para medir aciertos.

**Incertidumbre, de frente:** salvo la vigilancia (que evita perder preguntas enteras) y el registro (que permite medir), ninguna mejora de esta lista tiene pruebas sólidas de que suba la nota de un bot como el nuestro. Lo más probable es que cada una aporte menos de 1-2 puntos por pregunta, y este otoño no podremos distinguir mejoras tan pequeñas del ruido.

Repositorio consultado (solo lectura): `C:/Users/Administrador/Proyectos/metaculus-quant/.claude/worktrees/elastic-maxwell-4718c9` (docs/ESTADO.md, .github/workflows/run_bot_on_tournament.yaml).