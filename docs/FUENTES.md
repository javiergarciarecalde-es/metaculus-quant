# Fuentes

«verificado» = lo leímos nosotros directamente. «visto en web» = solo de segunda mano
(buscador, notas de otros). «no carga» = intentado y falló.

| Fuente | Estado | Notas |
|---|---|---|
| Anuncio FutureEval otoño 2026 (metaculus.com/notebooks/45615) | **verificado** 25/09 y releído 27/09/2026 (desde local) | créditos ~100 $ iniciales y el doble para código abierto, formulario obligatorio, fechas, encuesta. Torneos para bots: temporada FutureEval (300-400 preguntas), MiniBench (~60 cada 2 semanas), Market Pulse Q4 y Metaculus Cup (sin premio). **Los créditos son solo para MiniBench y FutureEval**, que son los dos del bot |
| Correo de créditos de Metaculus (27/09/2026, 15:55) | visto por el usuario y el mando (no lo leímos nosotros) | 100 $ para FutureEval y MiniBench (se pidieron 270 $); sube sola si la MiniBench va por encima de la media, hasta ~775 $; extra por código abierto tras una primera ventana; «experimental» |
| OpenRouter «API Key Status»: `GET https://openrouter.ai/api/v1/key` (openrouter.ai/docs/api-reference/limits) | **verificado en su documentación** 27/09/2026 | devuelve `data` con `usage`, `usage_daily`, `limit`, `limit_remaining` (null = sin límite), `label` (no se guarda nunca). Gratis. El bot lo usa para el tope de gasto (`bot/presupuesto.py`) |
| Análisis primavera 2026 (metaculus.com/notebooks/45373) | **verificado** 25/09/2026 | tabla de modelos, tamaño de equipo, encuesta (Opus ~0, GPT-5.4 0,42) |
| Recursos para bots (metaculus.com/notebooks/38928) | **verificado** 25/09/2026; **normas releídas** 28/09/2026 desde local (página actualizada el 26/09/2026) | créditos por OpenRouter; sufijo `:online` con búsqueda nativa cubierta. **Normas:** se puede actualizar el bot («We encourage updates»); prohibido previsualizar cómo pronostica preguntas abiertas o próximas y ajustarlo según eso, y relanzarlo sobre una pregunta porque no guste; «only submit one forecast per question»; probar en preguntas de fuera del torneo, en las ya cerradas o en la zona de pruebas; un humano puede lanzar el bot a mano, pero el bot pronostica y comenta por la API; comentarios privados (Metaculus los hace públicos al cerrar); para cobrar, descripción del bot «con las actualizaciones importantes» e inspección. Nada dice de repositorios ni registros públicos |
| Página /futureeval/participate | visto en web | pasos: crear bot en Ajustes → My Forecasting Bots, «Show Bot Token» (textos de la web) |
| Plantilla oficial github.com/Metaculus/metac-bot-template (main.py, README, workflows) | verificado | por raw.githubusercontent.com, 24/09 y 25/09/2026 |
| Formulario de créditos https://forms.gle/aQdYMq9Pisrf1v7d8 | verificado (enlace en la plantilla y en el anuncio) | el formulario en sí no se abrió |
| nostreambot github.com/No-Stream/nostreambot-metaculus-bot | verificado | LICENSE MIT; llm_configs.py, FUTURE.md, docs/operations.md, docs/roster_history.md (25/09: ya usa gpt-6-sol + opus-5.5) |
| Blog del autor de nostreambot (nostream.substack.com, 2 entradas) | verificado (resumen automático) | «mejor varios modelos que un modelo varias veces»; 0,50-1 $/pregunta |
| Puntuación github.com/Metaculus/metaculus scoring/utils.py y score_math.py | verificado | take = max(puntuación,0)²; spot peer |
| forecasting-tools 0.3.1 (PyPI) | verificado | instalada y leída; FE_FALL_2026_ID = 33121 (fall-futureeval-2026) y CURRENT_MINIBENCH_ID = "minibench" (releído 27/09/2026: son los dos torneos de los créditos); hace falta que salgan ≥ la mitad de las pasadas; `MonetaryCostManager` = freno de gasto por pregunta (no mide la búsqueda `:online`) |
| Lista de modelos de OpenRouter (openrouter.ai/api/v1/models) | **verificado** 25/09/2026 | nombres y precios en vivo; gpt-4o-search-preview ya no existe |
| Facturación de GitHub Actions (docs.github.com) | verificado (resumen automático) | 2.000 min/mes en privados, públicos gratis, 0,006 $/min, se bloquea sin tarjeta |
| Normas citadas en github.com/Daatan/retro/issues/616 | visto en web | reglas de «sin humano», ventana ~1,5 h |
| Bots rivales de código abierto (joy-void-joy, alekthebear/castor, maradotwebp/5cast, geemus, Panshul42, edisonymy y ~15 más) y notebooks 43497/45336/45382 de Metaculus | verificado por agentes (25/09) | ver `docs/ESTUDIO_BOTS.md`; licencias anotadas allí |
