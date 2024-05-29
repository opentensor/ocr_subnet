<div align="center">

<img src="docs/infinite-games.jpeg" alt="Project Logo" width="200"/>

# **Infinite Games** 


[Discord](https://discord.gg/eZaZ6unD) • 
[Website](https://www.infinitegam.es/) • [Network](https://taostats.io/) 

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

</div>



<!-- update with discord invite link -->

</div>

  <!--
  <a href="">Twitter</a> -->
    
  <!-- <a href="">Bittensor</a> -->


# Forecasting of Future Events

##  Introduction


We incentivize the prediction of future events. We currently restrict the prediction space to binary future events listed on Polymarket. We will expand soon to new markets and providers. We are focused on *judgemental forecasting* rather than *statistical forecasting*. We hence expect the models used by miners to be LLMs. 

### High-level mechanism

Miners submit their predictions to validators. Each prediction has to be done early enough before the event underlying the prediction settles. Once the event settles, the validators that received the prediction score the miner.

## LLMs open new predictive capabilities

Making predictions is a hard task that requires cross-domain knowledge and intuition. It is often limited in explanatory reasoning and domain-specific (the expert in predicting election results will differ from the one predicting the progress in rocket-engine technology) ([1]). At the same time it is fundamental to human society, from geopolitics to economics. 

<!-- The COVID-19 measures for example were based on epidemiological forecasts. Science is another area where prediction is crucial ([2]) to determine new designs or to predict the outcome of experiments (executing one experiment is costly). Such predictions rely on the knowledge of thousands papers and on multidisciplinary and multidimensional analysis (*can a study replicate ? should one use a molecular or behavioral approach?*). -->

LLMs approach or surpass human forecasting abilities. They near on average the crowd prediction on prediction market events ([1]), and surpass humans in predicting neuroscience results ([2]). They are also shown to be calibrated with their predictions i.e confident when right. Through their generalization capabilities and unbounded information processing, LLMs have the potential to automate the prediction process or complement humans. 


### Real-world applications

The value of the subnet first relies in the improvement of the efficiency of prediction markets. This value can be extracted by validators through arbitrage. The validators may obtain a better knowledge of the probability of an event settling and communicate this information to a prediction market by opening a position. 

The first applications built on top of our subnet could be related to prediction markets. A trader could query our market to obtain the most up to date and relevant predictions to their portfolio based on the current news landscape (LLMs would be constantly ingressing the most up to date and relevant news articles). They could then readjust their positions accordingly or trade directly on this information. 

In the long term, a validator could provide paid economic forecasts or more generally the output of any forward-looking task addressed to an LLM ([2]). A customer might then provide a series of paid sub-queries related to the information they aim at retrieving.

<!-- It could also be used by scientists to design their experiment and frame their ideas. For example, the value of a paper often resides in the way the results are presented and cross-analysed. One way resulting in poor conclusions while the other giving good results. An LLM might help detect the adequate framework. -->


## Miners 

Miners compete by sending to the validators a dictionary where the key is a [Polymarket condition id](https://docs.polymarket.com/#overview-8) to an event $E$ and the value is a probability $p$ that $E$ is realized. For example, $E$ could be *SBF is sentenced to life*.


### Miner strategy 

A reference providing a **baseline miner** strategy is the article ["Approaching Human Level Forecasting with Langage Models"](https://arxiv.org/html/2402.18563v1?s=35) ([1]). The authors fine-tune an LLM to generate predictions on binary events (including the ones listed on Polymarket) which nears the performance of human forecasters when submitting a forecast for each prediction, and which beats human forecasters in a setting where the LLM can choose to give a prediction or not based on its confidence.


## Validators

Validators record the miners' predictions and score them once the Polymarket events settles. At each event settlement, a score is added to the moving average of the miner's score. This simple model ensures that all validators score the miners at roughly the same time. Importantly, we implement a **cutoff** for the submission time of a prediction, currently set at 24 hours. This means that miners must submit their prediction for a given Polymarket event 24 hours before the settlement time.

## Scoring rule
*We will launch our subnet with model 1 and then move to model 2.*

Denote by $S(p_i, o_i) = (o_i - p_i)^2$ the quadratic scoring rule (the Brier score) for a prediction $p_i$ of a binary event $E_i$ and where $o_i$ is $0$ or $1$ depending on the realization of $E_i$. The lower the quadratic scoring rule the better the score. A quadratic scoring rule is strictly proper i.e it strictly incentivizes miner to report their true prediction.

### model 1

The validators directly use a **quadratic scoring rule** on the miners' predictions. If the miner predicted that $E_i$ be realized with probability $p_i$, upon settlement of the outcome the validator scores the miner by adding $S(p_i, o_i)$ to their moving average of the miner's score.

### model 2

In this model, we discard the moving average update and validators record the scores they obtained at settlement time. The validators then all update the aggregated scores of miners at an agreed upon time. 

We implement a **sequentially shared quadratic scoring rule**. This allows us to score $0$ miners that do not bring new information to the market, as well as to bring value by aggregating information. 
The scoring rule functions by scoring each miner relatively to the previous one. The score of the miner $j$ is then $S_j = S(p_j, o_i) - S(p_{j-1}, o_i)$ where $p_{j-1}$ is the submission of the previous miner. Importantly this payoff can be negative, therefore in practice when aggregating the scores of a miner we add a $\max(-,0)$ operation. 

The aggregated score of a miner that a validator sends to the blockchain is the following:

$$\frac{1}{N} \sum_j S_j$$
where $N$ is the number of events that the validator registered as settled during the tempo.

We give miners a score of $0$ on the events for which they did not submit a prediction.

In the first iteration of the model, instead of paying the miner for their delta to the previous prediction, we will pay them for their delta to the Polymarket probability at the submission time i.e $S(p_j, o_i) - S(\text{price on polymarket at t}, o_i)$ where $p_j$ is submitted at $t$.

## Incentive compability

See [here](docs/mechanism.md) for a discussion of our mechanism.

## Roadmap

We first aim at adjusting the scoring rule by updating to the *model 1* described above. We will likely implement several other updates in order to make the mechanism more robust. One of them could be a commit-reveal step for the predictions submitted by miners. Some updates may be due to experimental data.

We would also possibly like to make the prediction framework more LLM specific and create mechanisms that explicitely generate data for the fine-tuning of prediction focused LLMs.

We plan to extend the set of predicted events to other prediction markets and event providers (Metacalculus, Azuro). Our goal is to obtain a continuous feed of organic events by using e.g Reuters' API or WSJ headlines. 

<!-- In the limit, miners could update the weights of an entire LLM.-->


## Running a miner or validator

The miner and validator logic is contained in the appropriate files in `neuron`. As a miner you should implement your prediction strategy in the `forward` function. For a validator the provided script should be enough. 

First clone this repo by running `git clone https://github.com/amedeo-gigaver/infinite_games.git`. Then to run a miner or validator:

1. Set up a venv: `python -m venv venv` and activate: `source venv/bin/activate`
2. Set up your wallets. For instructions on how to do this, see the next section.
3. Navigate to the repo : `cd infinite_games` 
4. Install dependencies: `pip install -r requirements.txt`
5. Run the appropriate script, replacing values in curly brackets: `python neurons/{miner}.py --netuid 30  --wallet.name {default} --wallet.hotkey {default}`
6. The venv should be active whenever the neurons are run.

### PM2 Installation

Install and run pm2 commands to keep your miner and validator online at all times.


`sudo apt update`

`sudo apt install npm` 

`sudo npm install pm2 -g`

`Confirm pm2 is installed and running correctly`

`pm2 ls`


Example Command for validator

`pm2 start neurons/validator.py --interpreter /usr/bin/python3  --name validator -- --wallet.name validator --netuid 155 --wallet.hotkey hotkey --subtensor.network testnet --logging.debug` 

Example Command for miner

`pm2 start neurons/miner.py --interpreter /usr/bin/python3  --name miner -- --wallet.name miner --netuid 155 --wallet.hotkey hotkey --subtensor.network testnet --logging.debug`

Variable Explanation

--wallet.name: Provide the name of your wallet.
--wallet.hotkey: Enter your wallet's hotkey.
--netuid: Use 155 for testnet.
--subtensor.network: Specify the network you want to use (finney, test, local, etc).
--logging.debug: Adjust the logging level according to your preference.
--axon.port: Specify the port number you want to use.
--neuron.name: Trials for this miner go in miner.root / (wallet_cold - wallet_hot) / miner.name.
--neuron.device: Device to run the validator on. cuda or cpu

Monitor the status and logs:

`pm2 status`
`pm2 logs 0`

### Computational requirements

Currently the requirements are minimal for a validator and depend on the model used for the miner. We will update this section regularly.

## Setting up a bittensor wallet
A detailed explanation of how to set up a wallet can be found [here](https://docs.bittensor.com/getting-started/wallets). 
We also provide some indications [here](docs/wallet-setup.md).



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
