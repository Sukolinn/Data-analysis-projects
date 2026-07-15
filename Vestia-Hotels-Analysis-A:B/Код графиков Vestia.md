# Графики — Vestia Hospitality Group
## Код для воспроизведения и редактирования на Mac

---

## Установка зависимостей

```bash
pip install matplotlib pandas numpy scipy
```

---

## Блок настройки — запускать перед каждым графиком

```python
import matplotlib
matplotlib.use('Agg')          # убери эту строку если хочешь видеть график в окне, а не только сохранять
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy import stats
import os

# ── ПУТИ ─────────────────────────────────────────────────────────────────────
DATA_PATH   = "hotel_bookings.csv"   # полный путь к CSV, если файл не в той же папке
OUTPUT_DIR  = "."                    # папка для сохранения PNG

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── ПАЛИТРА ВШЭ + HIGH FINANCE ────────────────────────────────────────────────
HSE_NAVY   = '#0F2D69'   # тёмно-синий ВШЭ — основной
HSE_BLUE   = '#374B9B'   # синий ВШЭ — вторичный
BLUE_LIGHT = '#C9D6E5'   # светло-голубой — фоны, нейтральные бары
COPPER     = '#B87333'   # медь — второй акцент (Algarve, Test-группа)
GRAY_HSE   = '#939598'   # серый ВШЭ — нейтральный, исторические данные
TEAL       = '#1A7A60'   # тёмно-зелёный — положительный эффект
LGRID      = '#E6E7E8'   # очень светлый — линии сетки
TEXT       = '#0F172A'   # почти-чёрный — основной текст
SUBTLE     = '#6B7280'   # серый — подписи, сноски

plt.rcParams.update({
    'font.family'       : 'sans-serif',
    'font.sans-serif'   : ['Arial', 'Helvetica Neue', 'DejaVu Sans'],
    'font.size'         : 9,
    'figure.facecolor'  : 'white',
    'axes.facecolor'    : 'white',
    'text.color'        : TEXT,
    'xtick.color'       : SUBTLE,
    'ytick.color'       : SUBTLE,
    'xtick.major.size'  : 0,
    'ytick.major.size'  : 0,
    'axes.spines.top'   : False,
    'axes.spines.right' : False,
    'axes.spines.left'  : False,
    'axes.spines.bottom': False,
    'axes.unicode_minus': False,
})

# ── ЗАГРУЗКА ДАННЫХ ───────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)

month_map = {
    'January':1, 'February':2, 'March':3,    'April':4,
    'May':5,     'June':6,     'July':7,      'August':8,
    'September':9,'October':10,'November':11,'December':12
}
df['arrival_month_num'] = df['arrival_date_month'].map(month_map)
df['arrival_date'] = pd.to_datetime(dict(
    year  = df['arrival_date_year'],
    month = df['arrival_month_num'],
    day   = df['arrival_date_day_of_month']
))
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['revenue']      = df['adr'] * df['total_nights']

print("Данные загружены:", df.shape)
```

---

---

# График 1 — Ежемесячная выручка

**Что показывает:** выручку группы по месяцам с июля 2015 по август 2017.
Только реализованные бронирования (is_canceled == 0, total_nights > 0, adr > 0).

**Зачем нужен:** устанавливает контекст — бизнес растёт, есть чёткая сезонность
(пики в июле–августе). Три оттенка синего показывают год к году.

**Что можно менять:** подписи на пиках (конкретные месяцы), диапазон дат,
цвета годов.

```python
# ── ДАННЫЕ ───────────────────────────────────────────────────────────────────
monthly = (
    df[(df['is_canceled']==0) & (df['total_nights']>0) & (df['adr']>0)]
    .groupby(['arrival_date_year','arrival_month_num'])['revenue']
    .sum()
    .reset_index()
    .sort_values(['arrival_date_year','arrival_month_num'])
)

month_ru = {1:'янв',2:'фев',3:'мар',4:'апр',5:'май',6:'июн',
            7:'июл',8:'авг',9:'сен',10:'окт',11:'ноя',12:'дек'}

labels = [f"{month_ru[int(r['arrival_month_num'])]}"
          for _, r in monthly.iterrows()]

rev     = (monthly['revenue'] / 1000).tolist()   # в тыс. €
years   = monthly['arrival_date_year'].tolist()
colors  = ['#ADCDE8' if y==2015 else '#4D90C0' if y==2016 else HSE_NAVY
           for y in years]
x       = list(range(len(rev)))

# ── ГРАФИК ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 4.2))
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_axisbelow(True)
ax.yaxis.grid(True, color=LGRID, linewidth=0.7, zorder=0)
ax.tick_params(length=0, labelsize=8)

ax.bar(x, rev, color=colors, width=0.72, zorder=3)

# Разделители лет
for xv in [5.5, 17.5]:
    ax.axvline(xv, color='#DDDDDD', lw=0.8, ls=':', zorder=2)
for mid, yr in [(2.5,'2015'), (11.5,'2016'), (22.0,'2017')]:
    ax.text(mid, max(rev)*1.085, yr, ha='center', fontsize=8,
            color=SUBTLE, fontstyle='italic')

# X-тики каждые 3 месяца
sel = list(range(0, len(x), 3))
ax.set_xticks(sel)
ax.set_xticklabels([labels[i] for i in sel], fontsize=7.5)
ax.set_xlim(-0.6, len(x)-0.4)
ax.set_ylim(0, max(rev)*1.13)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda v,_: f'€{int(v):,}'.replace(',','\u202f')+'тыс.'))

# Пики августов
for xi, yi in [(1,rev[1]), (13,rev[13]), (25,rev[25])]:
    ax.annotate(f'€{yi:.0f}тыс.', xy=(xi,yi), xytext=(xi,yi+40),
                ha='center', va='bottom', fontsize=7, color=HSE_NAVY,
                fontweight='bold',
                arrowprops=dict(arrowstyle='-', color='#AAAAAA', lw=0.6))

# Легенда
patches = [mpatches.Patch(fc='#ADCDE8', label='2015'),
           mpatches.Patch(fc='#4D90C0', label='2016'),
           mpatches.Patch(fc=HSE_NAVY,  label='2017')]
ax.legend(handles=patches, frameon=False, fontsize=8, ncol=3,
          loc='lower center', bbox_to_anchor=(0.5, -0.20),
          handlelength=1.1, handleheight=0.9)

ax.text(0.995, -0.20,
        'Учтены только реализованные бронирования  ·  Источник: внутренние данные Vestia Hospitality',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=6.5, color=SUBTLE)
fig.suptitle('Ежемесячная выручка (тыс. €)  ·  Vestia Hospitality Group, июл. 2015 – авг. 2017',
             x=0.012, y=1.03, ha='left', fontsize=10.5, fontweight='bold', color=TEXT)

fig.tight_layout(pad=0.5)
fig.savefig(f'{OUTPUT_DIR}/chart1_revenue.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart1_revenue.png сохранён")
```

---

---

# График 2 — Сезонность ADR: Lisboa vs Algarve

**Что показывает:** средний суточный тариф по месяцам (усреднение за 2015–2017)
для двух отелей. Наглядно демонстрирует принципиальное различие двух объектов:
Lisboa стабилен (€82–120), Algarve — резко сезонный (€49 зимой, €181 в августе).

**Зачем нужен:** обосновывает тезис «два разных бизнеса под одной крышей»
и объясняет сложность управления группой.

