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

import bittensor as bt

import os
from PIL import Image

from ocr_subnet.protocol import OCRSynapse
from ocr_subnet.validator.reward import get_rewards
from ocr_subnet.utils.uids import get_random_uids
from ocr_subnet.validator.generate import create_invoice
from ocr_subnet.validator.corrupt import corrupt_image

def generate_image(image_type='invoice', corrupt=False):
    """
    Generates a random invoice image to be sent to the miner.

    Returns:
    - PIL.Image: The generated image.

    # TODO: return image and label (i.e. annotations for scoring)
    """
    root_dir = './data/images/'
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    if image_type == 'invoice':
        path = create_invoice(root_dir=root_dir)
    else:
        raise NotImplementedError(f"Image type {image_type} not implemented.")

    if corrupt:
        path = path.replace('.pdf', '_corrupt.pdf')
        path = corrupt_image(path)

    return path


def load_image(path):
    """
    Loads an image from the given path.

    Args:
    - path (str): The path to the image.

    Returns:
    - PIL.Image: The loaded image.
    """
    return Image.open(path)


async def forward(self):
    """
    The forward function is called by the validator every time step.

    It is responsible for querying the network and scoring the responses.

    Args:
        self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

    """

    # get_random_uids is an example method, but you can replace it with your own.
    miner_uids = get_random_uids(self, k=self.config.neuron.sample_size)

    # Create a random image and load it.
    image_path = generate_image()
    image = load_image(image_path)

    # Create synapse object to send to the miner and attach the image.
    # TODO: it's probably not possible to send the image directly, so you'll need to encode it somehow.
    synapse = OCRSynapse(image = image)

    # The dendrite client queries the network.
    responses = self.dendrite.query(
        # Send the query to selected miner axons in the network.
        axons=[self.metagraph.axons[uid] for uid in miner_uids],
        # Pass the synapse to the miner.
        synapse=synapse,
        # All responses have the deserialize function called on them before returning.
        # You are encouraged to define your own deserialization function.
        deserialize=True,
    )

    # Log the results for monitoring purposes.
    bt.logging.info(f"Received responses: {responses}")

    # TODO: We need ground truth labels to score the responses!
    rewards = get_rewards(self, query=self.step, responses=responses)

    bt.logging.info(f"Scored responses: {rewards}")
    # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
    self.update_scores(rewards, miner_uids)
