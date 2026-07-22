# Сквозной pipeline «Фабрики гипотез» (BPMN)

Диаграмма описывает 11 шагов реального (real-case) конвейера
`hypothesis_factory.pipeline._run_real_case_pipeline`. В скобках указаны
функция/модуль и объём артефакта на дефолтном KPI (снижение потерь
элемента 28 / элемента 29).

```mermaid
flowchart TD
    subgraph IN[" Вход "]
        D1[("JSON-сводка 4 отчётов<br/>nornickel_real_case_data_summary.json")]
        D2[("Экспертные гипотезы<br/>Гипотезы *.docx — таблицы")]
    end

    S1["1. Приём данных<br/><i>load_real_case_data()</i><br/>→ 230 наблюдений + 27 эксп. гипотез"]
    S2["2. Сборка документов<br/><i>build_real_case_documents()</i><br/>→ 5 SourceDocument"]
    S3["3. Чанкинг<br/><i>chunk_documents()</i>"]
    S4["4. Извлечение фактов / claims<br/><i>build_real_case_claims()</i><br/>→ 94 факта о потерях + 27 эксп."]
    S5["5. Извлечение сущностей<br/><i>extract_entities()</i><br/>→ 133 сущности"]
    S6["6. Матрица изученности<br/><i>build_tailings_coverage_matrix()</i>"]
    S7["7. Граф знаний<br/><i>build_knowledge_graph()</i>"]
    S8["8. Поиск зон неопределённости<br/><i>find_tailings_uncertainty_zones()</i><br/>→ 28 зон"]
    S9["9. Генерация гипотез<br/><i>generate_hypotheses()</i><br/>→ top-8 зон по приоритету"]
    S10["10. Скоринг и ранжирование<br/><i>scorer.final_score()</i> + сортировка<br/>→ 8 ранжированных гипотез"]
    S11["11. Экспорт<br/><i>export_json / report_docx</i><br/>→ JSON · CSV · DOCX"]

    D1 --> S1
    D2 --> S1
    S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9 --> S10 --> S11

    S8 -. "зоны типов: coarse_locked_loss(8),<br/>missing_process_link(6),<br/>contradiction(6), expert_unvalidated(8)" .- S9
    S4 -. "evidence для гипотез" .- S9

    subgraph OUT[" Выход "]
        R1[["Ранжированный список гипотез<br/>с планом мин. эксперимента"]]
    end
    S11 --> R1
```

## Пояснения к шагам

| # | Шаг | Модуль | Что делает |
|---|-----|--------|-----------|
| 1 | Приём данных | `data_loaders/real_case_loader.py`, `hypotheses_docx_parser.py` | Читает JSON-сводку хвостов (4 фабрики) и парсит экспертные гипотезы из таблиц `.docx`. |
| 2 | Сборка документов | `real_case_loader.build_real_case_documents` | Собирает 5 текстовых документов (база знаний + по фабрике + экспертный). |
| 3 | Чанкинг | `ingestion/chunking.py` | Режет документы на чанки для последующего анализа/поиска. |
| 4 | Факты / claims | `real_case_loader.build_real_case_claims` | 94 факта о потерях по классам + 27 экспертных утверждений → `EvidenceClaim`. |
| 5 | Сущности | `extraction/entity_extractor.py` | Правиловое извлечение сущностей (фабрика, класс, элемент, оборудование…). |
| 6 | Матрица изученности | `analysis/tailings_analyzer.build_tailings_coverage_matrix` | Покрытие «фабрика×тип×элемент×класс», статус (well/weakly/uncovered). |
| 7 | Граф знаний | `graph/graph_builder.py` | Строит граф из claims для связей и косвенных путей. |
| 8 | Зоны неопределённости | `analysis/tailings_analyzer.find_tailings_uncertainty_zones` | Формирует и приоритизирует 28 зон 4 типов. Приоритет = `0.5·kpi + 0.35·gap + 0.15·max(contradiction,indirect)`. |
| 9 | Генерация гипотез | `generation/hypothesis_generator.py` | Из top-8 зон строит проверяемые гипотезы (что менять, механизм, мин. эксперимент). |
| 10 | Скоринг / ранжирование | `scoring/scorer.py`, `scoring/profiles.py` | Взвешенная оценка value/novelty/feasibility/evidence/uncertainty − risk − cost, сортировка. |
| 11 | Экспорт | `export/export_json.py`, `export/report_docx.py` | Выгрузка результата в JSON / CSV / DOCX. |

> Генерация детерминированная, без LLM (`generation/llm_client.py` — заглушка-хук).
