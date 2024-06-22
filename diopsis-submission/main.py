import argparse
from pathlib import Path
import pandas
import pickle
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import pandas as pd
import torch.nn as nn
from torchvision.models import efficientnet_v2_m
import torch

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.model = efficientnet_v2_m(weights=None)

        # Freeze the weights of the model
        for param in self.model.parameters():
            param.requires_grad = False

        # Unfreeze the last layer
        for param in self.model.classifier.parameters():
            param.requires_grad = True
        
        # Add a classfier layer for each level
        self.levels = []
        for level in range(1, 7):
            self.levels.append(nn.Sequential(
                nn.Linear(1000, 512),
                nn.ReLU(),
                nn.Linear(512, 256),
                nn.ReLU(),
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, level)
            ))


    def forward(self, x):
        x = self.model(x)
        
        # Get the prediction for each level
        predictions = {}
        for i, level in enumerate(self.levels):
            predictions[f'level_{i + 1}'] = level(x)

        return predictions


def predict(inputs: Path):    
    inputs = list(inputs)
    predictions = {
        "image_uid": [],
        "level_0": [],
        "level_0_probability": [],
        "level_1": [],
        "level_1_probability": [],
        "level_2": [],
        "level_2_probability": [],
        "level_3": [],
        "level_3_probability": [],
        "level_4": [],
        "level_4_probability": [],
        "level_5": [],
        "level_5_probability": []
    }

    model = Model()
    model.load_state_dict(torch.load('model.pth', map_location=torch.device('cpu')))
    model.eval()

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    encoded_names = pd.read_csv('name_to_ancestors_with_levels.csv')

    for input in inputs:
        image = Image.open(input).convert("RGB")
        image = transform(image).to( "cpu")

        # predict
        output = model(image.unsqueeze(0))
        i = 0
        for key, value in output.items():
            # Extract the value of the encoded name that matches the maximum value of the output
            encoded_name_max = output[f'level_{i+1}'].argmax().item()

            # Apply the first condition: matching 'encoded_name'
            condition_1 = (encoded_names['encoded_name'] == encoded_name_max)

            # Apply the second condition: matching 'level'
            condition_2 = (encoded_names['level'] == i + 1)

            # Combine the conditions
            combined_condition = condition_1 & condition_2

            # Use the combined condition to filter the DataFrame and select the 'name' value
            name = encoded_names[combined_condition]['name'].values[0]
            probability = F.softmax(value, dim=1).max().item()
            if name[0:4] == 'None':
                name = ""
                probability = ""

            predictions[f'level_{i}'].append(name)
            predictions[f'level_{i}_probability'].append(probability)
            i += 1

        predictions["image_uid"].append(input.stem)


    return mapping_to_csv(predictions)

def mapping_to_csv(values: dict[str: any]):
    columns = ["image_uid","level_0","level_0_probability","level_1","level_1_probability","level_2","level_2_probability","level_3","level_3_probability","level_4","level_4_probability","level_5","level_5_probability"]

    return pandas.DataFrame(columns=columns, data=values)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input_path", help="Path to input images"
    )

    parser.add_argument(
        "output_path", help="Path to output csv"
    )

    args = parser.parse_args()

    predict(Path(args.input_path).glob("*.jpg")).to_csv(args.output_path, index=False)
