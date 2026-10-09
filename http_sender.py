import requests
import json
import time

url="https://httpbin.org/post"

payload={
"device_id":"ESP32_001",
"temperature":25.4,
"humidity":60
}

start=time.time()

response=requests.post(url,json=payload)

end=time.time()

print("Status :",response.status_code)
print("Payload :",json.dumps(payload))
print("Time :",round((end-start)*1000,2),"ms")