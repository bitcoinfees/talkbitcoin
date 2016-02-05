import code
import socket

import bitcoin
from bitcoin.messages import *
from bitcoin.net import *
from _talkbitcoin import PeerConn, MsgList

peer = None


def connect(host="localhost", port=bitcoin.params.DEFAULT_PORT,
            sendversion=True):
    global peer
    if peer is not None:
        if not peer.is_alive():
            peer = None
        else:
            print("Already connected to a peer. Call disconnect() first.")
            return
    conn = socket.create_connection((host, port))
    peer = PeerConn(conn)
    peer.start()
    print("Connected to {}.".format(peer.peername))

    if sendversion:
        send(msg_version())
        print("Version message sent.")


def disconnect():
    global peer
    if peer is not None:
        peer.stop()
        peer.join()
        print("Disconnected from {}.".format(peer.peername))
        peer = None


def send(msg):
    global peer
    if peer is None or not peer.is_alive():
        status()
    else:
        peer.send(msg)


def recv():
    """Receive all buffered messages."""
    msgs = MsgList()
    while True:
        msg = peer.recv()
        if msg is None:
            break
        msgs.append(msg)
    return msgs


def status():
    global peer
    if peer is None or not peer.is_alive():
        print("Not connected.")
        peer = None
    else:
        print("Connected to {}: {} messages in receive buffer.".
              format(peer.peername, peer.recvq.qsize()))

st = status  # Alias


if __name__ == "__main__":
    st = status
    code.interact(local=locals())
    disconnect()
