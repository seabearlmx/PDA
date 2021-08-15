import numpy as np
import os.path as osp
from padan.utils import project_root
from padan.utils.serialization import json_load
from padan.dataset.base_dataset import BaseDataset
from PIL import Image

DEFAULT_INFO_PATH = project_root / 'advent/dataset/cityscapes_list/info.json'
ssl_dir = ''
class CityscapesDataSet(BaseDataset):
    def __init__(self, root, list_path, set='val',
                 max_iters=None,
                 crop_size=(321, 321), mean=(128, 128, 128),
                 load_labels=True,
                 info_path=DEFAULT_INFO_PATH, labels_size=None):
        super().__init__(root, list_path, set, max_iters, crop_size, labels_size, mean)

        # self.set = set
        self.train_label_size = crop_size
        self.load_labels = load_labels
        self.info = json_load(info_path)
        self.class_names = np.array(self.info['label'], dtype=np.str)
        self.mapping = np.array(self.info['label2train'], dtype=np.int)
        self.map_vector = np.zeros((self.mapping.shape[0],), dtype=np.int64)
        for source_label, target_label in self.mapping:
            self.map_vector[source_label] = target_label

    def get_metadata(self, name):
        img_file = self.root / 'leftImg8bit' / self.set / name
        label_name = name.replace("leftImg8bit", "gtFine_labelIds")
        label_file = self.root / 'gtFine' / self.set / label_name
        return img_file, label_file

    def map_labels(self, input_):
        return self.map_vector[input_.astype(np.int64, copy=False)]

    def __getitem__(self, index):
        img_file, label_file, name = self.files[index]
        label = self.get_labels(label_file)
        # print(label.shape)
        label = self.map_labels(label).copy()
        image = self.get_image(img_file)
        image = self.preprocess(image)
        if len(ssl_dir) > 0 and self.set == 'train':
            label = Image.open(osp.join(ssl_dir, name.split('/')[-1]))
            label = label.resize(self.train_label_size, Image.NEAREST)
            label = np.asarray(label, np.int64)
            return image.copy(), label.copy(), np.array(image.shape), name
        return image.copy(), label, np.array(image.shape), name
