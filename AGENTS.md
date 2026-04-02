# Codex Handoff Document — Weed Scouting Dashboard

> **Язык документа:** русский (термины, имена функций, фрагменты кода — на английском)  
> **Назначение:** полная техническая спецификация для передачи проекта Codex или любому AI-ассистенту по программированию.

---

## Содержание

1. [Обзор проекта](#1-обзор-проекта)
2. [Технологический стек](#2-технологический-стек)
3. [Структура данных](#3-структура-данных)
4. [Ключевые формулы (КРИТИЧНО)](#4-ключевые-формулы-критично)
5. [Структура файлов](#5-структура-файлов)
6. [Архитектура HTML-файла](#6-архитектура-html-файла)
7. [Ключевые JavaScript-функции](#7-ключевые-javascript-функции)
8. [Архитектура CSS](#8-архитектура-css)
9. [Фильтры](#9-фильтры)
10. [Экспорт в PDF](#10-экспорт-в-pdf)
11. [Добавление новых данных](#11-добавление-новых-данных)
12. [Известные проблемы и примечания](#12-известные-проблемы-и-примечания)
13. [Что Codex должен знать перед редактированием](#13-что-codex-должен-знать-перед-редактированием)

---

## 1. Обзор проекта

**Weed Scouting Dashboard** — это интерактивный дашборд для анализа данных разведки сорняков на сельскохозяйственных полях.

### Ключевые характеристики

| Параметр | Значение |
|---|---|
| Тип | Single-file HTML (один файл) |
| Размер файла | ~1.3 МБ |
| Количество строк | ~1700+ |
| Хостинг | Статический сайт (без сервера) |
| Сборка | Не требуется (no build step) |
| Пакетный менеджер | Не используется (no npm) |

### Принцип работы

- Весь CSS, JavaScript и данные встроены **inline** в единственный файл `index.html`.
- Данные хранятся в JS-переменной `RAW_DATA` как массив объектов прямо в теле `<script>`.
- Никакого серверного рендеринга, никаких API-запросов во время работы — всё происходит в браузере пользователя.
- Файл можно открыть локально двойным щелчком или задеплоить на любой статический хостинг (GitHub Pages, Netlify, S3 и т.д.).

---

## 2. Технологический стек

Все зависимости загружаются через CDN — никаких локальных node_modules не существует.

```html
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<!-- Chart.js 4.4.0 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<!-- jsPDF 2.5.1 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

| Технология | Версия | Назначение |
|---|---|---|
| HTML5 | — | Разметка |
| CSS3 | — | Стилизация (custom properties, grid, flexbox) |
| Vanilla JavaScript | ES6+ | Вся логика (без фреймворков) |
| Chart.js | 4.4.0 (CDN) | Графики и диаграммы |
| jsPDF | 2.5.1 (CDN) | Генерация PDF-отчётов |
| Inter | Google Fonts | Типографика |

> **Важно:** Никаких фреймворков (React, Vue, Angular), никаких сборщиков (Webpack, Vite), никаких пакетных менеджеров. Только чистый HTML + CSS + JS.

---

## 3. Структура данных

### Источник данных

Файл: `/home/user/workspace/data_compact.json`

- **6 269 записей** (сорняки, зафиксированные на полях)
- Данные охватывают **4 фермы**, **5 лет** (2021–2025), **143 уникальных поля**, **46 видов сорняков**

### Компактная схема записи (compact keys)

Для экономии места в inline-массиве используются сокращённые ключи:

```json
{
  "fi": "Field_ID",
  "w":  "Weed name",
  "wc": "WeedClass",
  "pr": "Pressure text",
  "f":  "Field name",
  "fm": "Farm name",
  "ar": 123.4,
  "cr": "Crop name",
  "sb": "Scouted by",
  "yr": 2024,
  "sd": "2024-07-15",
  "ps": 2
}
```

### Расшифровка полей

| Ключ | Полное имя | Тип | Описание |
|---|---|---|---|
| `fi` | FieldID | string | Уникальный идентификатор поля |
| `w` | WeedName | string | Название вида сорняка |
| `wc` | WeedClass | string | Класс сорняка: `"Broadleaf"` или `"Grass"` |
| `pr` | PressureText | string | Текстовое описание давления (напр. `"Light"`) |
| `f` | FieldName | string | Название поля |
| `fm` | FarmName | string | Название фермы |
| `ar` | AreaAcres | number | Площадь поля в акрах |
| `cr` | CropName | string | Культура на поле |
| `sb` | ScoutedBy | string | Имя агронома/скаутера |
| `yr` | Year | number | Год разведки |
| `sd` | ScoutingDate | string | Дата разведки в формате `YYYY-MM-DD` |
| `ps` | PressureScore | number | Числовой балл давления (1–6) |

### Справочные значения

**Фермы (`fm`):**
- `Gottfried Farms JV`
- `D&C Farms Ltd`
- `LA Gott Farms`
- `Leibel Farm`

**Годы (`yr`):** 2021, 2022, 2023, 2024, 2025

**PressureScore — шкала давления:**

| Балл (`ps`) | Текст (`pr`) |
|---|---|
| 1 | Very Light |
| 2 | Light |
| 3 | Moderate |
| 4 | Heavy |
| 5 | Very Heavy |
| 6 | Heavy Patches |

---

## 4. Ключевые формулы (КРИТИЧНО)

### 4.1 WeedRiskScore (WRS)

WRS — основной агрономический показатель риска для поля. Шкала: **0–100**.

Формула перенесена из Power BI DAX. Реализация в JavaScript:

```javascript
// Шаг 1: Сгруппировать записи по паре (Field, Weed), вычислить средний ps для каждого сорняка
// Шаг 2: avgPS_field = среднее из всех avgPS сорняков данного поля
// Шаг 3: highPct = кол-во сорняков с avgPS >= 4 / общее кол-во уникальных сорняков на поле
// Шаг 4: WRS = (avgPS_field / 6 * 50) + (highPct * 50)
```

Пример реализации:

```javascript
function computeWRS(fieldRecords) {
    // Шаг 1: группировка по сорняку
    const weedMap = {};
    for (const r of fieldRecords) {
        if (!weedMap[r.w]) weedMap[r.w] = [];
        weedMap[r.w].push(r.ps);
    }

    const weedNames = Object.keys(weedMap);
    if (weedNames.length === 0) return 0;

    // Средний PS каждого сорняка
    const weedAvgs = weedNames.map(w => {
        const scores = weedMap[w];
        return scores.reduce((a, b) => a + b, 0) / scores.length;
    });

    // Шаг 2: средний PS по полю
    const avgPS_field = weedAvgs.reduce((a, b) => a + b, 0) / weedAvgs.length;

    // Шаг 3: доля "тяжёлых" сорняков
    const highCount = weedAvgs.filter(avg => avg >= 4).length;
    const highPct = highCount / weedAvgs.length;

    // Шаг 4: итоговый WRS
    return (avgPS_field / 6 * 50) + (highPct * 50);
}
```

### Зоны риска WRS

| Диапазон | Зона | CSS-класс | Цвет |
|---|---|---|---|
| 0 – 30 | Low | `.zone-low` | Жёлтый |
| 30 – 60 | Moderate | `.zone-mod` | Оранжевый |
| 60 – 100 | High | `.zone-high` | Красный |

> **КРИТИЧНО:** Формула WRS присутствует в коде в **двух местах** — в `updateKPIs()` и в `updateChart2()`. При изменении логики необходимо обновить **оба**.

---

### 4.2 KPI: Avg Pressure Score

```javascript
// Простое среднее значение поля ps по всем отфильтрованным записям
const avgPS = filteredData.reduce((sum, r) => sum + r.ps, 0) / filteredData.length;
```

### 4.3 KPI: Fields Scouted

```javascript
// Количество уникальных названий полей в отфильтрованных данных
const fieldsScouted = new Set(filteredData.map(r => r.f)).size;
```

---

## 5. Структура файлов

```
/home/user/workspace/
│
├── weed_dashboard/
│   └── index.html                ← ЕДИНСТВЕННЫЙ ФАЙЛ ПРОЕКТА
│                                    (весь CSS, JS и данные — внутри)
│
├── DataScoutGGDL.xlsx            ← Исходный Excel-файл с данными разведки
├── weed_data_clean.json          ← 6 269 записей, полные названия ключей
├── data_compact.json             ← 6 269 записей, компактные ключи
└── codex_handoff.md              ← Этот документ
```

> `weed_data_clean.json` и `data_compact.json` — это одни и те же данные. Компактная версия используется в `index.html` для экономии места.

---

## 6. Архитектура HTML-файла

Файл `index.html` состоит из трёх крупных блоков. Ниже — приблизительные маркеры строк:

```
index.html
│
├── Lines   1 –   11  │ <head>
│                     │   - <meta charset>, viewport
│                     │   - Google Fonts (Inter)
│                     │   - Chart.js CDN
│                     │   - jsPDF CDN
│
├── Lines  12 –  800  │ <style>
│                     │   - :root переменные
│                     │   - Layout (header, sidebar, grid)
│                     │   - Компоненты (KPI cards, charts, table, panel)
│                     │   - Зоны риска (.zone-low, .zone-mod, .zone-high)
│                     │   - Адаптивность
│
├── Lines 800 – 1100  │ <body>
│                     │   - Шапка (header) с заголовком и кнопкой Reset
│                     │   - Боковая панель фильтров (.filter-sidebar)
│                     │   - KPI-карточки (.kpi-cards)
│                     │   - Блок с тремя чартами (.charts-grid)
│                     │   - Таблица с пагинацией (.data-table)
│                     │   - Summary-панель (.summary-panel, slide-in справа)
│
└── Lines 1100 –  end │ <script>
    │
    ├── ~Line  347    │   // === DATA SOURCE
    │                 │   const RAW_DATA = [ ... ];   // ~1 МБ inline JSON
    │
    ├── ~Line  547    │   // === KPI CALCULATIONS
    │                 │   Fields Scouted, Avg PS, Avg WRS
    │
    ├── ~Line  678    │   // === WEED RISK SCORE FORMULA
    │                 │   Вычисление WRS в updateChart2()
    │
    ├── ~Line 1302    │   _pdfData = { ... }
    │                 │   Сохранение данных поля для PDF-экспорта
    │
    └── ~Line 1392    │   // === PDF EXPORT
                      │   exportFieldPDF() — генерация и скачивание PDF
```

---

## 7. Ключевые JavaScript-функции

### 7.1 `applyFilters()`

```javascript
// Читает состояние всех чекбоксов фильтров
// Фильтрует RAW_DATA → записывает результат в глобальный массив filteredData
// Вызывает все функции обновления UI
function applyFilters() {
    // ... читает выбранные Farm, Year, Field, Weed
    filteredData = RAW_DATA.filter(r => {
        // логика фильтрации
    });
    updateKPIs();
    updateChart1();
    updateChart2();
    updateChart3();
    updateTable();
}
```

**Роль:** центральная точка обновления всего дашборда. Вызывается при любом изменении фильтров.

---

### 7.2 `updateKPIs()`

Вычисляет и отображает три KPI-карточки:
- **Fields Scouted** — `new Set(filteredData.map(r => r.f)).size`
- **Avg Pressure Score** — среднее `ps` по `filteredData`
- **Avg WRS** — средний WeedRiskScore по всем полям (содержит копию WRS-формулы)

> **КРИТИЧНО:** содержит полную реализацию WRS-формулы. Дублируется в `updateChart2()`.

---

### 7.3 `updateChart1()`

**Тип:** горизонтальная гистограмма  
**Данные:** Avg Pressure Score по видам сорняков (топ-20)  
**Экземпляр:** `chart1Instance`

```javascript
function updateChart1() {
    if (chart1Instance) chart1Instance.destroy(); // ОБЯЗАТЕЛЬНО перед пересозданием
    // ... вычисление агрегатов
    chart1Instance = new Chart(ctx, { type: 'bar', ... });
}
```

---

### 7.4 `updateChart2()`

**Тип:** вертикальная гистограмма  
**Данные:** WeedRiskScore по полям (топ-30)  
**Экземпляр:** `chart2Instance`  
**Интерактивность:** клик на столбец → вызов `showFieldSummary(fieldName)`

> **КРИТИЧНО:** Содержит вторую копию WRS-формулы. При изменении логики — обновлять здесь тоже.

```javascript
// Обработчик клика на Chart2
onClick: (event, elements) => {
    if (elements.length > 0) {
        const fieldName = labels[elements[0].index];
        showFieldSummary(fieldName);
    }
}
```

---

### 7.5 `updateChart3()`

**Тип:** сгруппированная горизонтальная гистограмма  
**Данные:** Avg PS по полям, разбито по WeedClass (Broadleaf / Grass), топ-25  
**Экземпляр:** `chart3Instance`

---

### 7.6 `updateTable()`

**Назначение:** отображает таблицу сырых записей из `filteredData`  
**Возможности:** пагинация, сортировка по столбцам

---

### 7.7 `showFieldSummary(fieldName)`

**Назначение:** открывает правую slide-in панель с полным анализом поля

Выполняет:
1. Фильтрует `filteredData` по `fieldName`
2. Вычисляет все метрики поля (WRS, avgPS, список сорняков, тренды по годам)
3. Вызывает `generateVerdict(...)` для генерации агрономической оценки
4. Заполняет `_pdfData` — глобальный объект для PDF-экспорта
5. Добавляет CSS-класс `.open` к панели (запускает CSS-анимацию)

```javascript
function showFieldSummary(fieldName) {
    const fieldRecords = filteredData.filter(r => r.f === fieldName);
    // ... вычисления
    _pdfData = {
        fieldName, farm, area, years, crops, scoutedBy,
        wrs, avgPS, topWeeds, yearTrend, verdict
    };
    summaryPanel.classList.add('open');
}
```

---

### 7.8 `generateVerdict(...)`

**Назначение:** автоматически генерирует текстовую агрономическую оценку поля на английском языке  
**Возвращает:** HTML-строку (используется в панели и в PDF после удаления тегов)

```javascript
// Использование в панели:
verdictEl.innerHTML = generateVerdict(wrs, topWeeds, yearTrend);

// Использование в PDF (strip HTML tags):
const verdictText = generateVerdict(...).replace(/<[^>]+>/g, '');
```

---

### 7.9 `exportFieldPDF()`

**Назначение:** генерирует и скачивает PDF-отчёт по текущему полю  
**Источник данных:** глобальная переменная `_pdfData`  
**Библиотека:** `window.jspdf.jsPDF`

Подробнее — в разделе [10. Экспорт в PDF](#10-экспорт-в-pdf).

---

### 7.10 `closeSummary()`

```javascript
function closeSummary() {
    summaryPanel.classList.remove('open');
}
```

---

### 7.11 `buildFilters()`

**Назначение:** при инициализации страницы заполняет все четыре фильтра (Farm, Year, Field, Weed) динамически из `RAW_DATA`  
**Тип элементов:** multi-select выпадающие списки с чекбоксами и строкой поиска

---

## 8. Архитектура CSS

### 8.1 CSS Custom Properties

Все ключевые цвета и отступы объявлены как переменные в `:root`:

```css
:root {
    --color-bg: #f0f4f8;
    --color-header: #1e293b;
    --color-primary: #3b82f6;
    --color-sidebar-bg: #ffffff;
    --color-card-bg: #ffffff;
    --color-border: #e2e8f0;
    --color-text: #1e293b;
    --color-text-muted: #64748b;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    /* и другие */
}
```

### 8.2 Layout

```
┌─────────────────────────────────────────────────────┐
│                    <header>                         │  ← background: #1e293b (тёмный)
├───────────┬─────────────────────────────────────────┤
│           │  KPI Cards (flex row)                   │
│  Filter   ├─────────────────────────────────────────┤
│  Sidebar  │  Charts Grid (CSS Grid, 3 columns)      │
│  (fixed   ├─────────────────────────────────────────┤
│  width)   │  Data Table (paginated)                 │
└───────────┴─────────────────────────────────────────┘
                                              ┌─────────┐
                                              │ Summary │  ← position: fixed; right: 0
                                              │  Panel  │     slide-in из правого края
                                              └─────────┘
```

### 8.3 Ключевые CSS-классы

| Класс / Селектор | Описание |
|---|---|
| `.filter-sidebar` | Левая боковая панель с фильтрами, фиксированная ширина, `overflow-y: scroll` |
| `.kpi-cards` | Flex-контейнер для KPI-карточек |
| `.charts-grid` | CSS Grid, 3 колонки для трёх чартов |
| `.summary-panel` | Правая панель анализа поля, `position: fixed; right: 0` |
| `.summary-panel.open` | Состояние открытой панели: `transform: translateX(0)` |
| `.zone-low` | Жёлтая заливка — WRS 0–30 (Low risk) |
| `.zone-mod` | Оранжевая заливка — WRS 30–60 (Moderate risk) |
| `.zone-high` | Красная заливка — WRS 60–100 (High risk) |
| `.export-pdf-btn` | Кнопка экспорта PDF в шапке summary-панели |

### 8.4 Анимация summary-панели

```css
.summary-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 480px;
    height: 100vh;
    transform: translateX(100%);       /* скрыта за правым краем */
    transition: transform 0.3s ease;
    z-index: 1000;
}

.summary-panel.open {
    transform: translateX(0);          /* выдвигается на экран */
}
```

---

## 9. Фильтры

### Четыре фильтра

| Фильтр | Поле данных | Особенности |
|---|---|---|
| Farm | `fm` | Multi-select, чекбоксы |
| Year | `yr` | Multi-select, чекбоксы |
| Field | `f` | Multi-select, чекбоксы + **строка поиска** |
| Weed | `w` | Multi-select, чекбоксы + **строка поиска** |

### Логика фильтрации

```javascript
// Пустой выбор (ничего не отмечено) = показать ВСЕ данные
const farmFilter    = getSelectedValues('farm-filter');    // [] = all
const yearFilter    = getSelectedValues('year-filter');
const fieldFilter   = getSelectedValues('field-filter');
const weedFilter    = getSelectedValues('weed-filter');

filteredData = RAW_DATA.filter(r =>
    (farmFilter.length  === 0 || farmFilter.includes(r.fm)) &&
    (yearFilter.length  === 0 || yearFilter.includes(r.yr)) &&
    (fieldFilter.length === 0 || fieldFilter.includes(r.f)) &&
    (weedFilter.length  === 0 || weedFilter.includes(r.w))
);
```

### Кнопка Reset

```html
<button onclick="resetAllFilters()">Reset All Filters</button>
```

`resetAllFilters()` снимает все чекбоксы и вызывает `applyFilters()` — дашборд возвращается к полному датасету.

---

## 10. Экспорт в PDF

### Расположение кнопки

```html
<!-- В шапке summary-панели, рядом с кнопкой закрытия ✕ -->
<div class="summary-panel-header">
    <h2>Field Summary</h2>
    <button class="export-pdf-btn" onclick="exportFieldPDF()">Export PDF</button>
    <button onclick="closeSummary()">✕</button>
</div>
```

### Инициализация jsPDF

```javascript
function exportFieldPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
    // ...
}
```

### Содержание PDF-отчёта

1. **Шапка:** название поля, название фермы
2. **Метаданные:** площадь (акры), диапазон лет, культуры, агрономы
3. **KPI-карточки:** Fields Scouted, Avg PS, WRS
4. **Бейдж риска:** Low / Moderate / High (с цветовой индикацией)
5. **Топ-10 сорняков:** таблица с мини-барами (пропорциональные полосы)
6. **Тренд по годам:** бары WRS/PS по каждому году
7. **Агрономическая оценка:** текст из `generateVerdict()` (HTML-теги удалены)
8. **Примечание о формуле WRS:** описание методологии
9. **Футер:** нумерация страниц

### Источник данных для PDF

```javascript
// _pdfData заполняется в showFieldSummary() при открытии панели
let _pdfData = null;

function showFieldSummary(fieldName) {
    // ... вычисления ...
    _pdfData = {
        fieldName,
        farm,
        area,
        years,       // массив уникальных годов
        crops,       // массив уникальных культур
        scoutedBy,   // массив агрономов
        wrs,         // число 0-100
        avgPS,       // среднее давление
        topWeeds,    // топ-10 сорняков [{name, avgPS, weedClass}]
        yearTrend,   // [{year, wrs, avgPS}]
        verdict      // HTML-строка агрономической оценки
    };
}
```

### Имя выходного файла

```javascript
const dateStr = new Date().toISOString().slice(0, 10); // "YYYY-MM-DD"
const safeName = _pdfData.fieldName.replace(/[^a-zA-Z0-9]/g, '_');
doc.save(`WeedReport_${safeName}_${dateStr}.pdf`);
```

### Формат: A4 Portrait

```javascript
const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'   // 210 × 297 мм
});
```

---

## 11. Добавление новых данных

### Процесс обновления данных

1. Открыть `DataScoutGGDL.xlsx`, добавить строки той же структуры (те же колонки).
2. Запустить Python-скрипт экстракции (или вручную добавить JSON-объекты в массив `RAW_DATA` внутри `index.html`).
3. **Изменений в коде не требуется** — все фильтры и графики строятся динамически из данных через `buildFilters()`.

### Структура новой записи (для ручного добавления)

```json
{
  "fi": "NEW_FIELD_001",
  "w":  "Wild Oat",
  "wc": "Grass",
  "pr": "Moderate",
  "f":  "New Field Name",
  "fm": "Farm Name",
  "ar": 250.0,
  "cr": "Canola",
  "sb": "John Smith",
  "yr": 2025,
  "sd": "2025-07-20",
  "ps": 3
}
```

### Важные ограничения при добавлении данных

- Значения `wc` должны быть строго `"Broadleaf"` или `"Grass"` (Chart3 группирует по этому полю)
- Значения `ps` должны быть целым числом от 1 до 6
- Формат `sd` — строго `"YYYY-MM-DD"`
- Строки с `w` = `"Notes"`, `"Additional"` и с `yr` = `1900` **исключаются** из данных при очистке

---

## 12. Известные проблемы и примечания

### Проблема 1: Дублирующиеся поля с пробелом в имени

- В исходном Excel поле `"Whits"` и `"Whits "` (с пробелом в конце) — это фактически одно поле, но JS воспринимает их как два разных.
- **Следствие:** Power BI показывает **144 поля**, наш дашборд — **143**.
- **Источник:** проблема качества данных в исходном файле Excel.
- **Решение:** при необходимости добавить `.trim()` при загрузке данных: `r.f = r.f.trim()`.

### Проблема 2: Незначительное расхождение WRS с Power BI

- Наш дашборд использует **локальный знаменатель** (уникальные сорняки на конкретном поле).
- Power BI DAX использует **глобальный контекст** фильтрации.
- **Следствие:** расхождение ~3.7 пунктов для некоторых полей.
- **Вывод:** локальный метод агрономически корректнее, так как WRS рассчитывается относительно разнообразия сорняков именно на данном поле.

### Примечание 3: Деструкция экземпляров Chart.js

Перед каждым пересозданием чарта необходимо вызывать `.destroy()`, иначе Chart.js выдаёт ошибку "Canvas is already in use":

```javascript
if (chart1Instance) chart1Instance.destroy();
chart1Instance = new Chart(ctx, config);
```

### Примечание 4: `_pdfData` может быть null

`exportFieldPDF()` следует вызывать только после открытия summary-панели — иначе `_pdfData` будет `null`. В коде должна быть защита:

```javascript
function exportFieldPDF() {
    if (!_pdfData) {
        console.warn('No field selected for PDF export');
        return;
    }
    // ...
}
```

---

## 13. Что Codex должен знать перед редактированием

### Правило 1: Не трогать `RAW_DATA`

Массив `RAW_DATA` — это ~1 МБ встроенного JSON (~6 269 объектов). **Не нужно его регенерировать, пересчитывать или воспроизводить.** Ссылайтесь на него как на источник данных. Вносить изменения только в код вокруг него.

### Правило 2: WRS-формула присутствует в двух местах

WRS-логика дублирована:
- `updateKPIs()` — для вычисления среднего WRS по всем полям (KPI-карточка)
- `updateChart2()` — для вычисления WRS каждого поля (данные для графика)

**При любом изменении формулы — обновлять оба места.**

### Правило 3: Уничтожение экземпляров Chart.js

Перед пересозданием любого чарта:

```javascript
// ОБЯЗАТЕЛЬНО
if (chart1Instance) chart1Instance.destroy();
if (chart2Instance) chart2Instance.destroy();
if (chart3Instance) chart3Instance.destroy();
```

Пропуск `.destroy()` приводит к ошибке рендера и утечке памяти.

### Правило 4: `filteredData` — глобальный массив

Все функции обновления (`updateKPIs`, `updateChart1`, `updateChart2`, `updateChart3`, `updateTable`) читают данные из **одного глобального источника** — `filteredData`. Его обновляет только `applyFilters()`.

```javascript
let filteredData = []; // глобальный — не объявлять внутри функций
```

### Правило 5: `_pdfData` заполняется только при открытии панели

```javascript
let _pdfData = null; // глобальный
// Заполняется в showFieldSummary(), читается в exportFieldPDF()
```

Никогда не вызывать `exportFieldPDF()` без предварительного открытия summary-панели.

### Правило 6: `generateVerdict()` возвращает HTML

```javascript
// Для отображения в панели — напрямую:
verdictEl.innerHTML = generateVerdict(wrs, topWeeds, yearTrend);

// Для PDF (нужен plain text) — удалить теги:
const verdictText = generateVerdict(wrs, topWeeds, yearTrend)
    .replace(/<[^>]+>/g, '');
```

### Правило 7: Chart.js 4.x — breaking changes

Используется Chart.js **4.4.0** (не 3.x). API конфигурации графиков изменился. Примеры из интернета для версии 3.x могут не работать:

```javascript
// Chart.js 4.x — правильно:
scales: {
    x: { ... },
    y: { ... }
}

// Chart.js 3.x — устаревший синтаксис (НЕ использовать):
scales: {
    xAxes: [{ ... }],  // ❌ не работает в 4.x
    yAxes: [{ ... }]   // ❌ не работает в 4.x
}
```

### Правило 8: jsPDF — правильное обращение к классу

```javascript
// Правильно (UMD-сборка через CDN):
const { jsPDF } = window.jspdf;
const doc = new jsPDF({ ... });

// Неправильно:
const doc = new jsPDF({ ... }); // ❌ jsPDF не глобальный без деструктуризации
```

---

## Быстрый справочник

### Глобальные переменные

| Переменная | Тип | Назначение |
|---|---|---|
| `RAW_DATA` | `Array` | Все данные (~6 269 записей), не изменяется |
| `filteredData` | `Array` | Текущий отфильтрованный датасет |
| `chart1Instance` | `Chart` | Экземпляр Chart.js для Chart 1 |
| `chart2Instance` | `Chart` | Экземпляр Chart.js для Chart 2 |
| `chart3Instance` | `Chart` | Экземпляр Chart.js для Chart 3 |
| `_pdfData` | `Object\|null` | Данные текущего поля для PDF-экспорта |

### Порядок вызова функций при загрузке страницы

```javascript
document.addEventListener('DOMContentLoaded', () => {
    buildFilters();   // 1. Заполняет фильтры из RAW_DATA
    applyFilters();   // 2. Применяет фильтры (все пустые → все данные)
                      //    → updateKPIs(), updateChart1/2/3(), updateTable()
});
```

### Порядок вызова при клике на поле в Chart2

```
onClick → showFieldSummary(fieldName)
            → вычисления метрик
            → generateVerdict(...)
            → заполнение _pdfData
            → summaryPanel.classList.add('open')
                → [пользователь видит панель]
                → [при клике "Export PDF"] → exportFieldPDF()
                    → читает _pdfData
                    → генерирует A4 PDF
                    → doc.save("WeedReport_...")
```

---

*Документ сгенерирован: 2026-04-01. Версия проекта: 1.0.*  
*Для вопросов по логике данных — обращаться к `DataScoutGGDL.xlsx` и `data_compact.json`.*
