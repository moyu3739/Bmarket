from concurrent.futures import ThreadPoolExecutor
from clashAPI import Selector, Mode, clashAPI

class proxy:
    def __init__(self, selector, external_controller = "127.0.0.1:9090", secret = ""):
        try:
            self.clash = clashAPI(external_controller, secret)
        except:
            raise ConnectionError(f"Clash 连接失败，请检查 Clash 是否已启动并在端口 '{external_controller}'")
        self.selector = selector
        self.all_proxy = self.clash.get_all_proxy(selector)
        

    def test_all_proxy(self, target_url, timeout = 2000):
        with ThreadPoolExecutor() as executor:
            self.delays = {
                proxy: delay for proxy, delay in zip(
                    self.all_proxy,
                    executor.map(
                        lambda x: self.clash.get_proxy_delay(
                            proxy_name=x,
                            target_url=target_url,
                            timeout=timeout,
                            except_value=99999,
                        ),
                        self.all_proxy
                    )
                )
            }

    def change_proxy(self):
        self.all_proxy.remove(self.clash.get_now_proxy(self.selector))
        self.test_all_proxy("https://mail.bilibili.com")
        min_delay_proxy = min(self.delays, key=self.delays.get)
        self.clash.set_proxy(min_delay_proxy, self.selector)





if __name__ == "__main__":
    p = proxy(Selector.PAYPAL)
    print("---------------")
    # p.test_all_proxy("https://mail.bilibili.com")
    # print({k: v for k, v in p.delays.items() if v != 99999})
    p.change_proxy()