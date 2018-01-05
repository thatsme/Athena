#!/usr/bin/env python
import argparse
import logging
import sys
import asyncio
import websockets
import functools
import os
import signal
from trafaret_config import commandline
from lib.util import CLIENT_CONFIG

message_count = 0

def ask_exit(signame, loop):
    """
    Get the exit signal and stop the loop
    :param signame: Signame
    :param loop: Asyncio loop
    :return:
    """
    print("got signal %s: exit".format(signame))
    loop.stop()

async def senddata(msg, lserver):
    """
    Send message to local application server
    :param msg: Message to send
    :param lserver: Local application server
    :return:
    """
    global message_count
    async with websockets.connect(lserver) as websocketlocal:
        await websocketlocal.send(msg)
        message_count += 1
        print("client message number > {}".format(message_count))
        server_message_count = await websocketlocal.recv()
        print("<server message count {}".format(server_message_count))

async def myservice(r, l, s):
    """
    Main service function
    :param r: Remote Blockchain websocket api
    :param l: Local application server
    :param s: Type of remote service to invoke
    :return:
    """
    async with websockets.connect(r) as websocketremote:
        ##
        ## For full list of services go to
        ## https://blockchain.info/api/api_websocket
        ##
        #service = '{"op":"unconfirmed_sub"}'
        #service = '{"op": "ping_tx"}'
        print(type(s),s)
        print(type(r),r)
        await websocketremote.send(s)
        print("client> {}".format(s))
        while True:
            result = await websocketremote.recv()
            print("<blockchain {}".format(result))
            await senddata(result, l)


def main(argv):

    """
    Main , if debug is needed, add --debug=True to sc script

    :param argv:
    :return:
    """

    logging.basicConfig(level=logging.DEBUG)

    ap = argparse.ArgumentParser()
    commandline.standard_argparse_options(ap, default_config='./config/client.yaml')

    #
    # define your command-line arguments here
    #
    options = ap.parse_args(argv)

    config = commandline.config_from_options(options, CLIENT_CONFIG)

    if config["debug"]:
        print("Blockchain remote server ",config["blockchain"]["server"])
        print("Blockchain service key ",config["blockchain"]["service_key"])
        print("Blockchain service val ",config["blockchain"]["service_value"])
        print("Local Server ", config["local_server"]["server"])

    blservice = '{{"{}":"{}"}}'.format(config["blockchain"]["service_key"], config["blockchain"]["service_value"])

    #blservice = '{"op":"unconfirmed_sub"}'

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame, loop))

    print("Event loop running forever, press Ctrl+C to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())

    loop.run_until_complete(myservice(config["blockchain"]["server"], config["local_server"]["server"], blservice))
    loop.run_forever()


if __name__=='__main__':
    main(sys.argv[1:])
