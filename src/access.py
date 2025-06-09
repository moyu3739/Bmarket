from requests import post
from typing import List
from Item import Item


def read_cookie():
    try:
        with open("cookie.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        raise FileNotFoundError("Cookie 缺失或已失效，请重新配置 Cookie")
    
def get_all_browsers():
    import browser_cookie3
    return {
        "edge": browser_cookie3.edge,
        "chrome": browser_cookie3.chrome,
        "chromium": browser_cookie3.chromium,
        "firefox": browser_cookie3.firefox,
        "opera": browser_cookie3.opera,
        "safari": browser_cookie3.safari,
    }
    
def fetch_cookie_from_browser(browser: str, domain: str) -> str:
    # 获取浏览器的 cookie
    all_browsers = get_all_browsers()
    if browser not in all_browsers:
        raise ValueError(f"Unsupported browser: {browser}.")
    cj = all_browsers[browser](domain_name=domain)
          
    # 将全部 cookie 放进一个字符串
    cookie_str = ""
    for cookie in cj:
        # print(f"【{cookie.domain}||{cookie.name}】{cookie.value}")
        cookie_str += f"{cookie.name}={cookie.value}; "

    return cookie_str

def fetch_cookie_and_save(browser: str) -> str:
    cookie = fetch_cookie_from_browser(browser, "bilibili.com")
    with open("cookie.txt", "w", encoding="utf-8") as f:
        f.write(cookie)
    return cookie

class access:
    def __init__(self):
        self.MARKET_URL = "https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list"
        self.HEADERS = {
            "Cookie": read_cookie(),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        }

    def get_market_data(
        self,
        category_filter: str,
        next_id: str = None,
        sort_type: str = "TIME_DESC",
        price_filter: List[str] = [],
        discount_filter: List[str] = [],
    ):
        response = post(
            url=self.MARKET_URL,
            headers=self.HEADERS,
            json={
                "categoryFilter": category_filter,
                "nextId": next_id,
                "sortType": sort_type,
                "priceFilter": price_filter,
                "discountFilter": discount_filter,
            },
        )
        return response.json()
    
    def filter_data(self, data: dict, keywords = [], shieldwords = []): 
        result = []
        for item_record in data:
            id = item_record.get("c2cItemsId", None)
            name = item_record.get("c2cItemsName", None)
            price = float(item_record.get("showPrice", None))
            origin_price = float(item_record.get("showMarketPrice", None))
            detail_list = item_record.get("detailDtoList", [])

            item = Item(id, name, price, origin_price, detail_list)
            if item.Filtrate(keywords, shieldwords):
                result.append(item)
        return result
    
    def fetch(self, next_id, category: str, sort: str, keywords = [], shieldwords = []):
        data = self.get_market_data(
            next_id=next_id,
            category_filter=category,
            discount_filter=[],
            price_filter=[],
            sort_type=sort,
        )
        data = data.get("data", {})
        nextId = data.get("nextId", None)
        result = self.filter_data(data.get("data", []), keywords, shieldwords)
        return nextId, result



if __name__ == "__main__":
    # cookie = fetch_cookie_from_browser("edge", "bilibili.com")
    # print(cookie)
    acc = access()
    data = acc.get_market_data("2312")
    import json
    with open("test.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
