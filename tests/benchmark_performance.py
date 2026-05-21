import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'middleware')))
from main import calculate_canonical_hash
from fabric_stub import fabric_client

def run_performance_benchmark():
    print("==================================================================")
    print(" СТАРТ НАВАНТАЖУВАЛЬНОГО ТЕСТУВАННЯ (БЕНЧМАРК ШВИДКОДІЇ)")
    print("==================================================================")
    
    iterations = 100
    payload = {"device_id": "meter_bench", "timestamp": 1716312000, "voltage": 220.0, "consumption_kwh": 100.0}
    
    # 1. Тест швидкості хешування
    start_time = time.time()
    for _ in range(iterations):
        _ = calculate_canonical_hash(payload)
    total_hash_time = time.time() - start_time
    avg_hash_time = (total_hash_time / iterations) * 1000 # в мілісекундах

    # 2. Тест швидкості запису в імітацію смарт-контракту
    start_time = time.time()
    for i in range(iterations):
        h = calculate_canonical_hash(payload)
        fabric_client.save_state_hash("meter_bench", 1716312000 + i, h)
    total_blockchain_time = time.time() - start_time
    avg_blockchain_time = (total_blockchain_time / iterations) * 1000

    print("\n==================================================================")
    print(" РЕЗУЛЬТАТИ НАВАНТАЖУВАЛЬНОГО ТЕСТУВАННЯ")
    print("==================================================================")
    print(f"[*] Загальна кількість ітерацій: {iterations}")
    print(f"[*] Середній час генерації канонічного хешу: {avg_hash_time:.4f} мс")
    print(f"[*] Середній час консенсусу смарт-контракту: {avg_blockchain_time:.2f} мс")
    print("==================================================================")

if __name__ == "__main__":
    run_performance_benchmark()