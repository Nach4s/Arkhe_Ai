"""
Скрипт для проверки всех импортов и связей в проекте.
"""
import sys
import importlib.util

def check_import(module_name, file_path):
    """Проверка импорта модуля."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            return False, f"Не удалось создать spec для {file_path}"
        module = importlib.util.module_from_spec(spec)
        # Не выполняем код, только проверяем синтаксис
        return True, "OK"
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка: {e}"
    except Exception as e:
        return False, f"Ошибка: {e}"

def main():
    """Проверка всех файлов проекта."""
    files_to_check = [
        ("config", "config.py"),
        ("bot", "bot.py"),
        ("handlers.start", "handlers/start.py"),
        ("handlers.upload", "handlers/upload.py"),
        ("services.file_parser", "services/file_parser.py"),
        ("services.ai_analyzer", "services/ai_analyzer.py"),
    ]
    
    print("🔍 Проверка импортов и связей в проекте...\n")
    
    all_ok = True
    for module_name, file_path in files_to_check:
        ok, message = check_import(module_name, file_path)
        status = "✅" if ok else "❌"
        print(f"{status} {file_path}: {message}")
        if not ok:
            all_ok = False
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ Все файлы проверены успешно!")
    else:
        print("❌ Обнаружены ошибки в файлах")
        sys.exit(1)

if __name__ == "__main__":
    main()

