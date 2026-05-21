import time

class FabricNetworkStub:
    """
    Клас-заглушка (Stub) для імітації роботи Hyperledger Fabric SDK 
    та логічної взаємодії з методами смарт-контракту на Node.js.
    """
    def __init__(self):
        # Використання внутрішнього словника в ролі імітації розподіленого реєстру (Ledger).
        self._ledger = {}

    def save_state_hash(self, device_id: str, timestamp: int, data_hash: str):
        """Імітація виклику методу смарт-контракту 'SaveStateHash'."""
        # Імітація реальної затримки блокчейн-мережі на досягнення консенсусу (100 мс).
        time.sleep(0.1)  
        key = f"{device_id}_{timestamp}"
        self._ledger[key] = data_hash
        print(f"[MIDDLEWARE -> BLOCKCHAIN] Смарт-контракт Node.js успішно записав еталонний хеш для ключа {key}.")

    def get_state_hash(self, device_id: str, timestamp: int) -> str:
        """Імітація виклику методу смарт-контракту 'GetStateHash'."""
        key = f"{device_id}_{timestamp}"
        return self._ledger.get(key)

# Створення єдиного глобального об'єкта клієнта блокчейну для використання в системі.
fabric_client = FabricNetworkStub()