from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser
from clashAPI import Selector, Mode, clashAPI


def read_proxy_config(file_path):
    cfp = ConfigParser()
    flag = cfp.read(file_path, encoding='utf-8')
    if not flag:
        raise FileNotFoundError(f"[错误] 缺少配置文件 '{file_path}'")

    try:
        config = {}
        config["host"] = cfp.get('proxy config', 'host')
        config["port"] = cfp.get('proxy config', 'port')
        config["selector"] = cfp.get('proxy config', 'selector')
        config["secret"] = cfp.get('proxy config', 'secret')
        return config
    except:
        raise Exception(f"[错误] 配置文件 {file_path} 格式错误，或未包含必要字段：host, port, selector, secret")

class proxy:
    def __init__(self, config_file = "./config.txt"):
        config = read_proxy_config(config_file)
        try:
            self.clash = clashAPI(f"{config["host"]}:{config["port"]}", config["secret"])
        except:
            raise ConnectionError(f"[错误] Clash 连接失败，请检查 Clash 是否已启动并在端口 '{config["host"]}:{config["port"]}' 监听")
        self.selector = config["selector"]
        try:
            self.all_proxy = self.clash.get_all_proxy(self.selector)
        except:
            raise Exception(f"[错误] 获取代理列表失败，请检查配置文件 '{config_file}' 中的 selector 是否正确")

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
        self.all_proxy.remove(self.clash.get_now_proxy(self.selector))
        if self.all_proxy == []: return "无可用代理"
        self.test_all_proxy("https://mall.bilibili.com")
        min_delay_proxy = min(self.delays, key=self.delays.get)
        if self.delays[min_delay_proxy] == 9999: return "所有代理延迟过高，无法使用代理"
        self.clash.set_proxy(min_delay_proxy, self.selector)
        return "ok"





if __name__ == "__main__":
    p = proxy(Selector.PAYPAL)
    print("---------------")
    # p.test_all_proxy("https://mall.bilibili.com")
    # print({k: v for k, v in p.delays.items() if v != 99999})
    p.change_proxy()