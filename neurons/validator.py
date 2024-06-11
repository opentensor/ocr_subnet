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

import asyncio
import random
import time
import aiohttp
import bittensor as bt
import torch
import collections as c
import requests
import json
import infinite_games

# import base validator class which takes care of most of the boilerplate
from infinite_games.base.validator import BaseValidatorNeuron
from infinite_games.events.azuro import AzuroEventProvider
from infinite_games.events.base import EventStatus, ProviderEvent

RETRY_TIME = 5 # In seconds
#CUTOFF = 7200 # Roughly a day
CUTOFF = 10


class MinerSubmissions:
    """
    Contains deques of miner responses, with timestamps. The newest submission is on the left.
    """
    def __init__(self, cutoff):
        self.cutoff = cutoff
        self.miners = {}
    
    class Submission:
        def __init__(self, time, answer):
            self.time = time
            self.answer = answer

    def insert(self, miner_uid_t, cid, current_time, answer):
        miner_uid = int(miner_uid_t)
        questions = self.miners.get(miner_uid)
        if questions is None:
            self.miners[miner_uid] = {}
            questions = self.miners[miner_uid]
        deq = questions.get(cid)
        if deq is None:
            questions[cid] = c.deque()
            deq = questions[cid]
        if len(deq) > 0 and deq[-1].answer == answer:
            return
        else:
            deq.appendleft(self.Submission(current_time, answer))

    def get(self, miner_uid_t, cid, current_time):
        miner_uid = int(miner_uid_t)
        questions = self.miners.get(miner_uid)
        if questions is None:
            return None
        deq = questions.get(cid)
        if deq is None:
            return None
        result = None
        for sub in deq:
            if current_time - sub.time >= self.cutoff:
                result = sub.answer
                break
        questions.pop(cid) # Clean up the results, they won't be needed
        return result



async def retry_to_effect(session, url):
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        await asyncio.sleep(RETRY_TIME)


def get_answer(market):
    toks = market["tokens"]
    if toks[0]["winner"]:
        return 1
    elif toks[1]["winner"]:
        return 2
    else:
        return None


async def crawl_market(session, cid, seq, blocktime):
    if seq != blocktime:
        # Uncomment this to see events fired
        # bt.logging.info("Event fired: {}".format(cid))
        check = await retry_to_effect(session, "https://clob.polymarket.com/markets/{}".format(cid))
        # from pprint import pprint
        # pprint(check)
        # print(check.get('market_slug'), 'Ends: ', check.get('end_date_iso'), ' Options: ', ','.join((map(lambda t: t.get('outcome', ''), check.get('tokens', [])))))

        # pprint(check.get('questions'),check['tokens'])
        # if cid == "0x002a797edf040e8a053e62b26d85a0292df091c5cacb303ae31407c8a050a32c":
        if not check:
            bt.logging.error(f"Error fetching event {cid}, skip.")
            return
        if check.get('market_slug') == "will-a-republican-win-maryland-us-senate-election":
            bt.logging.info("Event resolved (debug): {}".format(cid))
            check["closed"] = True
            check["tokens"][0]["winner"] = True
            # print(check)
            # settled_markets.append(check)
        return check


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
        self.active_markets = {}
        self.submissions = MinerSubmissions(CUTOFF)
        self.blocktime = 0
        self.event_provider = AzuroEventProvider()
        self.event_provider.on_event_updated_hook(self.on_event_update)
        loop = asyncio.get_event_loop()
        loop.create_task(self.event_provider.listen_events())

    def on_event_update(self, pe: ProviderEvent):
        if pe.status == EventStatus.SETTLED:
            miner_uids = infinite_games.utils.uids.get_all_uids(self)

            scores = []
            for uid in miner_uids:
                ans = pe.miner_predictions.get(uid)
                if ans is None:
                    scores.append(0)
                else:
                    ans = max(0, min(1, ans))  # Clamp the answer
                    correct_ans = pe.answer
                    if correct_ans == 2:
                        scores.append(ans**2)
                    elif correct_ans == 1:
                        scores.append((1-ans)**2)
                    else:
                        scores.append(0)
                        bt.logging.warning(f"Unknown result from market: {pe.event_type} - {pe.event_id}")
            self.update_scores(torch.FloatTensor(scores), miner_uids)

    async def forward(self):
        """
        The forward function is called by the validator every time step.

        """

        block_start = self.block
        miner_uids = infinite_games.utils.uids.get_all_uids(self)
        # update markets

        bt.logging.info("Syncing provider market events...")
        await self.event_provider.sync_events()

        # Create synapse object to send to the miner.
        synapse = infinite_games.protocol.EventPredictionSynapse()
        synapse.init(list(self.event_provider.registered_events.values()))
        # print("Synapse body hash", synapse.computed_body_hash)
        bt.logging.info(f'Axons: {len(self.metagraph.axons)}')
        for axon in self.metagraph.axons:
            bt.logging.info(f'IP: {axon.ip}, hotkey id: {axon.hotkey}')

        bt.logging.info("Querying miners... ")
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
            for (cid, ans) in resp.events.items():
                self.submissions.insert(uid, cid, self.blocktime, ans)
        bt.logging.info("Received responses")
        self.blocktime += 1
        while block_start == self.block:
            time.sleep(1)


# The main function parses the configuration and runs the validator.

bt.debug(True)
if __name__ == "__main__":
    with Validator() as validator:
        while True:
            validator.print_info()
            bt.logging.info("Validator running...", time.time())
            time.sleep(5)
