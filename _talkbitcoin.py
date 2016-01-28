import socket
import threading
import Queue
from bitcoin.net import PROTO_VERSION
from bitcoin.messages import MsgSerializable


class PeerConn(threading.Thread):

    def __init__(self, conn, protover=PROTO_VERSION):
        """Pass in an established connection."""
        self.conn = conn
        self.peername = conn.getpeername()
        self.protover = protover
        self.recvq = Queue.Queue()
        self.sendq = Queue.Queue()
        self._stopflag = threading.Event()
        super(PeerConn, self).__init__()

    def run(self):
        sendhandler = threading.Thread(target=self._handle_send)
        recvhandler = threading.Thread(target=self._handle_recv)
        sendhandler.start()
        recvhandler.start()
        recvhandler.join()
        self.stop()
        sendhandler.join()

    def send(self, msg):
        if msg is None:
            # Disallow, because None msg is a signal to stop.
            # Use self.stop to close the connection.
            raise ValueError("Msg must not be None.")
        self.sendq.put(msg)

    def recv(self):
        try:
            return self.recvq.get(block=False)
        except Queue.Empty:
            return None

    def _handle_send(self):
        while True:
            msg = self.sendq.get()
            if msg is None:
                break
            try:
                msg.stream_serialize(self.conn.makefile(mode='w'))
            except Exception as e:
                print("Msg send error: {}".format(e))

    def _handle_recv(self):
        while True:
            try:
                msg = MsgSerializable.stream_deserialize(
                    self.conn.makefile(mode='r'),
                    protover=self.protover)
            except Exception as e:
                msg = e
                if not self._stopflag.is_set():
                    print("Peer connection closed unexpectedly.")
                break
            finally:
                self.recvq.put(msg)

    def stop(self):
        self._stopflag.set()
        self.sendq.put(None)
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self.conn.close()


class MsgList(list):

    MAXDISPLAYLEN = 72

    def msgrepr(self, msg):
        m = repr(msg)
        if len(m) > self.MAXDISPLAYLEN:
            m = m[:self.MAXDISPLAYLEN] + "..."
        return m

    def __repr__(self):
        return "\n".join([
            "{:<3}: {}".format(i, self.msgrepr(msg))
            for i, msg in enumerate(self)])
