import sys
import json
from PyQt5.QtWidgets import QApplication, QDialog

from EasyPyQt import *


class CookieEditWindow(QDialog):
    def __init__(self, left = 100, top = 100):
        super().__init__()
        self.title = "编辑 Cookie"
        self.left = left
        self.top = top
        self.width = 600
        self.height = 600
        self.InitUI()

        # 读取 cookie.txt 文件
        try:
            with open("cookie.txt", "r", encoding="utf-8") as f:
                self.textbox_cookie.setPlainText(f.read())
        except:
            pass

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 多行文本框
        self.textbox_cookie = MultiLinePlainTextbox(self, placeholder="在此输入 Cookie")

        # 取消和确定按钮
        self.button_cancel = Button(
            self, "取消", h=40,
            color="#fff", bg_color="#fc5531", on_click=self.OnClickCancel,
        )
        self.button_ok = Button(
            self, "确定", h=40,
            color="#fff", bg_color="#7ac13f", on_click=self.OnClickOk,
        )
        self.layout_buttons = WrapLayout([self.button_cancel, self.button_ok], "H")

        # 整体布局
        self.layout = WrapLayout([self.textbox_cookie, self.layout_buttons], "V")
        self.setLayout(self.layout)

        self.show()

    def OnClickCancel(self):
        self.close()

    def OnClickOk(self):
        cookie = self.textbox_cookie.toPlainText()
        with open("cookie.txt", "w", encoding="utf-8") as f:
            f.write(cookie)
        self.close()


class MySQLConfigEditWindow(QDialog):
    def __init__(self, left = 100, top = 100):
        super().__init__()
        self.title = "编辑 MySQL 配置"
        self.left = left
        self.top = top
        self.width = 400
        self.height = 400
        self.InitConfig()
        self.InitUI()

    def InitConfig(self):
        # 读取 config.json 文件
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f).get("config", {})
        except:
            self.config = {}

        mysql_config = self.config.get("mysql", {})
        self.host = mysql_config.get("host")
        self.port = mysql_config.get("port")
        self.user = mysql_config.get("user")
        self.passwd = mysql_config.get("passwd")
        self.db = mysql_config.get("db")
        self.charset = mysql_config.get("charset")

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # host
        self.label_host = Label(self, "主机地址", h=30)
        self.textbox_host = Textbox(self, self.host, "主机地址", h=30, w=300)
        # port
        self.label_port = Label(self, "端口号", h=30)
        self.textbox_port = Textbox(self, self.port, "端口号", h=30, w=300)
        # user
        self.label_user = Label(self, "用户名", h=30)
        self.textbox_user = Textbox(self, self.user, "用户名", h=30, w=300)
        # passwd
        self.label_passwd = Label(self, "密码", h=30)
        self.textbox_passwd = Textbox(self, self.passwd, "密码", h=30, w=300)
        # db
        self.label_db = Label(self, "数据库", h=30)
        self.textbox_db = Textbox(self, self.db, "数据库", h=30, w=300)
        # charset
        self.label_charset = Label(self, "字符编码", h=30)
        self.textbox_charset = Textbox(self, self.charset, "字符编码", h=30, w=300)

        # 标签布局
        self.layout_labels = WrapLayout([
            self.label_host,
            self.label_port,
            self.label_user,
            self.label_passwd,
            self.label_db,
            self.label_charset,
        ], "V")
        # 输入框布局
        self.layout_textbox = WrapLayout([
            self.textbox_host,
            self.textbox_port,
            self.textbox_user,
            self.textbox_passwd,
            self.textbox_db,
            self.textbox_charset,
        ], "V")

        # 全部配置布局
        self.config_layout = WrapLayout([self.layout_labels, self.layout_textbox], "H")

        # 取消和确定按钮
        self.button_cancel = Button(
            self, "取消", h=40,
            color="#fff", bg_color="#fc5531", on_click=self.OnClickCancel,
        )
        self.button_ok = Button(
            self, "确定", h=40,
            color="#fff", bg_color="#7ac13f", on_click=self.OnClickOk,
        )
        self.layout_buttons = WrapLayout([self.button_cancel, self.button_ok], "H")

        # 整体布局
        self.layout = WrapLayout([self.config_layout, self.layout_buttons], "V")
        self.setLayout(self.layout)

        self.show()

    def OnClickCancel(self):
        self.close()

    def OnClickOk(self):
        mysql_config = {
            "host": self.textbox_host.text(),
            "port": self.textbox_port.text(),
            "user": self.textbox_user.text(),
            "passwd": self.textbox_passwd.text(),
            "db": self.textbox_db.text(),
            "charset": self.textbox_charset.text(),
        }
        self.config["mysql"] = mysql_config
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({"config": self.config}, f, ensure_ascii=False, indent=4)
        self.close()


class ClashConfigEditWindow(QDialog):
    def __init__(self, left = 100, top = 100):
        super().__init__()
        self.title = "编辑 Clash 配置"
        self.left = left
        self.top = top
        self.width = 400
        self.height = 300
        self.InitConfig()
        self.InitUI()

    def InitConfig(self):
        # 读取 config.json 文件
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f).get("config", {})
        except:
            self.config = {}

        clash_config = self.config.get("clash", {})
        self.host = clash_config.get("host")
        self.port = clash_config.get("port")
        self.selector = clash_config.get("selector")
        self.secret = clash_config.get("secret")

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # host
        self.label_host = Label(self, "主机地址", h=30)
        self.textbox_host = Textbox(self, self.host, "主机地址", h=30, w=300)
        # port
        self.label_port = Label(self, "端口号", h=30)
        self.textbox_port = Textbox(self, self.port, "端口号", h=30, w=300)
        # selector
        self.label_selector = Label(self, "Selector", h=30)
        self.textbox_selector = Textbox(self, self.selector, "Selector", h=30, w=300)
        # secret
        self.label_secret = Label(self, "密钥", h=30)
        self.textbox_secret = Textbox(self, self.secret, "密钥（一般默认为空）", h=30, w=300)

        # 标签布局
        self.layout_labels = WrapLayout([
            self.label_host,
            self.label_port,
            self.label_selector,
            self.label_secret,
        ], "V")
        # 输入框布局
        self.layout_textbox = WrapLayout([
            self.textbox_host,
            self.textbox_port,
            self.textbox_selector,
            self.textbox_secret,
        ], "V")

        # 全部配置布局
        self.config_layout = WrapLayout([self.layout_labels, self.layout_textbox], "H")

        # 取消和确定按钮
        self.button_cancel = Button(
            self, "取消", h=40,
            color="#fff", bg_color="#fc5531", on_click=self.OnClickCancel,
        )
        self.button_ok = Button(
            self, "确定", h=40,
            color="#fff", bg_color="#7ac13f", on_click=self.OnClickOk,
        )
        self.layout_buttons = WrapLayout([self.button_cancel, self.button_ok], "H")

        # 整体布局
        self.layout = WrapLayout([self.config_layout, self.layout_buttons], "V")
        self.setLayout(self.layout)

        self.show()

    def OnClickCancel(self):
        self.close()

    def OnClickOk(self):
        clash_config = {
            "host": self.textbox_host.text(),
            "port": self.textbox_port.text(),
            "selector": self.textbox_selector.text(),
            "secret": self.textbox_secret.text(),
        }
        self.config["clash"] = clash_config
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump({"config": self.config}, f, ensure_ascii=False, indent=4)
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ClashConfigEditWindow()
    return_val = app.exec_()
    sys.exit(return_val)
