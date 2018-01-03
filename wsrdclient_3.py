#!/usr/bin/env python

import asyncio
import websockets
import functools
import os
import signal
import fire

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
        await websocketremote.send(s)
        print("client> {}".format(s))
        while True:
            result = await websocketremote.recv()
            print("<blockchain {}".format(result))
            await senddata(result, l)


def main(remote_server, local_server, service, debug=False):
    """
    Main , if debug is needed, add --debug=True to sc script

    :param remote_server:
    :param local_server:
    :param service:
    :return:
    """
    if debug:
        print(remote_server, type(remote_server))
        print(local_server, type(local_server))
        print(service, type(service))
    ##
    ## If no data is passed with fire, get some
    ## defaults
    ##
    if not remote_server:
        remote_server = 'wss://ws.blockchain.info/inv'
    if not local_server:
        local_server = 'ws://localhost:5555'
    if not service:
        service = '{"op":"unconfirmed_sub"}'

    loop = asyncio.get_event_loop()
    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(ask_exit, signame))

    print("Event loop running forever, press Ctrl+C to interrupt.")
    print("pid %s: send SIGINT or SIGTERM to exit." % os.getpid())

    loop.run_until_complete(myservice(remote_server, local_server, service))
    loop.run_forever()


if __name__=='__main__':
    fire.Fire()

