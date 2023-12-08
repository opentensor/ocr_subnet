# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# TODO(developer): Set your name
# Copyright © 2023 <your name>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import torch
from typing import List
from PIL import Image
from ocr_subnet.protocol import OCRSynapse
from ocr_subnet.validator.utils import get_iou, get_edit_distance, get_font_distance

"""
Loss function for OCR model:

$$ L = \sum_i \alpha_p L^p_i + \alpha_f L^f_i + \alpha_t L^t_i $$

where

$ L^p_i $ is the loss for section i based on positional/layout correctness. This should be zero if the OCR model returns the exact box on the page.

We propose that the positional loss is the intersection over union of the bounding boxes:
$$ L^p_i = IOU(\hat{b}_i, b_i) $$

where $ \hat{b}_i $ is the predicted bounding box and $ b_i $ is the ground truth bounding box.


$ L^f_i $ is the loss for section i based on font correctness. This should be zero if the OCR model returns the exact font for the section, including font family, font size and perhaps even colors.

We propose that the font loss is a delta between the predicted font and the ground truth font plus the square of the difference in font size:
$$ L^f_i = \alpha_f^f (1 - \delta(\hat{f}_i, f_i) )+ \alpha_f^s (\hat{s}_i - s_i)^2 $$

$ L^t_i $ is the loss for section i based on text correctness. This should be zero if the OCR model returns the exact text for the section.

We propose that the text loss is the edit distance between the predicted text and the ground truth text:
$$ L^t_i = ED(\hat{t}_i, t_i) $$

where $ ED $ is the edit distance function. This is equivalent to the Levenshtein distance.

$ \alpha_p, \alpha_f, \alpha_t $ are weights for each of the loss terms. These will impact the difficulty of the OCR challenge as text correctness is likely much easier than position correctness etc.

We will invert the loss to produce a reward which is to be maximized by the miner. The reward is:

$$ R = 1 / L $$

where $ L $ is the loss function defined above. This probably some epsilon to avoid division by zero.
"""


def loss(label: dict, pred: dict, alpha_p=1.0, alpha_f=1.0, alpha_t=1.0):
    """
    Score a section of the image based on the section's correctness.
    Correctness is defined as:
    - the intersection over union of the bounding boxes,
    - the delta between the predicted font and the ground truth font,
    - and the edit distance between the predicted text and the ground truth text.

    Args:
    - label (dict): The ground truth data for the section.
    - pred (dict): The predicted data for the section.

    Returns:
    - float: The score for the section. Bounded between 0 and 1.
    """
    # position loss is IOU of the bounding boxes
    if pred.get('position'):
        position_loss = get_iou(label['position'], pred['position'])
    else:
        # otherwise set to max loss
        position_loss = 1.0

    if pred.get('font'):
        font_loss = get_font_distance(label['font'], pred['font']) # this should actually calculate the font loss
    else:
        font_loss = 1.0

    if pred.get('text'):
        text_loss = get_edit_distance(label['text'], pred['text'])
    else:
        text_loss = 1.0

    return (alpha_p * position_loss + alpha_f * font_loss + alpha_t * text_loss) / (alpha_p + alpha_f + alpha_t)


def reward(image_data: List[dict], response: OCRSynapse) -> float:
    """
    Reward the miner response to the OCR request. This method returns a reward
    value for the miner, which is used to update the miner's score.

    Args:
    - image (List[dict]): The true data underlying the image sent to the miner.
    - response (OCRSynapse): Response from the miner.

    The expected fields in each section of the response are:
    - position (List[int]): The bounding box of the section e.g. [x0, y0, x1, y1]
    - font (dict): The font of the section e.g. {'family': 'Times New Roman', 'size':12}
    - text (str): The text of the section e.g. 'Hello World!'

    Returns:
    - float: The reward value for the miner.
    """
    predictions = response.response
    if predictions is None:
        return 0.0
    # TODO: Add more specific type checking
    """
    We can also build in some deisrable default behaviour in case the miner is unable to do the task in the desired way:
    - If response is a `str`, then we just assume that the order of sections is correct and the text is correct.
    - If response is a `List[str]`, then we assume that the order of sections is correct but the text is not.
    - If response is a `List[dict]`, then we assume that the miner has provided all the information we need.
    """

    predictions_loss = torch.mean([loss(label, pred) for label, pred in zip(image_data, predictions)])

    # TODO: Use max time to calculate time penalty
    alpha_time = 1.0
    time_loss = alpha_time * response.response_time / 10

    # convert loss to reward (invert and scale)
    return 1.0 / (predictions_loss + time_loss + 1e-6)


def get_rewards(
    self,
    image_data: List[dict],
    responses: List[OCRSynapse],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given image and responses.

    Args:
    - image (List[dict]): The true data underlying the image sent to the miner.
    - responses (List[OCRSynapse]): A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given image and responses.
    """
    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [reward(image_data, response) for response in responses]
    ).to(self.device)
