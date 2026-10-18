from ubuntu:20.04

RUN apt-get update && apt-get install -y curl python3 python3-pip iptables


WORKDIR /opt/buffalo

RUN python3 -m pip install wheel
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN sh -c "mkdir bin && curl 'https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.10.11-7231b3ef.tar.gz' > bin/geth_alltools.tar.gz"

RUN cd bin && tar xzvf geth_alltools.tar.gz && cd .. && mv bin/geth-alltools-* bin/geth

COPY artifacts/contracts/nft.sol/PhishToken.json .
COPY artifacts/contracts/registry.sol/Registry.json .
COPY allkeys.txt .
COPY keys/ keys/
COPY genesis.json .
COPY start_srv.sh .
COPY trickle_ether.py .
COPY deploy_team_default_contract.py .
COPY flag_srv.py .
COPY exploit.py .
RUN chmod +x start_srv.sh

CMD ./start_srv.sh

