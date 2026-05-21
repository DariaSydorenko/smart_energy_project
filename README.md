# ⚡ SmartEnergy: IoT Telemetry Resilience System

![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-%3E%3D18.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-latest-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-Microservices-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📖 Про проєкт

**SmartEnergy** — це програмний комплекс (Proof of Concept), розроблений для забезпечення функціональної стійкості систем Інтернету речей (IoT) в енергетичному секторі. Головна мета проєкту — автоматичне виявлення кібератак класу **FDIA (False Data Injection Attack)** та запобігання прийняттю рішень на основі скомпрометованих даних.

Архітектура побудована на принципі **сепарації потоків даних (Data Separation)** та використанні контуру зворотного зв'язку (Resilience Loop):
1. Сирі телеметричні дані записуються у високошвидкісну реляційну СУБД.
2. Криптографічний зліпок (канонічний SHA-256 хеш) цих даних асинхронно фіксується у незмінному розподіленому реєстрі (Blockchain).
3. Перед виконанням критичних команд система верифікує локальний хеш з еталоном у блокчейні.

## 🏗 Стек технологій

* **IoT Data Ingestion:** MQTT (Eclipse Paho)
* **Middleware & Logic:** Python 3.14
* **Relational Database:** PostgreSQL (psycopg2)
* **Distributed Ledger / Blockchain:** Hyperledger Fabric (Node.js Chaincode)
* **Testing:** `unittest` (Python)

## 📂 Структура репозиторію

```text
smart_energy_project/
├── chaincode/              # Смарт-контракт для Hyperledger Fabric
│   ├── index.js            # Логіка смарт-контракту (Node.js)
│   └── package.json        # Залежності
├── middleware/             # Проміжне ПЗ для обробки даних
│   ├── db_client.py        # ORM / Робота з PostgreSQL
│   ├── fabric_stub.py      # Інтерфейс взаємодії з Blockchain-мережею
│   ├── main.py             # Точка входу: підписка на MQTT, хешування, сепарація
│   └── requirements.txt    # Залежності Python
├── simulator/              # Генерація тестових даних
│   └── meter_sim.py        # Імітація розумного лічильника (MQTT Publisher)
└── tests/                  # Інтеграційні та модульні тести
    ├── fdia_attack_sim.py  # Сценарій симуляції атаки та роботи контуру стійкості
    └── test_middleware.py  # Unit-тести криптографічного ядра