**Что можно менять:** какие месяцы аннотировать, ширину заливки, наличие стрелки-разрыва.

```python
# ── ДАННЫЕ ───────────────────────────────────────────────────────────────────
nc = df[(df['is_canceled']==0) & (df['adr']>0)]

city_adr   = nc[nc['hotel']=='City Hotel'].groupby('arrival_month_num')['adr'].mean()
resort_adr = nc[nc['hotel']=='Resort Hotel'].groupby('arrival_month_num')['adr'].mean()

months_ru2 = ['янв','фев','мар','апр','май','июн',
               'июл','авг','сен','окт','ноя','дек']
xi = np.arange(12)
lisb  = [city_adr.get(m, np.nan)   for m in range(1,13)]
alg   = [resort_adr.get(m, np.nan) for m in range(1,13)]

# ── ГРАФИК ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9.5, 4.6))
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_axisbelow(True)
ax.yaxis.grid(True, color=LGRID, linewidth=0.7, zorder=0)
ax.tick_params(length=0, labelsize=8)

# Заливки между кривыми
ax.fill_between(xi, lisb, alg,
                where=[a>l for a,l in zip(alg,lisb)],
                alpha=0.07, color=COPPER, interpolate=True)
ax.fill_between(xi, lisb, alg,
                where=[a<=l for a,l in zip(alg,lisb)],
                alpha=0.07, color=HSE_NAVY, interpolate=True)

ax.plot(xi, lisb, color=HSE_NAVY, lw=2.4, marker='o', ms=5,
        markerfacecolor='white', markeredgewidth=1.8, zorder=4,
        label='Vestia Lisboa')
ax.plot(xi, alg,  color=COPPER,   lw=2.4, marker='o', ms=5,
        markerfacecolor='white', markeredgewidth=1.8, zorder=4,
        label='Vestia Algarve')

# Стрелка-разрыв в августе
ax.annotate('', xy=(7, alg[7]), xytext=(7, lisb[7]),
            arrowprops=dict(arrowstyle='<->', color='#999999', lw=1.0,
                            mutation_scale=10))
ax.text(7.2, (lisb[7]+alg[7])/2, 'разрыв\n3,7×', fontsize=7.5,
        color=SUBTLE, va='center')

# Точечные подписи (янв, авг, дек)
for i in [0, 7, 11]:
    ax.text(i, lisb[i]+5, f'€{lisb[i]:.0f}', ha='center', fontsize=6.5,
            color=HSE_NAVY, fontweight='bold')
    ax.text(i, alg[i]-9,  f'€{alg[i]:.0f}',  ha='center', fontsize=6.5,
            color=COPPER,   fontweight='bold')

ax.set_xticks(xi)
ax.set_xticklabels(months_ru2, fontsize=8.5)
ax.set_ylim(25, 215)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'€{int(v)}'))
ax.legend(frameon=False, fontsize=8.5, loc='upper left',
          handlelength=1.6, handleheight=0.9)

ax.text(0.995, -0.13,
        'Среднее за 2015–2017  ·  Без учёта отменённых бронирований',
        transform=ax.transAxes, ha='right', va='bottom', fontsize=6.5, color=SUBTLE)
fig.suptitle('Средний суточный тариф по месяцам (€)  ·  Сравнение двух объектов',
             x=0.012, y=1.03, ha='left', fontsize=10.5, fontweight='bold', color=TEXT)

fig.tight_layout(pad=0.5)
fig.savefig(f'{OUTPUT_DIR}/chart2_seasonality.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart2_seasonality.png сохранён")
```

---

---

# График 3 — Каналы бронирования: доля vs уровень отмен

**Что показывает:** две горизонтальные панели. Слева — доля бронирований
по каналу. Справа — уровень отмен по тому же каналу. Канал «Прямые» выделен
тёмно-синим (spotlight approach), остальные — светло-голубые.

**Зачем нужен:** ключевой слайд EDA. Сразу виден парадокс: прямой канал
маленький по объёму (10,6%), но лучший по качеству (cancel rate 15,3% vs 36,7% у OTA).

**Что можно менять:** список каналов, порядок сортировки, цвет spotlight.

```python
# ── ДАННЫЕ ───────────────────────────────────────────────────────────────────
channels_ru = ['Корпоративные', 'Прямые', 'Группы', 'Offline агентства', 'Online агентства']
shares  = [4.4, 10.6, 16.6, 20.3, 47.3]
cancels = [18.7, 15.3, 61.1, 34.3, 36.7]

bar_col = [HSE_NAVY if c=='Прямые' else BLUE_LIGHT for c in channels_ru]

# ── ГРАФИК ───────────────────────────────────────────────────────────────────
fig, (ax_s, ax_c) = plt.subplots(1, 2, figsize=(11.5, 3.9))

for ax in (ax_s, ax_c):
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=LGRID, linewidth=0.7, zorder=0)
    ax.yaxis.grid(False)
    ax.tick_params(length=0, labelsize=8)

y = np.arange(len(channels_ru))

# Левая панель — доля бронирований
ax_s.barh(y, shares, color=bar_col, height=0.52, zorder=3)
ax_s.set_yticks(y)
ax_s.set_yticklabels(channels_ru, fontsize=8.5, color=TEXT)
ax_s.set_xlim(0, 60)
ax_s.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v)}%'))
ax_s.tick_params(axis='x', labelsize=7.5, labelcolor=SUBTLE)
ax_s.set_title('Доля бронирований', fontsize=9.5, color=TEXT, pad=10,
               loc='left', fontweight='bold')
for i, v in enumerate(shares):
    is_d = channels_ru[i]=='Прямые'
    ax_s.text(v+0.8, i, f'{v:.1f}%', va='center',
              fontsize=8 if is_d else 7.5,
              fontweight='bold' if is_d else 'normal',
              color=HSE_NAVY if is_d else TEXT)

# Правая панель — уровень отмен
ax_c.barh(y, cancels, color=bar_col, height=0.52, zorder=3)
ax_c.set_yticks(y)
ax_c.set_yticklabels([], fontsize=8.5)
ax_c.set_xlim(0, 78)
ax_c.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v)}%'))
ax_c.tick_params(axis='x', labelsize=7.5, labelcolor=SUBTLE)
ax_c.set_title('Уровень отмен', fontsize=9.5, color=TEXT, pad=10,
               loc='left', fontweight='bold')
for i, v in enumerate(cancels):
    is_d = channels_ru[i]=='Прямые'
    ax_c.text(v+0.8, i, f'{v:.1f}%', va='center',
              fontsize=8 if is_d else 7.5,
              fontweight='bold' if is_d else 'normal',
              color=HSE_NAVY if is_d else TEXT)

legend_els = [mpatches.Patch(fc=HSE_NAVY,   label='Прямой канал'),
              mpatches.Patch(fc=BLUE_LIGHT,  label='Прочие каналы')]
fig.legend(handles=legend_els, frameon=False, fontsize=8,
           loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.06),
           handlelength=1.1, handleheight=0.85)
fig.text(0.5, -0.12,
         'Источник: внутренние данные Vestia Hospitality, 2015–2017',
         ha='center', fontsize=6.5, color=SUBTLE)
fig.suptitle('Каналы бронирования: объём и уровень отмен',
             x=0.012, y=1.05, ha='left', fontsize=10.5, fontweight='bold', color=TEXT)

fig.tight_layout(pad=0.8)
fig.savefig(f'{OUTPUT_DIR}/chart3_channels.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart3_channels.png сохранён")
```

