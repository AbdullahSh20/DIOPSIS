import argparse
import random
from pathlib import Path
import json
import cv2
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, Dense, Flatten
import numpy as np

def build_model(input_shape):
    base_model = MobileNetV2(input_shape=input_shape, include_top=False)
    x = base_model.output
    x = Conv2D(128, (3, 3), activation='relu')(x)
    x = Flatten()(x)
    outputs = Dense(5, activation='sigmoid')(x)  # 4 for bounding box, 1 for class probability

    model = Model(inputs=base_model.input, outputs=outputs)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def predict(inputs, model, weights_path):
    model.load_weights(weights_path)
    inputs = list(inputs)
    ids = [Path(input).stem for input in inputs]
    
    results = []
    for img_path in inputs:
        img = cv2.imread(str(img_path))
        img_resized = cv2.resize(img, (224, 224))
        img_resized = np.expand_dims(img_resized, axis=0)
        
        prediction = model.predict(img_resized)[0]
        
        x_min = int(prediction[0] * img.shape[1])
        y_min = int(prediction[1] * img.shape[0])
        x_max = int(prediction[2] * img.shape[1])
        y_max = int(prediction[3] * img.shape[0])
        probability = prediction[4]
        
        if probability > 0.5:  # Assuming 0.5 as threshold for detection
            result = {
                "annotations": [
                    {
                        "labels": [
                            {
                                "probability": probability,
                                "name": "Object",
                            }
                        ],
                        "shape": {
                            "x": x_min,
                            "y": y_min,
                            "width": x_max - x_min,
                            "height": y_max - y_min,
                        }
                    }
                ]
            }
        else:
            result = {"annotations": []}  # No objects detected
        
        results.append(result)
    
    result = [{"id": cid, "result": cresult} for cid, cresult in zip(ids, results)]
    
    destination_dir = Path("/output/")
    destination_dir.mkdir(parents=True, exist_ok=True)
    for res in result:
        filename = destination_dir / f"{res['id']}.json"
        with open(str(filename), "w") as file:
            json.dump(res['result'], file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", help="Path to input images")
    parser.add_argument("output_path", help="Path to output json")
    parser.add_argument("weights_path", help="Path to model weights")
    args = parser.parse_args()

    input_shape = (224, 224, 3)
    model = build_model(input_shape)
    predict(Path(args.input_path).glob("*.jpg"), model, args.weights_path)