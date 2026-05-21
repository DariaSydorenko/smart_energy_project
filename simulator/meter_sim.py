import json
import time
import paho.mqtt.client as mqtt

def send_telemetry():
    """
    Імітація генерації даних фізичним лічильником 
    та їх відправлення через протокол MQTT.
    """
    # Створення клієнта для підключення до мережі.
    client = mqtt.Client()
    
    # Підключення до публічного брокера HiveMQ, синхронізованого з Middleware.
    client.connect("broker.hivemq.com", 1883, 60)

    # Формування структури пакету згідно з вимогами дисертації.
    payload = {
        "device_id": "meter_01",
        "timestamp": 1716312000,   # Фіксація часу для забезпечення відтворюваності тестування атаки.
        "voltage": 220.5,          # Вимірювання напруги в мережі.
        "consumption_kwh": 150.0   # Обсяг спожитої електроенергії.
    }

    print(f"[ЛІЧИЛЬНИК IoT] Згенеровано нові показники: {payload}")
    
    # Публікація (відправлення) даних у топік, що прослуховується Middleware.
    client.publish("smartenergy/telemetry", json.dumps(payload))
    print("[ЛІЧИЛЬНИК IoT] Пакет успішно відправлено в MQTT-канал. Відключення.")
    
    # Виконання відключення від брокера.
    client.disconnect()

if __name__ == "__main__":
    # Ініціалізація та запуск процедури відправлення телеметрії.
    send_telemetry()