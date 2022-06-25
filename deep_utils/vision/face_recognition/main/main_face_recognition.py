import os
from abc import abstractmethod
from deep_utils.utils.pickle_utils.pickles import dump_pickle
from deep_utils.main_abs.main import MainClass
from deep_utils.utils.utils.main import dictnamedtuple
from deep_utils.utils.dir_utils.main import remove_create
from deep_utils.utils.os_utils.os_path import split_extension
from deep_utils.utils.logging_utils.logging_utils import log_print

OUTPUT_CLASS = dictnamedtuple(
    "FaceRecognizer", ["encodings"])


class FaceRecognition(MainClass):
    def __init__(self, name, file_path, **kwargs):
        super().__init__(name, file_path=file_path, **kwargs)
        self.output_class = OUTPUT_CLASS

    @abstractmethod
    def extract_faces(self, img, is_rgb, get_time=False) -> OUTPUT_CLASS:
        pass

    def extract_dir(
            self,
            image_directory,
            extensions=(".png", ".jpg", ".jpeg"),
            res_dir=None,
            remove_res_dir=False,
    ):
        import cv2
        results = dict()
        remove_create(res_dir, remove=remove_res_dir)
        for item_name in os.listdir(image_directory):
            _, extension = os.path.splitext(item_name)
            if extension in extensions:
                img_path = os.path.join(image_directory, item_name)
                img = cv2.imread(img_path)
                result = self.extract_faces(img, is_rgb=False, get_time=True, )
                print(f'{img_path}: time= {result["elapsed_time"]}')

                if res_dir:
                    dump_pickle(os.path.join(res_dir, split_extension(item_name, extension=".pkl")), result.encodings)
                results[img_path] = result['encodings']
        return results

    def extract_dir_of_dir(
            self,
            input_directory,
            image_dir_name="cropped",
            encoding_dir_name="encodings",
            extensions=(".png", ".jpg", ".jpeg"),
            remove_encoding=True,
    ):
        for directory_name in sorted(os.listdir(input_directory)):
            directory_path = os.path.join(input_directory, directory_name)
            images_dir = os.path.join(directory_path, image_dir_name)
            cropped_dir = os.path.join(directory_path, encoding_dir_name)
            if not os.path.isdir(directory_path) or not os.path.isdir(images_dir):
                log_print(None, f"Skip {directory_path}...")
            remove_create(cropped_dir, remove=remove_encoding)
            self.extract_dir(images_dir, extensions=extensions, res_dir=cropped_dir, remove_res_dir=remove_encoding)