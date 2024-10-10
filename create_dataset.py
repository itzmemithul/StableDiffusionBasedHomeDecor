import os
import json
import datasets

project_root_path = os.environ["PROJECT_ROOT_PATH"]

class ImageDataset(datasets.GeneratorBasedBuilder):
    def _info(self):
        return datasets.DatasetInfo(
            features=datasets.Features({
                'image': datasets.Image(),
                'desc': datasets.Value('string')
            })
        )

    def _split_generators(self, dl_manager):

        train_metadata_path = project_root_path + "/datasets/train/annotations/annotations.json"
        train_images_dir = project_root_path +  "/datasets/train/images"

        validation_metadata_path = project_root_path + "/datasets/val/annotations/annotations.json"
        validation_images_dir = project_root_path +  "/datasets/val/images"

        test_metadata_path = project_root_path + "/datasets/test/annotations/annotations.json"
        test_images_dir = project_root_path +  "/datasets/test/images"

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    'metadata_path': train_metadata_path,
                    'images_dir': train_images_dir
                }
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "metadata_path": validation_metadata_path,
                    "images_dir": validation_images_dir,
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "metadata_path": test_metadata_path,
                    "images_dir": test_images_dir,
                }
            )
        ]

    def _generate_examples(self, metadata_path, images_dir):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        for idx, record in enumerate(metadata):
            yield idx, {
                'image': f"{images_dir}/{record['file_name']}",
                'desc': record['desc']
            }