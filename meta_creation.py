## Method to finally create one json 
import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

path_json_files = os.getenv("PROJECT_ROOT_PATH")

# def normalize_filename(file_name):
#     return file_name.replace('.jpg.jpg', '.jpg')  # Adjust as necessary

# def combine_descriptions(file_name):

#     # Method to combined items from each preprocessed json file
#     # Input: file_name is the name of the image file being considered
    
#     descriptions = []
#     normalized_file_name = normalize_filename(file_name)
#     print(f"\nChecking for file: {normalized_file_name}")
#     for data in [categories_images, annotations_main, img_to_desc, products_dict, room_to_items, room_to_categories]:
#         # print(f"Checking data source: {data}") 
#         for item in data:
#             # print(f"Processing item: {item}")
#             item_file_name = normalize_filename(item.get('file_name', ''))
#             item_desc = item.get('desc', '')
#             # Check if desc is a dictionary and extract text accordingly
#             if isinstance(item_desc, dict):
#                 # Modify this part based on the structure of your desc field
#                 item_desc = item_desc.get('text', '')  # Adjust key as needed
            
#             # Ensure item_desc is a string before stripping
#             if isinstance(item_desc, str):
#                 item_desc = item_desc.strip()
#             else:
#                 item_desc = ''  # If not a string, set to empty
#             print(f"Comparing JSON file name: {item_file_name} with image file name: {normalized_file_name}")  # Debugging
 
#             if item_file_name == normalized_file_name and item_desc and item_desc.lower() != 'no description':
#                 print(f"Match found for {file_name}, adding description: {item_desc}")  # Debugging
#                 if item_desc not in descriptions:
#                     descriptions.append(item_desc)

#     descriptions = list(set(descriptions))
#     combined = ". ".join(descriptions).replace('..', '.')

#     return combined
def combine_descriptions(file_name):

    # Method to combined items from each preprocessed json file
    # Input: file_name is the name of the image file being considered
    
    descriptions = []
    for data in [categories_images, annotations_main, img_to_desc, products_dict, room_to_items, room_to_categories]:
        for item in data:
            if item['file_name'] == file_name:
                if (len(item['desc']) > 0) & (item['desc'].lower() != 'no description'):
                    print(file_name)
                    if item['desc'] not in descriptions:
                        descriptions.append(item['desc'])
    list(set(descriptions))

    return ". ".join(descriptions).replace('..','.')


## main function
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description= 'Script to merge the description for images genertaed by BLIP and provided by Ikea '
    )
    parser.add_argument(
        "--path_to_categories_dict",
        type = str,
        help = 'path to room category',
        default = 'ikea-master/ikea-master/pickle_processed/categories_dict.json'
    )
    parser.add_argument(
        "--caption_generated",
        type = str,
        help = 'the path for BLIP generated cations in json file',
        default = 'annotations.json'
    )
    parser.add_argument(
        "--ikea_category_img_dict",
        type = str,
        help = 'path to preprocessed categories_images dict json file',
        default = 'ikea-master/ikea-master/pickle_processed/categories_images_dict.json'
    )
    parser.add_argument(
        "--ikea_img_desc_dict",
        type = str,
        help = 'path to preprocessed img to desc json',
        default = 'ikea-master/ikea-master/pickle_processed/img_to_desc.json'
    )
    parser.add_argument(
        "--ikea_products_dict",
        type = str,
        help = 'path to preprocessed product dict json',
        default = 'ikea-master/ikea-master/pickle_processed/products_dict.json'
    )
    parser.add_argument(
        "--path_to_images",
        type = str,
        help = 'path to all the images',
        default = 'ikea-master/ikea-master/images'
    )
    parser.add_argument(
        "--path_to_room_to_item",
        type = str,
        help = 'path to rooms and items in it, useful in many ways',
        default = 'ikea-master/ikea-master/pickle_processed/room_to_items.json'
    )



    # Read argumnets
    args = parser.parse_args()
    # data_path = args.data_path
    caption_generated = args.caption_generated
    ikea_category_img_dict = args.ikea_category_img_dict
    path_to_categories_dict = args.path_to_categories_dict
    ikea_img_desc_dict = args.ikea_img_desc_dict
    ikea_products_dict = args.ikea_products_dict
    path_to_images = args.path_to_images
    path_to_room_to_item = args.path_to_room_to_item
    

    # Reading the mentioned json files:
    #1. caption generated by model:
    with open(os.path.join(path_json_files,caption_generated)) as f:
        annotations_main = json.load(f)
    
    #2. desc provided by ikea: map between images and the category img beong to
    with open(os.path.join(path_json_files,ikea_category_img_dict)) as f:
        categories_images = json.load(f)

    #3. describing object in each image
    with open(os.path.join(path_json_files,ikea_img_desc_dict)) as f:
        img_to_desc = json.load(f)

    #4. describing the products in greater word count
    with open(os.path.join(path_json_files,ikea_products_dict)) as f:
        products_dict = json.load(f)
    
    #5. room to list of items in it
    with open(os.path.join(path_json_files,path_to_room_to_item)) as f:
        room_to_items = json.load(f)
    
    #6. mapping for room theme and type
    with open(os.path.join(path_json_files,path_to_categories_dict)) as f:
        room_to_categories = json.load(f)


    combined_desc = []
    all_file_names = os.listdir(os.path.join(path_json_files,path_to_images))
    for file_name in all_file_names:
        combined_desc.append({
            "file_name" : file_name,
            "desc" : combine_descriptions(file_name)
        })
    
    print('**********final_result************',combined_desc)
    

    with open(os.path.join(path_json_files,'annotations_ikea.json'), 'w') as annotations_file:
        json.dump(combined_desc, annotations_file, indent=4)

    print(f"Annotations file created at: {os.path.join(path_json_files,'annotations_ikea.json')}")

