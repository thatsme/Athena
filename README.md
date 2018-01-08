# Athena

Example of Bitcoin Blockchain transaction reader with output 
on Redis queue, wsrdclient_3 script connect to blockchain.info 
websocket streaming services, read transaction and push them to 
local websocket server.
From wsserver_3 script the data are pushed to redis server, with 
with predefined data structure.


# Code Example


# Motivation
proof of concept

# Installation
Work with python >= 3.6

pip install -r requirements.txt

modify the client and server yaml file based on your
systems configuration 

Server start : 

python wsserver_3.py

Client start : 

python wsrdclient_3.py

# API Reference
tbd

# Tests
tbd

# Contributors


# License
MIT License
  