---

---

# График 4 — Дерево метрик

**Что показывает:** иерархию метрик компании. NSM (RevPAR) → Уровень 1 (ADR
и Realization Rate) → Уровень 2 (канальный микс, тип объекта, уровень отмен,
повторные гости). В каждом блоке — реальные числа из датасета.

**Зачем нужен:** показывает, что мы понимаем бизнес-логику и знаем, как
каждая метрика связана с другой.

**Что можно менять:** тексты в блоках (числа), цвета уровней, положение блоков,
размер фигуры для лучшей читаемости.

```python
# ── ГРАФИК ───────────────────────────────────────────────────────────────────
# Этот график — чистая рисовка, данных из CSV не требует.
# Числа захардкожены по результатам анализа.

fig, ax = plt.subplots(figsize=(18, 9))
ax.set_xlim(0, 18); ax.set_ylim(0, 9)
ax.axis('off')

WHITE = '#FFFFFF'

def draw_box(cx, cy, w, h, bgcolor, lines, text_color=WHITE):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                                boxstyle="round,pad=0.07",
                                facecolor=bgcolor, edgecolor='none', zorder=3))
    dy = h / (len(lines)+1)
    for i, (txt, fs, bold) in enumerate(lines):
        ax.text(cx, cy+h/2-dy*(i+1), txt, ha='center', va='center',
                fontsize=fs, color=text_color,
                fontweight='bold' if bold else 'normal', zorder=4)

def conn(pts):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color='#BBBBBB', lw=1.3, zorder=1,
            solid_capstyle='round', solid_joinstyle='round')

# Позиции блоков (cx, cy, w, h)
NX,NY,NW,NH  = 9.0, 7.6, 8.5, 1.1
AX,AY,AW,AH  = 4.0, 5.05, 4.2, 1.0
RX,RY,RW,RH  = 14.0, 5.05, 4.2, 1.0
C1X,C1Y,C1W,C1H = 2.2, 2.25, 3.1, 1.9
C2X,C2Y,C2W,C2H = 6.2, 2.25, 3.1, 1.9
C3X,C3Y,C3W,C3H = 10.9, 2.25, 3.1, 1.9
C4X,C4Y,C4W,C4H = 14.9, 2.25, 3.1, 1.9

JY1, JYL, JYR = 6.1, 3.4, 3.4

for pts in [
    [(NX, NY-NH/2),(NX, JY1)],
    [(AX, JY1),(RX, JY1)],
    [(AX, JY1),(AX, AY+AH/2)],
    [(RX, JY1),(RX, RY+RH/2)],
    [(AX, AY-AH/2),(AX, JYL)],
    [(C1X,JYL),(C2X,JYL)],
    [(C1X,JYL),(C1X,C1Y+C1H/2)],
    [(C2X,JYL),(C2X,C2Y+C2H/2)],
    [(RX, RY-RH/2),(RX, JYR)],
    [(C3X,JYR),(C4X,JYR)],
    [(C3X,JYR),(C3X,C3Y+C3H/2)],
    [(C4X,JYR),(C4X,C4Y+C4H/2)],
]: conn(pts)

draw_box(NX,NY,NW,NH, HSE_NAVY,
         [('NSM: RevPAR (прокси)', 14, True),
          ('ADR × Realization Rate  ≈  €63 / ночь', 11, False)])
draw_box(AX,AY,AW,AH, HSE_BLUE,
         [('ADR', 14, True), ('€100 / ночь', 11, False)])
draw_box(RX,RY,RW,RH, HSE_BLUE,
         [('Realization Rate', 14, True),
          ('63,0%  =  1 − уровень отмен', 11, False)])
draw_box(C1X,C1Y,C1W,C1H, BLUE_LIGHT,
         [('Канальный микс', 12, True),
          ('Прямые — €115', 11, False),
          ('Online TA — €117', 11, False),
          ('Корп. — €69', 11, False)], TEXT)
draw_box(C2X,C2Y,C2W,C2H, BLUE_LIGHT,
         [('Тип объекта', 12, True),
          ('Lisboa — €108', 11, False),
          ('Algarve — €93', 11, False),
          ('Сезонный пик ×3,7', 11, False)], TEXT)
draw_box(C3X,C3Y,C3W,C3H, BLUE_LIGHT,
         [('Уровень отмен', 12, True),
          ('Прямые — 15,3%', 11, False),
          ('Online TA — 36,7%', 11, False),
          ('Группы — 61,1%', 11, False)], TEXT)
draw_box(C4X,C4Y,C4W,C4H, BLUE_LIGHT,
         [('Повторные гости', 12, True),
          ('Доля — 3,2%', 11, False),
          ('Отмены — 14,5%', 11, False),
          ('Новые — 37,8%', 11, False)], TEXT)

for y, lbl in [(NY,'NSM'), (AY,'Уровень 1'), (C1Y,'Уровень 2')]:
    ax.text(0.28, y, lbl, ha='center', va='center', fontsize=10,
            color=SUBTLE, fontstyle='italic', rotation=90,
            clip_on=False, zorder=5)

ax.text(NX, 0.42,
        'Net RevPAR ≈ €57/ночь  (−10,1% — взвешенная комиссия OTA, ставка 17%)',
        ha='center', fontsize=9.5, color=SUBTLE, fontstyle='italic')

ax.text(0.012, 0.97, 'Дерево метрик  ·  Vestia Hospitality Group',
        transform=ax.transAxes, fontsize=13, fontweight='bold', color=TEXT, va='top')

fig.tight_layout(pad=0.3)
fig.savefig(f'{OUTPUT_DIR}/chart_tree.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart_tree.png сохранён")
```

---

---

# График 5 — Динамика RevPAR (NSM)

**Что показывает:** ежемесячный RevPAR (прокси = ADR × Realization Rate)
по двум отелям за весь период датасета. Тёмно-синий — Lisboa, медь — Algarve.
Аннотированы августовские пики каждого года.

**Зачем нужен:** демонстрирует динамику главной метрики. Видно, что NSM
растёт (туристический бум), но с сильной волатильностью у Algarve.

**Что можно менять:** какие пики аннотировать, ylim, ширину линий.

