import argparse
import logging
import sys
import asyncio
import websockets
import json
import functools
import os
import signal
from aioredis import create_redis
from lib.models import Transactions
from uuid import uuid4
from trafaret_config import commandline
from lib.util import SERVER_CONFIG

msg_queue = asyncio.Queue()
message_count = 0

def ask_exit(signame, loop):
    print("got signal %s: exit" % signame)
    loop.stop()

def hello_world(loop):
    print('Test server on Mac')

async def consumer_handler(websocket):
    global msg_queue
    while True:
        try:
            message = await websocket.recv()
            await msg_queue.put(message)
            print("Message queued")
            await websocket.send(str(message_count))
        except:
            pass

async def producer_handler(websocket):
    global msg_queue
    global message_count
    while True:
        print("Waiting for message in queue")
        message = await msg_queue.get()
        print("Get message from queue")
        dataDict = json.loads(message)
        db = await create_redis(('192.168.1.72', 6379), loop=None, encoding='utf-8')
        transactionList = dataDict["x"]["inputs"]
        i = 0
        for a in transactionList:
            my_uuid = str(uuid4())
            my_tx_index = a["prev_out"]["tx_index"]
            my_addr = a["prev_out"]["addr"]
            my_value = a["prev_out"]["value"]
            my_transaction = Transactions(
                uuid=my_uuid,
                tx_index=my_tx_index,
                addr = my_addr,
                value = my_value,
            )
            await my_transaction.save(db)
            print('Transaction {} with uuid {},{} ..Saved'.format(i, my_uuid, my_addr))
            #await consumer_handler()

            #retrieved_transaction = await Transactions.load(db, my_uuid)
            #print('Retrieved {}'.format(retrieved_transaction.as_dict()))
            i += 1

        message_count += 1
        print("Message count {}".format(message_count))

async def handler(websocket, path):
    print("Got a new connection...")
    consumer_task = asyncio.ensure_future(consumer_handler(websocket))
    producer_task = asyncio.ensure_future(producer_handler(websocket))

    done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
    print("Connection closed, canceling pending tasks")
    #for task in pending:
    #    task.cancel()


#def main(local_server=None, port=None, debug=False):
def main(argv):

    logging.basicConfig(level=logging.DEBUG)

    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(ap, default_config='./config/server.yaml')
    #
    # define your command-line arguments here
    #
    options = ap.parse_args(argv)

    config = commandline.config_from_options(options, SERVER_CONFIG)

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    print("Event loop running forever, press Ctrl+C to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())


    start_server = websockets.serve(handler, config["local_server"]["server"], config["local_server"]["port"])

    loop.set_debug(config["debug"])
    loop.call_soon(hello_world, loop)
    loop.run_until_complete(start_server)
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.run_forever()

if __name__=='__main__':
    main(sys.argv[1:])