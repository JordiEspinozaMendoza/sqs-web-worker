import cv2
import numpy as np
import base64

import io
from matplotlib import pyplot as plt


def labelImage(image, detections):
    try:
        image = np.array(image)

        for coordinates in detections:
            xmin = int(coordinates["xmin"])
            ymin = int(coordinates["ymin"])
            xmax = int(coordinates["xmax"])
            ymax = int(coordinates["ymax"])
            confidence = coordinates["confidence"]
            name = coordinates["name"]

            label = f"{name} {confidence:.2f}"

            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 4)

            cv2.putText(
                image,
                label,
                (xmin, ymin - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 0),
                1,
            )

        return cv2.imencode(".jpg", image)[1].tobytes()

    except Exception as e:
        print(e, "labelImage")
        return []