```python
# ── ДАННЫЕ ───────────────────────────────────────────────────────────────────
def monthly_metrics(subset):
    nc  = subset[(subset['is_canceled']==0) & (subset['adr']>0)]
    adr = nc.groupby(['arrival_date_year','arrival_month_num'])['adr'].mean()
    tot = subset.groupby(['arrival_date_year','arrival_month_num'])['is_canceled'].count()
    cnc = subset.groupby(['arrival_date_year','arrival_month_num'])['is_canceled'].sum()
    m   = pd.DataFrame({'adr': adr, 'cancel_rate': cnc/tot}).dropna()
    m['realization'] = 1 - m['cancel_rate']
    m['revpar']      = m['adr'] * m['realization']
    return m.reset_index().sort_values(
        ['arrival_date_year','arrival_month_num']).reset_index(drop=True)

city   = monthly_metrics(df[df['hotel']=='City Hotel'])
resort = monthly_metrics(df[df['hotel']=='Resort Hotel'])

month_ru_s = {1:'янв',2:'фев',3:'мар',4:'апр',5:'май',6:'июн',
              7:'июл',8:'авг',9:'сен',10:'окт',11:'ноя',12:'дек'}

def xlabels(m):
    return [f"{month_ru_s[int(r['arrival_month_num'])]}\n'{str(int(r['arrival_date_year']))[2:]}"
            for _, r in m.iterrows()]

city_xl = xlabels(city)
xi      = np.arange(len(city))
sel     = list(range(0, len(xi), 3))

# ── ГРАФИК ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 4.5))
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_axisbelow(True)
ax.yaxis.grid(True, color=LGRID, linewidth=0.7, zorder=0)
ax.tick_params(length=0, labelsize=8)

ax.plot(xi, city['revpar'],   color=HSE_NAVY, lw=2.2, marker='o', ms=4,
        markerfacecolor='white', markeredgewidth=1.5, zorder=4, label='Vestia Lisboa')
ax.plot(xi, resort['revpar'], color=COPPER,   lw=2.2, marker='o', ms=4,
        markerfacecolor='white', markeredgewidth=1.5, zorder=4, label='Vestia Algarve')

# Пики августов
for df_h, col, voff in [(city, HSE_NAVY, 4), (resort, COPPER, -9)]:
    for idx, row in df_h.iterrows():
        if int(row['arrival_month_num']) == 8:
            ax.text(idx, row['revpar']+voff, f"€{row['revpar']:.0f}",
                    ha='center', fontsize=6.5, color=col, fontweight='bold')

for xv in [5.5, 17.5]:
    ax.axvline(xv, color='#CCCCCC', lw=0.8, ls=':', zorder=2)
for mid, yr in [(2.5,'2015'),(11.5,'2016'),(22.0,'2017')]:
    ax.text(mid, 138, yr, ha='center', fontsize=8, color=SUBTLE, fontstyle='italic')

ax.set_xticks(sel)
ax.set_xticklabels([city_xl[i] for i in sel], fontsize=7.5, linespacing=1.1)
ax.set_xlim(-0.6, len(xi)-0.4)
ax.set_ylim(0, 145)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'€{int(v)}'))
ax.legend(frameon=False, fontsize=8.5, loc='upper left', handlelength=1.5)

ax.text(0.5, -0.16,
        'RevPAR (прокси) = ADR × Realization Rate  ·  Источник: внутренние данные Vestia Hospitality',
        transform=ax.transAxes, ha='center', va='bottom', fontsize=6.5, color=SUBTLE)
fig.suptitle('RevPAR (прокси)  ·  Динамика NSM по объектам, июл. 2015 – авг. 2017',
             x=0.012, y=1.03, ha='left', fontsize=10.5, fontweight='bold', color=TEXT)

fig.tight_layout(pad=0.5)
fig.savefig(f'{OUTPUT_DIR}/chart_revpar.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart_revpar.png сохранён")
```

---

---

# График 6 — Декомпозиция RevPAR: ADR + Realization Rate

**Что показывает:** две панели. Слева — ежемесячный ADR по двум отелям
(растёт год к году). Справа — ежемесячный Realization Rate (= 1 − cancel rate):
горизонтальные пунктирные линии показывают среднее — оно не улучшается.

**Зачем нужен:** ключевой вывод шага 2: «Рост RevPAR идёт только через ADR
(внешний фактор), Realization Rate стагнирует — это операционная проблема».

**Что можно менять:** аннотацию "Рост ADR", расположение легенды, ylim.

```python
# (используем city и resort из предыдущего блока)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))

for ax in (ax1, ax2):
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=LGRID, linewidth=0.7, zorder=0)
    ax.tick_params(length=0, labelsize=8)
    ax.set_xticks(sel)
    ax.set_xticklabels([city_xl[i] for i in sel], fontsize=7.5, linespacing=1.1)
    ax.set_xlim(-0.6, len(xi)-0.4)
    for xv in [5.5, 17.5]:
        ax.axvline(xv, color='#CCCCCC', lw=0.8, ls=':', zorder=2)

# Левая: ADR
ax1.plot(xi, city['adr'],   color=HSE_NAVY, lw=2.2, marker='o', ms=3.5,
         markerfacecolor='white', markeredgewidth=1.5, zorder=4, label='Vestia Lisboa')
ax1.plot(xi, resort['adr'], color=COPPER,   lw=2.2, marker='o', ms=3.5,
         markerfacecolor='white', markeredgewidth=1.5, zorder=4, label='Vestia Algarve')
ax1.set_ylim(30, 230)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'€{int(v)}'))

# Подписи августовских пиков для ADR
for df_h, col, voff in [(city, HSE_NAVY, 5), (resort, COPPER, -11)]:
    for idx, row in df_h.iterrows():
        if int(row['arrival_month_num']) == 8:
            ax1.text(idx, row['adr']+voff, f"€{row['adr']:.0f}",
                     ha='center', fontsize=6.5, color=col, fontweight='bold')

ax1.set_title('Уровень 1А: ADR', fontsize=10, color=TEXT, pad=8,
              loc='left', fontweight='bold')
ax1.legend(frameon=False, fontsize=8, loc='upper left', handlelength=1.3)

# Правая: Realization Rate
ax2.plot(xi, city['realization']*100,   color=HSE_NAVY, lw=2.2, marker='o', ms=3.5,
         markerfacecolor='white', markeredgewidth=1.5, zorder=4, label='Vestia Lisboa')
ax2.plot(xi, resort['realization']*100, color=COPPER,   lw=2.2, marker='o', ms=3.5,
         markerfacecolor='white', markeredgewidth=1.5, zorder=4, label='Vestia Algarve')
ax2.set_ylim(20, 100)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v)}%'))

avg_c = city['realization'].mean()*100
avg_r = resort['realization'].mean()*100
ax2.axhline(avg_c, color=HSE_NAVY, lw=0.9, ls='--', alpha=0.5)
ax2.axhline(avg_r, color=COPPER,   lw=0.9, ls='--', alpha=0.5)
ax2.text(25.4, avg_c+1.5, f'ср. {avg_c:.0f}%', fontsize=6.5, color=HSE_NAVY)
ax2.text(25.4, avg_r-3.5, f'ср. {avg_r:.0f}%', fontsize=6.5, color=COPPER)

ax2.text(13, 28, 'Нет значимой динамики за весь период',
         fontsize=7.5, color=SUBTLE, fontstyle='italic', ha='center')
ax2.set_title('Уровень 1Б: Realization Rate (1 − отмены)',
              fontsize=10, color=TEXT, pad=8, loc='left', fontweight='bold')
ax2.legend(frameon=False, fontsize=8, loc='lower left', handlelength=1.3)

fig.text(0.5, -0.04,
         'Realization Rate = 1 − уровень отмен  ·  Источник: внутренние данные Vestia Hospitality',
         ha='center', fontsize=6.5, color=SUBTLE)
fig.suptitle('Декомпозиция RevPAR: ADR растёт, Realization Rate стагнирует',
             x=0.012, y=1.03, ha='left', fontsize=10.5, fontweight='bold', color=TEXT)

fig.tight_layout(pad=0.5)
fig.savefig(f'{OUTPUT_DIR}/chart_decomp.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart_decomp.png сохранён")
```

---

---

# График 7 — A/A тест: проверка однородности групп

**Что показывает:** три панели. 1) Распределение lead time в группах A и B
(гистограмма). 2) Распределение каналов (сгруппированные бары). 3) Cancel rate
в A и B (должны быть одинаковые). Для каждого — p-значение теста однородности.

