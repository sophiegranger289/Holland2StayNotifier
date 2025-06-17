import time
from h2snotifier import main

while True:
    try:
        main.main()
    except Exception as e:
        print(f"[ERROR] {e}")
    time.sleep(3)  # 每 5 分钟执行一次
