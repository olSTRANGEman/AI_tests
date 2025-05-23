import subprocess
import json
import re
import os
import tempfile
from collections import defaultdict
from typing import List, Set, Tuple, Dict
import ast
import requests
import yaml
import html
from io import StringIO
from radon.visitors import ComplexityVisitor
from pylint.lint import Run
from pylint.reporters.text import TextReporter

# pip install radon pylint requests pyyaml pytest-json-report

# Файл с тестами (обязательно .py)
TEST_FILEs = ["sub_test/subtest.py"]

# Базовый URL для извлечения эндпоинтов
BASE_URL = "https://petstore.swagger.io/v2"

# Пути спецификации
ENDPOINTS = [
    "/swagger.json",
    "/openapi.json",
    "/swagger.yaml",
    "/openapi.yaml",
    "/v2/swagger.json",
]

ACCEPTABLE_CODES = [400, 401, 403, 404, 405, 409, 415, 422]

def run_pytest_json(test_name: str = None, report_file: str = "report.json") -> dict:
    cmd = [
        "pytest",
        TEST_FILE if not test_name else f"{TEST_FILE}::{test_name}",
        "--json-report",
        f"--json-report-file={report_file}",
        "--maxfail=0"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        print(f"❌ pytest завершился с кодом {proc.returncode}")
        print(proc.stderr)
        return {}
    try:
        with open(report_file, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Не найден {report_file}")
        print("Проверьте, установлен ли плагин pytest-json-report: pip install pytest-json-report")
        return {}


def extract_longrepr_text(lr) -> str:
    if isinstance(lr, str):
        return html.unescape(lr)
    elif isinstance(lr, dict):
        return html.unescape(lr.get("message", "") or lr.get("repr", "") or str(lr))
    elif isinstance(lr, list):
        return "\n".join(str(item) for item in lr if isinstance(item, str))
    else:
        return str(lr)
    

def get_pass_fail_rate_firs(report: dict) -> Tuple[int, int]:
    """
    Выводит сводные метрики по тестам:
     - total, corrected_cnt/%, suspicious_cnt/% 
     - Adjusted Pass Rate
    Возвращает (passed, failed).
    """
    tests = report.get("tests", [])
    total = len(tests)

    adjusted = []
    suspicious = []

    for t in tests:
        if t.get("outcome") != "passed":
            text = extract_longrepr_text(t["call"].get("longrepr", ""))
            nid = t["nodeid"]

            # 1) assert 200 == CODE
            if any(re.search(rf"assert\s+200\s+==\s+{c}", text) for c in ACCEPTABLE_CODES):
                adjusted.append(nid)
                continue

            # 2) assert 200 in [C1, C2, ...]
            m = re.search(r"assert\s+200\s+in\s+[\[\(]([^\]\)]+)[\]\)]", text)
            if m:
                try:
                    codes = [int(c.strip()) for c in m.group(1).split(",")]
                    if any(c in ACCEPTABLE_CODES for c in codes):
                        adjusted.append(nid)
                        continue
                except ValueError:
                    pass

            # 3) assert 4xx == 200
            if re.search(r"assert\s+4\d\d\s+==\s+200", text):
                suspicious.append(nid)

    corrected_cnt   = len(adjusted)
    suspicious_cnt  = len(suspicious)
    passed          = sum(1 for t in tests if t.get("outcome") == "passed" or t["nodeid"] in adjusted)
    failed          = total - passed
    total_nonzero   = total or 1

    print("\n📊 Результаты get_pass_fail_rate:")
    print(f"🎯 Pass Rate: {passed}/{total} ({passed/total_nonzero:.1%})")

    return passed, failed

def get_pass_fail_rate_sec(report: dict) -> Tuple[int, int]:
    """
    Выводит сводные метрики по тестам:
     - total, corrected_cnt/%, suspicious_cnt/% 
     - Adjusted Pass Rate
    Возвращает (passed, failed).
    """
    tests = report.get("tests", [])
    total = len(tests)

    adjusted = []
    suspicious = []

    for t in tests:
        if t.get("outcome") != "passed":
            text = extract_longrepr_text(t["call"].get("longrepr", ""))
            nid = t["nodeid"]

            # 1) assert 200 == CODE
            if any(re.search(rf"assert\s+200\s+==\s+{c}", text) for c in ACCEPTABLE_CODES):
                adjusted.append(nid)
                continue

            # 2) assert 200 in [C1, C2, ...]
            m = re.search(r"assert\s+200\s+in\s+[\[\(]([^\]\)]+)[\]\)]", text)
            if m:
                try:
                    codes = [int(c.strip()) for c in m.group(1).split(",")]
                    if any(c in ACCEPTABLE_CODES for c in codes):
                        adjusted.append(nid)
                        continue
                except ValueError:
                    pass

            # 3) assert 4xx == 200
            if re.search(r"assert\s+4\d\d\s+==\s+200", text):
                suspicious.append(nid)

    corrected_cnt   = len(adjusted)
    suspicious_cnt  = len(suspicious)
    passed          = sum(1 for t in tests if t.get("outcome") == "passed" or t["nodeid"] in adjusted)
    failed          = total - passed
    total_nonzero   = total or 1

    print(f"✔️ Скорректировано (200==4xx / in [...]): {corrected_cnt} ({corrected_cnt/total_nonzero*100:.1f}%)")
    print(f"🟡 Подозрительных (4xx==200): {suspicious_cnt} ({suspicious_cnt/total_nonzero*100:.1f}%)")

    return passed, failed


def print_pass_fail_details(report: dict) -> None:
    """
    Печатает списки:
     - скорректированные тесты (assert 200==4xx и in [...])
     - подозрительные тесты (assert 4xx(500)==200)
    """
    tests = report.get("tests", [])
    adjusted = []
    suspicious = []

    for t in tests:
        if t.get("outcome") != "passed":
            text = extract_longrepr_text(t["call"].get("longrepr", ""))
            nid = t["nodeid"]

            if any(re.search(rf"assert\s+200\s+==\s+{c}", text) for c in ACCEPTABLE_CODES):
                adjusted.append(nid)
                continue
            m = re.search(r"assert\s+200\s+in\s+[\[\(]([^\]\)]+)[\]\)]", text)
            if m:
                try:
                    codes = [int(c.strip()) for c in m.group(1).split(",")]
                    if any(c in ACCEPTABLE_CODES for c in codes):
                        adjusted.append(nid)
                        continue
                except ValueError:
                    pass
            if re.search(r"assert\s+4\d\d\s+==\s+200", text):
                suspicious.append(nid)
            if re.search(r"assert\s+5\d\d\s+==\s+200", text):
                suspicious.append(nid)

    if adjusted:
        print("\n✔️ Список скорректированных тестов:")
        for nid in adjusted:
            print(f"   - {nid}")
    if suspicious:
        print("\n🟡 Список подозрительных тестов:")
        for nid in suspicious:
            print(f"   - {nid}")







def extract_used_endpoints(test_file: str) -> Set[Tuple[str, str]]:
    text = open(test_file, encoding='utf-8').read()

    # 1) Собираем все определения переменных URL
    url_var_pattern = re.compile(
        r'(\w+)\s*=\s*'
        r'(?:f?["\']\{?BASE_URL\}?/([^"\'\?]+)(?:\?[^"\']*)?["\']'
        r'|BASE_URL\s*\+\s*["\']([^"\\?]+)["\'])',
        re.IGNORECASE
    )
    url_vars: Dict[str, str] = {}
    for m in url_var_pattern.finditer(text):
        var = m.group(1)
        raw = m.group(2) or m.group(3)
        url_vars[var] = raw.strip('/')

    # 2) Паттерны прямых вызовов
    direct_patterns = [
        re.compile(
            r'requests\.(get|post|put|delete)\s*\(\s*f?["\']'
            r'(?:\{?BASE_URL\}?/)?([^"\'\?]+?)(?:\?[^"\']*)?["\']\s*(?:,.*)?\)',
            re.IGNORECASE
        ),
        re.compile(
            r'send_request\(\s*["\'](GET|POST|PUT|DELETE)["\']\s*,\s*f?["\']'
            r'(?:\{?BASE_URL\}?/)?([^"\'\?]+)(?:\?[^"\']*)?["\']',
            re.IGNORECASE
        ),
        re.compile(
            r'send_request\(\s*["\'](GET|POST|PUT|DELETE)["\']\s*,\s*'
            r'BASE_URL\s*\+\s*["\']([^"\\?]+)["\']',
            re.IGNORECASE
        ),
    ]
    var_call_pattern = re.compile(
        r'(?:requests\.(get|post|put|delete)|send_request)\s*\(\s*'
        r'(?:["\'](GET|POST|PUT|DELETE)["\']\s*,\s*)?'
        r'(\w+)',
        re.IGNORECASE
    )

    fixed_segments = {
        'pet', 'store', 'order', 'user',
        'findByStatus', 'findByTags',
        'inventory', 'login', 'logout'
    }
    endpoints: Set[Tuple[str, str]] = set()

    # 3) Обработка прямых вызовов
    for pat in direct_patterns:
        for method, raw in pat.findall(text):
            m = method.upper()
            core = raw.strip('/')
            segs = [seg if seg in fixed_segments else '{param}' for seg in core.split('/')]
            endpoints.add((m, '/' + '/'.join(segs)))

    # 4) Обработка вызовов через переменные
    for m1, m2, var in var_call_pattern.findall(text):
        method = (m1 or m2).upper()
        if var in url_vars:
            core = url_vars[var]
            segs = [seg if seg in fixed_segments else '{param}' for seg in core.split('/')]
            endpoints.add((method, '/' + '/'.join(segs)))

    return endpoints


def parse_openapi(spec_data: bytes | str) -> dict:
    if isinstance(spec_data, bytes):
        spec_data = spec_data.decode('utf-8')
    try:
        if spec_data.lstrip().startswith('{'):
            return json.loads(spec_data)
        return yaml.safe_load(spec_data)
    except Exception as e:
        print(f"❌ Ошибка при разборе спецификации: {e}")
        return {}


def get_pass_fail_rate(report: dict) -> Tuple[int, int]:
    tests = report.get("tests", [])
    total = len(tests)

    # Категории для сбора
    adjusted_4xx_from_200 = []       # assert 200 == 4xx или in [...]
    suspicious_4xx_eq_200 = []       # assert 4xx == 200
    all_adjusted = []

    for t in tests:
        if t.get("outcome") != "passed":
            call_data = t.get("call", {})
            raw_longrepr = call_data.get("longrepr", "")
            text = extract_longrepr_text(raw_longrepr)

            matched = False
            nodeid = t["nodeid"]

            # Тип 1: assert 200 == 4xx
            for code in ACCEPTABLE_CODES:
                if re.search(rf"assert\s+200\s+==\s+{code}", text):
                    adjusted_4xx_from_200.append(nodeid)
                    matched = True
                    break

            # Тип 2: assert 200 in [400, 404] или (400, 415)
            if not matched:
                match = re.search(r"assert\s+200\s+in\s+[\[\(]([^\]\)]+)[\]\)]", text)
                if match:
                    codes_str = match.group(1)
                    try:
                        codes = [int(c.strip()) for c in codes_str.split(",")]
                        if any(code in ACCEPTABLE_CODES for code in codes):
                            adjusted_4xx_from_200.append(nodeid)
                            matched = True
                    except ValueError:
                        pass

            # Тип 3: assert 4xx == 200 (подозрительный)
            if not matched:
                match = re.search(r"assert\s+(4\d\d)\s+==\s+200", text)
                if match:
                    suspicious_4xx_eq_200.append(nodeid)

            # Все зачтённые как пройденные
            if matched:
                all_adjusted.append(nodeid)

    # Подсчёт
    passed = sum(1 for t in tests if t.get("outcome") == "passed" or t["nodeid"] in all_adjusted)
    failed = total - passed

    # Отчёт
    print("\n📊 Результаты анализа:")
    print(f"✅ Всего тестов: {total}")
    print(f"✔️ Корректировки (assert 200 == 4xx / in [...]): {len(adjusted_4xx_from_200)} "
          f"({len(adjusted_4xx_from_200) / total * 100:.1f}%)")
    print(f"🟡 Подозрительные (assert 4xx == 200): {len(suspicious_4xx_eq_200)} "
          f"({len(suspicious_4xx_eq_200) / total * 100:.1f}%)")
    print(f"✅ Adjusted Pass Rate: {passed}/{total} ({passed / total:.1%})")

    return passed, failed



def measure_api_coverage(
    used_status_codes: Dict[Tuple[str, str], Set[str]],
    openapi_spec: dict
) -> None:
    """
    Считает, сколько из всех определённых в spec endpoints
    были «частично покрыты» —
      1) либо получили хоть один статус-код (ключи used_status_codes пересекаются с Specification_codes),
      2) либо это «пустые» endpoints (в spec нет реальных response-кодов, только default).

    Выводит:
      🧪 API partly Endpoint Coverage: X/Y (Z%)
    """
    # 1) Собираем из spec все эндпоинты и их реальные коды (без 'default'):
    Specification_codes: Dict[Tuple[str, str], Set[str]] = {}
    for raw_path, methods in openapi_spec.get('paths', {}).items():
        norm = re.sub(r'\{\w+\}', '{param}', raw_path)
        for method, op in methods.items():
            m = method.upper()
            if m not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
                continue
            codes = {
                code for code in op.get('responses', {})
                if code.lower() != 'default'
            }
            Specification_codes[(m, norm)] = codes

    total = len(Specification_codes)

    # 2a) Эндпоинты с реальным покрытием: есть и в used_status_codes, и в Specification_codes
    used_eps = {ep for ep in used_status_codes if ep in Specification_codes and used_status_codes[ep]}

    # 2b) «Пустые» endpoints (только default)
    empty_eps = {ep for ep, codes in Specification_codes.items() if not codes}

    # 3) «Частично покрыты» = union этих двух множеств
    covered_eps = used_eps | empty_eps
    covered = len(covered_eps)

    # 4) Вычисляем процент
    pct = (covered / total * 100) if total else 0.0

    print(f"\n🧪 API partly Endpoint Coverage: {covered}/{total} ({pct:.1f}%)")




def extract_used_status_codes(test_file: str) -> Dict[tuple[str, str], Set[str]]:
    # Читаем файл построчно
    with open(test_file, encoding='utf-8') as f:
        lines = f.read().splitlines()

    # Регулярное выражение для поиска вызовов requests
    call_re = re.compile(
        r'requests\.(get|post|put|delete)\s*\(\s*f?["\']\{BASE_URL\}/([^"\'\?]+?)(?:\?[^"\']*)?["\']',
        re.IGNORECASE
    )
    # Регулярное выражение для поиска утверждений статус-кодов
    assert_re = re.compile(r'assert\s+(?P<var>\w+)\.status_code\s*==\s*(?P<code>\d{3})')

    # Словарь для хранения результатов
    used_status_codes: Dict[tuple[str, str], Set[str]] = {}

    # Фиксированные сегменты пути (не заменяются на {param})
    fixed_segments = {'pet', 'store', 'order', 'user', 'findByStatus', 'uploadImage', 'inventory', 'login', 'logout', 'createWithArray', 'createWithList'}

    # Проходим по строкам файла
    for idx, line in enumerate(lines):
        # Ищем вызов HTTP
        call_match = call_re.search(line)
        if call_match:
            method = call_match.group(1).upper()  # Например, "POST"
            raw_path = call_match.group(2)        # Например, "pet" или "pet/9999"

            # Нормализуем путь
            segs = raw_path.split('/')
            norm_segs = [seg if seg in fixed_segments else '{param}' for seg in segs]
            norm_path = '/' + '/'.join(norm_segs)  # Например, "/pet" или "/pet/{param}"

            # Ищем утверждение в следующей или через одну строке
            for offset in (1, 2):
                if idx + offset < len(lines):
                    assert_match = assert_re.search(lines[idx + offset])
                    if assert_match:
                        code = assert_match.group('code')  # Например, "200"
                        # Добавляем результат в словарь
                        key = (method, norm_path)
                        used_status_codes.setdefault(key, set()).add(code)
                        break  # Нашли утверждение, дальше не ищем

    return used_status_codes



def extract_openapi_responses(spec: dict) -> Dict[Tuple[str, str], Set[str]]:
    responses = {}
    for path, methods in spec.get('paths', {}).items():
        norm_path = re.sub(r'\{\w+\}', '{param}', path)
        for method, op in methods.items():
            method = method.upper()
            if method not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
                continue
            codes = {
                code for code in op.get('responses', {}).keys()
                if code.isdigit()
            }
            responses[(method, norm_path)] = codes
    return responses


def count_tests(test_file: str) -> int:
    """
    Подсчитывает количество тестов в файле (функций, начинающихся с 'def test_').

    Аргументы:
        test_file: Путь к тестовому файлу.

    Возвращает:
        int: Количество тестов.
    """
    try:
        with open(test_file, encoding='utf-8') as f:
            return sum(1 for line in f if line.strip().startswith('def test_'))
    except Exception as e:
        print(f"⚠️ Ошибка при чтении файла тестов: {e}")
        return 1  # Возвращаем 1, чтобы избежать деления на ноль
    
def analyze_unSpecification_status_codes(
    test_file: str,
    openapi_spec: dict
) -> List[Tuple[str, str, str, str]]:
    """
    Печатает только сводную метрику:
      ❗ Процент незаявленных статус-кодов: X / total_tests (Y%)
    Возвращает список unSpecification_cases для детализации.
    """
    Specification = extract_openapi_responses(openapi_spec)
    used     = extract_used_status_codes(test_file)
    total    = count_tests(test_file)

    unSpecification = []
    for (m, path), codes in used.items():
        exp_set = Specification.get((m, path), set())
        for code in codes:
            if code not in exp_set:
                unSpecification.append((m, path, code, ",".join(sorted(exp_set))))

    cnt = len(unSpecification)
    pct = cnt/ (total or 1) * 100
    print(f"❗ Незаявленные статус-коды: {cnt} / {total} ({pct:.1f}%)\n")

    return unSpecification



def analyze_unSpecification_status_det(
    test_file: str,
    openapi_spec: dict
) -> None:
    """
    Детализация для analyze_unSpecification_status_metrics:
      - список незаявленных случаев
    """
    # прямо дублируем логику, без вызова metrics-функции
    Specification = extract_openapi_responses(openapi_spec)
    used     = extract_used_status_codes(test_file)

    unSpecification = []
    for (method, path), codes in used.items():
        exp_set = Specification.get((method, path), set())
        for code in codes:
            if code not in exp_set:
                unSpecification.append((method, path, code, ",".join(sorted(exp_set))))

    if unSpecification:
        print("\n❗ Список незаявленных случаев:")
        for m, path, actual, exp in unSpecification:
            print(f"   - {m} {path}: получили {actual}, ожидали [{exp or '-'}]")



def show_status_code_coverage_sec(
    used_status_codes: Dict[Tuple[str, str], Set[str]],
    openapi_spec: dict
) -> None:
    """
    Среднее покрытие по разделам граф.
    """
    import re

    # Собираем ожидаемые коды по (METHOD, PATH)
    Specification_codes: Dict[Tuple[str, str], List[str]] = {}
    for raw_path, methods in openapi_spec.get('paths', {}).items():
        norm = re.sub(r'\{\w+\}', '{param}', raw_path)
        for http_method, op_obj in methods.items():
            m = http_method.upper()
            if m not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
                continue
            codes = list(op_obj.get('responses', {}).keys())
            Specification_codes[(m, norm)] = sorted(codes)

    # Подготовка строк: сортируем по path
    rows = []
    for (method, path) in sorted(Specification_codes.keys(), key=lambda x: (x[1], x[0])):
        exp_codes = Specification_codes[(method, path)]
        recv = sorted(used_status_codes.get((method, path), []))
        declared = set(exp_codes)
        actual_declared = [code for code in recv if code in declared]
        missing = sorted(declared - set(actual_declared))

        # Обработка случая с единственным default
        if declared == {'default'}:
            coverage_pct = 100.0
            actual_declared = ['default']
            missing = []
        else:
            coverage_pct = (len(actual_declared) / len(declared)) * 100.0 if declared else 0.0

        rows.append({
            'method': method,
            'path': path,
            'Specification': ','.join(exp_codes) or '-',
            'Expected': ','.join(recv) or '-',
            'missing': ','.join(missing) or '-',
            'coverage_pct': coverage_pct,
        })

    # Средние показатели
    avg_pct = sum(r['coverage_pct'] for r in rows) / len(rows) if rows else 0.0
    print(f"\nСредний процент покрытия по endpoint: {avg_pct:.1f}%")

    # Средний процент покрытия по секциям
    section_stats: Dict[str, List[float]] = {}
    for r in rows:
        section = r['path'].split('/')[1] if '/' in r['path'] else r['path']
        section_stats.setdefault(section, []).append(r['coverage_pct'])
    print("Средний процент покрытия по разделам:")
    for sec, pct_list in sorted(section_stats.items()):
        sec_avg = sum(pct_list) / len(pct_list)
        print(f"  - {sec}: {sec_avg:.1f}%")



def show_status_code_coverage(
    used_status_codes: Dict[Tuple[str, str], Set[str]],
    openapi_spec: dict
) -> None:
    """
    Для каждого эндпоинта из openapi_spec сравнивает
    объявленные коды ответов (включая 'default') и те, что реально получили,
    и выводит таблицу с дополнительной статистикой.
    """
    import re

    # Собираем ожидаемые коды по (METHOD, PATH)
    Specification_codes: Dict[Tuple[str, str], List[str]] = {}
    for raw_path, methods in openapi_spec.get('paths', {}).items():
        norm = re.sub(r'\{\w+\}', '{param}', raw_path)
        for http_method, op_obj in methods.items():
            m = http_method.upper()
            if m not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
                continue
            codes = list(op_obj.get('responses', {}).keys())
            Specification_codes[(m, norm)] = sorted(codes)

    # Подготовка строк: сортируем по path
    rows = []
    for (method, path) in sorted(Specification_codes.keys(), key=lambda x: (x[1], x[0])):
        exp_codes = Specification_codes[(method, path)]
        recv = sorted(used_status_codes.get((method, path), []))
        declared = set(exp_codes)
        actual_declared = [code for code in recv if code in declared]
        missing = sorted(declared - set(actual_declared))

        # Обработка случая с единственным default
        if declared == {'default'}:
            coverage_pct = 100.0
            actual_declared = ['default']
            missing = []
        else:
            coverage_pct = (len(actual_declared) / len(declared)) * 100.0 if declared else 0.0

        rows.append({
            'method': method,
            'path': path,
            'Specification': ','.join(exp_codes) or '-',
            'Expected': ','.join(recv) or '-',
            'missing': ','.join(missing) or '-',
            'coverage_pct': coverage_pct,
        })



    # Вычисляем размеры столбцов
    headers = ['METHOD', 'PATH', 'Specification', 'Expected', 'Missing', 'CovPct']
    col_widths = {h: len(h) for h in headers}
    for r in rows:
        col_widths['METHOD'] = max(col_widths['METHOD'], len(r['method']))
        col_widths['PATH'] = max(col_widths['PATH'], len(r['path']))
        col_widths['Specification'] = max(col_widths['Specification'], len(r['Specification']))
        col_widths['Expected'] = max(col_widths['Expected'], len(r['Expected']))
        col_widths['Missing'] = max(col_widths['Missing'], len(r['missing']))
        formatted_pct = f"{r['coverage_pct']:.1f}%"
        col_widths['CovPct'] = max(col_widths['CovPct'], len(formatted_pct))

    # Печатаем заголовок
    header_line = (
        f"{headers[0]:<{col_widths['METHOD']}} | "
        f"{headers[1]:<{col_widths['PATH']}} | "
        f"{headers[2]:<{col_widths['Specification']}} | "
        f"{headers[3]:<{col_widths['Expected']}} | "
        f"{headers[4]:<{col_widths['Missing']}} | "
        f"{headers[5]:>{col_widths['CovPct']}}"
    )
    sep = ' | '.join('-' * col_widths[h] for h in headers)
    print()
    print(header_line)
    print(sep)

    # Печатаем строки
    for r in rows:
        print(
            f"{r['method']:<{col_widths['METHOD']}} | "
            f"{r['path']:<{col_widths['PATH']}} | "
            f"{r['Specification']:<{col_widths['Specification']}} | "
            f"{r['Expected']:<{col_widths['Expected']}} | "
            f"{r['missing']:<{col_widths['Missing']}} | "
            f"{r['coverage_pct']:>{col_widths['CovPct']}.1f}%"
        )




def extract_test_names(test_file: str) -> List[str]:
    names: List[str] = []
    for line in open(test_file, encoding='utf-8'):
        m = re.match(r'\s*def\s+(test_\w+)', line)
        if m:
            names.append(m.group(1))
    return names



def measure_full_status_coverage(
    used_status_codes: Dict[Tuple[str, str], Set[str]],
    openapi_spec: dict
) -> None:
    """
    Считает процент endpoint-ов, у которых получены ВСЕ ожидаемые коды ответов,
    причём:
      - если в спецификации у endpoint-а не было ни одного реального кода (только default),
        он тоже считается полностью покрытым;
      - иначе проверяем, что Specification_codes ⊆ used_status_codes.
    
    Выводит:
      API Endpoint Coverage: X/Y (Z%)
    """
    # 1) Собираем из spec все endpoint-ы + реальные коды (без 'default')
    Specification: Dict[Tuple[str, str], Set[str]] = {}
    for raw_path, methods in openapi_spec.get('paths', {}).items():
        norm = re.sub(r'\{\w+\}', '{param}', raw_path)
        for method, op in methods.items():
            m = method.upper()
            if m not in {'GET','POST','PUT','DELETE','PATCH'}:
                continue
            codes = {
                code for code in op.get('responses', {})
                if code.lower() != 'default'
            }
            Specification[(m, norm)] = codes

    total = len(Specification)  # включает endpoint-ы с пустым Specification

    # 2) Считаем fully covered:
    #    - empty Specification → считаем покрытым
    #    - иначе Specification ⊆ used_status_codes
    fully = 0
    for ep, exp_codes in Specification.items():
        if not exp_codes:
            # в спецификации не было реальных кодов → считаем покрытым
            fully += 1
        else:
            recv = used_status_codes.get(ep, set())
            if exp_codes.issubset(recv):
                fully += 1

    pct = (fully / total * 100) if total else 0.0
    print(f"API Endpoint Coverage: {fully}/{total} ({pct:.1f}%)")





def detect_flaky_tests(test_names: List[str], module_path: str = None, repeat: int = 3) -> List[str]:
    """
    Запускает тесты через pytest несколько раз для выявления флаки-тестов.
    """
    flaky: List[str] = []
    for name in test_names:
        results = []
        for i in range(repeat):
            report_file = f"report_{name}_{i}.json"
            report = run_pytest_json(test_name=name, report_file=report_file)
            tests = report.get("tests", [])
            outcome = tests[0].get("outcome") if tests else "failed"
            results.append(outcome == "passed")
            # Clean up report file
            if os.path.exists(report_file):
                os.remove(report_file)
        if len(set(results)) > 1:
            flaky.append(name)
    print(f"⚠️ Flaky tests: {flaky or ['None']}")
    return flaky


def fetch_spec(base_url: str, paths: List[str]) -> bytes | None:
    for path in paths:
        url = base_url.rstrip('/') + path
        try:
            r = requests.get(url, timeout=5)
            ctype = r.headers.get('Content-Type', '')
            if r.status_code == 200 and ('application/json' in ctype or r.text.lstrip().startswith(('{', 'swagger:'))):
                print(f"✅ Spec found at: {url}")
                return r.content
        except requests.RequestException:
            pass
    print("❌ Spec not found on standard paths.")
    return None


# def calculate_cyclomatic_complexity(path: str) -> int:
#     code = open(path, 'r', encoding='utf-8').read()
#     visitor = ComplexityVisitor()
#     visitor.visit(ast.parse(code))
#     max_c = 0
#     for func in visitor.functions:
#         max_c = max(max_c, func.complexity)
#     print(f" Cyclomatic complexity: {max_c}")
#     return max_c


def analyze_style(path: str) -> float:
    # Перенаправляем весь вывод Pylint в буфер и не показываем его
    buffer = StringIO()
    reporter = TextReporter(buffer)
    run = Run([path, '--score=yes'], reporter=reporter, exit=False)
    score = run.linter.stats.global_note
    print(f"Style Score: {score:.1f}/10")
    return score


if __name__ == "__main__":
    for TEST_FILE in TEST_FILEs:
        print(TEST_FILE)
        # 1) Получаем и разбираем spec
        spec_bytes = fetch_spec(BASE_URL, ENDPOINTS)
        parsed = parse_openapi(spec_bytes) if spec_bytes else {}

        # 8) Pylint
        analyze_style(TEST_FILE)


        # 2) Запускаем pytest и считаем pass/fail
        report = run_pytest_json()
        get_pass_fail_rate_firs(report)

        # 3) Извлекаем все вызовы и коды
        used = extract_used_endpoints(TEST_FILE)
        used_status_codes = extract_used_status_codes(TEST_FILE)

        # 6) Полное покрытие **по статус-кодам**
        measure_full_status_coverage(used_status_codes, parsed)


        # Покрытие по разделам
        show_status_code_coverage_sec(used_status_codes, parsed)
        
        # 5) Частичное покрытие **по endpoint-ам** (метод+путь)
        measure_api_coverage(used_status_codes, parsed)
        analyze_unSpecification_status_codes(TEST_FILE, parsed)

        get_pass_fail_rate_sec(report)


        # 4) Таблица по всем status-кодам
        show_status_code_coverage(used_status_codes, parsed)
        analyze_unSpecification_status_det(TEST_FILE, parsed)
        print_pass_fail_details(report)


        # Долго, но надежно
        # names = extract_test_names(TEST_FILE)
        # detect_flaky_tests(names)

        print("\n"*3)