import os
import time
from datetime import datetime

API_TOKEN = os.getenv('API_TOKEN')


while True:
    print(f'API_TOKEN is {API_TOKEN}')
    print(f'And time is {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(1)
    pass
