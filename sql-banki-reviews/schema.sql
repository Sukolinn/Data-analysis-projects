-- ============================================================
-- Схема и нормализация данных
-- Предполагается, что сырая таблица reviews_raw уже загружена
-- из parquet (см. load_data.py) и содержит колонки:
--   review_id, bank, rating, date, title, text, y
-- ============================================================

-- Справочник банков
create table banks (
    bank_id   serial primary key,
    bank_name text not null unique
);

-- Заполняем уникальными банками из сырой таблицы
insert into banks (bank_name)
select distinct bank
from reviews_raw
order by bank;

-- Основная таблица отзывов со ссылкой на банк по ключу
create table reviews (
    review_id   int primary key,
    bank_id     int references banks(bank_id),
    review_date timestamp,
    rating      int,
    y           int,          -- 0 = негатив, 1 = позитив
    title       text,
    text        text
);

-- Переносим данные из сырой таблицы, подставляя bank_id вместо названия
insert into reviews (review_id, bank_id, review_date, rating, y, title, text)
select
    r.review_id,
    b.bank_id,
    r.date,
    r.rating,
    r.y,
    r.title,
    r.text
from reviews_raw r
join banks b on r.bank = b.bank_name;

-- Проверки после загрузки:
--   select count(*) from banks;    -- ожидаем 71
--   select count(*) from reviews;  -- ожидаем 8472

-- Сырая таблица больше не нужна
drop table reviews_raw;
