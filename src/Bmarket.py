from time import sleep
from access import access
from Log import *

CATEGORY_MAP = {
    "全部": "",
    "手办": "2312",
    "模型": "2066",
    "周边": "2331",
    "3C": "2273",
    "福袋": "fudai_cate_id",
}

SORT_MAP = {
    "时间降序（推荐）": "TIME_DESC",
    "价格升序": "PRICE_ASC",
    "价格降序": "PRICE_DESC",
}

def category2id(category: str):
    return CATEGORY_MAP.get(category, "")

def sort2type(sort: str):
    return SORT_MAP.get(sort, "TIME_DESC")

class Bmarket:
    def __init__(self, item_type, sort, keywords = [], shieldwords = []):
        self.item_type = item_type
        self.sort = sort
        self.keywords = keywords
        self.shieldwords = shieldwords
        self.bmarket_access = None

        self.next_id = None
        self.count_fetch = 0
        self.count_item = 0
        self.reconnect = 10 # 尝试重连的次数
        self.no_more = False

        # 初始化与市集的连接
        self.bmarket_access = access()

        Log.Print("开始获取商品信息...")

    def Fetch(self):
        for i in range(self.reconnect + 1):
            try:
                if self.no_more: return "no more"

                self.next_id, fetched = self.bmarket_access.fetch(
                    self.next_id,
                    category2id(self.item_type), sort2type(self.sort), self.keywords, self.shieldwords
                )

                self.count_item += len(fetched)
                if self.count_item % 100 == 0:
                    Log.Print(f"已获取 {self.count_item} 条记录")

                if not self.next_id:
                    if self.count_fetch == 0: return "invalid cookie"
                    else: self.no_more = True

                self.count_fetch += 1
                return fetched
            except Exception as e:
                if i < self.reconnect:
                    Log.Print("连接断开，可能触发风控，尝试自动重连...")
                    sleep(1) # 重连间隔，等待1秒后重连
                else: # 连续出现重连失败达到上限
                    return "reconnect failed"
