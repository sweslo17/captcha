import requests
import shutil
import time
import random

counter = 1911

while True:
    print(counter)
    url = 'http://railway.hinet.net/ImageOut.jsp?pageRandom=2'
    response = requests.get(url, stream=True)
    with open('./test_data/{}.jpg'.format(counter), 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
        del response
        counter += 1
    time.sleep(random.randint(100,500)/100)
