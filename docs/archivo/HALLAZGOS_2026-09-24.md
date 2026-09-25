# Hallazgos archivados (24/09/2026)

Movido de docs/HALLAZGOS.md el 25/09/2026 al pasar de ~400 líneas (CLAUDE.md, límites de tamaño). Texto sin cambios.

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

