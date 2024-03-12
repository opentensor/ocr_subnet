<div align="left">
  
# Forecasting of future events

## Problem

Making predictions is a hard task that requires cross-domain knowledge and intuition. It is often limited in explanatory reasoning and domain-specific (the expert in predicting election result will differ from the one predicting the rocket-engine progress) ([1]). At the same time it is fundamental to human society, from geopolitics to economics. The COVID-19 measures for example were based on epidemiological forecasts. Science is another area where prediction is crucial ([2]) to determine new designs or to predict the outcome of experiments (executing one experiment is costly). Such predictions rely on the knowledge of thousands papers and on multidisciplinary and multidimensional analysis (can a study replicate ? should one use a molecular or behavioral approach?).

LLMs can solve these challenges through their generalization capabilities and unbounded information processing. 


##  The subnet


We incentivize the prediction of future events. We currently restrict the prediction space to binary future events listed on Polymarket.

The immediate value that can be extracted by validators through this subnet is related to the improvement of the efficiency of prediction markets through arbitrage. The validators my obtain a better knowledge of the probability of an event settling and communicate this information to a prediction market by opening a position.    

We plan first to extend the set of predicted events to other prediction markets. We then aim at obtaining a continuous feed of organic events by using e.g a Reuters API. In the future, any headline of the WSJ could be an event on which a miner could be evaluated upon.

### Applications built on the subnet

In the same line, the first application built on top of our subnet could be related to prediction market. A trader could query our market to obtain the most up to date predictions according to the current news landscape (LLMs would be constantly ingressing the most up to date and relevant news articles). They could then readjust their positions accordingly / trade on this information.

More generally, a validator could provide payed economic forecasts to companies or individuals. It could also be used by scientists to design their experiment and frame their ideas. For example, the value of a paper often resides in the way the results are presented and cross-analysed. One way resulting in poor conclusions while the other giving good results. An LLM might help detect the adequate framework.




## Miners 

