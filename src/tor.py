from stem import Signal
from stem.control import Controller
import requests
import json


def switch_tor_proxy():
    """
    切换 Tor 代理地址
    :return: NULL
    """
    with Controller.from_port() as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)


for i in range(10):
    switch_tor_proxy()
    proxies = {'http': 'socks5://127.0.0.1:9150',
               'https': 'socks5://127.0.0.1:9150'}
    output = requests.get(
        "https://httpbin.org/ip",
        proxies=proxies
    )
    print(json.loads(output.content))