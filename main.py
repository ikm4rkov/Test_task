"""
Генератор отчетов по CSV

Скрипт обрабатывает один или несколько CSV-файлов с данными о работе сотрудников и их оплате,
и формирует текстовые отчеты, сгруппированные по отделам.

Поддерживаемые типы отчетов через опцию --report:
- payout: Вычисляет общую выплату (hours_worked * rate) на сотрудника, сгруппированную по отделам.
- mean_rate_department: Вычисляет среднюю часовую ставку для каждого отдела по всем файлам.

Предполагается, что все CSV-файлы используют запятую (`,`) как разделитель и имеют фиксированный набор столбцов (необязательно упорядоченный):
    id, email, name, department, hours_worked, [hourly_rate | rate | salary]

Некорректные строки (например, с пропущенными полями, недопустимыми значениями, отрицательными числами) пропускаются.

Пример использования:
    python main.py generic_tests/data1.csv generic_tests/data2.csv generic_tests/data3.csv --report mean_rate_department
    python main.py generic_tests/data1.csv generic_tests/data2.csv generic_tests/data3.csv --report payout
"""

import argparse
import os
import sys
from collections import defaultdict
from typing import List, Dict

# Константы
REQUIRED_COLUMNS = ['id', 'email', 'name', 'department', 'hours_worked']
RATE_COLUMNS = {'hourly_rate', 'rate', 'salary'}
CSV_SEPARATOR = ','


def parse_arguments() -> argparse.Namespace:
    """
    Обрабатывает аргументы командной строки.

    Возвращает:
        Namespace с распознанными аргументами.
    """
    parser = argparse.ArgumentParser(
        description="Создание отчетов по выплатам или ставкам на основе CSV-файлов."
    )
    parser.add_argument(
        'files',
        metavar='file',
        type=str,
        nargs='+',
        help='CSV-файлы с данными сотрудников'
    )
    parser.add_argument(
        '--report',
        choices=['payout', 'mean_rate_department'],
        required=True,
        help='Тип отчета для генерации'
    )
    return parser.parse_args()


def form_records(rows: List[Dict[str, str]], rate_column: str) -> List[Dict[str, object]]:
    """
    Формирует и валидирует записи из исходных строк CSV.

    Аргументы:
        rows: Список строк как словарей (заголовок -> значение)
        rate_column: Имя столбца с почасовой ставкой

    Возвращает:
        Список проверенных записей с расчетом выплат
    """
    records = []
    hours_list = []
    payouts = []

    for line_number, parts in enumerate(rows, 2):
        try:
            name = parts['name'].strip()
            department = parts['department'].strip()
            hours = float(parts['hours_worked'])
            rate = float(parts[rate_column])
        except (ValueError, KeyError):
            print(f"Строка {line_number} содержит некорректные данные. Пропуск.")
            continue

        if not name or not department or hours < 0 or rate < 0:
            continue

        payout = hours * rate
        hours_list.append(hours)
        payouts.append(payout)

        records.append({
            'name': name,
            'department': department,
            'hours': hours,
            'rate': rate,
            'payout': payout
        })

    # Пример других метрик для потенциального расширения функционала
    if payouts:
        mean_payout = sum(payouts) / len(payouts)
        max_hours = max(hours_list)
        _ = mean_payout, max_hours

    return records


def read_and_validate_file(filepath: str, valid_rate_keys: set[str]) -> List[Dict[str, object]]:
    """
    Читает CSV-файл и проверяет его структуру и данные.

    Аргументы:
        filepath: Путь к CSV-файлу
        valid_rate_keys: Допустимые имена столбцов с оплатой

    Возвращает:
        Список валидированных записей
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return []

    header = lines[0].strip().split(CSV_SEPARATOR)

    for col in REQUIRED_COLUMNS:
        if col not in header:
            raise ValueError(f"Отсутствует обязательный столбец '{col}' в файле {filepath}")

    rate_column = next((col for col in valid_rate_keys if col in header), None)
    if not rate_column:
        raise ValueError(f"Отсутствует столбец со ставкой из набора {valid_rate_keys} в файле {filepath}")

    mapped_rows = []
    for line_number, line in enumerate(lines[1:], 2):
        parts = line.strip().split(CSV_SEPARATOR)
        if len(parts) != len(header):
            print(f"Пропуск строки {line_number} в {filepath}: количество столбцов не совпадает.")
            continue
        mapped = dict(zip(header, parts))
        mapped_rows.append(mapped)

    return form_records(mapped_rows, rate_column)


def generate_payout_report(records: List[Dict[str, object]]) -> None:
    """
    Генерирует и выводит отчет по выплатам, сгруппированный по отделам.

    Аргументы:
        records: Список валидированных записей
    """
    grouped = defaultdict(list)
    for rec in records:
        grouped[rec['department']].append(rec)

    columns = ['name', 'hours', 'rate', 'payout']

    for dept, recs in grouped.items():
        print(f"\n{dept}")

        col_widths = {
            col: max(len(col), *(len(f"{r[col]:.0f}" if isinstance(r[col], float) else str(r[col]))
                                for r in recs))
            for col in columns
        }

        header = ""
        for i, col in enumerate(columns):
            tab = "\t" if i < len(columns) - 1 else ""
            header += f"{col:<{col_widths[col]}}" + tab
        print(header)

        dash_line = ""
        for i, col in enumerate(columns):
            tab = "\t" if i < len(columns) - 1 else ""
            dash_line += "-" * col_widths[col] + tab
        print(dash_line)

        for r in recs:
            line = ""
            for i, col in enumerate(columns):
                value = f"${int(r[col])}" if col == 'payout' else f"{r[col]}"
                tab = "\t" if i < len(columns) - 1 else ""
                line += f"{value:<{col_widths[col]}}" + tab
            print(line)


def generate_mean_rate_report(records: List[Dict[str, object]]) -> None:
    """
    Генерирует и выводит отчет со средней ставкой по отделам.

    Аргументы:
        records: Список валидированных записей
    """
    rate_data = defaultdict(list)
    for rec in records:
        rate_data[rec['department']].append(rec['rate'])

    print("\nDepartment\tMean Rate")
    print("----------\t---------")
    for dept, rates in rate_data.items():
        mean = sum(rates) / len(rates) if rates else 0
        print(f"{dept:<10}\t{mean:.2f}")


def main() -> None:
    """
    Основная логика программы:
    - Обрабатывает аргументы командной строки;
    - Загружает и валидирует CSV-файлы;
    - Генерирует отчет в зависимости от заданного режима.
    """
    args = parse_arguments()

    all_records = []
    for filepath in args.files:
        try:
            records = read_and_validate_file(filepath, RATE_COLUMNS)
            all_records.extend(records)
        except Exception as e:
            print(f"Ошибка при обработке файла {filepath}: {e}", file=sys.stderr)

    if args.report == 'payout':
        generate_payout_report(all_records)
    elif args.report == 'mean_rate_department':
        generate_mean_rate_report(all_records)
    else:
        print("Тип отчета не реализован. Выберите один из: 'payout', 'mean_rate_department'.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
