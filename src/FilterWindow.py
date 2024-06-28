import sys
from PyQt5.QtWidgets import QApplication, QDialog

from EasyPyQt import *
from Filter import *


class PriceFilter(ConjunctFilter):
    def __init__(self, min_price = None, max_price = None, min_oprice = None, max_oprice = None,
                 min_discount = None, max_discount = None):
        self.min_price = min_price
        self.max_price = max_price
        self.min_oprice = min_oprice
        self.max_oprice = max_oprice
        self.min_discount = min_discount
        self.max_discount = max_discount
        self.effective = min_price is not None or\
                         max_price is not None or\
                         min_oprice is not None or\
                         max_oprice is not None or\
                         min_discount is not None or\
                         max_discount is not None
        self.SetFilter()

    def SetFilter(self):
        self.filters = []
        if self.min_price is not None:
            self.filters.append(MinPriceFilter(self.min_price))
        if self.max_price is not None:
            self.filters.append(MaxPriceFilter(self.max_price))
        if self.min_oprice is not None:
            self.filters.append(MinOpriceFilter(self.min_oprice))
        if self.max_oprice is not None:
            self.filters.append(MaxOpriceFilter(self.max_oprice))
        if self.min_discount is not None:
            self.filters.append(MinDiscountFilter(self.min_discount))
        if self.max_discount is not None:
            self.filters.append(MaxDiscountFilter(self.max_discount))


class FilterWindow(QDialog):
    def __init__(self, price_filter = None, left = 100, top = 100):
        super().__init__()
        self.title = "筛选条件"
        self.left = left
        self.top = top
        self.width = 300
        self.height = 350
        self.InitUI()
        self.InitSetup(price_filter)

    def InitSetup(self, price_filter = None):
        if price_filter is not None:
            if price_filter.min_price: self.textbox_price_min.setText(str(price_filter.min_price))
            if price_filter.max_price: self.textbox_price_max.setText(str(price_filter.max_price))
            if price_filter.min_oprice: self.textbox_oprice_min.setText(str(price_filter.min_oprice))
            if price_filter.max_oprice: self.textbox_oprice_max.setText(str(price_filter.max_oprice))
            if price_filter.min_discount: self.textbox_discount_min.setText(str(price_filter.min_discount))
            if price_filter.max_discount: self.textbox_discount_max.setText(str(price_filter.max_discount))
        self.price_filter = price_filter

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 市集价区间
        self.textbox_price_min = Textbox(self, placeholder="最低价", w=75)
        self.label_price_hyphen = Label(self, "-", w=9)
        self.textbox_price_max = Textbox(self, placeholder="最高价", w=75)
        self.group_price = WrapGroup(self, "市集价",
            [self.textbox_price_min, self.label_price_hyphen, self.textbox_price_max], "H", align="center")
        
        # 原价区间
        self.textbox_oprice_min = Textbox(self, placeholder="最低价", w=75)
        self.label_oprice_hyphen = Label(self, "-", w=9)
        self.textbox_oprice_max = Textbox(self, placeholder="最高价", w=75)
        self.group_oprice = WrapGroup(self, "原价",
            [self.textbox_oprice_min, self.label_oprice_hyphen, self.textbox_oprice_max], "H", align="center")
        
        # 市集折扣区间
        self.textbox_discount_min = Textbox(self, placeholder="最低折扣", w=75)
        self.label_discount_hyphen = Label(self, "-", w=9)
        self.textbox_discount_max = Textbox(self, placeholder="最高折扣", w=75)
        self.group_discount = WrapGroup(self, "市集折扣",
            [self.textbox_discount_min, self.label_discount_hyphen, self.textbox_discount_max], "H", align="center")

        # 重置和确定按钮
        self.button_cancel = Button(
            self, "重置", h=40,
            color="#000", bg_color="#ccc", on_click=self.OnClickReset,
        )
        self.button_ok = Button(
            self, "确定", h=40,
            color="#fff", bg_color="#7ac13f", on_click=self.OnClickOk,
        )
        self.layout_buttons = WrapLayout([self.button_cancel, self.button_ok], "H")

        self.layout_main = WrapLayout(
            [self.group_price, self.group_oprice, self.group_discount, self.layout_buttons], "V")
        self.setLayout(self.layout_main)

        self.show()
        
    def ParseFloat(self, text: str, default_value = None) -> float:
        try:
            return float(text)
        except:
            return default_value
        
    def OnClickReset(self):
        self.textbox_price_min.setText("")
        self.textbox_price_max.setText("")
        self.textbox_oprice_min.setText("")
        self.textbox_oprice_max.setText("")
        self.textbox_discount_min.setText("")
        self.textbox_discount_max.setText("")

    def OnClickOk(self):
        min_price = self.ParseFloat(self.textbox_price_min.text())
        max_price = self.ParseFloat(self.textbox_price_max.text())
        min_oprice = self.ParseFloat(self.textbox_oprice_min.text())
        max_oprice = self.ParseFloat(self.textbox_oprice_max.text())
        min_discount = self.ParseFloat(self.textbox_discount_min.text())
        max_discount = self.ParseFloat(self.textbox_discount_max.text())
        self.price_filter = PriceFilter(min_price, max_price, min_oprice, max_oprice, min_discount, max_discount)
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    filter = PriceFilter(100, None, 150, 300, None, 0.6)

    ex = FilterWindow(filter)
    return_val = app.exec_()

    print(
        ex.price_filter.min_price,
        ex.price_filter.max_price,
        ex.price_filter.min_oprice,
        ex.price_filter.max_oprice,
        ex.price_filter.min_discount,
        ex.price_filter.max_discount
    )

    sys.exit(return_val)