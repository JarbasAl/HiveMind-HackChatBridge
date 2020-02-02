from threading import Thread
import json
import websocket
from time import sleep
from jarbas_utils.log import LOG


class HackChat:
    """A library to connect to https://hack.chat.
    <on_message> is <list> of callback functions to receive data from
    https://hack.chat. Add your callback functions to this attribute.
    e.g., on_message += [my_callback]
    The callback function should have 3 parameters, the first for the
    <HackChat> object, the second for the message someone sent and the
    third for the nickname of the sender of the message.

    https://github.com/gkbrk/hackchat
    """

    def __init__(self, nick, channel="programming", debug=True):
        """Connects to a channel on https://hack.chat.
        Keyword arguments:
        nick -- <str>; the nickname to use upon joining the channel
        channel -- <str>; the channel to connect to on https://hack.chat
        """
        self.debug = debug
        self.nick = nick
        self.channel = channel
        self.online_users = []
        self.on_message = []
        self.on_join = []
        self.on_open = []
        self.on_leave = []
        self.ws = websocket.create_connection("wss://hack.chat/chat-ws")
        self._send_packet({"cmd": "join", "channel": channel, "nick": nick})
        Thread(target=self._ping_thread).start()

    def send_message(self, msg):
        """Sends a message on the channel."""
        self._send_packet({"cmd": "chat", "text": msg})

    def _send_packet(self, packet):
        """Sends <packet> (<dict>) to https://hack.chat."""
        encoded = json.dumps(packet)
        self.ws.send(encoded)

    def run(self):
        """Sends data to the callback functions."""
        while True:
            result = json.loads(self.ws.recv())
            if self.debug:
                LOG.debug("[Raw Hackchat] " + str(result))

            if result["cmd"] == "chat" and not result["nick"] == self.nick:
                for handler in list(self.on_message):
                    handler(self, result["text"], result["nick"])
            elif result["cmd"] == "onlineAdd":
                self.online_users.append(result["nick"])
                for handler in list(self.on_join):
                    handler(self, result["nick"])
            elif result["cmd"] == "onlineRemove":
                self.online_users.remove(result["nick"])
                for handler in list(self.on_leave):
                    handler(self, result["nick"])
            elif result["cmd"] == "onlineSet":
                for nick in result["nicks"]:
                    self.online_users.append(nick)
                for handler in list(self.on_open):
                    handler(self, result["nicks"])

    def _ping_thread(self):
        """Retains the websocket connection."""
        while self.ws.connected:
            self._send_packet({"cmd": "ping"})
            sleep(60)
