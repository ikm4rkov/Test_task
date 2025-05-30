# Генератор отчетов по CSV-данным сотрудников

##  Описание

Скрипт `main.py` на Python обрабатывает один или несколько CSV-файлов с информацией о сотрудниках и формирует текстовые отчёты, аггрегированные по отделам.

### Поддерживаемые форматы отчетов:

- `--report payout`  
  Вычисляет выплату каждому сотруднику как `hours_worked * rate`.  
  Отображает таблицу с именем, часами, ставкой и итоговой выплатой.

- `--report mean_rate_department`  
  Вычисляет среднюю ставку оплаты по каждому отделу.

---

## Требования к CSV-файлам

- Разделитель: **запятая** `,`
- Обязательные колонки: `id`, `email`, `name`, `department`, `hours_worked`
- Одна из колонок для ставки оплаты: `hourly_rate`, `rate` или `salary`
- Список альтернативных заголовков для ставки оплаты может быт расширен
- Порядок колонок не имеет значения
- Отрицательные значения, пустые или некорректные строки — игнорируются

---

## Примеры запуска

```bash
python main.py generic_tests/data1.csv generic_tests/data2.csv generic_tests/data3.csv --report payout
python main.py generic_tests/data1.csv generic_tests/data2.csv generic_tests/data3.csv --report mean_rate_department
pytest --cov=main pytest_tests/
```
## Стурктура репозитория
```bash
├── main.py                # Основной скрипт для формирования отчетов
├── testing.py             # Скрипт для запуска всех тестов
├── README.md              # Описание проекта
│
├── generic_test/          # Предложенные для тестов данные и скриншоты запусков
│   ├── data1.csv
│   ├── data2.csv
│   ├── data3.csv
│   ├── example_mean.PNG
│   ├── example_payout.PNG
│   └── example_test_coverage.PNG
│
└── pytest_tests/          # Расширенные и нагрузочные тесты на pytest
    └── test_validation.py
```
## Установка
* Встроенные библиотеки Python3: argparse, os, sys, collections.
* Для тестирования использовалась библиотеки pytest и pytest-cov
```bash
pip install pytest
```
### Авторство
Марков Иван, 30.05.2025.