Miners compete by sending to the validators a dictionary where the key is a [Polymarket condition id](https://docs.polymarket.com/#overview-8) to an event $E$ and the value is a probability $p$ that $E$ is realized. For example, $E$ could be *SBF is sentenced to life*.


### Miner strategy 

A reference providing a baseline miner strategy is the article ["Approaching Human Level Forecasting with Langage Models"](https://arxiv.org/html/2402.18563v1?s=35) ([1]). The authors fine-tune an LLM to generate predictions on binary events (including the ones listed on Polymarket) which nears the performance of human forecasters when submitting a forecast for each prediction, and which beats human forecasters in a setting where the LLM can choose to give a prediction or not based on its confidence.


## Validators

Validators record the miners' predictions and score them once the Polymarket events settles. At each event settlement, a score is added to the moving average of the miner's score. This simple model ensures that all validators score the miners at roughly the same time. We also implement a cutoff for the submission time of a prediction, currently set at 24 hours. This means that miners must submit their prediction for a given Polymarket event 24 hours before the settlement time.

## Scoring methodology
*We are still in v0 but should upgrade the repo very soon.*

### v0

The validators only implement a quadratic scoring rule (the Brier score) on the miners' predictions. If the miner predicted that the binary outcome $1$ will be realized with probability $p$, upon settlement of the outcome the validator scores the miner by adding $(o_i - p_i)^2$ to their moving average of the miner's score, where $o_i$ is $0$ or $1$. 

### v1

In this model, we would discard the moving average update and validators would record the scores obtained at settlement time. They would then all update the aggregated scores of miners at an agreed upon time. 

Denote by $S(p_j, o_i) = (o_i - p_i)^2$ the quadratic scoring rule for a prediction $p_j$ of an event $E_i$ and where $o_i$ is $0$ or $1$ depending on the realization of $E_i$. The lower the quadratic scoring rule the better the score. A quadratic scoring rule is strictly proper i.e it strictly incentivizes miner to report their true prediction.


We implement a sequentially shared quadratic scoring rule. This allows us to score $0$ miners that do not bring new information to the market, as well as to bring value by aggregating information. 
This functions by scoring each miner relatively to the previous one. The score of the miner $j$ is then $S_j = S(p_j, o_i) - S(p_{j-1}, o_i)$ where $p_{j-1}$ is the submission of the previous miner. Importantly this payoff can be negative, therefore in practice when aggregating the scores of a miner we add a $\max(-,0)$ operation. 

The aggregated score of a miner that a validator sends to the blockchain is the following:

$$\frac{1}{N} \sum_j S_j$$
where $N$ is the number of events that the subnet registered as settled during the tempo.

We give miners a score of $0$ on the events for which they did not submit a prediction.


In the first implementation, instead of paying the miner for their delta to the previous prediction, we pay them for their delta to the Polymarket probability at the submission time i.e $S(p_j, o_i) - S(\text{price on polymarket at t}, o_i)$ where $p_j$ is submitted at $t$.

## Running a miner or validator

The miner and validator logic is contained in the appropriate files in `neuron`. As a miner you should implement your prediction strategy in the `forward` function. For a validator the provided script should be enough. 

First clone this repo by running `git clone https://github.com/amedeo-gigaver/infinite_games.git`. Then to run a miner or validator:

1. Set up a venv: `python -m venv venv` and activate: `source venv/bin/activate`
2. Set up your wallets. For instructions on how to do this, see the next section.
3. Navigate to the repo : `cd infinite_games` 
4. Install dependencies: `pip install -r requirements.txt`
5. Run the appropriate script, replacing values in curly brackets: `python neurons/{miner}.py --netuid 30  --wallet.name {default} --wallet.hotkey {default}`
6. The venv should be active whenever the neurons are run.

## Setting up a bittensor wallet
A detailed explanation of how to set up a wallet can be found [here](https://docs.bittensor.com/getting-started/wallets). 

Two important commands are `btcli wallet list` and `btcli wallet overview`. 

The first enables one to vizualize their wallets in a tree-like manner as well as which hotkeys are associated with a given coldkey. Importantly, one can see the wallet name that is associated with each pair of coldkey and hotkey. This is important since the names of the coldkey and the hotkey are used rather than the keys themselves when running bittensor commands related to wallets.  

The second enables one to see the subnets  in which their wallet is registered as well as the wallet's balance. 


## Incentive compability

The properness of the scoring rule ensures that the best outcome for the miner is to submit what they truly believe to be the probability distribution of the predicted event. The sequentially shared aspect ensures we only reward miners that bring new information. We aim at implementing soon a commit-reveal step as well for the miner prediction. This is however not crucial since the problem of copy-pasting is already handled by the scoring rule. It only makes the system more robust.

In this setting where miners do not risk a negative return for making bad predictions, we are faced with a sybil exploit which consists in deploying two miners with each predicting one outcome of the binary event with maximal confidence. This is mitigated by the registration cost a miner has to pay to enter a subnet, as well as by the upper bound on the number of miners that can participate in the subnet ($192$). 

## Future developments

As mentioned previously, we first aim at implementing a continuous stream of events for miners to do predictions.
We then aim at substantially developing the prediction framework by allowing for combinatorial updates in the futures i.e the ability for miners to add conditional logic to their prediction e.g *if the aggregated probability of event X passes a threshold Y, make prediction Z*. 
In the limit, miners could update the weights of an entire LLM.


## References

| Reference ID | Author(s) | Year | Title |
|--------------|-----------|------|-------|
| 1 | Halawi and al. | 2024| [Approaching Human Level Forecasting with Langage Models](https://arxiv.org/html/2402.18563v1?s=35)|
| 2 | Luo and al. | 2024 | [LLM surpass human experts in predicting neuroscience results](https://arxiv.org/pdf/2403.03230.pdf)|


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
