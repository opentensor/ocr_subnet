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

def hash_tensor(emission):
    bytes = []
    for f in emission:
        bytes.extend(struct.pack("f",f))
    return base64.decode(bytes)

class HashSynapse(bt.Synapse):
    needs_hash = True
    needs_tensor = False

    # Required request input, filled by sending dendrite caller. It is a base64 encoded string.
    next_emission_hash: str

    # Emission tensor corresponding to the previously submitted hash
    response = None

    def deserialize(self) -> List[dict]:
        """
        Deserialize the miner response.

        Returns:
        - List[dict]: The deserialized response, which is a list of dictionaries containing the extracted data.
        """
        return self.response
    
class EmissionSynapse(bt.Synapse):
    needs_hash = False
    needs_tensor = True

    # Required request input, filled by sending dendrite caller. It is a base64 encoded string.
    base64_image: str

    # Optional request output, filled by receiving axon.
    response: Optional[str] = None

    def insert_tensor(self, emission):
        self.response = hash_tensor(emission)

    def deserialize(self) -> str:
        """
        Deserialize the miner response.

        Returns:
        - List[dict]: The deserialized response, which is a list of dictionaries containing the extracted data.
        """
        return self.response
