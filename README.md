



# Indexer
- [Indexer](#indexer)
  * [Requirements](#requirements)
  * [Dependency Installation](#dependency-installation)
      - [Install Docker (Ubuntu)](#install-docker--ubuntu-)
 - [Automated Deployment](#automated-deployment)
   1. [Edit input file](#1)
   2. [Generate docker-compose](#2)
   3. [Start XQuery](#3)
   4. [Available Endpoints](#4)
 - [Templates](#templates)  
  * [Single Chain](#single_chain)
    1. [avax_query.yaml](#avax_query)
    2. [eth_query.yaml](#eth_query)
  * [Multi Chain](#multi_chain)
    1. [avax-eth-query.yaml](#multi_query)

 - [Help](#help)  

## Requirements <a name="requirements"></a>
- Docker
- docker-compose

## Dependency Installation <a name="dependency-installation"></a>
#### Install Docker (Ubuntu) <a name="install-docker--ubuntu-"></a>
```shell
sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

sudo apt install curl
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```


# Automated Deployment <a name="automated-deployment"></a>
- Runs indexer, DB, and hasura API endpoint
- requires at least 2vCPU

## General Schema 
### 1. Edit <ins>query.yaml</ins> input file <a name="1"></a>
```yaml
#mandatory
graph: Name of graph
#mandatory
endpoint: Graph endpoint
chains:
  #mandatory
  - name: Name of chain; no spaces required
    #mandatory
    host: Host address of chain; required http
    #mandatory
    port: Port of chain; if it doesn't exist leave empty
    #mandatory
    abi: ABI file; check provided abi format
    #mandatory
    query:
    - name: What events to search for
    #not mandatory
    address:
    - name: Router name; no spaces required
      address: Router address
    #not mandatory
    historical:
  - fromBlock: Starting block number for historical events; Expected number
```
### 2. Generate docker-compose <a name="2"></a>
For help try: `python3 generate-docker-compose.py --help`
```
python3 generate-docker-compose.py --yaml query.yaml --output docker-compose.yaml
```

### 3. Start XQuery <a name="3"></a>
```
docker-compose -f docker-compose.yaml up
```

### 4. Available endpoints <a name="4"></a>
* Hasura console

```http://localhost:80/hasura/```
* GraphQL endpoint

```http://localhost:80/{endpoint}/```

or

```http://localhost:80/graphql/```

# Templates <a name="templates"></a>
## Single chain <a name="single_chain"></a>
### avax-query.yaml <a name="avax_query"></a>
```yaml
# Single chain - AVAX
graph: AVAX
endpoint: /AVAX
chains:
  - name: AVAX
    host: https://api.avax.network/ext/bc/C/rpc
    port: 
    abi: avax_abi.json
    query:
    - name: Swap
    address:
    - name: Pangolin_Router
      address: '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'
    historical:
    - fromBlock: "6800000"
```
1. To generate docker-compose file run:

```python xquery.py --yaml avax-query.yaml --output avax-compose.yaml``` 

2. Start XQuery

```docker-compose -f avax-compose.yaml up --detach```

3. Access data 
* Hasura console

```http://localhost:80/hasura/```

* GraphQL endpoint

 ```http://localhost:80/AVAX/```

 or

  ```http://localhost:80/graphql/```

### eth-query.yaml <a name="eth_query"></a>
```yaml
#Single chain - ETH - infura
graph: ETH_infura
endpoint: /ETH
chains:
  - name: ETH
    host: https://:INFURA_SECRET@mainnet.infura.io/v3/INFURA_PROJECT
    port: 
    abi: eth_abi.json
    query:
    - name: Swap
    address:
    - name: Uniswap_Router_v2
      address: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    - name: Uniswap_Router_v3
      address: '0xe592427a0aece92de3edee1f18e0157c05861564'
    historical:
    - fromBlock: "13600000"
```
1. To generate docker-compose file run:

```python xquery.py --yaml eth-query.yaml --output eth-compose.yaml``` 

2. Start XQuery

```docker-compose -f eth-compose.yaml up --detach```

3. Access data 
* Hasura console

```http://localhost:80/hasura/```

* GraphQL endpoint

 ```http://localhost:80/ETH/```

or

  ```http://localhost:80/graphql/```
  
## Multi chain <a name="multi_chain"></a>
  ### avax-eth-query.yaml <a name="multi_query"></a>
```yaml
#Multi chain AVAX - ETH
graph: AVAX_ETH
endpoint: /multichainAVAXETH
chains:
  - name: AVAX
    host: https://api.avax.network/ext/bc/C/rpc
    port: 
    abi: avax_abi.json
    query:
    - name: Swap
    address:
    - name: Pangolin_Router
      address: '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'
    historical:
    - fromBlock: "6800000"
  - name: ETH
    host: https://:PROJECT_SECRET@mainnet.infura.io/v3/PROJECT_ID
    port: 
    abi: eth_abi.json
    query:
    - name: Swap
    address:
    - name: Uniswap_Router_v2
      address: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
    - name: Uniswap_Router_v3
      address: '0xe592427a0aece92de3edee1f18e0157c05861564'
    historical:
    - fromBlock: "13600000"
```
1. To generate docker-compose file run:

```python xquery.py --yaml avax-eth-query.yaml --output avax-eth-compose.yaml``` 

2. Start XQuery

```docker-compose -f avax-eth-compose.yaml up --detach```

3. Access data 
* Hasura console

```http://localhost:80/hasura/```

* GraphQL endpoint

 ```http://localhost:80/multichainAVAXETH```
 
or

  ```http://localhost:80/graphql/```
  

### Help <a name="help"></a>
```http://localhost:80/help.txt```
