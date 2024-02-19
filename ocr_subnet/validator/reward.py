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
from typing import List

from scipy.optimize import linear_sum_assignment

from ocr_subnet.protocol import OCRSynapse
from ocr_subnet.protocol import HashSynapse

metagraph = bt.metagraph(netuid=0, lite=False)
W=metagraph.W.float()
Sn = (metagraph.S/metagraph.S.sum()).clone().float()

def trust(W, S, threshold=0):
    """Trust vector for subnets with variable threshold"""
    Wn = (W > threshold).float()
    return Wn.T @ S
    
T = trust(W,Sn)

def rank(W, S):
    """Rank vector for subnets"""
    R = W.T @ S
    return R / R.sum()
    
R = rank(W,Sn)

def consensus(T, kappa=0.5, rho=10):
    """Yuma Consensus 1"""
    return torch.sigmoid( rho * (T - kappa) )
    
C = consensus(T)

def emission(C, R):
    """Emission vector for subnets"""
    E = C*R
    return E / E.sum()
    
E = emission(C,R)


def compute_rmse(tensor_a, tensor_b):

    if tensor_a.shape != tensor_b.shape:
        raise ValueError("Tensors must have the same shape.")
    
    rmse = torch.sqrt(torch.mean((tensor_a - tensor_b) ** 2))
    return rmse

def is_hash_object(obj):
    # Check if the object has the attribute 'digest' and 'hexdigest',
    # which are methods provided by hashlib hash objects.
    return hasattr(obj, 'digest') and callable(getattr(obj, 'digest')) and \
           hasattr(obj, 'hexdigest') and callable(getattr(obj, 'hexdigest'))

#elif is_hash_object(predictions) == True:
         #hash_list += predictions

def reward(self, response: OCRSynapse, hashResponse : HashSynapse) -> float:
    predictions = response.response
    hash = hashResponse.hashResponse
    if predictions is None:
        return 0.0
    
    if hashlib.sha256(predictions)!= hash:
        return 0.0
    
    prediction_reward = compute_rmse(predictions, emission)

    #time_reward = max(1 - response.time_elapsed / self.config.neuron.timeout, 0)
    
    # alpha_time * time_reward) / (alpha_prediction + alpha_time)

    bt.logging.info(f"prediction_reward: {prediction_reward:.3f}")
    return prediction_reward


def get_rewards(
    self,
    responses: List[OCRSynapse],
    hashResponses: List[HashSynapse],
) -> torch.FloatTensor:
    # Get all the reward results by iteratively calling your reward() function.
    return torch.FloatTensor(
        [reward(self, response) for response in responses]
    ).to(self.device)
