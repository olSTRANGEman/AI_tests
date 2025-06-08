import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import re

# Список папок с файлами отчетов
FOLDERS = [
    "/home/stranger/Документы/NEER 2.0/AI_test/Deepseek",
    "/home/stranger/Документы/NEER 2.0/AI_test/Gemini",
    "/home/stranger/Документы/NEER 2.0/AI_test/GPT",
    "/home/stranger/Документы/NEER 2.0/AI_test/Qwen",
    "/home/stranger/Документы/NEER 2.0/AI_test/Grok"
]

# Метрики для извлечения
METRICS = {
    "style_score": r"Style Score:\s*(\d+\.\d+)/10",
    "pass_rate": r"Pass Rate:\s*\d+/(\d+)\s*\((\d+\.\d+)%\)",
    "endpoint_coverage": r"API Endpoint Coverage:\s*\d+/(\d+)\s*\((\d+\.\d+)%\)",
    "partly_endpoint_coverage": r"API partly Endpoint Coverage\s*[:\s]\s*\d+/(\d+)\s*\((\d+\.\d+)%\)",
    "flaky_tests": r"⚠️?\s*Flaky tests:\s*\[([^\]]*)\]",
    "undeclared_status_codes": r"❗\s*Незаявленные статус-коды:\s*\d+\s*/\s*(\d+)\s*\((\d+\.\d+)%\)"
}

# Папка для сохранения диаграмм
OUTPUT_DIR = "charts"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def parse_report(file_path):
    """Парсинг одного файла отчета и извлечение метрик."""
    data = {}
    encodings = ['utf-8', 'utf-8-sig']
    content = None
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                break
        except UnicodeDecodeError:
            continue
    if content is None:
        print(f"Не удалось прочитать файл {file_path} с кодировками {encodings}.")
        for key in METRICS:
            data[key] = 0.0 if key != "flaky_tests" else 0
        return data

    lines = content.split('\n')
    print(f"\nОбработка файла: {file_path}")
    for key, pattern in METRICS.items():
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            try:
                if key == "style_score":
                    data[key] = float(match.group(1)) * 10
                elif key == "flaky_tests":
                    tests = match.group(1).strip()
                    data[key] = len(tests.split(',')) if tests else 0
                else:
                    data[key] = float(match.group(2)) if key.endswith("coverage") or key == "pass_rate" or key == "undeclared_status_codes" else int(match.group(1))
                print(f"  {key}: {data[key]}")
            except (IndexError, ValueError):
                print(f"Ошибка парсинга метрики {key} в файле {file_path}. Устанавливается 0.")
                data[key] = 0.0 if key != "flaky_tests" else 0
        else:
            print(f"Метрика {key} не найдена в файле {file_path}. Первые строки файла:")
            for i, line in enumerate(lines[:10], 1):
                print(f"Строка {i}: {line}")
            if key == "undeclared_status_codes":
                print("Строки, содержащие 'Незаявленные':")
                for i, line in enumerate(lines, 1):
                    if "Незаявленные" in line:
                        print(f"Строка {i}: {line}")
            data[key] = 0.0 if key != "flaky_tests" else 0
    return data

def collect_data_from_folder(folder):
    """Сбор данных из файлов в одной папке."""
    reports_data = []
    folder_path = folder
    if not os.path.exists(folder_path):
        print(f"Папка {folder_path} не найдена.")
        return reports_data
    for filename in sorted(os.listdir(folder_path)):
        if filename.startswith("v") and filename.endswith("_metrics_log.txt"):
            file_path = os.path.join(folder_path, filename)
            data = parse_report(file_path)
            data["filename"] = filename
            reports_data.append(data)
    return reports_data

