from abc import ABC, abstractmethod


class Item:
    id = 0
    name = ''
    price = 0
    origin_price = 0
    discount = 0
    detail_list = []

    def __init__(self, id_: str, name_: str, price_: float, origin_price_: float, detail_list_ = []):
        self.id = id_
        self.name = name_
        self.price = price_
        self.origin_price = origin_price_
        self.discount = float(price_) / float(origin_price_)
        self.detail_list = detail_list_
    
    # keywords := [ [...], [...] ]
    # keywords每一行内部为合取逻辑，行之间为析取逻辑
    # 如果没有关键词，返回empty_default
    @staticmethod
    def include(sentence: str, keywords = [], empty_default = True):
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
    def filter(self, keywords = [], shieldwords = []):
        flag_main = Item.include(self.name, keywords, True) and not Item.include(self.name, shieldwords, False)

        flag_detail = False
        for detail in self.detail_list:
            name = detail.get("name", "")
            if Item.include(name, keywords, True) and not Item.include(name, shieldwords, False):
                flag_detail = True
                break 
        return flag_main | flag_detail
    
    def process_url(self):
        return f"https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId={self.id}&from=market_index"

    def info(self):
        return f"{self.name} - {self.price}元（原价：{self.origin_price}元，{'%.2f'%self.discount}折） - {self.process_url()}"

    @staticmethod
    def to_json(item):
        return {
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "origin_price": item.origin_price,
            "detail_list": item.detail_list
        }
    
    @staticmethod
    def from_json(json_str):
        id = json_str["id"]
        name = json_str["name"]
        price = json_str["price"]
        origin_price = json_str["origin_price"]
        detail_list = json_str["detail_list"]
        return Item(id, name, price, origin_price, detail_list)


if __name__ == '__main__':
    item = Item("11111", "test", 10, 20, [])
    s = Item.to_json(item)
    print(s)
    item2 = Item.from_json(s)
    print(item2.info())