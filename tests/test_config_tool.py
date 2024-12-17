import unittest
import json
import subprocess
import os

class TestConfigTool(unittest.TestCase):
    # Определение путей с учетом родительской папки
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Папка, где находится данный скрипт
    TEST_INPUT_DIR = os.path.join(BASE_DIR, "..", "test_inputs")  # Родительская папка
    TEST_OUTPUT_DIR = os.path.join(BASE_DIR, "..", "tests", "test_outputs")  # Родительская папка
    SCRIPT_PATH = os.path.join(BASE_DIR, "..", "src", "config_tool.py")  # Путь к скрипту

    @classmethod
    def setUpClass(cls):
        os.makedirs(cls.TEST_INPUT_DIR, exist_ok=True)
        os.makedirs(cls.TEST_OUTPUT_DIR, exist_ok=True)

    def run_config_tool(self, input_json, output_file):
        """Вспомогательный метод для запуска config_tool.py"""
        input_path = os.path.join(self.TEST_INPUT_DIR, "input.json")
        output_path = os.path.join(self.TEST_OUTPUT_DIR, output_file)

        # Запись входного JSON в файл
        with open(input_path, "w", encoding="utf-8") as file:
            json.dump(input_json, file)

        # Запуск скрипта через subprocess
        with open(input_path, "r") as input_file:
            result = subprocess.run(
                ["python", self.SCRIPT_PATH, output_file],
                stdin=input_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

        return result, output_path

    def check_output(self, output_path, expected_content):
        """Вспомогательный метод для проверки выходного файла"""
        if not os.path.exists(output_path):
            self.fail(f"Output file does not exist: {output_path}")

        with open(output_path, "r", encoding="utf-8") as file:
            result_content = file.read().strip()
        self.assertEqual(result_content, expected_content.strip())

    def test_web_server_config(self):
        """Тест для конфигурации веб-сервера"""
        input_json = {
            "define": {"name": "DEFAULT_PORT", "value": 8080},
            "server": {
                "host": "localhost",
                "port": "^[DEFAULT_PORT + 2]",
                "modules": ["http", "cache", "security"]
            },
            "log": {
                "level": "info",
                "path": "/var/log/server.log"
            }
        }
        expected_output = """
-- Объявление константы DEFAULT_PORT
(define DEFAULT_PORT 8080);

-- Конфигурация сервера
$[
 server : $[
  host : "localhost",
  port : 8102,
  modules : list("http", "cache", "security"),
 ],
 log : $[
  level : "info",
  path : "/var/log/server.log",
 ],
]
"""
        result, output_path = self.run_config_tool(input_json, "web_server_output.txt")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.check_output(output_path, expected_output)

    def test_user_management_config(self):
        """Тест для конфигурации системы управления пользователями"""
        input_json = {
            "define": {"name": "MAX_LOGIN_ATTEMPTS", "value": 5},
            "users": {
                "admin": {
                    "password": "secure123",
                    "role": "superuser",
                    "max_attempts": "^[MAX_LOGIN_ATTEMPTS]"
                },
                "guest": {
                    "password": "guest",
                    "role": "readonly",
                    "max_attempts": "^[MAX_LOGIN_ATTEMPTS - 2]"
                }
            }
        }
        expected_output = """
-- Объявление константы MAX_LOGIN_ATTEMPTS
(define MAX_LOGIN_ATTEMPTS 5);

-- Конфигурация пользователей
$[
 users : $[
  admin : $[
   password : "secure123",
   role : "superuser",
   max_attempts : 5,
  ],
  guest : $[
   password : "guest",
   role : "readonly",
   max_attempts : 3,
  ],
 ],
]
"""
        result, output_path = self.run_config_tool(input_json, "user_management_output.txt")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.check_output(output_path, expected_output)

    def test_robot_config(self):
        """Тест для конфигурации робота"""
        input_json = {
            "define": {"name": "BASE_SPEED", "value": 100},
            "robot": {
                "motors": {
                    "left": {"speed": "^[BASE_SPEED]"},
                    "right": {"speed": "^[BASE_SPEED * 1.2]"}
                },
                "sensors": ["ultrasonic", "infrared", "camera"],
                "coordinates": {
                    "x": 10,
                    "y": 20,
                    "z": "^[BASE_SPEED / 2]"
                }
            }
        }
        expected_output = """
-- Объявление константы BASE_SPEED
(define BASE_SPEED 100);

-- Конфигурация робота
$[
 robot : $[
  motors : $[
   left : $[
    speed : 100,
   ],
   right : $[
    speed : 120.0,
   ],
  ],
  sensors : list("ultrasonic", "infrared", "camera"),
  coordinates : $[
   x : 10,
   y : 20,
   z : 50.0,
  ],
 ],
]
"""
        result, output_path = self.run_config_tool(input_json, "robot_config_output.txt")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.check_output(output_path, expected_output)

if __name__ == "__main__":
    unittest.main()
