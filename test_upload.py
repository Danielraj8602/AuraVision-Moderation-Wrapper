import requests
import cv2
import numpy as np

# Create a dummy image
img = np.zeros((100, 100, 3), dtype=np.uint8)
cv2.imwrite("dummy.jpg", img)

# Send to API
with open("dummy.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/process", files=files)
    print(response.status_code)
    print(response.text)
