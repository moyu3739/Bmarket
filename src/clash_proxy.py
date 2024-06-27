import json
from concurrent.futures import ThreadPoolExecutor
from ClashAPI import Selector, Mode, ClashAPI


def read_proxy_config(file_path = "config.json"):
    # 读取 config.json 文件
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            clash_config = json.load(f)["config"]["clash"]
    except:
        raise Exception(f"Clash 配置缺失或错误，请重新配置")
    
    # 检查 clash_config 是否包含 host, port, selector, secret 字段
    if not all([key in clash_config for key in ["host", "port", "selector", "secret"]]):
        raise Exception(f"Clash 配置缺失或错误，请重新配置")
    
    return clash_config    

class proxy:
    def __init__(self, config_file = "config.json"):
        config = read_proxy_config(config_file)
        self.host = config["host"]
        self.port = config["port"]
        self.secret = config["secret"]
        self.selector = config["selector"]

        try:
            self.clash = ClashAPI(f"{self.host}:{self.port}", self.secret)
        except:
            raise ConnectionError(f"Clash 连接失败，请检查 Clash 是否已启动并在端口 '{self.host}:{self.port}' 监听，以及 selector 是否正确")
        
        try:
            self.all_proxy = self.clash.get_all_proxy(self.selector)
            self.now_proxy = self.clash.get_now_proxy(self.selector)
        except:
            raise ConnectionError(f"获取代理列表失败，请检查 Clash 是否正在端口 '{self.host}:{self.port}' 监听，以及 selector 是否正确")

    def test_all_proxy(self, target_url, timeout = 3000):
        with ThreadPoolExecutor() as executor:
            self.delays = {
                proxy: delay for proxy, delay in zip(
                    self.all_proxy,
                    executor.map(
                        lambda x: self.clash.get_proxy_delay(
                            proxy_name=x,
                            target_url=target_url,
                            timeout=timeout,
                            except_value=9999,
                        ),
                        self.all_proxy
                    )
                )
            }

    def change_proxy(self):
        try:
            self.all_proxy.remove(self.clash.get_now_proxy(self.selector))
            if self.all_proxy == []: return "无可用代理"
            self.test_all_proxy("https://mall.bilibili.com")

            min_delay_proxy = min(self.delays, key=self.delays.get)
            if self.delays[min_delay_proxy] == 9999: return "所有可用代理延迟过高，无法使用代理"
            self.clash.set_proxy(min_delay_proxy, self.selector)
            self.now_proxy = min_delay_proxy
            return "ok"
        except:
            return f"与 Clash 通信失败，请检查 Clash 是否正在端口 '{self.host}:{self.port}' 监听"





if __name__ == "__main__":
    p = proxy(Selector.PAYPAL)
    print("---------------")
    # p.test_all_proxy("https://mall.bilibili.com")
    # print({k: v for k, v in p.delays.items() if v != 99999})
    p.change_proxy()