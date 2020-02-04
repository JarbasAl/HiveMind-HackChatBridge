from hackchat_bridge import JarbasHackChatBridge, platform
from jarbas_hive_mind import HiveMindConnection


def connect_hackchat_to_hivemind(channel,
                                 username="Jarbas_BOT",
                                 host="127.0.0.1",
                                 crypto_key="1L6z3WAtk4c5U9sS",
                                 port=5678, name="JarbasHackChatBridge",
                                 key="hackchat_key", useragent=platform):
    con = HiveMindConnection(host, port)

    terminal = JarbasHackChatBridge(channel=channel,
                                    username=username,
                                    crypto_key=crypto_key,
                                    headers=con.get_headers(name, key),
                                    useragent=useragent)

    con.secure_connect(terminal)


if __name__ == '__main__':
    # TODO argparse
    connect_hackchat_to_hivemind("JarbasAi")
