import json
import re
import sys
import argparse
import os

NAME_PATTERN = re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]*$")

class ConfigTranslator:
    def __init__(self):
        self.constants = {}

    def validate_name(self, name):
        """Проверка имени."""
        if not NAME_PATTERN.match(name):
            raise ValueError(f"Некорректное имя: '{name}'")

    def evaluate_expression(self, expression):
        """Вычисление арифметических выражений (поддержка +, -, *, /)."""
        try:
            return eval(expression, {}, self.constants)
        except Exception:
            raise ValueError(f"Ошибка вычисления выражения: {expression}")

    def parse_value(self, value):
        """Обработка значений: числа, строки, словари, константы."""
        if isinstance(value, dict):
            return self.translate_dict(value)
        elif isinstance(value, list):
            return self.translate_list(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str) and value.startswith("^["):
            expr = value[2:-1].strip()
            return str(self.evaluate_expression(expr))
        elif isinstance(value, str):
            return f"\"{value}\""
        else:
            raise ValueError(f"Неподдерживаемый тип значения: {value}")

    def translate_list(self, lst):
        """Обработка списков."""
        items = [self.parse_value(item) for item in lst]
        return "list(" + ", ".join(items) + ")"

    def translate_dict(self, data):
        """Преобразование словаря."""
        result = ["$["]
        for key, value in data.items():
            self.validate_name(key)
            translated_value = self.parse_value(value)
            result.append(f" {key} : {translated_value},")
        result.append("]")
        return "\n".join(result)

    def translate_constant(self, name, value):
        """Объявление и сохранение константы."""
        self.validate_name(name)
        self.constants[name] = value
        return f"(define {name} {value});"

    def translate(self, data):
        """Главный метод обработки входного JSON."""
        output = []
        for key, value in data.items():
            if key.startswith("define"):  # Объявление константы
                output.append(self.translate_constant(value["name"], value["value"]))
            elif key.startswith("^["):  # Вычисление константы
                const_name = key[2:-1].strip()
                output.append(f"^{const_name}")
            else:
                output.append(self.translate_dict({key: value}))
        return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Преобразование JSON в учебный конфигурационный язык.")
    parser.add_argument("output", help="Путь к выходному файлу")
    args = parser.parse_args()

    translator = ConfigTranslator()

    try:
        # Чтение JSON из stdin
        input_json = sys.stdin.read()
        data = json.loads(input_json)

        # Обработка данных
        result = translator.translate(data)

        # Запись в файл
        output_path = os.path.join("C:\\Users\\123\\Documents\\\config_dz_3-main", args.output)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(result)
        print(f"Файл успешно сохранён: {output_path}")

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
