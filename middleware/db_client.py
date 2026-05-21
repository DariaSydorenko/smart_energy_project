import psycopg2

# Конфігурація підключення до локального сервера PostgreSQL.
DB_CONFIG = {
    "dbname": "smartenergy",
    "user": "postgres",
    "password": "f3ZyCv3Qy",
    "host": "localhost",
    "port": "5432"
}

def init_db():
    """
    Ініціалізація бази даних (СУБД).
    Автоматичне створення таблиці для телеметрії та індексів у разі їх відсутності.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding('utf8')
        cursor = conn.cursor()
        
        # Створення таблиці телеметрії лічильників згідно зі специфікацією архітектури.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_records (
                id SERIAL PRIMARY KEY,
                device_id VARCHAR(50) NOT NULL,
                timestamp BIGINT NOT NULL,
                voltage FLOAT NOT NULL,
                consumption_kwh FLOAT NOT NULL
            );
        """)
        
        # Створення індексу для оптимізації майбутніх запитів верифікації.
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_timestamp 
            ON telemetry_records (device_id, timestamp);
        """)
        
        conn.commit()
        print("[БАЗА ДАНИХ] Ініціалізацію успішно виконано. Таблиця ready!")
        
    except Exception as e:
        print(f"[ПОМИЛКА БД] Не вдалося ініціалізувати базу даних: {e}")
    finally:
        # Закриття з'єднання з базою даних.
        if 'conn' in locals() and conn:
            conn.close()

def insert_telemetry(data: dict):
    """
    Оперативний синхронний запис сирих даних телеметрії в PostgreSQL.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding('utf8')
        cursor = conn.cursor()
        
        # Виконання SQL-запиту на додавання нового запису телеметрії.
        cursor.execute("""
            INSERT INTO telemetry_records (device_id, timestamp, voltage, consumption_kwh)
            VALUES (%s, %s, %s, %s);
        """, (data['device_id'], data['timestamp'], data['voltage'], data['consumption_kwh']))
        
        conn.commit()
        print(f"[БАЗА ДАНИХ] Дані для {data['device_id']} успішно збережено в PostgreSQL.")
        
    except Exception as e:
        print(f"[ПОМИЛКА БД] Помилка під час вставки даних: {e}")
    finally:
        # Закриття з'єднання з базою даних.
        if 'conn' in locals() and conn:
            conn.close()