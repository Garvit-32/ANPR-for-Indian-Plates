import cv2
import torch
import numpy as np
from func import *
from lprnet import *
from torchvision import transforms

transformation = transforms.Compose(
    [transforms.ToPILImage(), transforms.ToTensor()])


def normalize(image):
    return transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])(
        transformation(image)
    )


def preprocess_image(image):

    image = normalize(image)
    return torch.unsqueeze(image, dim=0)


def runner(frame, model, lpr_weights):

    frame = cv2.resize(frame, (1920, 1080))
    frame1 = frame
    image = preprocess_image(frame)
    debug_program = True
    cuda = False
    # if torch.cuda.is_available():
    #     image = image.cuda()

    with torch.no_grad():
        prediction = model(image, (1080, 1920))
        prediction = (
            torch.argmax(prediction["output"], dim=1)
            .cpu()
            .squeeze(dim=0)
            .numpy()
            .astype(np.uint8)
        ).reshape(frame.shape[0], frame.shape[1], 1)

        cropped_images, coordinates, centroid = plate_cropper(
            prediction, frame)
        final_image = frame1
        if len(cropped_images) != 0:
            labels = get_lprnet_preds(cropped_images, lpr_weights, cuda)
        data_dictionary = {}
        if debug_program:
            if len(cropped_images) != 0:
                data_dictionary = details(
                    prediction, labels, coordinates, centroid)
                final_image = overlay_colour(prediction, frame, centroid)
                final_image = write_string(
                    prediction, frame, coordinates, centroid, labels
                )

        return final_image, data_dictionary