**Зачем нужен:** доказывает, что случайный сплит 50/50 сработал корректно —
группы статистически неразличимы до начала эксперимента.

**Что можно менять:** seed рандомизации (np.random.seed(42)), список
проверяемых характеристик, вид ошибочных баров.

```python
np.random.seed(42)

# Целевая аудитория
eligible = df[
    (df['lead_time'] >= 60) &
    (~df['market_segment'].isin(['Groups','Corporate','Complementary','Aviation','Undefined']))
].copy().reset_index(drop=True)
eligible['group'] = np.random.choice(['A','B'], size=len(eligible), p=[0.5,0.5])

A = eligible[eligible['group']=='A']
B = eligible[eligible['group']=='B']

# Тесты однородности
_, p_mw = stats.mannwhitneyu(A['lead_time'], B['lead_time'], alternative='two-sided')
ct_seg = pd.crosstab(eligible['market_segment'], eligible['group'])
_, p_chi2, _, _ = stats.chi2_contingency(ct_seg)
ct_cr = pd.crosstab(eligible['group'], eligible['is_canceled'])
_, p_cr, _, _ = stats.chi2_contingency(ct_cr)

segments = ['Online TA', 'Offline TA/TO', 'Direct']
a_sh = [A[A['market_segment']==s].shape[0]/len(A)*100 for s in segments]
b_sh = [B[B['market_segment']==s].shape[0]/len(B)*100 for s in segments]
cr_A = A['is_canceled'].mean()
cr_B = B['is_canceled'].mean()

# ── ГРАФИК ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

def style(ax):
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=8)

def pbox(ax, p, test):
    col = '#1A7A60'
    ax.text(0.97, 0.95, f'{test}\np = {p:.3f}',
            transform=ax.transAxes, ha='right', va='top', fontsize=8,
            color=col, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#F6FBF7', edgecolor='none'))

# Панель 1: Lead time
ax = axes[0]; style(ax)
bins = np.arange(60, 380, 20)
ax.hist(A['lead_time'], bins=bins, alpha=0.65, color=HSE_NAVY, density=True,
        label='Группа A', zorder=3)
ax.hist(B['lead_time'], bins=bins, alpha=0.55, color=COPPER, density=True,
        label='Группа B', zorder=2)
ax.yaxis.grid(True, color=LGRID, linewidth=0.6, zorder=0)
ax.set_xlabel('Lead time (дней)', fontsize=8.5)
ax.set_ylabel('Плотность', fontsize=8.5)
ax.set_xlim(55, 380)
ax.legend(frameon=False, fontsize=8)
pbox(ax, p_mw, 'Mann-Whitney U')
ax.set_title('Lead time', fontsize=10, fontweight='bold', pad=8, loc='left')

# Панель 2: Канальный сегмент
ax = axes[1]; style(ax)
x3 = np.arange(len(segments)); w = 0.35
ax.bar(x3-w/2, a_sh, width=w, color=HSE_NAVY, alpha=0.85, label='Группа A', zorder=3)
ax.bar(x3+w/2, b_sh, width=w, color=COPPER,   alpha=0.75, label='Группа B', zorder=3)
for i,(a,b) in enumerate(zip(a_sh,b_sh)):
    ax.text(i-w/2, a+0.3, f'{a:.1f}%', ha='center', fontsize=7, color=HSE_NAVY)
    ax.text(i+w/2, b+0.3, f'{b:.1f}%', ha='center', fontsize=7, color=COPPER)
ax.yaxis.grid(True, color=LGRID, linewidth=0.6, zorder=0)
ax.set_xticks(x3); ax.set_xticklabels(segments, fontsize=8)
ax.set_ylabel('Доля в группе (%)', fontsize=8.5)
ax.legend(frameon=False, fontsize=8)
pbox(ax, p_chi2, 'χ²-тест')
ax.set_title('Канальный сегмент', fontsize=10, fontweight='bold', pad=8, loc='left')

# Панель 3: Cancel rate A/A
ax = axes[2]; style(ax)
bars = ax.bar(['Группа A','Группа B'], [cr_A*100, cr_B*100],
               color=[HSE_NAVY, COPPER], alpha=0.85, width=0.45, zorder=3)
ax.yaxis.grid(True, color=LGRID, linewidth=0.6, zorder=0)
ax.set_ylim(0, 55)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v)}%'))
for bar, val in zip(bars,[cr_A,cr_B]):
    ax.text(bar.get_x()+bar.get_width()/2, val*100+0.3,
            f'{val:.1%}', ha='center', fontsize=9, fontweight='bold')
pbox(ax, p_cr, 'χ²-тест')
ax.set_title('Cancel rate (A/A-тест)', fontsize=10, fontweight='bold', pad=8, loc='left')

fig.text(0.5, -0.03,
         'Все p-значения > 0,05 — группы статистически однородны  ·  '
         'Целевая аудитория: lead time ≥ 60 дней, Direct / Online TA / Offline TA',
         ha='center', fontsize=7, color=SUBTLE)
fig.suptitle('A/A-тест: проверка однородности групп  ·  Гипотеза 1 (Невозвратный тариф)',
             x=0.012, y=1.04, ha='left', fontsize=11, fontweight='bold', color=TEXT)

fig.tight_layout(pad=0.8)
fig.savefig(f'{OUTPUT_DIR}/chart_aa_test.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart_aa_test.png сохранён")
```

---

---

# График 8 — Расчёт размера выборки

**Что показывает:** слева — кривая мощности (как мощность теста растёт
с размером выборки), отмечена точка n=292 при мощности 80%. Справа —
сводная таблица параметров теста.

**Зачем нужен:** обосновывает выбор n=292 на группу и длительность 14 дней.

**Что можно менять:** параметры (p_base, p_treat, alpha, power),
цвет точки, содержимое таблицы.

