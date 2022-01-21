

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


## <ins>query.yaml</ins> input file format <a name="0"></a>
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
### Use with [EXRPROXY-ENV](https://github.com/blocknetdx/exrproxy-env) repo 
#### Requirements
- `Docker`
- `Docker-Compose`
- `Servicenode Private Key`
- `Port 80 must be opened on the host`

#### 1. Manually edit your environment data

```
export PUBLIC_IP=""  # Update with your public ip address
export SN_NAME="servicenode01"  # Update with your snode name
export SN_KEY="servicenodeprivatekey"  # Update with your snode private key
export SN_ADDRESS="servicenodekeyaddress"  # Update with your snode address
export RPC_USER="user"
export RPC_PASSWORD="password"
docker-compose -f "docker-compose.yml" up -d --build
```

#### 2. Clone repo - using the command below you can clone this repo with XQuery submodule

```
git clone --recursive https://github.com/blocknetdx/exrproxy-env.git
```

```
cd exrproxy-env
```

```
git submodule update --init --recursive
```

#### 3. Input file - Edit your XQuery integration input file with your desired graph 

Check for reference for local nodes:

```
autobuild/examples/xquery-gethINT-avaxINT.yaml
```

To use external connections check:

```
autobuild/examples/xquery-gethEXT-avaxEXT.yaml
```

#### 4. Change to autobuild directory

```
cd autobuild
```

#### 5. Install python requirements if not already installed
```
pip3 install -r requirements.txt
```

#### 6. Generate docker-compose stack

```
python app.py --yaml examples/xquery-gethINT-avaxINT.yaml
```

#### 7. Change to the root folder of the repo and move/copy the generated files

```
mv autobuild/dockercompose-custom.yaml docker-compose.yml
mv autobuild/xquery.yaml xquery.yaml
```

#### 8. Build images

```
docker-compose build
```

#### 9. Deploy stack

```
docker-compose -f docker-compose.yml up -d --build
```

#### 10. Create project

```
curl http://127.0.0.1/xrs/projects \
                    -X POST \
                    -H "Content-Type: application/json" \
                    -d '{"jsonrpc":"2.0","method":"request_project","params": [],"id":1}'
```

#### 11. With the api-key provided and after payment get your data

```
curl http://127.0.0.1/xrs/xquery/<PROJECT-ID>/help -X POST -H "Api-Key:<API-KEY>"
```

#### 12. Test XQuery via python code

Check the python script in autobuild/xq.py

```
python3 exrproxy-env/autobuild/xq.py --projectid YOUR-PROJECT-ID --apikey YOUR-API-KEY
```



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

