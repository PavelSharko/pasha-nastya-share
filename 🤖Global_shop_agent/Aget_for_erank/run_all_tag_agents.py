import subprocess
import sys
import os
import time

# Конфигурация путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(script_name, args=None):
    script_path = os.path.join(AGENT_DIR, script_name)
    print(f"\n" + "="*50)
    print(f"🚀 ЗАПУСК: {script_name}")
    print("="*50)
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ОШИБКА при запуске {script_name}: {e}")
        return False

def manual_flow():
    # Импортируем pre_tag_agent для получения списка
    sys.path.append(AGENT_DIR)
    import pre_tag_agent
    
    topics = pre_tag_agent.update_queue() # Показывает что есть в отчете
    if not topics:
        print("🛑 Темы не найдены. Проверьте папку actual_topics.")
        return

    print("\nВведите номера тем через запятую (например: 1,3) или 'all' для всех:")
    choice = input("Ваш выбор: ").strip().lower()

    selected_topics = []
    if choice == 'all':
        selected_topics = topics
    else:
        try:
            indices = [int(i.strip()) - 1 for i in choice.split(',')]
            selected_topics = [topics[i] for i in indices if 0 <= i < len(topics)]
        except:
            print("❌ Неверный ввод.")
            return

    if not selected_topics:
        print("🛑 Темы не выбраны.")
        return

    # Добавляем в очередь выбранное
    pre_tag_agent.update_queue(topics_to_add=selected_topics)

    # Предлагаем запустить второй скрипт
    run_script("erank_queue_runner.py")
    
    # Третий скрипт (аналитик) запускаем всегда в конце
    run_script("tag_strategist_agent.py")

def auto_flow():
    # 1. Добавляем ВСЕ из последнего отчета
    import pre_tag_agent
    topics = pre_tag_agent.update_queue()
    if topics:
        pre_tag_agent.update_queue(topics_to_add=topics)

    # 2. Запускаем воркер в режиме auto
    run_script("erank_queue_runner.py", args=["procces_run: auto"])

    # 3. Запускаем стратега
    run_script("tag_strategist_agent.py")

def main():
    # Проверяем аргументы командной строки
    args_str = " ".join(sys.argv)
    is_auto = "procces_run: auto" in args_str

    if is_auto:
        print("🤖 РЕЖИМ: АВТОМАТ (auto)")
        auto_flow()
    else:
        print("👤 РЕЖИМ: РУЧНОЙ (manual)")
        manual_flow()

    print("\n" + "✨"*25)
    print("🎉 ЦИКЛ ОБРАБОТКИ ЗАВЕРШЕН!")
    print("✨"*25 + "\n")

if __name__ == "__main__":
    main()
