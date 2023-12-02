import requests
import os
import base64
from dotenv import load_dotenv
import sys

load_dotenv()


def getPredictionFromRoboflow(image):
    try:
        ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY")
        ROBOFLOW_PROJECT_NAME = os.environ.get("ROBOFLOW_PROJECT_NAME")
        ROBOFLOW_PROJECT_VERSION = os.environ.get("ROBOFLOW_PROJECT_VERSION")

        url = f"https://detect.roboflow.com/{ROBOFLOW_PROJECT_NAME}/{ROBOFLOW_PROJECT_VERSION}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        params = {
            "api_key": ROBOFLOW_API_KEY,
            "image": image
        }

        response = requests.post(url, headers=headers, params=params)

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
        error = str(e)

        print(error, sys.exc_info()[-1].tb_lineno, getPredictionFromRoboflow)
        return []