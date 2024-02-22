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


import bittensor as bt
from typing import Optional, List
import struct
import hashlib
import base64
from torch import FloatTensor

def hash_tensor(emission):
    bytes = b''
    for f in emission:
        bytes += struct.pack("f",f)
    return base64.encodebytes(hashlib.sha256(bytes).digest())
    
class EmissionSynapse(bt.Synapse):

    # Required request input, filled by sending dendrite caller.
    statement: str

    # Optional request outputs, filled by receiving axon. 
    # Do not write to these directly, use the provided methods.
    response_tensor: Optional[List[float]] = None
    response_hash: Optional[bytes] = None

    def insert_hash_tensor(self, emission: FloatTensor):
        """Inserts a prediction for the next block into the synapse"""
        self.response_hash = hash_tensor(emission)

    def insert_tensor(self, emission: FloatTensor):
        """Inserts the tensor which was sent as a prediction in the previous block into the synapse"""
        if emission is None:
            return
        self.response_tensor = emission.tolist()

    def deserialize(self) -> str:
        """
        Deserialize the miner response.
        """
        return hash_tensor(self.response)
