# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

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
import bittensor as bt
import hashlib
import math
from typing import List

from scipy.optimize import linear_sum_assignment

class EmissionSource:
    def __init__(self):
        self.metagraph = bt.metagraph(netuid=1, lite=False, sync=False)
        self.emission = None

    def sync(self):
        self.metagraph.sync()
        self.emission = None

    def calculate_emission(self):
        if self.emission:
            return self.emission
        self.emission = self.metagraph.E.float()
        return self.emission


def compute_rmse(tensor_a, tensor_b):

    if tensor_a.shape != tensor_b.shape:
        raise ValueError("Tensors must have the same shape.")
    
    rmse = torch.sqrt(torch.mean((tensor_a - tensor_b) ** 2))
    bt.logging.debug(f"Got rmse: {rmse}")
    return rmse

def reward(self, unhash, hash, emission) -> float:
    predictions = unhash
    if predictions is None or hash is None:
        return 0.0
    
    if hash_tensor(predictions) != hash:
        return 0.0
    
    #print("PRED:", emission, predictions) # DEBUG
    prediction_reward = 0.0 - compute_rmse(predictions, emission)
    c = 1.0 # scaling factor
    scaled_reward = torch.atan(c*prediction_reward) + math.pi/2
    
    #time_reward = max(1 - response.time_elapsed / self.config.neuron.timeout, 0)
    
    # alpha_time * time_reward) / (alpha_prediction + alpha_time)

    bt.logging.info(f"prediction_reward: {scaled_reward:.3f}")
    return scaled_reward


def get_rewards(
    self,
    hashes,
    unhashed,
    emission,
) -> torch.FloatTensor:
    # Get all the reward results by iteratively calling your reward() function.
    #print("Calculating rewards:", hashes, unhashed)
    return torch.FloatTensor(
        [reward(self, unhash, hashes.get(uid), emission) for (uid, unhash) in unhashed.items()]
    ).to(self.device)
