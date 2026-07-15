# Курсовая: анализ отзывов об обслуживании юр. лиц (banki.ru)

## Структура

```
banki-reviews-coursework/
├── coursework.ipynb     # основной артефакт: анализ от данных до интерпретации модели
├── scraper.py           # парсер banki.ru/services/responses/list/?type=business
├── requirements.txt
├── data/
│   ├── raw/             # parquet-батчи с сырыми отзывами (по 25 на страницу)
│   ├── processed.parquet  # кэш после очистки и лемматизации
│   └── progress.json    # чекпойнт для резюмируемого парсинга
└── scraper.log          # лог парсера
```

## Запуск

```bash
# создать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# (1) собрать отзывы (можно запускать многократно — продолжит с last_completed_page)
python scraper.py --max-pages 3000

# (2) выполнить анализ
.venv/bin/python -m ipykernel install --user --name banki-venv --display-name "Python 3 (banki venv)"
jupyter nbconvert --to notebook --execute coursework.ipynb \
    --output coursework.ipynb \
    --ExecutePreprocessor.kernel_name=banki-venv
# либо открыть в Jupyter Lab/VS Code и Run All
```

## Результаты (на 8472 размеченных отзывах)

- Целевая переменная: рейтинг 4–5 → удовлетворён (`y=1`), 1–2 → не удовлетворён (`y=0`), 3 исключён.
- Baseline LogReg на TF-IDF (1- и 2-граммы): **ROC-AUC ≈ 0.97**, accuracy 0.965 при majority-class baseline 0.913.
- Все три гипотезы подтверждены в топ-25 позитивных коэффициентах модели:
  - **Оперативность**: `быстро`, `быстрый`, `минута`, `оперативно`.
  - **Поддержка**: `помочь`, `помощь`, `объяснить`, `оператор`, `онлайн чат`.
  - **Персонализация**: `удобный` (а также пограничные `приятный`, `чётко`).
- Тематические маркеры (доля лемм из словаря темы) у довольных клиентов:
  - оперативность в 3.6× выше, поддержка в 2.2×, персонализация в 1.5×.
