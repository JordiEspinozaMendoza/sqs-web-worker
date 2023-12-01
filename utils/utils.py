import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()


def getPredictionFromRoboflow(image):
    try:
        image64 = base64.b64encode(image)

        ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
        ROBOFLOW_PROJECT_NAME = os.environ.get("ROBOFLOW_PROJECT_NAME")
        ROBOFLOW_PROJECT_VERSION = os.environ.get("ROBOFLOW_PROJECT_VERSION")

        url = f"https://detect.roboflow.com/{ROBOFLOW_PROJECT_NAME}/{ROBOFLOW_PROJECT_VERSION}"

        payload = image64
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "api_key": ROBOFLOW_API_KEY,
        }

        response = requests.post(url, headers=headers, data=payload, params=params)

        res = response.json()

        detections = []

        for detection in res["predictions"]:
            detections.append(
                {
                    "name": detection["class"],
                    "confidence": detection["confidence"],
                    "xmin": detection["x"] - detection["width"] / 2,
                    "ymin": detection["y"] - detection["height"] / 2,
                    "xmax": detection["x"] + detection["width"] / 2,
                    "ymax": detection["y"] + detection["height"] / 2,
                }
            )

        return detections

    except Exception as e:
        print(e, "getPredictionFromRoboflow")
        return []