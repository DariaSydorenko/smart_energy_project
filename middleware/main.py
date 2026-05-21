import json
import hashlib
import threading
import paho.mqtt.client as mqtt
from db_client import insert_telemetry, init_db
from fabric_stub import fabric_client

def calculate_canonical_hash(payload: dict) -> str:
    """
    Метод криптографічногольного контролю станів (State Hashing).
    Сортування ключів JSON за алфавітом (sort_keys=True) для канонізації 
    з метою запобігання руйнуванню хешу через зміну порядку полів, та обчислення відбитка SHA-256.
    """
    canonical_json = json.dumps(payload, sort_keys=True).encode('utf-8')
    return hashlib.sha256(canonical_json).hexdigest()

def async_blockchain_write(device_id: str, timestamp: int, data_hash: str):
    """
    Запуск окремого асинхронного потоку для взаємодії з блокчейн-рівнем.
    Запобігання блокуванню системи реального часу через триваліший запис у розподілений реєстр.
    """
    fabric_client.save_state_hash(device_id, timestamp, data_hash)

def on_message(client, userdata, msg):
    """Коллбек-функція, що автоматично спрацьовує при надходженні нового пакету з MQTT."""
    try:
        # Декодування вхідного потоку байтів у словник Python.
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"\n[MIDDLEWARE] Отримано новий пакет телеметрії від пристрою: {payload.get('device_id')}")

        # Крок 1: Синхронне обчислення цифрового зліпка (хешу).
        data_hash = calculate_canonical_hash(payload)
        print(f"[MIDDLEWARE] Згенеровано канонічний SHA-256 хеш: {data_hash}")
        
        # Крок 2: Сепарація даних — негайне збереження оперативних даних у СУБД PostgreSQL.
        insert_telemetry(payload)

        # Крок 3: Асинхронний запис у Блокчейн (ініціалізація та запуск фонового потоку).
        blockchain_thread = threading.Thread(
            target=async_blockchain_write, 
            args=(payload['device_id'], payload['timestamp'], data_hash)
        )
        blockchain_thread.start()

    except Exception as e:
        print(f"[MIDDLEWARE ПОМИЛКА] Помилка під час обробки вхідних даних: {e}")

if __name__ == "__main__":
    # Попередня перевірка наявності та автоматичне створення таблиць у СУБД PostgreSQL.
    init_db()
    
    # Налаштування клієнта MQTT.
    client = mqtt.Client()
    client.on_message = on_message
    
    # Підключення до публічного тестового брокера HiveMQ для імітації доставки даних.
    client.connect("broker.hivemq.com", 1883, 60)
    
    # Виконання підписки на топік телеметрії.
    client.subscribe("smartenergy/telemetry")
    
    print("[MIDDLEWARE] Сервіс успішно запущено. Очікування потоку даних з MQTT...")
    # Запуск постійного прослуховування мережевого інтерфейсу.
    client.loop_forever()