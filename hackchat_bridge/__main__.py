from hackchat_bridge import JarbasHackChatBridge, platform
from jarbas_hive_mind import HiveMindConnection


def connect_hackchat_to_hivemind(channel,
                                 username="Jarbas_BOT",
                                 host="wss://127.0.0.1",
                                 crypto_key=None,
                                 port=5678, name="JarbasHackChatBridge",
                                 key="unsafe", useragent=platform):
    con = HiveMindConnection(host, port)

    terminal = JarbasHackChatBridge(channel=channel,
                                    username=username,
                                    crypto_key=crypto_key,
                                    headers=con.get_headers(name, key),
                                    useragent=useragent)

    con.connect(terminal)


if __name__ == '__main__':
    # TODO argparse
    connect_hackchat_to_hivemind("GoldyfruitHiveMindDemo")