```python
# (используем eligible из предыдущего блока)

p_base  = eligible['is_canceled'].mean()
p_treat = 0.30 * 0.05 + 0.70 * p_base   # uptake 30%, cancel = 5%
delta   = p_base - p_treat

z_alpha = stats.norm.ppf(0.975)    # двусторонний α=0.05
ns      = np.arange(50, 600, 5)

def power_fn(n, p1, p2):
    se = np.sqrt(p1*(1-p1)/n + p2*(1-p2)/n)
    z  = abs(p1-p2)/se
    return stats.norm.cdf(z - z_alpha) + stats.norm.cdf(-z - z_alpha)

powers = [power_fn(n, p_base, p_treat) for n in ns]

# n при мощности 80%
n_req = int(np.ceil(
    ((z_alpha + stats.norm.ppf(0.80))**2 *
     (p_base*(1-p_base) + p_treat*(1-p_treat))) / delta**2
))

# ── ГРАФИК ───────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

for ax in (ax1, ax2):
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, labelsize=8.5)

# Кривая мощности
ax1.plot(ns, [p*100 for p in powers], color=HSE_NAVY, lw=2.2, zorder=3)
ax1.axhline(80, color=COPPER, lw=1.2, ls='--', zorder=2)
ax1.axvline(n_req, color=COPPER, lw=1.2, ls='--', zorder=2)
ax1.fill_between(ns, [p*100 for p in powers], 0,
                 where=[p>=0.80 for p in powers], alpha=0.08, color=HSE_NAVY)
ax1.scatter([n_req], [80], color=COPPER, s=60, zorder=5)
ax1.text(n_req+10, 75, f'n = {n_req}\n(мощность 80%)', fontsize=8.5, color=COPPER, va='top')
ax1.text(480, 82, '80%', fontsize=8.5, color=COPPER)
ax1.yaxis.grid(True, color=LGRID, linewidth=0.6, zorder=0)
ax1.set_xlim(50, 580)
ax1.set_ylim(0, 105)
ax1.set_xlabel('Размер выборки (на группу)', fontsize=9)
ax1.set_ylabel('Статистическая мощность (%)', fontsize=9)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v)}%'))
ax1.set_title('Мощность теста vs размер выборки', fontsize=10, fontweight='bold', pad=8, loc='left')

# Таблица параметров
ax2.axis('off')
params = [
    ('Параметр', 'Значение'),
    ('Базовый cancel rate (p₁)', f'{p_base:.3f}  ({p_base:.1%})'),
    ('Ожидаемый cancel rate (p₂)', f'{p_treat:.3f}  ({p_treat:.1%})'),
    ('Ожидаемый Δ Realization Rate', f'+{delta:.1%}'),
    ('Уровень значимости (α)', '0,05'),
    ('Статистическая мощность (1−β)', '80%'),
    ('Критерий', 'z-тест для двух долей'),
    ('Размер выборки (на группу)', str(n_req)),
    ('Итого (обе группы)', str(n_req*2)),
    ('Поток: целевых брон./день', '≈ 60'),
    ('Минимальная длительность', '≈ 10 дней'),
    ('Рекомендуемая длительность', '14 дней (2 недели)'),
]

row_colors  = [HSE_NAVY] + ['white' if i%2==0 else '#F2F5F8' for i in range(len(params)-1)]
text_colors = ['#FFFFFF'] + [TEXT]*(len(params)-1)

for i, ((k, v), bg, tc) in enumerate(zip(params, row_colors, text_colors)):
    y = 1.0 - i*(1.0/(len(params)+0.5))
    ax2.add_patch(plt.Rectangle((0, y-0.06), 1.0, 0.08,
                                  facecolor=bg, edgecolor='none',
                                  transform=ax2.transAxes, zorder=1))
    ax2.text(0.03, y-0.02, k, transform=ax2.transAxes,
             fontsize=8.5 if i>0 else 9, fontweight='bold' if i==0 else 'normal',
             color=tc, va='center', zorder=2)
    ax2.text(0.97, y-0.02, v, transform=ax2.transAxes,
             fontsize=8.5 if i>0 else 9, fontweight='bold' if i==0 else 'normal',
             color=tc, va='center', ha='right', zorder=2)
ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
ax2.set_title('Параметры теста', fontsize=10, fontweight='bold', pad=8, loc='left')

fig.suptitle('Расчёт размера выборки  ·  Гипотеза 1 (Невозвратный тариф)',
             x=0.012, y=1.04, ha='left', fontsize=11, fontweight='bold', color=TEXT)
fig.tight_layout(pad=0.8)
fig.savefig(f'{OUTPUT_DIR}/chart_sample_size.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart_sample_size.png сохранён")
```

---

---

# График 9 — Продолжение временного ряда

**Что показывает:** три панели. Верхняя (основная метрика) — исторические
данные + 14-дневная симуляция для контроля и теста. Нижние две (контр-метрики)
— только период эксперимента, скользящее среднее за 3 дня + пунктирный ориентир
ожидаемого уровня.

**Зачем нужен:** выполняет требование задания «продолжить временной ряд».
Наглядно показывает, что тест выше контроля по Realization Rate, а ADR
и объём лишь незначимо снижаются.

**Что можно менять:** seed симуляции (np.random.seed(2026)), uptake (0.30),
скидку (0.07), длительность N=14.

