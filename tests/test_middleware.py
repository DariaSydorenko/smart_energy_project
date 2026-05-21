import sys
import os
import unittest

# Додавання шляху до папки middleware для забезпечення імпорту логіки.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'middleware')))
from main import calculate_canonical_hash

class TestSmartEnergyMiddleware(unittest.TestCase):

    def test_canonical_json_ordering(self):
        """
        Перевірка стійкості алгоритму до зміни порядку ключів у структурі JSON.
        Фінальний криптографічний хеш має залишатися ідентичним при будь-якій послідовності полів.
        """
        payload_1 = {"device_id": "meter_01", "timestamp": 1716312000, "consumption_kwh": 150.0}
        payload_2 = {"consumption_kwh": 150.0, "device_id": "meter_01", "timestamp": 1716312000}
        
        hash_1 = calculate_canonical_hash(payload_1)
        hash_2 = calculate_canonical_hash(payload_2)
        
        # Перевірка еквівалентності отриманих хеш-значень для ідентичних даних.
        self.assertEqual(hash_1, hash_2, "Помилка: канонізація структури JSON не виконана.")

    def test_avalanche_effect(self):
        """
        Перевірка наявності лавинного ефекту (avalanche effect).
        Мінімальна модифікація вхідних даних має призводити до повної зміни значення контрольного хешу.
        """
        payload_exact = {"device_id": "meter_01", "timestamp": 1716312000, "consumption_kwh": 150.0}
        payload_modified = {"device_id": "meter_01", "timestamp": 1716312000, "consumption_kwh": 150.01} # Модифікація значення на 0.01.
        
        hash_exact = calculate_canonical_hash(payload_exact)
        hash_modified = calculate_canonical_hash(payload_modified)
        
        # Перевірка наявності розбіжностей між обчисленими значеннями хешів.
        self.assertNotEqual(hash_exact, hash_modified, "Помилка: лавинний ефект криптографічного перетворення відсутній.")

if __name__ == "__main__":
    # Ініціалізація та виконання комплексу модульних тестів.
    unittest.main()