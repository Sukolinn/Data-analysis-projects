# Онтология предметной области (ER-диаграмма)

Модель данных «Фабрики гипотез»: от фабрики и её хвостов до зон
неопределённости и гипотез. Соответствует типам в
`hypothesis_factory/models.py` и загрузчику `real_case_loader.py`.

```mermaid
erDiagram
    FACTORY ||--o{ OBSERVATION : "даёт наблюдения по хвостам"
    FACTORY ||--o{ EXPERT_HYPOTHESIS : "экспертный мозговой штурм"

    TAILINGS_TYPE ||--o{ OBSERVATION : "тип хвостов"
    ELEMENT ||--o{ OBSERVATION : "теряемый элемент (28/29)"
    SIZE_CLASS ||--o{ OBSERVATION : "класс крупности"
    MINERAL_FORM ||--o{ OBSERVATION : "минеральная форма (опц.)"

    OBSERVATION ||--|| EVIDENCE_CLAIM : "→ факт о потерях (TAIL-*)"
    EXPERT_HYPOTHESIS ||--|| EVIDENCE_CLAIM : "→ экспертное утверждение (EXP-*)"

    UNCERTAINTY_ZONE }o--o{ EVIDENCE_CLAIM : "supporting / conflicting"
    UNCERTAINTY_ZONE }o--o{ ENTITY : "linked_entities"
    EQUIPMENT ||--o{ UNCERTAINTY_ZONE : "узел схемы / оборудование"

    HYPOTHESIS ||--|| UNCERTAINTY_ZONE : "origin_uncertainty_zone"
    HYPOTHESIS }o--o{ EVIDENCE_CLAIM : "evidence"
    HYPOTHESIS ||--|| SCORES : "scores"

    ENTITY {
        string id
        string name
        string type "Factory|TailingsType|Element|ParticleSizeClass|MineralForm|Equipment|Process|KPI|..."
    }
    FACTORY {
        string name "КГМК | НОФ Вкр | НОФ мед | ТОФ"
    }
    TAILINGS_TYPE {
        string name "породные | пирротиновые | отвальные"
    }
    ELEMENT {
        string code "element_28 (Ni) | element_29 (Cu)"
    }
    SIZE_CLASS {
        string label "+125 | +71 | -125+71 | -71+45 | -45+20 | -20+10 | -10"
    }
    EQUIPMENT {
        string name "мельница | классификатор | гидроциклон | грохот | флотомашина ..."
    }
    OBSERVATION {
        string factory
        string tailings_type
        string element
        string particle_size_class
        float  loss_share_pct
        float  loss_mass_t
        bool   extractable
        string row_ref
    }
    EVIDENCE_CLAIM {
        string id "TAIL-* | EXP-*"
        string subject
        string relation
        string object
        string direction
        float  confidence
    }
    EXPERT_HYPOTHESIS {
        string factory
        string text
        int    index
        string source_file
    }
    UNCERTAINTY_ZONE {
        string id
        string type "coarse_locked_loss | fine_particle_loss | missing_process_link | contradiction | expert_unvalidated ..."
        string description
        float  kpi_relevance
        float  gap_severity
        float  priority
    }
    HYPOTHESIS {
        string id "HYP-*"
        string title
        string what_to_change
        string mechanism
        string minimal_experiment
        string success_criteria
    }
    SCORES {
        float value
        float novelty
        float feasibility
        float evidence
        float uncertainty_importance
        float risk
        float cost
        float final_score
    }
```

## Ключевые связи

- **Фабрика → наблюдения**: каждая из 4 фабрик даёт строки по хвостам; строка
  разворачивается в наблюдения по элементу 28 и 29 (всего 230).
- **Наблюдение → факт**: числовые потери превращаются в `EvidenceClaim`
  `TAIL-*` (94 шт.); экспертные идеи — в `EXP-*` (27 шт.).
- **Зона неопределённости** связывает сущности (фабрика, класс, элемент,
  оборудование) и опирается на факты; всего 28 зон 4 типов.
- **Гипотеза** порождается ровно из одной зоны (`origin_uncertainty_zone`),
  цитирует факты как evidence и несёт вектор оценок `SCORES`.
