import pytest
import sys
import os
import io
from contextlib import redirect_stdout

# Добавляем родительскую директорию в путь, чтобы можно было импортировать main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import (
    read_and_validate_file,
    form_records,
    generate_payout_report,
    generate_mean_rate_report,
    RATE_COLUMNS
)


def test_file_with_column_mismatch(tmp_path):
    """
    Проверяет, что строка с неполным количеством столбцов, чем в заголовке, пропускается.
    """
    file = tmp_path / "mismatch.csv"
    file.write_text(
        "id,email,name,department,hours_worked,rate\n"
        "1,test,Alice,Marketing,40\n"  # Отсутствует значение rate
        "2,test,Bob,Sales,35,55"
    )
    records = read_and_validate_file(str(file), RATE_COLUMNS)
    assert len(records) == 1
    assert records[0]['name'] == 'Bob'


def test_file_with_only_header(tmp_path):
    """
    Проверяет, что файл с заголовком, но без данных возвращает пустой список.
    """
    file = tmp_path / "header_only.csv"
    file.write_text("id,email,name,department,hours_worked,rate\n")
    records = read_and_validate_file(str(file), RATE_COLUMNS)
    assert records == []


def test_empty_file(tmp_path):
    """
    Проверяет поведение при полностью пустом файле.
    """
    file = tmp_path / "empty.csv"
    file.write_text("")
    records = read_and_validate_file(str(file), RATE_COLUMNS)
    assert records == []


def test_generate_payout_report_output_formatting(capsys):
    """
    Проверяет форматирование вывода отчета о выплатах.
    """
    records = [
        {'name': 'Alice', 'department': 'HR', 'hours': 40, 'rate': 50, 'payout': 2000},
        {'name': 'Bob', 'department': 'HR', 'hours': 35, 'rate': 60, 'payout': 2100}
    ]
    generate_payout_report(records)
    captured = capsys.readouterr()
    assert "HR" in captured.out
    assert "Alice" in captured.out
    assert "$2000" in captured.out
    assert "$2100" in captured.out


def test_generate_mean_rate_report_output(capsys):
    """
    Проверяет корректность расчета и вывода среднего значения ставки по отделам.
    """
    records = [
        {'name': 'Alice', 'department': 'HR', 'hours': 40, 'rate': 50, 'payout': 2000},
        {'name': 'Bob', 'department': 'HR', 'hours': 35, 'rate': 60, 'payout': 2100},
        {'name': 'Charlie', 'department': 'Sales', 'hours': 38, 'rate': 70, 'payout': 2660}
    ]
    generate_mean_rate_report(records)
    captured = capsys.readouterr()
    assert "HR" in captured.out
    assert "Sales" in captured.out
    assert "55.00" in captured.out
    assert "70.00" in captured.out


from main import main as main_func


def test_main_unknown_report(monkeypatch, capsys, tmp_path):
    """
    Проверяет поведение при передаче неподдерживаемого типа отчета.
    Ожидается завершение программы с ошибкой и вывод сообщения.
    """
    file = tmp_path / "valid.csv"
    file.write_text("id,email,name,department,hours_worked,rate\n1,test,Alice,HR,40,50")

    monkeypatch.setattr(sys, 'argv', ['main.py', str(file), '--report', 'unsupported'])
    with pytest.raises(SystemExit):
        main_func()
    assert "Unimplemented report" in capsys.readouterr().err
