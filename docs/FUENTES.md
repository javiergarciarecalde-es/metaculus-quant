# Fuentes

«verificado» = lo leímos nosotros directamente. «visto en web» = solo de segunda mano
(buscador, notas de otros). «no carga» = intentado y falló.

| Fuente | Estado | Notas |
|---|---|---|
| Anuncio FutureEval otoño 2026 (metaculus.com/notebooks/45615) | **verificado** 25/09/2026 (desde local; el 24/09 no cargaba desde la nube) | créditos ~100 $ iniciales y el doble para código abierto, formulario obligatorio, fechas, encuesta |
| Análisis primavera 2026 (metaculus.com/notebooks/45373) | **verificado** 25/09/2026 | tabla de modelos, tamaño de equipo, encuesta (Opus ~0, GPT-5.4 0,42) |
| Recursos para bots (metaculus.com/notebooks/38928) | **verificado** 25/09/2026 | créditos por OpenRouter; sufijo `:online` con búsqueda nativa cubierta |
| Página /futureeval/participate | visto en web | pasos: crear bot en Ajustes → My Forecasting Bots, «Show Bot Token» (textos de la web) |
| Plantilla oficial github.com/Metaculus/metac-bot-template (main.py, README, workflows) | verificado | por raw.githubusercontent.com, 24/09 y 25/09/2026 |
| Formulario de créditos https://forms.gle/aQdYMq9Pisrf1v7d8 | verificado (enlace en la plantilla y en el anuncio) | el formulario en sí no se abrió |
| nostreambot github.com/No-Stream/nostreambot-metaculus-bot | verificado | LICENSE MIT; llm_configs.py, FUTURE.md, docs/operations.md, docs/roster_history.md (25/09: ya usa gpt-6-sol + opus-5.5) |
| Blog del autor de nostreambot (nostream.substack.com, 2 entradas) | verificado (resumen automático) | «mejor varios modelos que un modelo varias veces»; 0,50-1 $/pregunta |
| Puntuación github.com/Metaculus/metaculus scoring/utils.py y score_math.py | verificado | take = max(puntuación,0)²; spot peer |
| forecasting-tools 0.3.1 (PyPI) | verificado | instalada y leída; FE_FALL_2026_ID = 33121; hace falta que salgan ≥ la mitad de las pasadas |
| Lista de modelos de OpenRouter (openrouter.ai/api/v1/models) | **verificado** 25/09/2026 | nombres y precios en vivo; gpt-4o-search-preview ya no existe |
| Facturación de GitHub Actions (docs.github.com) | verificado (resumen automático) | 2.000 min/mes en privados, públicos gratis, 0,006 $/min, se bloquea sin tarjeta |
| Normas citadas en github.com/Daatan/retro/issues/616 | visto en web | reglas de «sin humano», ventana ~1,5 h |
| Bots rivales de código abierto (joy-void-joy, alekthebear/castor, maradotwebp/5cast, geemus, Panshul42, edisonymy y ~15 más) y notebooks 43497/45336/45382 de Metaculus | verificado por agentes (25/09) | ver `docs/ESTUDIO_BOTS.md`; licencias anotadas allí |
