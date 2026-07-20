-- ============================================================
-- SQL-анализ отзывов о банках (banki.ru)
-- Данные: 8 472 отзыва, 71 банк. Классы y: 0 = негатив, 1 = позитив.
--
-- Схема:
--   banks(bank_id, bank_name)
--   reviews(review_id, bank_id, review_date, rating, y, text, title)
--
-- Демонстрирует: агрегации, JOIN, подзапросы (в т.ч. коррелированные),
-- CTE (в т.ч. многоступенчатые), оконные функции.
-- ============================================================


-- ============================================================
-- БЛОК 1. АГРЕГАЦИИ
-- ============================================================

-- 1. Распределение классов тональности: количество и доля.
--    Ожидаемо ~1:10 (737 негативных / 7735 позитивных).
select
    y,
    count(*) as rev_cnt,
    count(*) * 1.0 / sum(count(*)) over () as share
from reviews
group by y;

-- 2. Топ-10 банков по числу отзывов (по bank_id; имена подтягиваются в блоке 2).
select
    bank_id,
    count(*) as rev_cnt
from reviews
group by bank_id
order by rev_cnt desc
limit 10;

-- 3. Средняя длина текста отзыва по классу тональности.
--    Гипотеза: негативные отзывы длиннее (люди подробнее описывают проблему).
select
    y,
    avg(length(text)) as avg_len_text
from reviews
group by y;

-- 4. Банки с долей негатива выше средней по всей выборке (подзапрос в HAVING).
select
    bank_id,
    avg(case when y = 0 then 1.0 else 0.0 end) as neg_share
from reviews
group by bank_id
having avg(case when y = 0 then 1.0 else 0.0 end) >
    (select avg(case when y = 0 then 1.0 else 0.0 end) from reviews);


-- ============================================================
-- БЛОК 2. JOIN И ПОДЗАПРОСЫ
-- ============================================================

-- 5. Топ-5 банков по доле негатива среди банков с >= 20 отзывами (JOIN + HAVING).
select
    b.bank_name,
    avg(case when r.y = 0 then 1.0 else 0.0 end) as neg_share
from reviews r
join banks b on r.bank_id = b.bank_id
group by b.bank_name
having count(*) >= 20
order by neg_share desc
limit 5;

-- 6. Расхождение оценки и тональности: высокий rating при негативе (и наоборот).
--    Порог симметричный (<=2 / >=4), чтобы не ловить нейтральные rating=3.
--    Кандидаты на сарказм или ошибки разметки.
select review_id, bank_id, rating, y, title
from reviews
where (rating >= 4 and y = 0)
   or (rating <= 2 and y = 1);

-- 7. Отзывы длиннее среднего по своему банку (коррелированный подзапрос).
select review_id, bank_id, rating, y, length(text) as text_len
from reviews r1
where length(text) >
    (select avg(length(text)) from reviews r2 where r1.bank_id = r2.bank_id);

-- 8. Матрица rating x тональность: сколько отзывов в каждой ячейке.
select
    rating,
    y,
    count(*) as cnt
from reviews
group by rating, y
order by rating, y;


-- ============================================================
-- БЛОК 3. CTE
-- ============================================================

-- 9. Банки с долей негатива выше 50% (одиночный CTE).
with neg AS (
    select
        bank_id,
        avg(case when y = 0 then 1.0 else 0.0 end) as neg_share
    from reviews
    group by bank_id
)
select bank_id, neg_share
from neg
where neg_share > 0.5
order by neg_share desc;

-- 10. Категоризация банков по доле негатива + подсчёт в каждой категории
--     (двухступенчатый CTE).
with neg as (
    select
        bank_id,
        avg(case when y = 0 then 1.0 else 0.0 end) as neg_share
    from reviews
    group by bank_id
),
categorized as (
    select
        bank_id,
        neg_share,
        case
            when neg_share > 0.5 then 'проблемный'
            when neg_share > 0.3 then 'средний'
            else 'хороший'
        end as category
    from neg
)
select
    category,
    count(*) as bank_cnt
from categorized
group by category
order by bank_cnt desc;

-- 11. Согласованность двух метрик удовлетворённости по банку:
--     средний rating vs доля позитива. Сравниваются РАНГИ (шкалы разные:
--     rating 1-5 и доля 0-1 напрямую несопоставимы).
--     Большой разрыв рангов = метрики "спорят" между собой.
with agg as (
    select
        bank_id,
        avg(rating) as avg_rating,
        avg(case when y = 1 then 1.0 else 0.0 end) as pos_share
    from reviews
    group by bank_id
),
ranked as (
    select
        bank_id,
        rank() over (order by avg_rating desc) as avg_rating_rank,
        rank() over (order by pos_share desc)  as pos_share_rank
    from agg
)
select
    bank_id,
    avg_rating_rank,
    pos_share_rank,
    abs(avg_rating_rank - pos_share_rank) as rank_gap
from ranked
order by rank_gap desc;


-- ============================================================
-- БЛОК 4. ОКОННЫЕ ФУНКЦИИ
-- ============================================================

-- 12. Ранжирование банков по доле негатива: RANK vs DENSE_RANK
--     (демонстрация разницы при совпадающих значениях).
with neg as (
    select
        bank_id,
        avg(case when y = 0 then 1.0 else 0.0 end) as neg_share
    from reviews
    group by bank_id
)
select
    bank_id,
    neg_share,
    rank()       over (order by neg_share desc) as rnk,
    dense_rank() over (order by neg_share desc) as dense_rnk
from neg
order by neg_share desc;

-- 13. Топ-3 самых длинных отзыва внутри каждого банка
--     (ROW_NUMBER + PARTITION BY).
with ranked as (
    select
        review_id,
        bank_id,
        length(text) as text_len,
        row_number() over (partition by bank_id order by length(text) desc) as rn
    from reviews
)
select review_id, bank_id, text_len
from ranked
where rn <= 3
order by bank_id, text_len desc;

-- 14. Отклонение rating отзыва от среднего rating его банка
--     (оконный AVG без схлопывания строк). Сортировка по модулю отклонения —
--     самые "нетипичные" для своего банка отзывы сверху.
with dev as (
    select
        review_id,
        bank_id,
        rating,
        rating - avg(rating) over (partition by bank_id) as rating_deviation
    from reviews
)
select review_id, bank_id, rating, rating_deviation
from dev
order by abs(rating_deviation) desc;

-- 15. Доля каждого банка в общем потоке отзывов + накопительный итог
--     (оконный SUM с рамкой ROWS UNBOUNDED PRECEDING).
select
    bank_id,
    count(*) as cnt,
    count(*) * 1.0 / sum(count(*)) over () as share,
    sum(count(*)) over (
        order by count(*) desc
        rows unbounded preceding
    ) as running_total
from reviews
group by bank_id
order by cnt desc;
