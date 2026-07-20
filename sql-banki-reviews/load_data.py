"""
Загрузка отзывов из parquet в PostgreSQL (таблица reviews_raw).
Дальнейшая нормализация — в schema.sql.

Пароль читается из переменной окружения PG_PASSWORD, чтобы не хранить
его в коде:  export PG_PASSWORD="..."  (или задать в своём окружении).
"""

import os
import pandas as pd
from sqlalchemy import create_engine

PARQUET_PATH = "processed.parquet"      # путь к своему файлу
DB_NAME = "banki_reviews"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

password = os.environ.get("PG_PASSWORD")
if not password:
    raise SystemExit("Задай пароль: export PG_PASSWORD='...'")

df = pd.read_parquet(PARQUET_PATH)

# оставляем только нужные для SQL колонки (text_clean/text_lemm — для модели, не нужны здесь)
df = df[["review_id", "bank", "rating", "date", "title", "text", "y"]]

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

df.to_sql("reviews_raw", engine, if_exists="replace", index=False)
print(f"Загружено строк: {len(df)}")
