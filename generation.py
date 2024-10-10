import os
import json
from PIL import Image
import torch
# from torchvision import transforms
from transformers import BlipProcessor, BlipForConditionalGeneration
from alive_progress import alive_bar
import time
from dotenv import load_dotenv

load_dotenv()

project_root_path = os.getenv("PROJECT_ROOT_PATH")
print(f"PROJECT_ROOT_PATH: {project_root_path}")  # Debug print


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
objects_extraction_dir = 'ikea-master/ikea-master/images'
annotation_path = 'ikea-master/ikea-master/ikea_processed_data'

def generate_caption(image_path):
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(raw_image, return_tensors="pt").to(device)

    generation_args = {
    "max_length": 500,  # Maximum length of the caption
    "num_beams": 5,    # Beam search with 5 beams
    "temperature": 1.0, # Sampling temperature
    "top_k": 50,       # Top-k sampling
    "top_p": 0.95,     # Top-p (nucleus) sampling
    "no_repeat_ngram_size": 2  # Prevent repetition of 2-grams
    }

    out = model.generate(**inputs, **generation_args)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

annotations = []

for root, dirs, files in os.walk(objects_extraction_dir):
    for file in files:
        if file.lower().endswith(('png', 'jpg', 'jpeg')):
            image_path = os.path.join(root, file)
            caption = generate_caption(image_path)
            annotations.append({"file_name": file, "desc": caption})
            # time.sleep(.001)
            # bar()

annotations_file_path = os.path.join(annotation_path, 'annotations_trial.json')
with open(annotations_file_path, 'w') as annotations_file:
    json.dump(annotations, annotations_file, indent=4)

print(f"Annotations file created at: {annotations_file_path}")