def plot_folder_data(folder, reports_data):
    """Генерация горизонтальной диаграммы с наложением для процентных метрик и отдельной для flaky_tests."""
    if not reports_data:
        print(f"Нет данных для папки {folder}.")
        return

    # Извлечение данных
    labels = [data["filename"] for data in reports_data]
    pass_rates = [data.get("pass_rate", 0.0) for data in reports_data]
    endpoint_coverages = [data.get("endpoint_coverage", 0.0) for data in reports_data]
    partly_endpoint_coverages = [data.get("partly_endpoint_coverage", 0.0) for data in reports_data]
    style_scores = [data.get("style_score", 0.0) for data in reports_data]
    flaky_tests = [data.get("flaky_tests", 0) for data in reports_data]
    undeclared_status_codes = [data.get("undeclared_status_codes", 0.0) for data in reports_data]

    # Вывод данных для отладки
    print(f"\nДанные для папки {folder}:")
    for i, label in enumerate(labels):
        print(f"  {label}:")
        print(f"    pass_rate: {pass_rates[i]}")
        print(f"    endpoint_coverage: {endpoint_coverages[i]}")
        print(f"    partly_endpoint_coverage: {partly_endpoint_coverages[i]}")
        print(f"    style_score: {style_scores[i]}")
        print(f"    undeclared_status_codes: {undeclared_status_codes[i]}")
        print(f"    flaky_tests: {flaky_tests[i]}")

    # Подготовка метрик для наложения (сортировка по убыванию для каждого файла)
    metrics_data = []
    for i in range(len(labels)):
        metrics = [
            (pass_rates[i], "Процент успешных тестов (%)", "#4C78A8"),
            (endpoint_coverages[i], "Покрытие endpoint-ов (%)", "#F28E2B"),
            (partly_endpoint_coverages[i], "Частичное покрытие endpoint-ов (%)", "#E15759"),
            (style_scores[i], "Оценка стиля (%)", "#76B7B2"),
            (undeclared_status_codes[i], "Незаявленные статус-коды (%)", "#59A14F")
        ]
        metrics.sort(key=lambda x: x[0], reverse=True)
        metrics_data.append(metrics)

    # Генерация горизонтальной диаграммы с наложением
    fig, ax = plt.subplots(figsize=(12, len(labels) * 0.6 + 2))
    y = np.arange(len(labels))

    for i in range(len(labels)):
        left = 0
        for value, label, color in metrics_data[i]:
            bars = ax.barh(y[i], value, left=left, label=label if i == 0 else "", color=color, alpha=0.8)
            left = 0  # Сбрасываем left, чтобы метрики накладывались

    # Добавление линий сетки
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Установка максимума по оси X
    ax.set_xlim(0, 100)

    # Удаление подписи оси X
    ax.set_xlabel("")

    # Заголовок
    ax.set_title(f"{os.path.basename(folder)} - Процентные метрики", fontsize=12)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()

    # Перемещение легенды под диаграмму
    ax.legend(bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=3, frameon=False)

    plt.tight_layout(pad=4.0)
    output_file = os.path.join(OUTPUT_DIR, f"{os.path.basename(folder)}_stacked.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Диаграмма с наложением для {os.path.basename(folder)} сохранена как {output_file}")

    # Диаграмма для количественных метрик
    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(labels))
    ax.plot(x, flaky_tests, label="Flaky тесты", color="#8C8C8C", marker='o', linewidth=2)

    # Добавление линий сетки
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    ax.set_ybound(lower=0)
    ax.set_ylabel("Количество", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.legend()

    plt.tight_layout(pad=4.0)
    output_file = os.path.join(OUTPUT_DIR, f"{os.path.basename(folder)}_flaky_tests.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Диаграмма количественных метрик для папки {folder} сохранена как {output_file}")



def plot_models_comparison(all_data):
    """Генерация сравнительных диаграмм для всех моделей, используя только v7_metrics_log.txt."""
    if not all_data:
        print("Нет данных для сравнения моделей.")
        return

    # Фильтрация данных только для v7_metrics_log.txt
    model_data = {}
    for data in all_data:
        if data["filename"] == "v7_metrics_log.txt":
            model = data["folder"]
            if model not in model_data:
                model_data[model] = {}
            for key in METRICS:
                model_data[model][key] = data.get(key, 0.0 if key != "flaky_tests" else 0)

    # Извлечение значений для сравнительных диаграмм
    labels = []
    pass_rates = []
    endpoint_coverages = []
    partly_endpoint_coverages = []
    style_scores = []
    flaky_tests = []
    undeclared_status_codes = []
    for model in sorted(model_data.keys()):
        labels.append(model)
        pass_rates.append(model_data[model].get("pass_rate", 0.0))
        endpoint_coverages.append(model_data[model].get("endpoint_coverage", 0.0))
        partly_endpoint_coverages.append(model_data[model].get("partly_endpoint_coverage", 0.0))
        style_scores.append(model_data[model].get("style_score", 0.0))
        flaky_tests.append(model_data[model].get("flaky_tests", 0))
        undeclared_status_codes.append(model_data[model].get("undeclared_status_codes", 0.0))

    # Словарь для процентных метрик с цветами
    percent_metrics = {
        "pass_rate": (pass_rates, "Процент успешных тестов (%)", "#4C78A8"),
        "endpoint_coverage": (endpoint_coverages, "Покрытие endpoint-ов (%)", "#F28E2B"),
        "partly_endpoint_coverage": (partly_endpoint_coverages, "Частичное покрытие endpoint-ов (%)", "#E15759"),
        "style_score": (style_scores, "Оценка стиля (%)", "#76B7B2"),
        "undeclared_status_codes": (undeclared_status_codes, "Незаявленные статус-коды (%)", "#59A14F")
    }

    # Генерация отдельных горизонтальных диаграмм для каждой процентной метрики
    for metric_name, (values, label, color) in percent_metrics.items():
        fig, ax = plt.subplots(figsize=(10, len(labels) * 0.5 + 2))
        y = np.arange(len(labels))
        bars = ax.barh(y, values, color=color)

        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Значения (%)", fontsize=10)
        ax.set_title(label)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.invert_yaxis()

        for bar in bars:
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                    ha='left', fontsize=8)

        plt.tight_layout(pad=4.0)
        output_file = os.path.join(OUTPUT_DIR, f"models_{metric_name}_comparison.png")
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Сравнительная диаграмма для {metric_name} сохранена как {output_file}")

    # Гистограмма для flaky_tests (без подписей над столбцами)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(labels))
    bar_width = 0.6
    ax.bar(x, flaky_tests, width=bar_width, color="#8C8C8C")

    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    ax.set_ylabel("Количество flaky тестов", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)

    plt.tight_layout(pad=4.0)
    output_file = os.path.join(OUTPUT_DIR, "models_flaky_tests_comparison.png")
    plt.savefig(output_file, dpi=300)
    plt.close()
    print(f"Гистограмма flaky_tests сохранена как {output_file}")




def main():
    """Основная функция для обработки отчетов и генерации диаграмм."""
    all_data = []
    for folder in FOLDERS:
        reports_data = collect_data_from_folder(folder)
        plot_folder_data(folder, reports_data)
        for data in reports_data:
            data["folder"] = os.path.basename(folder)
            all_data.append(data)
    
    plot_models_comparison(all_data)

if __name__ == "__main__":
    main()