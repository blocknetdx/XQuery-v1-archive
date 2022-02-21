import json
import time
import zmq
import sys
import os
from utils.xquery import XQuery

POD_TOKEN_INCREMENT = 500
FRONTEND_PORT = os.environ.get('ZMQ_GATEWAY_PORT2', 5556)
BACKEND_PORT = os.environ.get('ZMQ_GATEWAY_PORT1', 5555)
connections = {}
txs = []

import logging

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname:<8} {message}",
    style='{',
)

logger = logging.getLogger('main.py')

def main():
    global frontend, backend, context, txs
    try:
        logger.info('Initializing')

        context = zmq.Context()

        frontend = context.socket(zmq.PULL)
        frontend.set_hwm(0)
        frontend.bind("tcp://*:{}".format(FRONTEND_PORT))

        logger.info('Frontend listening on port {}'.format(FRONTEND_PORT))

        # backend = context.socket(zmq.PUSH)
        backend = context.socket(zmq.PUB)
        backend.set_hwm(0)
        backend.setsockopt(zmq.LINGER, 0)
        backend.bind("tcp://*:{}".format(BACKEND_PORT))
        logger.info('Backend listening on port {}'.format(BACKEND_PORT))


        while True:
            try:
                if len(txs) >= 1000:
                    txs = txs[1000:]

                try:
                    for connection in connections.copy():
                        if connections[connection]['init'] != 0 and (int(time.time()) - connections[connection]['init']) >= 300:
                            logger.info('Removing connection: {}'.format(connections[connection]))
                            del connections[connection]

                        if connections[connection]['init'] == 0 and (int(time.time()) - connections[connection]['ping']) >= 300:
                            logger.info('Removing connection: {}'.format(connections[connection]))
                            del connections[connection]
                except Exception as e:
                    logger.critical("Exception: ",exc_info=True)

                msg = frontend.recv()
                j = json.loads(msg)

                data = []
                if j['topic'] == 'trades':
                    for message in j['data']:
                        item = XQuery()
                        for attr in list(message):
                            setattr(item, attr, message[attr])

                        if any((x.xhash == item.xhash) for x in txs):
                            logger.info(f'ALREADY QUERY:{item.query_name} XHASH:{item.xhash} TX:{item.tx_hash}')

                            continue
                        else:
                            logger.info(f'PASSED QUERY:{item.query_name} XHASH:{item.xhash} TX:{item.tx_hash}')
                            data.append(message)
                            txs.insert(0, item)

                    backend.send_json({
                        'topic': 'trades',
                        'data': data
                    })
                elif j['topic'] == 'connect':
                    logger.info(j)

                    connection_id = j['data']['id']
                    if connection_id in connections:
                        continue

                    connections[connection_id] = {
                        # 'limit': limit,
                        'ping': int(time.time()),
                        'init': int(time.time())
                    }

                    logger.info(connections[connection_id])

                    backend.send_json({
                        'topic': connection_id,
                        'data': connections[connection_id]
                    })
                    continue
                elif j['topic'] == 'ping':
                    connection_id = j['data']['id']
                    if connection_id in connections:
                        connections[connection_id]['init'] = 0
                        connections[connection_id]['ping'] = int(time.time())
                        logger.info(connections[connection_id])

                elif j['topic'] == 'disconnect':
                    logger.info(j)

                    connection_id = j['data']['id']
                    if connection_id in connections:
                        del connections[connection_id]
            except Exception as e:
                logger.critical("Exception: ",exc_info=True)

    except Exception as e:
        logger.critical('Closing sockets',exc_info=True)
        frontend.close()
        backend.close()
        context.term()
        logger.critical('Closed',exc_info=True)
    finally:
        logger.info('Closing sockets')
        frontend.close()
        backend.close()
        context.term()
        logger.info('Closed')


if __name__ == "__main__":
    main()