```python
# (используем eligible, p_base из предыдущих блоков)

e17      = eligible[eligible['arrival_date_year']==2017].copy()
days_in  = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31}
hist_real = e17.groupby('arrival_month_num')['is_canceled'].mean().apply(lambda x:1-x)
adr_mean = e17[e17['is_canceled']==0]['adr'].mean()
adr_std  = e17[e17['is_canceled']==0]['adr'].std()
hist_vol = (e17.groupby('arrival_month_num')['is_canceled'].count() /
            e17.groupby('arrival_month_num')['is_canceled'].count().index.map(days_in))
vol_base = hist_vol[hist_vol.index>=6].mean()

p_treat2 = 0.30*0.05 + 0.70*p_base
adr_trt  = (0.30*0.93 + 0.70)*adr_mean
vol_trt  = vol_base*0.95

N, D = 14, 60
month_ru_s2 = {1:'янв',2:'фев',3:'мар',4:'апр',5:'май',6:'июн',
               7:'июл',8:'авг',9:'сен',10:'окт',11:'ноя',12:'дек'}

def rolling3(lst): return [np.mean(lst[max(0,i-2):i+1]) for i in range(len(lst))]
def ca2(lst):      return [np.mean(lst[:i+1]) for i in range(len(lst))]

hm = sorted(hist_real.index.tolist())

np.random.seed(2026)
ctrl_r = [(D-np.random.binomial(D,p_base))/D  for _ in range(N)]
trt_r  = [(D-np.random.binomial(D,p_treat2))/D for _ in range(N)]
np.random.seed(303);  ctrl_a = rolling3([np.random.normal(adr_mean, adr_std*0.10) for _ in range(N)])
np.random.seed(102);  trt_a  = rolling3([np.random.normal(adr_trt,  adr_std*0.10) for _ in range(N)])
np.random.seed(404);  ctrl_v = rolling3([np.random.poisson(vol_base) for _ in range(N)])
trt_v  = rolling3([max(int(c*0.95),0) for c in [np.random.poisson(vol_base) for _ in range(N)]])

HX = list(range(len(hm))); EX = [len(hm)+2.0+i for i in range(N)]
SEP = len(hm)+1.0; XMAX = EX[-1]+0.4
ht = [(x, month_ru_s2[m]) for x,m in zip(HX,hm)]
et = [(EX[i], f'Д{i+1}') for i in range(N) if (i+1)%2==0]
ax1_ticks=[x for x,_ in ht]+[x for x,_ in et]
ax1_lbls =[l for _,l in ht]+[l for _,l in et]
DX = list(range(N))
d_ticks=[i for i in DX if (i+1)%2==0]; d_lbls=[f'Д{i+1}' for i in d_ticks]

fig = plt.figure(figsize=(15, 7))
gs  = gridspec.GridSpec(2,2,figure=fig,height_ratios=[1.65,1],
                         hspace=0.52,wspace=0.22,left=0.06,right=0.94,top=0.88,bottom=0.09)
ax1=fig.add_subplot(gs[0,:]); ax2=fig.add_subplot(gs[1,0]); ax3=fig.add_subplot(gs[1,1])

def styleax(ax):
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_axisbelow(True); ax.yaxis.grid(True,color=LGRID,linewidth=0.6,zorder=0)
    ax.tick_params(length=0,labelsize=10)

# Панель 1: Realization Rate
styleax(ax1)
ax1.axvspan(EX[0]-0.7,EX[-1]+0.7,alpha=0.06,color=HSE_NAVY,zorder=0)
ax1.axvline(SEP,color='#BBBBBB',lw=1.0,ls=':',zorder=2)
rv=[hist_real.get(m,np.nan) for m in hm]
ax1.plot(HX,[v*100 for v in rv],color=GRAY_HSE,lw=2.5,marker='o',ms=6,
         markerfacecolor='white',markeredgewidth=2,zorder=4)
ax1.plot(EX,[v*100 for v in ctrl_r],color=HSE_NAVY,lw=0.9,alpha=0.28,zorder=3)
ax1.plot(EX,[v*100 for v in ca2(ctrl_r)],color=HSE_NAVY,lw=2.5,ls='--',zorder=4)
ax1.plot(EX,[v*100 for v in trt_r],color=COPPER,lw=0.9,alpha=0.28,zorder=3)
ax1.plot(EX,[v*100 for v in ca2(trt_r)],color=COPPER,lw=2.5,zorder=4)
ax1.axhline((1-p_treat2)*100,color=COPPER,lw=0.9,ls=':',alpha=0.45,xmin=0.56)
ax1.axhline((1-p_base)*100,color=HSE_NAVY,lw=0.9,ls=':',alpha=0.45,xmin=0.56)
ax1.text(XMAX+0.2,(1-p_treat2)*100+0.5,f'Тест: {(1-p_treat2)*100:.1f}%',
         fontsize=10,color=COPPER,va='bottom',ha='left',fontweight='bold',clip_on=False)
ax1.text(XMAX+0.2,(1-p_base)*100-0.5,f'Контроль: {(1-p_base)*100:.1f}%',
         fontsize=10,color=HSE_NAVY,va='top',ha='left',fontweight='bold',clip_on=False)
legend_els=[
    Line2D([0],[0],color=GRAY_HSE,lw=2.5,marker='o',ms=5,
           markerfacecolor='white',markeredgewidth=1.8,label='Исторические данные'),
    Line2D([0],[0],color=HSE_NAVY,lw=2.5,ls='--',label='Контроль (накопл. среднее)'),
    Line2D([0],[0],color=COPPER,lw=2.5,label='Тест (накопл. среднее)'),
]
ax1.legend(handles=legend_els,frameon=False,fontsize=9.5,
           loc='upper left',bbox_to_anchor=(0.01,0.99),handlelength=1.5,ncol=1)
ax1.set_ylim(42,94)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_:f'{int(v)}%'))
ax1.set_ylabel('Realization Rate',fontsize=11)
ax1.set_title('Целевая метрика: Realization Rate',fontsize=12,fontweight='bold',pad=8,loc='left')
ax1.set_xticks(ax1_ticks); ax1.set_xticklabels(ax1_lbls,fontsize=9.5)
ax1.set_xlim(-0.5,XMAX+3.5)

# Панель 2: ADR
styleax(ax2)
ax2.axhline(adr_mean,color=HSE_NAVY,lw=1.8,ls='--',alpha=0.55,zorder=2)
ax2.axhline(adr_trt, color=COPPER,  lw=1.8,ls='--',alpha=0.55,zorder=2)
ax2.plot(DX,ctrl_a,color=HSE_NAVY,lw=2.5,ls='--',zorder=4)
ax2.plot(DX,trt_a, color=COPPER,  lw=2.5,        zorder=4)
ax2.text(N-0.3,ctrl_a[-1]+0.4,'Контроль',fontsize=10,color=HSE_NAVY,va='bottom',ha='right',fontweight='bold')
ax2.text(N-0.3,trt_a[-1]-0.4,'Тест',    fontsize=10,color=COPPER,  va='top',   ha='right',fontweight='bold')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_:f'€{int(v)}'))
ax2.set_ylabel('ADR (€)',fontsize=11)
ax2.set_title('Контр-метрика 1: ADR  ·  скользящее среднее 3д',
              fontsize=12,fontweight='bold',pad=8,loc='left')
ax2.set_xticks(d_ticks); ax2.set_xticklabels(d_lbls,fontsize=9.5); ax2.set_xlim(-0.5,N-0.3)

# Панель 3: Volume
styleax(ax3)
ax3.axhline(vol_base,color=HSE_NAVY,lw=1.8,ls='--',alpha=0.55,zorder=2)
ax3.axhline(vol_trt, color=COPPER,  lw=1.8,ls='--',alpha=0.55,zorder=2)
ax3.plot(DX,ctrl_v,color=HSE_NAVY,lw=2.5,ls='--',zorder=4)
ax3.plot(DX,trt_v, color=COPPER,  lw=2.5,        zorder=4)
ax3.text(N-0.3,ctrl_v[-1]+0.5,'Контроль',fontsize=10,color=HSE_NAVY,va='bottom',ha='right',fontweight='bold')
ax3.text(N-0.3,trt_v[-1]-0.5,'Тест',    fontsize=10,color=COPPER,  va='top',   ha='right',fontweight='bold')
ax3.set_ylabel('Бронирований / день',fontsize=11)
ax3.set_title('Контр-метрика 2: Объём бронирований  ·  скользящее среднее 3д',
              fontsize=12,fontweight='bold',pad=8,loc='left')
ax3.set_xticks(d_ticks); ax3.set_xticklabels(d_lbls,fontsize=9.5); ax3.set_xlim(-0.5,N-0.3)

fig.suptitle('Продолжение временного ряда  ·  Гипотеза 1 (Невозвратный тариф)',
             x=0.012,y=0.97,ha='left',fontsize=14,fontweight='bold',color=TEXT)
fig.text(0.5,0.01,
    'Контроль: p_cancel=0,420  ·  Тест: 30% — невозвратный тариф (p=0,05), 70% — стандарт  ·  '
    'Пунктир (тонкий) = ожидаемый уровень  ·  Линии = накопл./скользящее среднее',
    ha='center',fontsize=9,color=SUBTLE)

fig.savefig(f'{OUTPUT_DIR}/chart_timeseries.png',dpi=300,bbox_inches='tight',facecolor='white')
plt.close()
print("chart_timeseries.png сохранён")
```

---

---

# График 10 — Итоги A/B-теста

**Что показывает:** три панели. 1) Барчарт cancel rate: контроль vs тест
с планками ошибок (95% ДИ). 2) z-распределение: красные области отвержения H₀,
вертикальная линия на z=4,67. 3) Waterfall бизнес-эффекта: валовая выручка →
минус стоимость скидок → чистый эффект.

**Зачем нужен:** финальный слайд анализа. Показывает, что H₀ отвергается
с p < 0,001 и что эффект составляет €1,2 млн в год.

**Что можно менять:** значения p_ctrl, p_trt (вычислены из симуляции),
все числа бизнес-эффекта, цвета bars.

