<div align="left">

# Prediction subnet

## Forecasting of future world events 
*We are still in v0 but should upgrade the repo very soon.*

We incentivize the prediction of future events. We currently restrict the space to binary future events listed on Polymarket. Miners compete by sending to the validators a vector of probabilities for each event that we support. 
For example, for two binary events $E_1$ and $E_2$ a miner would submit a vector $(p_1, p_2)$ with $p_i$ the probability that $E_i$ is realized. For example, $E_1$ could be *SBF is sentenced to life*.  
In the future, any headline of the WSJ could be an event on which a miner could be evaluated upon. 


## Scoring methodology
### v0

Currently, miners simply submit a vector of $0$ and $1$ encoding which outcome they believe will happen for a given event. The validator scores them then 0 or 1 depending on whether they guessed right.

### v1
Denote by $S(p_j, o_i)$ the quadratic scoring rule for a prediction $p_j$ of the event $E_i$ which returns $(o_i - p_i)^2$, where $o_i$ is $0$ or $1$ depending on the realization of $E_i$. The lower the quadratic scoring rule the better the score. A quadratic scoring rule is proper i.e it incentivizes miner to report their true prediction.


We implement a sequentially shared quadratic scoring rule. This allows us to score $0$ miners that do not bring new information to the market, as well as to bring value by aggregating information. 
This functions by scoring each miner relatively to the previous one. The score of the miner $j$ is then $S(p_j, o_i) - S(p_{j-1}, o_i)$ where $p_{j-1}$ is the submission of the previous miner. Importantly this payoff can be negative, therefore in practice when aggregating the scores of a miner we add a $\max(-,0)$ operation.
In our current implementation instead of paying the miner for their delta to the previous prediction, we pay them for their delta to the polymarket price for this event i.e $S(p_j, o_i) - S(\text{price on polymarket at t}, o_i)$ for $p_j$ submitted at $t$.


We do not force miners to predict the whole set of events but we give them a score of $0$ on the events for which they did not submit a prediction.

In this setting where miners do not risk a negative return for making bad predictions, we are faced with a sybil exploit which consists in deploying two miners with each predicting one outcome of the binary event with maximal confidence. This is mitigated by the registration cost a miner has to pay to enter a subnet, as well as by the upper bound on the number of miners that can participate in the subnet ($192$). 

We aim at substantially developing this framework by allowing combinatorial updates in the futures i.e the ability for miners to add conditional logic to their prediction e.g *if the aggregated probability of event X passes a threshold Y, make prediction Z*. 
In the limit, miners could update the weights of an entire LLM.


## Miner strategy 

A reference for a miner strategy should be the article ["Approaching Human Level Forecasting with Langage Models"](https://arxiv.org/html/2402.18563v1?s=35) by Halawi and al. They fine-tune an LLM to generate predictions on binary events (such as the ones listed on Polymarket) that nears the performance of the crowd when submitting a forecast for each prediction, and that beats the crowd in a setting where the LLM can choose to give a prediction or not.

## Running a miner or validator

The miner and validator logic is contained in the appropriate files in `neuron`. As a miner you should implement your prediction strategy in the `forward` function. For a validator the provided script should be enough. 

First clone this repo by running `git clone https://github.com/amedeo-gigaver/credible_subnet.git`. Then to run a miner or validator:

1. Set up a venv: `python -m venv venv` and activate: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your wallets. For examples on how to do this, see the next section.
4. Run the appropriate script, replacing values in curly brackets: `python neurons/{miner}.py --netuid 30  --wallet.name {default} --wallet.hotkey {default}`
5. The venv should be active whenever the neurons are run.

## Setting up a bittensor wallet
A detailed explanation of how to set up a wallet can be found [here](https://docs.bittensor.com/getting-started/wallets). 

Two important commands are `btcli wallet list` and `btcli wallet overview`. The first one allows you to vizualize your wallets in a tree-like manner where one can clearly see each coldkey as well as the hotkeys that are associated with it. The second one allows you to see the subnets in which you are registered as well as your balance. Importantly the `btcli wallet list` command allows you to see the wallet name that is associated with each pair of coldkey and hotkey. This is important since you use the names of the coldkey and the hotkey rather than the keys themselves to run bittensor commands related to wallets.  

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
