import requests
from typing import List
from concurrent.futures import ThreadPoolExecutor


class Selector:
    GLOBAL = "GLOBAL"
    RULE = "节点选择"
    AUTO = "自动选择"
    FINAL = "Final"
    FAILOVER = "故障转移"
    YOUTUBE = "YouTube"
    NETFLIX = "Netflix"
    DISNEY = "Disney"
    BAHAMUT = "Bahamut"
    BILIBILI = "Bilibili"
    SPOTIFY = "Spotify"
    STEAM = "Steam"
    TELEGRAM = "Telegram"
    GOOGLE = "Google"
    MICROSOFT = "Microsoft"
    OPENAI = "OpenAI"
    PAYPAL = "PayPal"
    APPLE = "Apple"

class Mode:
    GLOBAL = "Global"
    RULE = "Rule"
    DIRECT = "Direct"

def access_msg(status_code, content) -> dict:
    return {"status": status_code, "content": content}


class ClashAPI:
    def __init__(self, external_controller = "127.0.0.1:9090", secret = ""):
        if not external_controller.startswith("http"):
            self.exc = "http://" + external_controller
        self.secret = secret
        self.headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {secret}",
        }
        if not self.test_clash_conn():
            raise ConnectionError(f"fail to connect Clash server at '{self.exc}'")

    # test the connection to the Clash server
    def test_clash_conn(self, timeout = 2000) -> bool:
        try:
            url = f"{self.exc}/configs"
            response = requests.get(url, headers=self.headers, timeout=timeout)
            return response.ok
        except:
            return False

    # get the name of the current proxy
    def get_now_proxy(self, selector = Selector.GLOBAL, timeout = 2000) -> str:
        url = f"{self.exc}/proxies/{selector}"
        response = requests.get(url, headers=self.headers, timeout=timeout)
        if response.ok:
            return response.json()["now"]
        else:
            raise Exception(access_msg(response.status_code, response.content.decode("utf-8")))

    # get the names of all proxies     
    def get_all_proxy(self, selector = Selector.GLOBAL, timeout = 2000) -> List[str]:
        url = f"{self.exc}/proxies/{selector}"
        response = requests.get(url, headers=self.headers, timeout=timeout)
        if response.ok:
            return response.json()["all"]
        else:
            raise Exception(access_msg(response.status_code, response.content.decode("utf-8")))
    
    # get the delay of a proxy to a target url
    # `except_filter`  When response not OK:
    # if the status code is in `except_filter` return `except_value`, else raise Exception
    def get_proxy_delay(self, proxy_name: str, target_url: str, timeout = 5000, except_filter = [503, 504], except_value = -1) -> int:
        url = f"{self.exc}/proxies/{proxy_name}/delay?url={target_url}&timeout={timeout}"
        response = requests.get(url, headers=self.headers, timeout=timeout)
        if response.ok:
            return response.json()["delay"]
        else:
            if response.status_code in except_filter:
                return except_value
            else:
                raise Exception(access_msg(response.status_code, response.content.decode("utf-8")))

    # get the delay of all proxies to a target url   
    def get_all_delay(self, target_url, timeout = 5000, except_filter = [503, 504], except_value = -1) -> dict[str, int]:
        all_proxy = self.get_all_proxy()
        delays = {}
        with ThreadPoolExecutor() as executor:
            delays = {
                proxy: delay for proxy, delay in zip(
                    all_proxy,
                    executor.map(
                        lambda x: self.get_proxy_delay(
                            proxy_name=x,
                            target_url=target_url,
                            timeout=timeout,
                            except_filter=except_filter,
                            except_value=except_value
                        ),
                        all_proxy
                    )
                )
            }
        return delays

    # set the mode of proxy(eg. "Global", "Rule", "Direct") 
    def set_mode(self, mode = Mode.GLOBAL):
        url = f"{self.exc}/configs"
        body = {"mode": mode}
        response = requests.patch(url, headers=self.headers, json=body)
        if not response.ok:
            raise Exception(access_msg(response.status_code, response.content.decode("utf-8")))

    # set the proxy of a selector
    def set_proxy(self, proxy_name, selector = Selector.GLOBAL):
        url = f"{self.exc}/proxies/{selector}"
        body = {"name": proxy_name}
        response = requests.put(url, json=body, headers=self.headers)
        if not response.ok:
            raise Exception(access_msg(response.status_code, response.content.decode("utf-8")))
    



if __name__ == "__main__":
    api = ClashAPI()
    print(api.get_now_proxy(Selector.RULE))
    print("-------------------")
    print(api.get_all_proxy(Selector.GLOBAL))
    print("-------------------")
    print(api.get_proxy_delay("美国 1", "https://www.bilibili.com"))
    print("-------------------")
    print(api.set_mode(Mode.RULE))
    api.set_proxy("美国 2", Selector.RULE)
    