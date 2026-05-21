import sys
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

# Додавання шляху до папки middleware для забезпечення імпорту db_client та логіки хешування.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'middleware')))
from db_client import DB_CONFIG, insert_telemetry, init_db
from fabric_stub import fabric_client
from main import calculate_canonical_hash

def get_db_record(device_id: str, timestamp: int) -> dict:
    """
    Читання поточного стану телеметрії з реляційної бази даних PostgreSQL.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding('utf8')
    # Використання RealDictCursor для отримання даних у вигляді словника (формат JSON).
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT device_id, timestamp, voltage, consumption_kwh 
        FROM telemetry_records 
        WHERE device_id = %s AND timestamp = %s
    """, (device_id, timestamp))
    record = cursor.fetchone()
    conn.close()
    return dict(record) if record else None

def execute_resilience_loop(device_id: str, timestamp: int):
    """
    КОМПОНЕНТ Г: Контур зворотного зв'язку (Resilience Loop).
    Автоматичний запуск процедури перевірки ПЕРЕД виконанням критичних керуючих команд.
    """
    print("\n--- [КОНТУР ВЕРИФІКАЦІЇ] Старт перевірки цілісності даних ---")
    
    # 1. Читання поточного стану даних із СУБД PostgreSQL.
    local_data = get_db_record(device_id, timestamp)
    if not local_data:
        print("[ПОМИЛКА] Дані відсутні у базі даних.")
        return

    # 2. Обчислення канонічного хешу локальних даних, вилучених із реляційної таблиці.
    local_hash = calculate_canonical_hash(local_data)
    print(f"[*] Локальний хеш (СУБД PostgreSQL): {local_hash}")

    # 3. Направлення запиту до смарт-контракту Node.js для отримання еталонного відбитка.
    blockchain_hash = fabric_client.get_state_hash(device_id, timestamp)
    print(f"[*] Еталонний хеш (Ledger Блокчейн): {blockchain_hash}")

    # 4. Застосування логіки порівняння (Критерій функціональної стійкості).
    if local_hash == blockchain_hash:
        print("[УСПІХ] Верифікація пройдена! Дані є цілісними та довіреними.")
        print("[ДІЯ АВТОМАТИКИ] Дозвіл на виконання високорівневої команди.")
    else:
        print("\n[!!! КРИТИЧНА ТРИВОГА !!!] ВИЯВЛЕНО РОЗБІЖНІСТЬ ХЕШІВ!")
        print(" -> Спроба ін'єкції хибних даних (FDIA) або несанкціонований злам СУБД.")
        print("[ДІЯ АВТОМАТИКИ] БЛОКУВАННЯ керуючої команди для запобігання аварії.")
        print("[ROLLBACK] Ініціація автоматичного відновлення еталонного стану системи...")

def run_simulation():
    """
    КОМПОНЕНТ Ґ: Повний сценарій тестування працездатності системи.
    """
    init_db()
    
    # Формування еталонного пакету телеметрії.
    payload = {
        "device_id": "meter_01",
        "timestamp": 1716312000,
        "voltage": 220.5,
        "consumption_kwh": 150.0
    }

    print("==================================================================")
    print(" ЕТАП 1: Нормальне функціонування (Запис даних та фіксація хешу)")
    print("==================================================================")
    # Імітація обробки даних через Middleware при отриманні пакету з MQTT.
    data_hash = calculate_canonical_hash(payload)
    insert_telemetry(payload)
    fabric_client.save_state_hash(payload['device_id'], payload['timestamp'], data_hash)
    
    time.sleep(0.5)
    print("\nСпроба системи виконати команду в нормальному (безпечному) режимі:")
    execute_resilience_loop(payload['device_id'], payload['timestamp'])

    print("\n==================================================================")
    print(" ЕТАП 2: Кібератака FDIA (Пряме несанкціоноване втручання в СУБД)")
    print("==================================================================")
    print("Зловмисник зламав сервер БД і змінює споживання в таблиці зі 150 на 50 в обхід Middleware...")
    
    # Імітація прямого несанкціонованого виконання SQL-запиту UPDATE в обхід захисних шлюзів.
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE telemetry_records 
        SET consumption_kwh = 50.0 
        WHERE device_id = 'meter_01' AND timestamp = 1716312000
    """)
    conn.commit()
    conn.close()
    print("[АТАКА] Дані всередині PostgreSQL успішно підроблено хакером!")

    print("\n==================================================================")
    print(" ЕТАП 3: Робота Модуля Стійкості (Детекція аномалії)")
    print("==================================================================")
    print("Спроба автоматики прийняти рішення на основі підроблених хакером даних:")
    execute_resilience_loop(payload['device_id'], payload['timestamp'])

if __name__ == "__main__":
    # Запуск комплексного сценарію моделювання.
    run_simulation()