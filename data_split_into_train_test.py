import os
import random
import shutil
from dotenv import load_dotenv
import json

load_dotenv()

'''
    Method to split datset to test, train, val and standout
'''

# Define number of images for each category
num_test = 100
num_validation = 100
num_standout = 100

project_root_path = os.getenv("PROJECT_ROOT_PATH")


annotations_from_llm_file_path = "annotations_from_llm.json"

## reading json files containing captions:
with open(os.path.join(project_root_path, annotations_from_llm_file_path), 'r') as f:
    data = json.load(f)

## Source path
source_path = os.path.join(project_root_path,'ikea-master/ikea-master/images')

destination_path = os.path.join(project_root_path,'datasets')

## creating directories:
os.makedirs(destination_path,exist_ok=True)
os.makedirs('./datasets/train/images',exist_ok=True)
os.makedirs('./datasets/train/annotations/',exist_ok=True)
os.makedirs('./datasets/test/images',exist_ok=True)
os.makedirs('./datasets/test/annotations/',exist_ok=True)
os.makedirs('./datasets/val/images',exist_ok=True)
os.makedirs('./datasets/val/annotations/',exist_ok=True)
os.makedirs('./datasets/standout/images',exist_ok=True)
os.makedirs('./datasets/standout/annotations/',exist_ok=True)

train_json= []
test_json= []
val_json= []
standout_json= []

# Distribute images and captions into respective folders:
for i, item in enumerate(data):
    if i < num_test:
        shutil.copy2(os.path.join(source_path, item.get('file_name')), os.path.join(destination_path,'test/images/'))
        test_json.append(item)
    elif num_test <= i < num_test + num_validation:
        shutil.copy2(os.path.join(source_path, item.get('file_name')), os.path.join(destination_path,'val/images/'))
        val_json.append(item)
    elif num_test + num_validation <= i < num_test + num_validation + num_standout:
        shutil.copy2(os.path.join(source_path, item.get('file_name')), os.path.join(destination_path,'standout/images/'))
        standout_json.append(item)
    else:
        shutil.copy2(os.path.join(source_path, item.get('file_name')), os.path.join(destination_path,'train/images/'))
        train_json.append(item)

# Writing the json file:
with open(os.path.join(destination_path,'test/annotations/annotations.json'), 'w') as annotations_file:
    json.dump(test_json, annotations_file, indent=4)
with open(os.path.join(destination_path,'val/annotations/annotations.json'), 'w') as annotations_file:
    json.dump(val_json, annotations_file, indent=4)
with open(os.path.join(destination_path,'standout/annotations/annotations.json'), 'w') as annotations_file:
    json.dump(standout_json, annotations_file, indent=4)
with open(os.path.join(destination_path,'train/annotations/annotations.json'), 'w') as annotations_file:
    json.dump(train_json, annotations_file, indent=4)

print("Splitting complete.")