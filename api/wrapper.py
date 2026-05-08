import os
import cv2
import time
import base64
import json
import requests
import numpy as np
from PIL import Image
from io import BytesIO

API_URL = "http://172.190.114.26:5000/inference/nudity/fileupload"

class UltimateModerationWrapper:
    def __init__(self):
        print("\n========================================")
        print(" ULTIMATE MODERATION WRAPPER STARTED ")
        print("========================================")

    def load_image(self, input_source):
        # URL
        if isinstance(input_source, str) and input_source.startswith("http"):
            print("Loading image from URL...")
            response = requests.get(input_source, timeout=20)
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # LOCAL BYTES
        elif isinstance(input_source, bytes):
            print("Loading image from bytes...")
            nparr = np.frombuffer(input_source, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # LOCAL FILE
        else:
            print("Loading local image...")
            image = cv2.imread(input_source)

        if image is None:
            raise Exception("Unable to load image")

        return image

    def calculate_brightness(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)

    def calculate_blur(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def estimate_noise(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).std()

    def gamma_correction(self, image, gamma=1.4):
        inv_gamma = 1.0 / gamma
        table = np.array([
            ((i / 255.0) ** inv_gamma) * 255
            for i in np.arange(0, 256)
        ]).astype("uint8")
        return cv2.LUT(image, table)

    def apply_clahe(self, image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        merged = cv2.merge((cl, a, b))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

    def denoise(self, image):
        return cv2.fastNlMeansDenoisingColored(image, None, 4, 4, 7, 21)

    def sharpen(self, image):
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        return cv2.filter2D(image, -1, kernel)

    def normalize_size(self, image):
        height, width = image.shape[:2]
        max_size = 1280
        if width > max_size:
            ratio = max_size / width
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return image

    def adaptive_enhancement(self, image):
        brightness = self.calculate_brightness(image)
        blur_score = self.calculate_blur(image)
        noise_score = self.estimate_noise(image)

        print(f"Brightness : {brightness:.2f}")
        print(f"Blur Score : {blur_score:.2f}")
        print(f"Noise Score: {noise_score:.2f}")

        enhanced = image.copy()

        if brightness < 70:
            print("Applying low-light enhancement...")
            enhanced = self.gamma_correction(enhanced, gamma=1.4)
            enhanced = self.apply_clahe(enhanced)

        if noise_score > 25:
            print("Applying denoising...")
            enhanced = self.denoise(enhanced)

        if blur_score < 100:
            print("Applying sharpening...")
            enhanced = self.sharpen(enhanced)

        enhanced = self.normalize_size(enhanced)
        return enhanced

    def encode_image(self, image):
        # Encode as JPEG
        _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        byte_data = buffer.tobytes()
        b64_data = base64.b64encode(byte_data).decode("utf-8")
        return byte_data, f"data:image/jpeg;base64,{b64_data}"

    def send_to_api(self, image_bytes):
        files = {
            "image": ("image.jpg", image_bytes, "image/jpeg")
        }
        data = {
            "n_top": "5",
            "version": "v61"
        }
        try:
            response = requests.post(API_URL, files=files, data=data, timeout=120)
            return response
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def extract_confidence(self, response_json):
        try:
            if isinstance(response_json, dict):
                predictions = response_json.get("predictions", {})
                if isinstance(predictions, dict) and len(predictions) > 0:
                    return max(predictions.values())
                elif isinstance(predictions, list) and len(predictions) > 0:
                    return predictions[0].get("confidence", 0)
        except:
            pass
        return 0

    def confidence_fusion(self, original_conf, enhanced_conf):
        return round(max(original_conf, enhanced_conf), 4)

    def process(self, input_source):
        total_start = time.time()
        
        # Load image
        original = self.load_image(input_source)
        
        # Enhance
        enhanced = self.adaptive_enhancement(original)
        
        # Encode images for API and Frontend
        orig_bytes, orig_b64 = self.encode_image(original)
        enh_bytes, enh_b64 = self.encode_image(enhanced)
        
        # API Inference
        print("\nRunning ORIGINAL inference...")
        orig_response = self.send_to_api(orig_bytes)
        orig_json = orig_response.json() if orig_response and orig_response.status_code == 200 else {}
        
        print("Running ENHANCED inference...")
        enh_response = self.send_to_api(enh_bytes)
        enh_json = enh_response.json() if enh_response and enh_response.status_code == 200 else {}
        
        # Confidence
        original_conf = self.extract_confidence(orig_json)
        enhanced_conf = self.extract_confidence(enh_json)
        final_confidence = self.confidence_fusion(original_conf, enhanced_conf)
        
        total_time = round(time.time() - total_start, 2)
        
        result = {
            "success": True,
            "processing_time": total_time,
            "original_confidence": original_conf,
            "enhanced_confidence": enhanced_conf,
            "final_confidence": final_confidence,
            "original_response": orig_json,
            "enhanced_response": enh_json,
            "original_image_b64": orig_b64,
            "enhanced_image_b64": enh_b64
        }
        
        return result