```python
# Числа из симуляции и расчётов (захардкожены для воспроизводимости)
p_ctrl  = 0.4393
p_trt_r = 0.3286
n_exp   = 840
z_stat  = 4.6654
z_crit  = 1.9600
p_val   = 0.000003

se_ctrl = np.sqrt(p_ctrl*(1-p_ctrl)/n_exp)
se_trt  = np.sqrt(p_trt_r*(1-p_trt_r)/n_exp)
ci95    = 1.96
ci_lo   = (p_ctrl-p_trt_r) - ci95*np.sqrt(se_ctrl**2+se_trt**2)
ci_hi   = (p_ctrl-p_trt_r) + ci95*np.sqrt(se_ctrl**2+se_trt**2)

gross   = 1_486_212
cost    = 281_901
net_eff = 1_204_311
add_bkn = 2425

RED_LIGHT = '#FFE4E4'
RED       = '#C0392B'

fig = plt.figure(figsize=(15, 6))
gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.30,
                         left=0.05, right=0.97, top=0.87, bottom=0.12)
ax1=fig.add_subplot(gs[0]); ax2=fig.add_subplot(gs[1]); ax3=fig.add_subplot(gs[2])

def styleax2(ax):
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=9.5)

# Панель 1: cancel rate bars
styleax2(ax1); ax1.yaxis.grid(True, color=LGRID, linewidth=0.6, zorder=0)
bars = ax1.bar(['Контроль','Тест'], [p_ctrl*100, p_trt_r*100],
               color=[HSE_NAVY, COPPER], width=0.45, zorder=3)
ax1.errorbar(['Контроль','Тест'],
             [p_ctrl*100, p_trt_r*100],
             yerr=[[ci95*se_ctrl*100, ci95*se_trt*100],
                   [ci95*se_ctrl*100, ci95*se_trt*100]],
             fmt='none', color='#555555', capsize=5, linewidth=1.5, zorder=4)
for bar, val in zip(bars, [p_ctrl, p_trt_r]):
    ax1.text(bar.get_x()+bar.get_width()/2, val*100+0.8,
             f'{val:.1%}', ha='center', fontsize=11, fontweight='bold')
delta_rr = p_ctrl - p_trt_r
ax1.annotate('', xy=(1, p_trt_r*100+2), xytext=(1, p_ctrl*100-2),
             arrowprops=dict(arrowstyle='<->', color=SUBTLE, lw=1.2))
ax1.text(1.26, (p_ctrl+p_trt_r)/2*100, f'Δ = −{delta_rr:.1%}',
         fontsize=10, color=TEXT, va='center', fontweight='bold')
ax1.set_ylim(0, 60)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_:f'{int(v)}%'))
ax1.set_ylabel('Cancel rate', fontsize=10.5)
ax1.set_title('Сравнение cancel rate\nконтроль vs тест', fontsize=11, fontweight='bold', pad=8, loc='left')
ax1.text(0.5,-0.14,f'95% ДИ для Δ: [{ci_lo:.1%}, {ci_hi:.1%}]',
         transform=ax1.transAxes, ha='center', fontsize=9, color=SUBTLE)

# Панель 2: z-распределение
styleax2(ax2)
x = np.linspace(-4.5, 5.2, 600)
y = stats.norm.pdf(x)
ax2.plot(x, y, color=HSE_NAVY, lw=2.0, zorder=4)
mask_r = x >= z_crit; mask_l = x <= -z_crit
ax2.fill_between(x, y, where=mask_r,             color=RED_LIGHT, alpha=0.85, zorder=2)
ax2.fill_between(x, y, where=mask_l,             color=RED_LIGHT, alpha=0.85, zorder=2)
ax2.fill_between(x, y, where=~mask_r & ~mask_l,  color='#EBF0F7', alpha=0.6, zorder=1)
for zc in [-z_crit, z_crit]:
    ax2.axvline(zc, color=RED, lw=1.2, ls='--', alpha=0.7, zorder=3)
ax2.text( z_crit+0.08, 0.33, f'z_crit\n+{z_crit:.2f}', fontsize=8.5, color=RED, va='top')
ax2.text(-z_crit-0.08, 0.33, f'z_crit\n−{z_crit:.2f}', fontsize=8.5, color=RED, va='top', ha='right')
ax2.axvline(z_stat, color=COPPER, lw=2.2, zorder=5)
ax2.text(z_stat+0.05, 0.18, f'z = {z_stat:.2f}', fontsize=9.5,
         color=COPPER, fontweight='bold', va='center')
ax2.text(0, 0.08, f'p = {p_val:.6f}\nH₀ отвергается',
         fontsize=10, color=RED, ha='center', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=RED, linewidth=1.0))
ax2.set_xlim(-4.5, 5.8); ax2.set_ylim(0, 0.46)
ax2.set_xlabel('z-значение', fontsize=10)
ax2.set_yticks([])
legend_els2 = [mpatches.Patch(facecolor=RED_LIGHT, edgecolor='none', label='Область отвержения H₀'),
               mpatches.Patch(facecolor='#EBF0F7', edgecolor='none', label='Область принятия H₀')]
ax2.legend(handles=legend_els2, frameon=False, fontsize=8.5, loc='upper left',
           handlelength=0.9, handleheight=0.8)
ax2.set_title('z-распределение\nдвусторонний тест, α = 0,05', fontsize=11, fontweight='bold', pad=8, loc='left')

# Панель 3: Waterfall
styleax2(ax3); ax3.yaxis.grid(True, color=LGRID, linewidth=0.6, zorder=0)
labels_w = ['Доп. выручка\n(реализ. брон.)', 'Стоимость\nскидок', 'Чистый\nэффект']
values_w = [gross, -cost, net_eff]
bottoms_w= [0, gross, 0]
colors_w = [TEAL, RED, TEAL]
for i, (lbl, val, bot, col) in enumerate(zip(labels_w, values_w, bottoms_w, colors_w)):
    height = abs(val)
    base   = bot if val>0 else bot+val
    ax3.bar(i, height, bottom=base, color=col, width=0.45, zorder=3, alpha=0.9)
    sign = '+' if val>0 else '−'
    ax3.text(i, base+height/2, f'{sign}€{abs(val)/1000:.0f} тыс.',
             ha='center', va='center', fontsize=10.5, fontweight='bold', color='white')
ax3.plot([0.23, 0.77], [gross, gross], color=SUBTLE, lw=0.8, ls='--')
ax3.plot([1.23, 1.77], [gross-cost, gross-cost], color=SUBTLE, lw=0.8, ls='--')
ax3.set_ylim(0, gross*1.18)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda v,_: f'€{int(v/1000)} тыс.' if v>0 else ''))
ax3.set_xticks([0,1,2]); ax3.set_xticklabels(labels_w, fontsize=9)
ax3.set_title('Годовой бизнес-эффект\n(целевая аудитория, n = 21 900 брон.)',
              fontsize=11, fontweight='bold', pad=8, loc='left')
ax3.text(0.5,-0.16,
         f'Доп. реализованных бронирований: {add_bkn:,} / год  ·  Avg выручка: €613 / бронирование',
         transform=ax3.transAxes, ha='center', fontsize=8.5, color=SUBTLE)

fig.suptitle('Итоги A/B-теста  ·  Гипотеза 1 (Невозвратный тариф)',
             x=0.012, y=0.97, ha='left', fontsize=14, fontweight='bold', color=TEXT)
fig.text(0.012, -0.02,
    'H₀: cancel rate_тест = cancel rate_контроль  ·  '
    'H₁: cancel rate_тест ≠ cancel rate_контроль  ·  '
    'z-тест для двух долей, α = 0,05',
    ha='left', fontsize=8.5, color=SUBTLE)

fig.savefig(f'{OUTPUT_DIR}/chart_ab_results.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("chart_ab_results.png сохранён")
```

---

---

## Запуск всех графиков сразу

Можно собрать все блоки в один файл `generate_charts.py` и запустить:

```bash
python generate_charts.py
```

Убедись, что `hotel_bookings.csv` лежит в той же папке или измени
`DATA_PATH` на полный путь к файлу.

Все 10 PNG будут сохранены в ту папку, что указана в `OUTPUT_DIR`.
MDEOF
