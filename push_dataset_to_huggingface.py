import os
from datasets import load_dataset
from dotenv import load_dotenv

load_dotenv()

# Set this environment variable in you local
project_root_path = os.getenv("PROJECT_ROOT_PATH")
hugging_face_user = os.getenv("HUGGING_FACE_USERNAME")

train_annotations_file_path = project_root_path + "/datasets/train/annotations/annotations.json"
test_annotations_file_path = project_root_path + "/datasets/test/annotations/annotations.json"
validation_annotations_file_path = project_root_path + "/datasets/val/annotations/annotations.json"

data_files = {"train":train_annotations_file_path, "test":test_annotations_file_path, "validation":validation_annotations_file_path}
dataset = load_dataset(project_root_path + '/create_dataset.py', data_files= data_files)

dataset.push_to_hub(hugging_face_user + "ikea_dataset")

