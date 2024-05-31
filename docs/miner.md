
# Miner

As a miner you should implement your prediction strategy in the `forward` function.

# System requirements

TBD

## Direct Run 

Run the following command inside the `infinite_games` directory:

`python neurons/miner.py --netuid 155 --subtensor.network test --wallet.name {default} --wallet.hotkey {default}`

## PM2 Installation

Install and run pm2 commands to keep your validator online at all times.


`sudo apt update`

`sudo apt install npm` 

`sudo npm install pm2 -g`

`Confirm pm2 is installed and running correctly`

`pm2 ls`


Example Command for miner

`pm2 start neurons/miner.py --interpreter /usr/bin/python3  --name miner -- --wallet.name miner --netuid 155 --wallet.hotkey hotkey --subtensor.network testnet --logging.debug`


Variable Explanation

--wallet.name: Provide the name of your wallet.
--wallet.hotkey: Enter your wallet's hotkey.
--netuid: Use 155 for testnet.
--subtensor.network: Specify the network you want to use (finney, test, local, etc).
--logging.debug: Adjust the logging level according to your preference.
--axon.port: Specify the port number you want to use.


Monitor the status and logs:

`pm2 status`
`pm2 logs 0`
