import os
import time

API_TOKEN = os.getenv('API_TOKEN')

while True:
    print(f'API_TOKEN is {API_TOKEN}')
    time.sleep(1)
    pass

