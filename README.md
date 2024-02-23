<div align="left">

# **The credibility subnet** <!-- omit in toc -->

## Introduction

The credibility subnet aims to address the vulnerabilities in the current Bittensor incentive mechanism, particularly concerning Sybil attacks where a miner and validator could be the same entity. A constructive redesign could involve a system where the validation of a miner's work relies on data that is not available at the time the miners submit their responses. This approach would make it significantly more challenging for a miner-validator collusion to game the system, as the correct response would be unknown at the time of submission, thereby necessitating genuine effort and predictive accuracy from the miners.

We are currently releasing the subnet by stage, focusing on responsible disclosure. We plan to allocate a significant portion of the revenue generated by the network to credibility research bounties.

We call the design we develop for this subnet **delayed validation based on future events**.
Validators assess the miners' work based on outcomes of future events that are unknown at the time of task completion. These events could initially be internal milestones or metrics within the Bittensor network itself, such as emission rates, network growth rates, transaction volumes, or other quantifiable metrics that can be predicted but not manipulated by individual actors. As the system matures, the scope of events could expand to include external world events, further reducing the predictability and potential for collusion.

Please find a detailed description of our vision [here](https://amedeo-gigaver.gitbook.io/subnet-30/).

## Incentive mechanism

*As a reminder, one bittensor epoch is called a tempo and lasts 360 blocks. At the end of a tempo the reward allocated to neurons is computed by the Bittensor consensus.*

Currently the miners are competing to predict the rate of allocation of emissions to neurons in subnet 1 which is encoded within an emission vector that can be accessed by passing the parameter 'emission' to a [metagraph object](https://docs.bittensor.com/python-api/html/autoapi/bittensor/metagraph/index.html). 
The scoring is based on [RMSE](https://en.wikipedia.org/wiki/Root-mean-square_deviation). Specifically the validator computes $1-RMSE(\text{prediction}, \text{realized emission vector})$. The protocol between the miner and the validator is the following:
1. The validator queries the miner
2. The miners submit a hash of their prediction for the next tempo as well as their prediction for the current emission vector. This prediction must correspond to the hash they submitted during the preceding epoch.
3. The validator checks the hashing condition and computes the RMSE based scoring on the miner's prediction. The validator also stores the submitted hash for the next tempo. 

## Running a miner or validator

The miner and validator logic is contained in the appropriate files in `neuron`. As a miner you should implement your prediction strategy in the `forward` function. For a validator the provided script should be enough. 

First clone this repo `git clone https://github.com/amedeo-gigaver/credible_subnet.git`. Then to run a miner or validator:

1. Set up a venv: `python -m venv venv` and activate: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your wallets. For examples on how to do this, see the next section.
4. Run the appropriate script, replacing values in curly brackets: `python neurons/{miner}.py --netuid 30  --wallet.name {default} --wallet.hotkey {default}`
5. The venv should be active whenever the neurons are run.

## Setting up a bittensor wallet
A detailed explanation of how to set up a wallet can be found [here](https://docs.bittensor.com/getting-started/wallets). 
Two important commands are `btcli wallet list` and `btcli wallet overview`. The first one allows you to vizualize your wallets in tree-like maner where you can clearly see each cold key and the hot keys that are associated with it. The second one allows you to see the subnets in which you are registered as well as your balance. Importantly the `btcli wallet list` command allows you to see the wallet name that is associated with each cold key and each hot key. This is important since you use the pair of names for the cold key and the hot key rather than the keys themselves to run the bittensor commands related to wallets.  

---

## License
This repository is licensed under the MIT License.
```text
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
```
