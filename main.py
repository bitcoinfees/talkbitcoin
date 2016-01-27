import code
import socket
from pprint import pprint

import bitcoin
from bitcoin.messages import *
import talkbitcoin

peer = None


def connect(host="localhost", port=bitcoin.params.DEFAULT_PORT):
    global peer
    if peer is not None:
        if not peer.is_alive():
            peer = None
        else:
            print("Already connected to a peer. Call disconnect() first.")
            return
    conn = socket.create_connection((host, port))
    peer = talkbitcoin.PeerConnection(conn)
    peer.start()
    print("Connected to {}.".format(peer.peername))


def disconnect():
    global peer
    if peer is not None:
        peer.stop()
        peer.join()
        print("Disconnected from {}.".format(peer.peername))
    else:
        peer = None


def status():
    global peer
    if peer is None or not peer.is_alive():
        print("Not connected.")
        peer = None
    else:
        print("Connected to {}: {} messages in receive buffer.".
              format(peer.peername, peer.recvq.qsize()))


def send(msg):
    global peer
    if peer is None or not peer.is_alive():
        status()
    else:
        peer.send(msg)


def recv():
    return peer.recv()


def recvall():
    """Receive all buffered messages."""
    msgs = []
    while True:
        msg = peer.recv()
        if msg is None:
            break
        msgs.append(msg)
    return msgs


def summarize(msgs):
    """Summary of the output of recvall."""
    for i, msg in enumerate(msgs):
        print("{:<3}: {}".format(i, msg.command))


if __name__ == "__main__":
    st = status
    code.interact(local=locals())
    disconnect()
