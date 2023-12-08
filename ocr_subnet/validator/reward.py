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


def score_section(image: Image, section: dict, alpha_p=1.0, alpha_f=1.0, alpha_t=1.0):
    """
    Score a section of the image based on the section's correctness.
    Correctness is defined as:
    - the intersection over union of the bounding boxes,
    - the delta between the predicted font and the ground truth font,
    - and the edit distance between the predicted text and the ground truth text.

    Args:
    - section (dict): The section of the image to score.

    Returns:
    - float: The score for the section.
    """
    # position loss is IOU of the bounding boxes
    rect1 = section.get('position')
    if rect1:
        position_loss = get_iou(rect1, image.position)
    else:
        # otherwise set to max loss
        position_loss = 1.0

    font1 = section.get('font')
    if font1:
        font_loss = get_font_distance(font1, image.font) # this should actually calculate the font loss
    else:
        font_loss = 1.0

    text1 = section.get('text')
    if text1:
        text_loss = get_edit_distance(text1, image.text)

    # TODO: convert loss to reward (invert and scale)
    # TODO: add time penalty
    return alpha_p * position_loss + alpha_f * font_loss + alpha_t * text_loss


def reward(image: Image, response: List[dict]) -> float:
    """
    Reward the miner response to the OCR request. This method returns a reward
    value for the miner, which is used to update the miner's score.

    Args:
    - image (Image): The image sent to the miner.
    - response (List[dict]): Response from the miner.
    
    The expected fields in each section of the response are:
    - position (List[int]): The bounding box of the section e.g. [10, 20, 30, 40]
    - font (dict): The font of the section e.g. {'family': 'Times New Roman', 'size':12}
    - text (str): The text of the section e.g. 'Hello World!'

    Returns:
    - float: The reward value for the miner.
    """

    return sum(score_section(section) for section in response)


def get_rewards(
    self,
    image: Image,
    responses: List[List[dict]],
) -> torch.FloatTensor:
    """
    Returns a tensor of rewards for the given image and responses.

    Args:
    - image (Image): The image sent to the miner.
    - responses (List[List[dict]]): A list of responses from the miner.

    Returns:
    - torch.FloatTensor: A tensor of rewards for the given image and responses.
    """
    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [reward(image, response) for response in responses]
    ).to(self.device)
