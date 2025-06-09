from abc import ABC, abstractmethod


class Item:
    id = 0
    name = ''
    price = 0
    origin_price = 0
    discount = 0
    detail_list = []

    def __init__(self, id: int, name: str, price: float, origin_price: float, detail_list = []):
        self.id = id
        self.name = name
        self.price = price
        self.origin_price = origin_price
        self.discount = float(price) / float(origin_price)
        self.detail_list = detail_list
    
    # keywords := [ [...], [...] ]
    # keywords每一行内部为合取逻辑，行之间为析取逻辑
    # 如果没有关键词，返回empty_default
    @staticmethod
    def Include(sentence: str, keywords = [], empty_default = True):
        if len(keywords) == 0: return empty_default
        for words_group in keywords:
            flag = True
            for keyword in words_group:
                if keyword not in sentence:
                    flag = False
                    break
            if flag: return True
        return False
    
    # 所有keywords都包含，所有shieldwords都不包含
    def Filtrate(self, keywords = [], shieldwords = []):
        flag_main = Item.Include(self.name, keywords, True) and not Item.Include(self.name, shieldwords, False)

        flag_detail = False
        for detail in self.detail_list:
            name = detail.get("name", "")
            if Item.Include(name, keywords, True) and not Item.Include(name, shieldwords, False):
                flag_detail = True
                break 
        return flag_main | flag_detail
    
    def GetItemURL(self):
        return f"https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId={self.id}&from=market_index"

    @staticmethod
    def ParseIdFromItemURL(url: str):
        params = url.split("&")
        for param in params:
            if param.startswith("itemsId="):
                return int(param.split("=")[1])
        return None

    def GetImageURL(self, w):
        img_url_base: str = self.detail_list[0].get("img", None) if len(self.detail_list) > 0 else None
        if img_url_base is not None:
            if img_url_base.startswith("https:"): return f"{img_url_base}@{w}w_{w}h_85q.webp"
            else: return f"https:{img_url_base}@{w}w_{w}h_85q.webp"
        else:
            return None

    def GetInfo(self):
        return f"{self.name} - {self.price}元（原价：{self.origin_price}元，{'%.2f'%self.discount}折） - {self.GetItemURL()}"

    @staticmethod
    def ToJson(item):
        return {
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "origin_price": item.origin_price,
            "detail_list": item.detail_list
        }
    
    @staticmethod
    def FromJson(item_dict: dict):
        id           = item_dict["id"]
        name         = item_dict["name"]
        price        = item_dict["price"]
        origin_price = item_dict["origin_price"]
        detail_list  = item_dict["detail_list"]
        return Item(id, name, price, origin_price, detail_list)


if __name__ == '__main__':
    item = Item("11111", "test", 10, 20, "image/url", [])
    s = Item.ToJson(item)
    print(s)
    item2 = Item.FromJson(s)
    print(item2.GetInfo())