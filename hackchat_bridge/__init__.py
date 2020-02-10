from jarbas_utils import create_daemon
from jarbas_hive_mind.slave.terminal import HiveMindTerminalProtocol, HiveMindTerminal
from jarbas_utils.log import LOG
from jarbas_utils.messagebus import Message
from hackchat_bridge.hackchat import HackChat

platform = "JarbasHackChatBridgeV0.3"


class JarbasHackChatBridgeProtocol(HiveMindTerminalProtocol):

    def onOpen(self):
        super().onOpen()
        LOG.info("Channel: {0}".format(self.factory.channel))
        LOG.info("Username: {0}".format(self.factory.username))
        self.factory.start_hackchat()


class JarbasHackChatBridge(HiveMindTerminal):
    protocol = JarbasHackChatBridgeProtocol

    def __init__(self, username, channel, *args, **kwargs):
        super(JarbasHackChatBridge, self).__init__(*args, **kwargs)
        self.status = "disconnected"
        self.client = None
        self.username = username
        self.channel = channel
        self.hackchat = HackChat(self.username, self.channel)

    def start_hackchat(self):
        self.hackchat.on_message += [self.on_hack_message]
        self.hackchat.on_join += [self.on_hack_join]
        self.hackchat.on_open += [self.on_hack_open]
        self.hackchat.on_leave += [self.on_hack_leave]
        create_daemon(self.hackchat.run)

    @property
    def online_users(self):
        return self.hackchat.online_users

    def on_hack_open(self, connector, users):
        if len(users) == 1:
            self.hackchat.send_message("This channel belongs to me")
        else:
            self.hackchat.send_message("I see {} online users"
                                       .format(len(users) - 1))

    def on_hack_join(self, connector, user):
        self.hackchat.send_message("Hello @{}".format(user))

    def on_hack_leave(self, connector, user):
        self.hackchat.send_message("@{} vanished from cyberspace".format(user))

    def on_hack_message(self, connector, message, user):
        utterance = message.lower().strip()
        if self.client and "@" + self.username.lower() in utterance:
            utterance = utterance.replace("@" + self.username.lower(), "")
            msg = {"data": {"utterances": [utterance], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {
                       "source": self.client.peer,
                       "destination": "hive_mind",
                       "platform": platform,
                       "user": {"hackchat_username": user}}}
            self.send_to_hivemind_bus(msg)

    def speak(self, utterance, user_data):
        user = user_data["hackchat_username"]
        utterance = "@{} , ".format(user) + utterance
        LOG.debug("Message: " + utterance)
        self.hackchat.send_message(utterance)

    def handle_incoming_mycroft(self, message):
        assert isinstance(message, Message)
        user_data = message.context.get("user")

        if user_data:
            if message.msg_type == "speak":
                utterance = message.data["utterance"]
                self.speak(utterance, user_data)
            elif message.msg_type == "hive.complete_intent_failure":
                LOG.error("complete intent failure")
                utterance = 'I don\'t know how to answer that'
                self.speak(utterance, user_data)

