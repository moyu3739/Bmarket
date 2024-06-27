from abc import ABC, abstractmethod
from Item import Item

class Filter(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def Judge(self, item: Item) -> bool:
        pass

class DefaultFilter(Filter):
    def Judge(self, item: Item) -> bool:
        return True
    
class NameFilter(Filter):
    def __init__(self, text: str):
        self.text = text

    def SetFilter(self, text: str):
        self.text = text

    def Judge(self, item: Item) -> bool:
        return self.text in item.name
    
class MinPriceFilter(Filter):
    def __init__(self, min_price):
        self.min_price = min_price

    def Judge(self, item: Item) -> bool:
        return float(item.price) >= self.min_price
    
class MaxPriceFilter(Filter):
    def __init__(self, max_price):
        self.max_price = max_price

    def Judge(self, item: Item) -> bool:
        return float(item.price) <= self.max_price
    
class MinOpriceFilter(Filter):
    def __init__(self, min_oprice):
        self.min_oprice = min_oprice

    def Judge(self, item: Item) -> bool:
        return float(item.origin_price) >= self.min_oprice
    
class MaxOpriceFilter(Filter):
    def __init__(self, max_oprice):
        self.max_oprice = max_oprice

    def Judge(self, item: Item) -> bool:
        return float(item.origin_price) <= self.max_oprice
    
class MinDiscountFilter(Filter):
    def __init__(self, min_discount):
        self.min_discount = min_discount

    def Judge(self, item: Item) -> bool:
        return float(item.discount) >= self.min_discount
    
class MaxDiscountFilter(Filter):
    def __init__(self, max_discount):
        self.max_discount = max_discount

    def Judge(self, item: Item) -> bool:
        return float(item.discount) <= self.max_discount

class ConjunctFilter(Filter):
    def __init__(self, filters):
        self.filters = filters

    def AddFilter(self, filter: Filter):
        self.filters.append(filter)

    def Judge(self, item: Item) -> bool:
        for filter in self.filters:
            if not filter.Judge(item): return False
        return True
    
class DisjunctFilter(Filter):
    def __init__(self, filters):
        self.filters = filters

    def AddFilter(self, filter: Filter):
        self.filters.append(filter)

    def Judge(self, item: Item) -> bool:
        if len(self.filters) == 0: return True
        for filter in self.filters:
            if filter.Judge(item): return True
        return False