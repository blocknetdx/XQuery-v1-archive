

Powered by    [Blocknet](https://blocknet.co) and  [XQuery](https://xquery.io/)

# Indexer - [EXRPROXY-ENV](https://github.com/blocknetdx/exrproxy-env) plugin
- [Indexer](#indexer)
  * [Requirements](#requirements)
  * [Dependency Installation](#dependency-installation)
      - [Install Docker (Ubuntu)](#install-docker--ubuntu-)
 - [Automated Deployment with EXRPROXY-ENV](#automated-deployment)
  * [Input file format](#0)
  * [Autobuild steps](#1)
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


# Automated Deployment with [EXRPROXY-ENV](https://github.com/blocknetdx/exrproxy-env) <a name="automated-deployment"></a>

Best suitable to be used with [EXRPROXY-ENV](https://github.com/blocknetdx/exrproxy-env) autobuild

- Runs indexer, DB, and hasura API endpoint
- requires at least 2vCPU


## <ins>query.yaml</ins> input file format (This .yaml file is auto-generated in Autobuild steps below.)<a name="0"></a>
```yaml
#mandatory
graph: Name of graph
#mandatory
endpoint: Graph endpoint
chains:
  #mandatory
  - name: Name of chain; no spaces required
    #mandatory
    rpc_host: Rpc endpoint of chain, host and ip;
    #mandatory
    abi: ABI file; check provided abi format
    #mandatory
    query:
    - name: What events to search for
    #mandatory
    address:
    - name: Router name; no spaces required
      address: Router address
    #not mandatory
    historical:
  - fromBlock: Starting block number for historical events; Expected number
```
## Autobuild steps <a name="1"></a>
#### Requirements
- `Port 80 must be opened on the host`

Follow the [Service Node Setup Guide](https://docs.blocknet.co/service-nodes/setup/).
That guide employs the autobuild tools in the [EXR ENV](https://github.com/blocknetdx/exrproxy-env) repo
to deploy XQuery within an EXR Environment.

Once the XQuery stack has been deployed in the EXR ENV, you can create a project and test the XQuery
deployment by following the [Project API](https://api.blocknet.co/#projects-api-xquery-hydra) and
the [XQuery API](https://api.blocknet.co/#xquery-api).

NOTE: If you want to create a project in the EXR ENV for testing, and you want to avoid making a payment to create the project,
check out the `projects.py` tool in your EXR ENV, located at `exrproxy-env/cli/projects.py`. Issue `projects.py -h` for help in using it.

# Templates <a name="templates"></a>
## Single chain <a name="single_chain"></a>
### avax-query.yaml <a name="avax_query"></a>
```yaml
# Single chain - AVAX
graph: AVAX
endpoint: /indexer
chains:
  - name: AVAX_PANGOLIN
    rpc_host: https://api.avax.network/ext/bc/C/rpc
    abi: abi/pangolinRouter.json
    query:
    - name: Swap
    address:
    - name: Pangolin_Router
      address: '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'
    historical:
    - fromBlock: "6800000"
```

### eth-query.yaml <a name="eth_query"></a>
```yaml
#Single chain - ETH - infura
graph: ETH
endpoint: /indexer
chains:
  - name: ETH_UNISWAP
    rpc_host: https://:INFURA_SECRET@mainnet.infura.io/v3/INFURA_PROJECT
    abi: abi/uniswapRouter.json
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

  
## Multi chain <a name="multi_chain"></a>
  ### avax-eth-query.yaml <a name="multi_query"></a>
```yaml
#Multi chain AVAX - ETH
graph: AVAX_ETH
endpoint: /indexer
chains:
  - name: AVAX_PANGOLIN
    rpc_host: https://api.avax.network/ext/bc/C/rpc
    abi: abi/pangolinRouter.json
    query:
    - name: Swap
    address:
    - name: Pangolin_Router
      address: '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106'
    historical:
    - fromBlock: "6800000"
  - name: ETH_UNISWAP
    rpc_host: https://:INFURA_SECRET@mainnet.infura.io/v3/INFURA_PROJECT
    abi: abi/uniswapRouter.json
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

