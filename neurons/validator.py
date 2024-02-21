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

import ocr_subnet

# import base validator class which takes care of most of the boilerplate
from ocr_subnet.base.validator import BaseValidatorNeuron
from ocr_subnet.validator.reward import EmissionSource

class Validator(BaseValidatorNeuron):
    """
    OCR validator neuron class.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()

        self.image_dir = './data/images/'
        self.emissions = EmissionSource()
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

    async def forward(self, hashResponse):
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

        # get_random_uids is an example method, but you can replace it with your own.
        miner_uids = ocr_subnet.utils.uids.get_random_uids(self, k=min(self.config.neuron.sample_size, self.metagraph.n.item()))

        # make a hash from the timestamp
        #filename = hashlib.md5(str(time.time()).encode()).hexdigest()

        # Create a random image and load it.
        #image_data = ocr_subnet.validator.generate.invoice(path=os.path.join(self.image_dir, f"{filename}.pdf"), corrupt=True)

        # Create synapse object to send to the miner and attach the image.
        synapse = ocr_subnet.protocol.HashSynapse(next_emission_hash = 'base64-encoded Sha256 hash of the next emission')

        # The dendrite client queries the network.
        responses = self.dendrite.query(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Pass the synapse to the miner.
            synapse=synapse,
            # Do not deserialize the response so that we have access to the raw response.
            deserialize=False,
        )
        previous_uids = self.previous_uids
        self.previous_uids = {}
        for (uid, resp) in zip(miner_uids, responses):
            if resp.response:
                self.previous_uids[uid] = resp.response["hash"]

        synapse = ocr_subnet.protocol.EmissionSynapse(emission = 'emission tensor corresponding to previously sent hash')
        #synapses = []
        #for resp in previous_uids:
        #    synapses.append(ocr_subnet.protocol.HashSynapse(base64_image = 'tensor corresponding to hash: {}'.format(resp["hash"])))

        check_responses = self.dendrite.query(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in previous_resp.keys()],
            # Pass the synapse to the miner.
            synapse=synapse,
            # Do not deserialize the response so that we have access to the raw response.
            deserialize=False,
        )
        unhashed = {}
        for (uid, resp) in zip(previous_resp.keys(), check_responses):
            if resp.response:
                unhashed[uid] = resp.response

        # Log the results for monitoring purposes.
        bt.logging.info(f"Received responses: {responses}")
        bt.logging.info(f"Received responses: {check_responses}")
        self.emissions.sync()
        e = self.emissions.calculate_emission()
        rewards = ocr_subnet.validator.reward.get_rewards(self, previous_uids, unhashed, e)

        bt.logging.info(f"Scored responses: {rewards}")

        miner_uids = [uid for uid in unhashed.keys()]
        # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
        self.update_scores(rewards, miner_uids)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
