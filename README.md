<div align="center">

# **The credibility subnet** <!-- omit in toc -->
[![Discord Chat](https://img.shields.io/discord/308323056592486420.svg)](https://discord.gg/bittensor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

---

## The Incentivized Internet <!-- omit in toc -->

[Discord](https://discord.gg/bittensor) • [Network](https://taostats.io/) • [Research](https://bittensor.com/whitepaper)
</div>

---
- [Subnet quickstarter](#subnet-quickstarter)
- [Introduction to subnets (Optional)](#introduction-to-subnets-optional)
- [Cloning the Bittensor Subnet Template](#cloning-the-bittensor-subnet-template)
- [Incorporating Python notebook code](#incorporating-python-notebook-code)
  - [Before you proceed](#before-you-proceed)
  - [Changing the code and filenames in this repo](#changing-the-code-and-filenames-in-this-repo)
  - [Code from notebook](#code-from-notebook)
- [Preparing to run the OCR subnet](#preparing-to-run-the-ocr-subnet)
- [Running the OCR subnet](#running-the-ocr-subnet)
- [License](#license)

---

## Subnet quickstarter

This repo shows how you can quickstart creating a Bittensor subnet. This is a companion repo for the [OCR Subnet Tutorial](https://docs.bittensor.com/tutorials/ocr-subnet-tutorial).

In specific, this repo demonstrates the power of:

- Starting from your Python notebook that contains the validated code for your incentive mechanism (in this case, the OCR), and
- Incorporating the Python notebook code into the [Bittensor Subnet Template](https://github.com/opentensor/bittensor-subnet-template) to quickly build a Bittensor subnet.

**Start with the template**

The Bittensor Subnet Template abstracts away the underlying complexity of Bittensor API, the underlying blockchain and other boilerplate code. The Bittensor Subnet Template also contains the required installation instructions, scripts, and files and functions for building Bittensor subnets with custom incentive mechanisms. 

**Incorporate Python notebook code**

In this repo we incorporate a custom incentive mechanism called **Optical Character Recognition (OCR)**. The Bittensor document [OCR Subnet Tutorial]() contains an introduction to the OCR subnet, links to the Python notebook and the detailed instructions for integrating the notebook code into this repo. 

---

## Introduction to subnets (Optional)

**You can skip this section if you** are already familiar with Bittensor subnets. 

The Bittensor blockchain hosts multiple self-contained incentive mechanisms called **subnets**. Subnets are playing fields in which:
- Subnet miners who produce value, and
- Subnet validators who produce consensus

determine together the proper distribution of TAO for the purpose of incentivizing the creation of value, i.e., generating digital commodities, such as intelligence or data. 

Each subnet consists of:
- Subnet miners and subnet validators.
- A protocol using which the subnet miners and subnet validators interact with one another. This protocol is part of the incentive mechanism.
- The Bittensor API using which the subnet miners and subnet validators interact with Bittensor's onchain consensus engine Yuma Consensus. The Yuma Consensus is designed to drive subnet validators and subnet miners into agreement on who is creating value and what that value is worth. 

**ALSO SEE**

- [Introduction](https://docs.bittensor.com/learn/introduction).

## Cloning the Bittensor Subnet Template

Read the [OCR Subnet Tutorial](https://docs.bittensor.com/tutorials/ocr-subnet-tutorial) first. Then follow the below steps when you are ready to create your own OCR Subnet repo.

1. Go to [Bittensor Subnet Template](https://github.com/opentensor/bittensor-subnet-template) and click on the **Use this template** dropdown on the top right. 
2. Click on **Create a new repository** and give your preferred name in the **Repository name** field. We will use the name **ocr_subnet** in this tutorial. 
3. Optionally provide a description in the **Description** field. 
4. Choose either **Public** or **Private**.
5. Click on **Create repository**.
6. GitHub will now show you your **ocr_subnet** repository page. 
7. Clone your **ocr_subnet** repo locally.

---

## Incorporating Python notebook code

### Before you proceed

Now we begin to incorporate our Python notebook code into this repo. At this stage we strongly recommend that you first go over the validated code in the Python notebook as presented in the [OCR Subnet Tutorial](https://docs.bittensor.com/tutorials/ocr-subnet-tutorial). Familiarize yourself with the code flow in the notebook before proceeding further.

### Changing the code and filenames in this repo

As described in [this section of Bittensor Subnet Template](https://github.com/opentensor/bittensor-subnet-template?tab=readme-ov-file#introduction), to write our own incentive mechanism, we must edit the below files in this cloned OCR subnet repo:

1. `template/protocol.py`: Contains the definition of the protocol used by subnet miners and subnet validators.
2. `neurons/miner.py`: Script that defines the subnet miner's behavior, i.e., how the subnet miner responds to requests from subnet validators.
3. `neurons/validator.py`: This script defines the subnet validator's behavior, i.e., how the subnet validator requests information from the subnet miners and determines the scores.

Below we show the changes we made to this OCR subnet repo. You can use your preferred names, but ensure that your code is consistent with the names you use.

- Renamed `/template` to `/ocr_subnet`.
- `ocr_subnet/protocol.py`: Renamed the synapse to `OCRSynapse` and provided the necessary attributes to communication between miner and validator.
- `ocr_subnet/forward.py`: Included the synthetic data generation (invoice pdf) and used `OCRSynapse`. 
- `ocr_subnet/reward.py`: Added custom loss function to calculate the reward.
- `neurons/miner.py`: Used `pytesseract` for OCR, and used `OCRSynapse` to communicate with validator.

**Additional changes**

In addition, make a note to update the following files:
- `README.md`: This file contains the documentation for the OCR project. 
- `contrib/CONTRIBUTING.md` and other files in `contrib`: Contains the instructions for contributing to your project. Update this file and the directory to reflect your project's contribution guidelines.
- `ocr_subnet/__init__.py`: This file contains the version of your project.
- `setup.py`: This file contains the metadata about your project. Update this file to reflect your project's metadata.

---

### Code from notebook 

Next, copy the code from the Python notebook into specific sections of this repo. Follow Steps 1 through 3 of [OCR Subnet Tutorial](https://docs.bittensor.com/tutorials/ocr-subnet-tutorial) and copy the code from the linked Python notebook into this repo. 


## Preparing to run the OCR subnet

Before you proceed with the installation and running of the subnet, note the following: 

- Use these instructions to run your subnet locally for your development and testing, or on Bittensor testnet or on Bittensor mainnet. 
- **IMPORTANT**: We **strongly recommend** that you first run your subnet locally and complete your development and testing before running the subnet on Bittensor testnet. Furthermore, make sure that you next run your subnet on Bittensor testnet before running it on the Bittensor mainnet.
- You can run your subnet either as a subnet owner, or as a subnet validator or as a subnet miner. 
- **IMPORTANT:** Make sure you are aware of the minimum compute requirements for your subnet. See the [Minimum compute YAML configuration](./min_compute.yml).
- Note that installation instructions differ based on your situation: For example, installing for local development and testing will require a few additional steps compared to installing for testnet. Similarly, installation instructions differ for a subnet owner vs a validator or a miner. 

## Running the OCR subnet

- **Running locally**: Follow the step-by-step instructions described in this section: [Running Subnet Locally](./docs/running_on_staging.md).
- **Running on Bittensor testnet**: Follow the step-by-step instructions described in this section: [Running on the Test Network](./docs/running_on_testnet.md).
- **Running on Bittensor mainnet**: Follow the step-by-step instructions described in this section: [Running on the Main Network](./docs/running_on_mainnet.md).

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
