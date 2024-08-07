from requests import post
from typing import List
from Item import Item


def get_cookie():
    try:
        with open("cookie.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        raise FileNotFoundError("Cookie 缺失或已失效，请重新配置 Cookie")

class access:
    def __init__(self):
        self.MARKET_URL = "https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list"
        self.HEADERS = {
            "Cookie": get_cookie(),
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
            c2cItemsId = item_record.get("c2cItemsId", None)
            showPrice = float(item_record.get("showPrice", None))
            showMarketPrice = float(item_record.get("showMarketPrice", None))
            c2cItemsName = item_record.get("c2cItemsName", None)
            detailDtoList = item_record.get("detailDtoList", [])
            item = Item(c2cItemsId, c2cItemsName, showPrice, showMarketPrice, detailDtoList)
            if item.filter(keywords, shieldwords):
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
