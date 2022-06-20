

Powered by    [Blocknet](https://blocknet.co) and  [XQuery](https://xquery.io/)

# Indexer - [EXRPROXY-ENV](https://github.com/blocknetdx/exrproxy-env) plugin
- [Indexer - EXRPROXY-ENV plugin](#indexer---exrproxy-env-plugin)
  - [Requirements <a name="requirements"></a>](#requirements-)
  - [Dependency Installation <a name="dependency-installation"></a>](#dependency-installation-)
      - [Install Docker (Ubuntu) <a name="install-docker--ubuntu-"></a>](#install-docker-ubuntu-)
- [Automated Deployment with EXRPROXY-ENV <a name="automated-deployment"></a>](#automated-deployment-with-exrproxy-env-)
  - [<ins>query.yaml</ins> input file format (This .yaml file is auto-generated in Autobuild steps below.)<a name="0"></a>](#insqueryyamlins-input-file-format-this-yaml-file-is-auto-generated-in-autobuild-steps-below)
  - [Autobuild steps <a name="1"></a>](#autobuild-steps-)
      - [Requirements](#requirements)
- [Templates <a name="templates"></a>](#templates-)
  - [Single chain <a name="single_chain"></a>](#single-chain-)
    - [pangolin-query.yaml <a name="avax_query"></a>](#pangolin-queryyaml-)
    - [uniswap-query.yaml <a name="eth_query"></a>](#uniswap-queryyaml-)
    - [pegasys-query.yaml <a name="nevm_query"></a>](#pegasys-queryyaml-)
  - [Multi chain <a name="multi_chain"></a>](#multi-chain-)
    - [pangolin-uniswap-pegasys-query.yaml <a name="multi_query"></a>](#pangolin-uniswap-pegasys-queryyaml-)

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
### pangolin-query.yaml <a name="avax_query"></a>
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

### uniswap-query.yaml <a name="eth_query"></a>
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

### pegasys-query.yaml <a name="nevm_query"></a>
```yaml
#Single chain - NEVM - pegasys
graph: NEVM
endpoint: /indexer
chains:
  - name: NEVM_PEGASYS
    rpc_host: https://rpc.syscoin.org/
    abi: abi/pegasysRouter.json
    query:
      - name: Withdrawal
      - name: Deposit
      - name: Approval
      - name: Burn
      - name: Mint
      - name: Swap
      - name: Sync
      - name: Transfer
    address:
    - name: Pegasys_Router
      address: '0x017dAd2578372CAEE5c6CddfE35eEDB3728544C4'
    historical:
    - fromBlock: "38202"
```
  
## Multi chain <a name="multi_chain"></a>
  ### pangolin-uniswap-pegasys-query.yaml <a name="multi_query"></a>
```yaml
#Multi chain AVAX - ETH - NEVM
graph: AVAX_ETH_NEVM
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
  - name: NEVM_PEGASYS
    rpc_host: https://rpc.syscoin.org/
    abi: abi/pegasysRouter.json
    query:
      - name: Withdrawal
      - name: Deposit
      - name: Approval
      - name: Burn
      - name: Mint
      - name: Swap
      - name: Sync
      - name: Transfer
    address:
    - name: Pegasys_Router
      address: '0x017dAd2578372CAEE5c6CddfE35eEDB3728544C4'
    historical:
    - fromBlock: "38202"

```
