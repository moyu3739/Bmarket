from abc import ABC, abstractmethod


class Item:
    id = 0
    name = ''
    price = 0
    origin_price = 0
    discount = 0
    detail_list = []

    def __init__(self, id_, name_, price_, origin_price_, detail_list_):
        self.id = id_
        self.name = name_
        self.price = price_
        self.origin_price = origin_price_
        self.discount = float(price_) / float(origin_price_)
        self.detail_list = detail_list_
    
    # keywords := [ [...], [...] ]
    # keywords每一行内部为合取逻辑，行之间为析取逻辑
    # 如果没有关键词，返回empty_default
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
