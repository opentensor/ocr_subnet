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

import os
import time
import hashlib
import bittensor as bt
import torch

import ocr_subnet

# import base validator class which takes care of most of the boilerplate
from ocr_subnet.base.validator import BaseValidatorNeuron
from ocr_subnet.validator.reward import EmissionSource

RETRY_TIME = 5 # In seconds

def retry_to_effect(url):
    try:
        return requests.get(url).json()
    except json.decoder.JSONDecodeError:
        time.sleep(RETRY_TIME)
        return retry_to_effect(url)

class Validator(BaseValidatorNeuron):
    """
    Validator neuron class.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

        self.blocktime = 1
        self.active_markets = {}

    def get_active_markets(self):
        first = True
        cursor = None
        while cursor != "LTE=":
            try:
                if first:
                    resp = requests.get("https://clob.polymarket.com/markets")
                    nxt = resp.json()
                    first = False
                else:
                    resp = requests.get("https://clob.polymarket.com/markets?next_cursor={}".format(cursor))
                    nxt = resp.json()
                cursor = nxt["next_cursor"]
                for mart in nxt["data"]:
                    self.active_markets[mart["condition_id"]] = idx
            except json.decoder.JSONDecodeError:
                print("Got error, retrying...")
                #print(resp.text)
                time.sleep(1)
        settled_markets = []
        for (cid, seq) in self.active_markets.items():
            if seq != idx:
                check = retry_to_effect("https://clob.polymarket.com/markets/{}".format(cid))
                if check["closed"]:
                    settled_markets.append(cid)
        for cid in settled_markets:
            self.active_markets.pop(cid)
        return settled_markets

    async def forward(self):
        """
        The forward function is called by the validator every time step.
        
        COMMENT - we want this to happen every tempo / epoch actually not every time step

        It consists of 3 important steps:
        - Generate a challenge for the miners (in this case it creates a synthetic invoice image)
        - Query the miners with the challenge
        - Score the responses from the miners

        Args:
            self (:obj:`bittensor.neuron.Neuron`): The neuron object which contains all the necessary state for the validator.

        """
        miner_uids = ocr_subnet.utils.uids.get_all_uids(self)

        #update markets
        settled_markets = self.get_active_markets()

        # Create synapse object to send to the miner.
        synapse = ocr_subnet.protocol.EmissionSynapse(self.active_markets)

        # The dendrite client queries the network.
        responses = self.dendrite.query(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Pass the synapse to the miner.
            synapse=synapse,
            # Do not deserialize the response so that we have access to the raw response.
            deserialize=False,
        )

        # Fetch previous responses and record the new ones
        previous_uids = self.previous_uids
        self.previous_uids = {}
        new_responses = {}
        for (uid, resp) in zip(miner_uids, responses):
            if resp.response_hash:
                self.previous_uids[uid.tolist()] = resp.response_hash
            if resp.response_tensor:
                new_responses[uid.tolist()] = torch.tensor(resp.response_tensor)

        bt.logging.debug(f"Received responses: {responses}")
        bt.logging.info("Received responses")
        if previous_uids is None:
            return

        # Calculate rewards
        rewards = ocr_subnet.validator.reward.get_rewards(self, previous_uids, new_responses, residue)

        bt.logging.info(f"Scored responses: {rewards}")

        # Redefine miner uids so they correspond to the rewards
        miner_uids = [uid for uid in new_responses.keys()]

        # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
        self.update_scores(rewards, miner_uids)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
