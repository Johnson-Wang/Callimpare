from itertools import izip
import numpy as np
from traits.has_traits import HasTraits
from traits.trait_types import DictStrAny, List, Str
import cv2 as cv
import os
class ImageSource(HasTraits):
    img_mat = None
    img_name = None
    def load_image(self, filename):
        self.img_name = os.path.basename(filename)
        self.img_mat = cv.imread(filename.encode('gbk'), 0)[::-1]