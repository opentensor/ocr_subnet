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
import collections as c

class MinerSubmissions:
    """
    Contains deques of miner responses, with timestamps. The newest submission is on the left.
    """
    def __init__(self, cutoff):
        self.cutoff = cutoff
        self.miners = {}
    
    class Submission:
        def __init__(time, answer):
            self.time = time
            self.answer = answer

    def insert(self, miner_uid, cid, current_time, answer):
        questions = self.miners.get(miner_uid)
        if questions is None:
            self.miners[miner_uid] = {}
            questions = self.miners[miner_uid]
        deq = questions.get(cid)
        if deq is None:
            questions[cid] = c.deque()
            deq = questions[cid]
        if deq[-1].answer == answer:
            return
        else:
            deq.appendleft(Submission(current_time, answer))

    def get(self, miner_uid, cid, current_time):
        questions = self.miners.get(miner_uid)
        if questions is None:
            return None
        deq = questions.get(cid)
        if deq is None:
            return None
        result = None
        for sub in deq:
            if current_time - sub.time > self.cutoff:
                result = sub.answer
                break
        questions.pop(cid) # Clean up the results, they won't be needed
        return result


    

import ocr_subnet

# import base validator class which takes care of most of the boilerplate
from ocr_subnet.base.validator import BaseValidatorNeuron
from ocr_subnet.validator.reward import EmissionSource

RETRY_TIME = 5 # In seconds
CUTOFF = 7200 # Roughly a day

def retry_to_effect(url):
    try:
        return requests.get(url).json()
    except json.decoder.JSONDecodeError:
        time.sleep(RETRY_TIME)
        return retry_to_effect(url)

def get_answer(market):
    toks = market["tokens"]
    if toks[0]["winner"]:
        return 1
    elif toks[1]["winner"]:
        return 2
    else:
        return None

class Validator(BaseValidatorNeuron):
    """
    Validator neuron class.

    This class inherits from the BaseValidatorNeuron class, which in turn inherits from BaseNeuron. The BaseNeuron class takes care of routine tasks such as setting up wallet, subtensor, metagraph, logging directory, parsing config, etc. You can override any of the methods in BaseNeuron if you need to customize the behavior.

    This class provides reasonable default behavior for a validator such as keeping a moving average of the scores of the miners and using them to set weights at the end of each epoch. Additionally, the scores are reset for new hotkeys at the end of each epoch.
    """

    def __init__(self, config=None, override_cutoff = False):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()
        if override_cutoff:
            self.blocktime = CUTOFF
        else:
            self.blocktime = 1
        self.active_markets = {}
        self.submissions = MinerSubmissions(CUTOFF)

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
                    settled_markets.append(check)
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
        synapse = ocr_subnet.protocol.EventPredictionSynapse(self.active_markets)

        # The dendrite client queries the network.
        responses = self.dendrite.query(
            # Send the query to selected miner axons in the network.
            axons=[self.metagraph.axons[uid] for uid in miner_uids],
            # Pass the synapse to the miner.
            synapse=synapse,
            # Do not deserialize the response so that we have access to the raw response.
            deserialize=False,
        )

        # Update answers
        for (uid, resp) in zip(miner_uids, responses):
            for (cid, ans) in resp.events:
                self.submissions.insert(uid, cid, self.blocktime, ans)

        bt.logging.debug(f"Received responses: {responses}")
        bt.logging.info("Received responses")

        # Score events
        for market in settled_markets:
            scores = []
            for uid in miner_uids:
                ans = self.submissions.get(uid, market["condition_id"], self.blocktime)
                if ans is None or ans == 0:
                    scores.append(0.5)
                else:
                    correct_ans = get_answer(market)
                    if correct_ans == ans:
                        scores.append(1)
                    else:
                        scores.append(0)
            self.update_scores(scores, miner_uids)

        # Update the scores based on the rewards. You may want to define your own update_scores function for custom behavior.
        self.update_scores(rewards, miner_uids)


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
