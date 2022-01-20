import torch
from torch import no_grad
from typing import Any, Dict, Optional, Union
from nomeroff_net.image_loaders import BaseImageLoader
from nomeroff_net.pipelines.base import Pipeline
from nomeroff_net.tools import unzip
from nomeroff_net.pipes.number_plate_localizators.yolo_v5_detector import Detector


class NumberPlateLocalization(Pipeline):
    """
    Number Plate Localization
    """

    def __init__(self,
                 task,
                 image_loader: Optional[Union[str, BaseImageLoader]],
                 path_to_model="latest",
                 **kwargs):
        super().__init__(task, image_loader, **kwargs)
        self.detector = Detector()
        self.detector.load(path_to_model)

    def sanitize_parameters(self, img_size=None, stride=None, min_accuracy=None, **kwargs):
        preprocess_parameters = {}
        postprocess_parameters = {}
        if img_size is not None:
            preprocess_parameters["img_size"] = img_size
        if stride is not None:
            preprocess_parameters["stride"] = stride
        if min_accuracy is not None:
            postprocess_parameters["min_accuracy"] = min_accuracy
        return preprocess_parameters, {}, postprocess_parameters

    def __call__(self, images: Any, **kwargs):
        return super().__call__(images, **kwargs)

    def preprocess(self, inputs: Any, **preprocess_parameters: Dict) -> Any:
        images = [self.image_loader.load(item) for item in inputs]
        model_inputs = self.detector.normalize_imgs(images, **preprocess_parameters)
        return unzip([model_inputs, images])

    @no_grad()
    def forward(self, inputs: Any, **forward_parameters: Dict) -> Any:
        model_inputs, images = unzip(inputs)
        x = torch.cat(model_inputs, dim=0)
        model_outputs = self.detector.model(x)[0]
        shape = model_outputs.shape
        model_outputs = model_outputs.reshape((shape[0], 1, shape[1], shape[2]))
        return unzip([model_outputs, model_inputs, images])

    def postprocess(self, inputs: Any, **postprocess_parameters: Dict) -> Any:
        model_outputs, images, orig_images = unzip(inputs)
        orig_img_shapes = [img.shape for img in orig_images]
        output = self.detector.postprocessing(model_outputs,
                                              images,
                                              orig_img_shapes,
                                              **postprocess_parameters)
        return unzip([output, orig_images])
