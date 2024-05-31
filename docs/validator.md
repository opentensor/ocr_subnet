

# Validator

Your validator will be sending binary outcomes events to miners. In the first phase of the subnet the events will come from prediction market APIs such as Polymarket or Manifold. Every time an event settles, your validator will score the miners that submitted a prediction for that event. The validator logic is essentially contained in the `neurons/validator.py` file.

**IMPORTANT**

Before attempting to register on mainnet, we strongly recommend that you run a validator on the testnet. For that matter ensure you add the appropriate testnet flag `--subtensor.network test`.

| Environment | Netuid |
| ----------- | -----: |
| Mainnet     |      TBD |
| Testnet     |    155 |



**DANGER**

- Do not expose your private keys.
- Only use your testnet wallet.
- Do not reuse the password of your mainnet wallet.
- Make sure your incentive mechanism is resistant to abuse.

# System Requirements

- Requires **Python 3.10.**
- [Bittensor](https://github.com/opentensor/bittensor#install)

Below are the prerequisites for validators. You may be able to make a validator work off lesser specs but it is not recommended.

- Currently computing requirements are minimal. A "Starter" server on [Render](https://render.com/) for $7/month should be enough. As we optimize the fetching and processing of events these requirements may evolve.

# Getting Started


The miner and validator logic is contained in the appropriate files in `neuron`. =

First clone this repo by running `git clone `. Then to run a miner or validator:


Clone repository

```bash
git clone https://github.com/amedeo-gigaver/infinite_games.git
```

Change directory

```bash
cd infinite_games
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate a Virtual Environment

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```
The venv should be active whenever the neurons are run.

## 2. Create Wallets

This step creates local coldkey and hotkey pairs for your validator.

The validator will be registered to the subnet specified. This ensures that the validator can run the respective validator scripts.

Create a coldkey and hotkey for your validator wallet.

```bash
btcli wallet new_coldkey --wallet.name validator
btcli wallet new_hotkey --wallet.name validator --wallet.hotkey default
```

## 2a. (Optional) Getting faucet tokens

Faucet is disabled on the testnet. Hence, if you don't have sufficient faucet tokens, ask the Bittensor Discord community for faucet tokens. Bittensor -> help-forum -> Requests for Testnet TAO

## 3. Register keys

This step registers your subnet validator keys to the subnet.

```bash
btcli subnet register --wallet.name validator --wallet.hotkey default
```

To register your validator on the testnet add the `--subtensor.network test` flag.

Follow the below prompts:

```bash
>> Enter netuid (0): # Enter the appropriate netuid for your environment
Your balance is: # Your wallet balance will be shown
The cost to register by recycle is τ0.000000001 # Current registration costs
>> Do you want to continue? [y/n] (n): # Enter y to continue
>> Enter password to unlock key: # Enter your wallet password
>> Recycle τ0.000000001 to register on subnet:8? [y/n]: # Enter y to register
📡 Checking Balance...
Balance:
  τ5.000000000 ➡ τ4.999999999
✅ Registered
```

## 4. Check that your keys have been registered

This step returns information about your registered keys.

Check that your validator key has been registered:

```bash
btcli wallet overview --wallet.name validator
```

To check your validator on the testnet add the `--subtensor.network test` flag

The above command will display the below:

```bash
Subnet: TBD # or 155 on testnet
COLDKEY    HOTKEY   UID  ACTIVE  STAKE(τ)     RANK    TRUST  CONSENSUS  INCENTIVE  DIVIDENDS  EMISSION(ρ)   VTRUST  VPERMIT  UPDATED  AXON  HOTKEY_SS58
validator  default  197    True   0.00000  0.00000  0.00000    0.00000    0.00000    0.00000            0  0.00000                56  none  5GKkQKmDLfsKaumnkD479RBoD5CsbN2yRbMpY88J8YeC5DT4
1          1        1            τ0.00000  0.00000  0.00000    0.00000    0.00000    0.00000           ρ0  0.00000
                                                                                Wallet balance: τ0.000999999
```

## 6. Running a Validator

### Direct Run 

Run the following command inside the `infinite_games` directory:

`python neurons/validator.py --netuid 155 --subtensor.network test --wallet.name {default} --wallet.hotkey {default}`


### PM2 Installation

Install and run pm2 commands to keep your validator online at all times.


`sudo apt update`

`sudo apt install npm` 

`sudo npm install pm2 -g`

`Confirm pm2 is installed and running correctly`

`pm2 ls`


Command to run the validator:

`pm2 start neurons/validator.py --interpreter /usr/bin/python3  --name validator -- --wallet.name validator --netuid 155 --wallet.hotkey hotkey --subtensor.network testnet --logging.debug` 


Explanation of each variable:

--wallet.name: Provide the name of your wallet.
--wallet.hotkey: Enter your wallet's hotkey.
--netuid: Use 155 for testnet.
--subtensor.network: Specify the network you want to use (finney, test, local, etc).
--logging.debug: Adjust the logging level according to your preference.
--axon.port: Specify the port number you want to use.

You can monitor the status and logs using these commands:

`pm2 status`
`pm2 logs 0`


## 7. Get emissions flowing

Register to the root network using the `btcli`:

```bash
btcli root register
```

To register your validator to the root network on testnet use the `--subtensor.network test` flag.

Then set your weights for the subnet:

```bash
btcli root weights
```

To set your weights on testnet `--subtensor.network test` flag.

## 8. Stopping your validator

To stop your validator, press CTRL + C in the terminal where the validator is running.

