import sys
from threading import Thread
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QComboBox, QGroupBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from EasyPyQt import *

from item import Item
from access import access, get_cookie
from Bmarket import Bmarket
from mysql_database import DB as MySQLDB
from sqlite_database import DB as SQLiteDB
from clash_proxy import proxy as ClashProxy

example_content = [
    ["FuRyu 初音未来 恋爱水手服灰色Ver. 景品手办" , "71.00" , "115.00" , "0.62" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41541953150&from=market_index"],
    ["TAITO AFG 初音未来 景品手办 再版" , "75.00" , "112.00" , "0.67" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41546391856&from=market_index"],
    ["世嘉 阿尼亚·福杰 夏日度假 景品手办" , "85.00" , "109.00" , "0.78" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41547663345&from=market_index"],
    ["寿屋 赛马娘 Pretty Derby 北部玄驹 手办" , "800.00","1022.00" , "0.78" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41548372436&from=market_index"],
    ["AniMester大漫匠 芙洛伦 手办" , "240.00" , "299.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41548950188&from=market_index"],
    ["GSAS 大道寺知世 手办" , "180.00" , "245.00" , "0.73" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41549071758&from=market_index"],
    ["世嘉 樱岛麻衣 夏裙Ver. 景品手办" , "80.00" , "109.00" , "0.73" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41549172105&from=market_index"],
    ["FuRyu 初音未来 新东京和服 手办 等4个商品" , "460.00" , "605.00" , "0.76" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41549311029&from=market_index"],
    ["ACTOYS 涂山红红 盛夏绽放 泳装Ver. 手办" , "269.00" , "580.00" , "0.46" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41549386607&from=market_index"],
    ["FuRyu 初音未来 热带果汁 景品手办" , "78.00" , "129.00" , "0.60" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41549509507&from=market_index"],
    ["TAITO 惠惠 水着ver. 景品手办" , "89.99" , "112.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41549777866&from=market_index"],
    ["TAITO 雷姆 护士女仆Renewal  景品手办 等7个商品" , "520.00" , "784.00" , "0.66" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41550109404&from=market_index"],
    ["角川 熊熊勇闯异世界 优奈 手办" , "600.00" , "1157.00" , "0.52" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41550366113&from=market_index"],
    ["TAITO 后藤独 私服ver. 景品手办" , "89.99" , "112.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41550765359&from=market_index"],
    ["世嘉 樱岛麻衣 CASUAL CLOTHES 景品手办" , "65.00" , "109.00" , "0.60" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41551552417&from=market_index"],
    ["Plum 哈曼 改 手办 再版" , "666.00" , "764.00" , "0.87" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41551820483&from=market_index"],
    ["世嘉 中野二乃 景品手办" , "66.10" , "109.00" , "0.61" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41551925334&from=market_index"],
    ["FuRyu 初音未来 恋爱水手服灰色Ver. 景品手办" , "75.00" , "115.00" , "0.65" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41552525074&from=market_index"],
    ["GSC 初音未来 交响乐2022Ver. 手办" , "1300.00","1499.00" , "0.87" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41552576024&from=market_index"],
    ["TAITO 喜多郁代 私服ver. 景品手办 等2个商品" , "180.00" , "224.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41552587931&from=market_index"],
    ["世嘉 江户川柯南 椅子Ver. 景品手办 再版" , "80.00" , "105.00" , "0.76" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41553105123&from=market_index"],
    ["世嘉 加藤惠 居家睡衣 景品手办" , "69.00" , "109.00" , "0.63" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41553338175&from=market_index"],
    ["AniMester大漫匠 芙洛伦 手办" , "240.00" , "299.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41553398319&from=market_index"],
    ["Max Factory 喜多川海梦 手办" , "629.99" , "775.00" , "0.81" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41553413381&from=market_index"],
    ["世嘉 埃列什基伽勒 景品手办" , "75.00" , "115.00" , "0.65" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41553442680&from=market_index"],
    ["ACTOYS 涂山红红 盛夏绽放 泳装Ver. 手办" , "260.00" , "580.00" , "0.45" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41554017793&from=market_index"],
    ["AniMester大漫匠 明日香 手办" , "720.00" , "980.00" , "0.73" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41554042013&from=market_index"],
    ["FuRyu 后藤独 景品手办" , "72.00" , "119.00" , "0.61" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41554263428&from=market_index"],
    ["世嘉 中野二乃 景品手办" , "55.00" , "109.00" , "0.50" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41554478342&from=market_index"],
    ["FuRyu 雅儿贝德 泳装  景品手办" , "75.00" , "115.00" , "0.65" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41554498294&from=market_index"],
    ["世嘉 莱莎琳·斯托特 景品手办 等2个商品" , "140.00" , "218.00" , "0.64" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41555789558&from=market_index"],
    ["TAITO 喜多郁代 私服ver. 景品手办" , "89.99" , "112.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41556032209&from=market_index"],
    ["TAITO 星野露比 制服ver. 景品手办 等2个商品" , "180.00" , "224.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41556144925&from=market_index"],
    ["F:NEX VOCALOID 初音未来 科技魔法ver. 手办","1250.00","1499.00" , "0.83" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41556299820&from=market_index"],
    ["TAITO 有马加奈 B小町ver. 景品手办" , "89.99" , "112.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557028235&from=market_index"],
    ["FuRyu 雅儿贝德 泳装  景品手办" , "75.00" , "115.00" , "0.65" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557041271&from=market_index"],
    ["FuRyu 芙莉莲 景品手办 再版" , "75.00" , "115.00" , "0.65" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557048011&from=market_index"],
    ["FuRyu 初音未来 紫罗兰 景品手办" , "90.00" , "129.00" , "0.70" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557061310&from=market_index"],
    ["Plum 香草 Q版手办" , "130.00" , "142.00" , "0.92" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557185812&from=market_index"],
    ["Ensoutoys 兔女郎丽奈 正比手办" , "560.00" , "699.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557356378&from=market_index"],
    ["寿屋 美少女雕像系列 拳皇2001 安琪尔 手办" , "638.00" , "796.00" , "0.80" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557362294&from=market_index"],
    ["GSC 月 Q版手办" , "369.00" , "369.00" , "1.00" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41557762663&from=market_index"],
    ["TAITO 白 Renewal ver.  景品手办" , "70.00" , "112.00" , "0.63" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41558450507&from=market_index"],
    ["TAITO 白 Renewal ver.  景品手办" , "69.00" , "112.00" , "0.62" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41558748485&from=market_index"],
    ["FuRyu 雷姆 花仙子 景品手办" , "79.00" , "115.00" , "0.69" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41558813353&from=market_index"],
    ["FuRyu 雅儿贝德 泳装  景品手办" , "80.00" , "115.00" , "0.70" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41558935623&from=market_index"],
    ["FuRyu 后藤独 景品手办" , "72.00" , "119.00" , "0.61" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41559140681&from=market_index"],
    ["Union Creative 出包王女 露恩·艾尔西·裘利亚 Darkness Ver. 手办" , "719.00" , "799.00" , "0.90" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41559499372&from=market_index"],
    ["世嘉 初音未来 star voice 景品手办" , "65.00" , "109.00" , "0.60" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41559857725&from=market_index"],
    ["Alphamax 约会大作战 时崎狂三 睡衣ver. 手办 再版" , "688.00" , "735.00" , "0.94" , "https://mall.bilibili.com/neul-next/index.html?page=magic-market_detail&noTitleBar=1&itemsId=41560007859&from=market_index"],
]

class RunThread(QThread):
    # 定义一个信号，用于在子线程中发出，主线程中接收
    signal = pyqtSignal(object)

    def __init__(self, item_type, sort, use_clash=False):
        super().__init__()
        self.item_type = item_type # 商品类型
        self.sort = sort # 排序方式
        self.use_clash = use_clash # 是否使用Clash代理
        
        self.bmarket = Bmarket(self.item_type, self.sort) # 连接市集
        self.running = True

    def run(self):
        try:
            self.clash = ClashProxy() if self.use_clash else None
        except Exception as e:
            self.running = False
            self.signal.emit(str(e)) # 发送错误信息
            return

        while self.running:
            fetched = self.bmarket.Fetch()
            if fetched == "no more":
                self.interrupt(fetched)
            elif fetched == "invalid cookie":
                self.interrupt(fetched)
            elif fetched == "reconnect failed":
                if self.use_clash:
                    print("自动重连失败，尝试切换代理...")
                    msg = self.clash.change_proxy() # 更换代理
                    if msg == "ok":
                        print(f"切换到代理 '{self.clash.now_proxy}'")
                        continue
                    else: self.interrupt(msg)
                else:
                    self.interrupt(fetched)
            else: # have fetched items successfully
                self.signal.emit(fetched)

    def interrupt(self, data):
        self.running = False
        self.signal.emit(data)

    def start(self):
        """
        开始爬取
        """
        self.running = True
        super().start()

    def pause(self):
        """
        发送暂停信号，但不等待线程结束
        """
        self.running = False
            
    def quit(self):
        """
        发送停止信号，然后等待线程结束
        """
        self.running = False # 发送停止信号
        self.wait() # 等待线程结束
            

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Bmarket"
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.status = "stop"
        self.InitUI()
        self.InitSetup()

    def InitSetup(self):
        self.item_type = self.box_item_type.currentText() # 商品类型 "全部"
        self.sort = self.box_sort.currentText() # 排序方式 "时间降序（推荐）"
        self.insert_method = self.box_insert_method.currentText() # 插入数据库方式 "合并"
        self.use_mysql = False
        self.use_sqlite = False
        self.use_clash = False
        self.show_item = True
        self.run_thread = None
        self.dbs = []
    
    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # 控制区
        self.InitControlGroup()

        # 隐藏控制区按钮
        self.button_hide_ctrl = Button(
            self,
            w=20, h=80,
            color="#888",
            text=">", tip="隐藏控制区",
            on_click=self.OnClickHideCtrl,
        )

        # 表格区
        self.table = Table(self, header=["商品", "市集价", "原价", "市集折扣", "链接"], content=example_content)
        self.checkbox_show_item = CheckBox(self, "实时显示商品", on_change=self.OnChangeShowItem)
        self.checkbox_show_item.setChecked(True)
        self.layout_table = WrapLayout([self.table, self.checkbox_show_item])

        # 整体布局
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.layout_table)
        self.layout.addWidget(self.button_hide_ctrl)
        self.layout.addWidget(self.group_ctrl)
        self.setLayout(self.layout)

        self.show()

    def InitControlGroup(self):
        # 选择商品类型
        self.box_item_type = ComboBox(self, ["全部", "手办", "模型", "3C", "福袋"])
        self.box_item_type.currentIndexChanged.connect(self.OnChangeItemType)
        self.group_item_type = WrapGroup(self, "商品类型", [self.box_item_type], "V")

        # 选择排序方式
        self.box_sort = ComboBox(self, ["时间降序（推荐）", "价格升序", "价格降序"])
        self.box_sort.currentIndexChanged.connect(self.OnChangeSort)
        self.group_sort = WrapGroup(self, "排序方式", [self.box_sort], "V")

        # 选择插入数据库方式
        self.box_insert_method = ComboBox(self, ["合并", "新增"])
        self.box_insert_method.currentIndexChanged.connect(self.OnChangeInsertMethod)
        self.box_insert_method.setEnabled(False)
        self.group_insert_method = WrapGroup(self, "插入数据库方式", [self.box_insert_method], "V")

        # cookie设置
        self.button_edit_cookie = Button(self, "编辑Cookie", h=40, on_click=self.OnClickEditCookie)
        self.group_edit_cookie = WrapGroup(self, "Cookie", [self.button_edit_cookie])
        
        # 选择使用的数据库
        # self.group_dbs_used, self.box_dbs_used = self.WrapCheckBoxs(self, "使用数据库", ["MySQL", "SQLite"])
        self.box_use_mysql = CheckBox(self, "MySQL", on_change=self.OnChangeUseMySQL)
        self.box_use_sqlite = CheckBox(self, "SQLite", on_change=self.OnChangeUseSQLite)
        self.group_dbs_used = WrapGroup(self, "使用数据库", [self.box_use_mysql, self.box_use_sqlite])
        
        # MySQL配置和测试按钮
        self.button_setup_mysql =Button(self, "配置MySQL", h=40, on_click=self.OnClickSetupMySQL)
        self.button_test_mysql = Button(self, "测试MySQL连接", h=40, on_click=self.OnClickTestMySQL)
        self.group_mysql = WrapGroup(self, "MySQL", [self.button_setup_mysql, self.button_test_mysql], "H")

        # Clash配置和测试按钮
        self.checkbox_use_clash = CheckBox(self, "风控时自动使用Clash切换代理", on_change=self.OnChangeUseClash)
        self.button_setup_clash = Button(self, "配置Clash", h=40, on_click=self.OnClickSetupClash)
        self.button_test_clash = Button(self, "测试Clash连接", h=40, on_click=self.OnClickTestClash)
        self.layout_setup_and_test_clash = WrapLayout([self.button_setup_clash, self.button_test_clash], "H")
        self.group_clash = WrapGroup(self, "Clash", [self.checkbox_use_clash, self.layout_setup_and_test_clash])

        # 开始、暂停、停止、继续按钮
        self.button_start = Button(self, "开始", h=60, font_style="黑体", font_size=20, color="#fff", bg_color="#7ac13f", on_click=self.OnClickStart)
        self.button_pause = Button(self, "运行中...", h=60, font_style="黑体", font_size=20, color="#fff", bg_color="#fd944d", on_click=self.OnClickPause)
        self.button_finish = Button(self, "结束", h=60, font_style="黑体", font_size=20, color="#fff", bg_color="#fc5531", on_click=self.OnClickFinish)
        self.button_continue = Button(self, "继续", h=60, font_style="黑体", font_size=20, color="#fff", bg_color="#7ac13f", on_click=self.OnClickContinue)
        self.layout_finish_or_continue = WrapLayout([self.button_finish, self.button_continue], "H")
        self.button_pause.setVisible(False)
        self.button_finish.setVisible(False)
        self.button_continue.setVisible(False)

        # 控制区布局
        self.group_ctrl = WrapGroup(self, "控制区", [
            self.group_item_type,
            self.group_sort,
            self.group_insert_method,
            self.group_edit_cookie,
            self.group_dbs_used,
            self.group_mysql,
            self.group_clash,
            self.button_start,
            self.button_pause,
            self.layout_finish_or_continue,
        ])

    ############################################################################################
    ####                                  以下是一些功能函数                                 ####
    ############################################################################################
    def HandleSignal(self, data):
        """
        在主线程中定义一个槽函数，用于处理信号
        """
        if data == "no more":
            print("没有更多商品了")

            # 如果插入数据库方式为“合并”，则删除无效数据并将临时表数据合并到主表
            if self.insert_method == "合并":
                for db in self.dbs:
                    db.remove_invalid()
                    db.flush_new()
            self.Finish() # 结束当前爬取任务
            QMessageBox.information(self, " ", "没有更多商品了", QMessageBox.Ok)
        elif data == "invalid cookie":
            print("Cookie 无效，请更新 Cookie")
            self.Finish() # 结束当前爬取任务
            QMessageBox.warning(self, " ", "Cookie 无效，请更新 Cookie", QMessageBox.Ok)
        elif data == "reconnect failed":
            print("自动重连失败，请选择接下来的操作...")
            
            # 选择接下来的操作
            # 如果使用数据库，则增加两个选项：新增记录、合并记录
            choices = ["再次重连", "直接结束"]
            tips = [
                "再次尝试连接市集，程序会继续运行，本次爬取已经获取到的记录不会丢失",
                "直接结束本次爬取，本次爬取已经获取到的记录将被丢弃，数据库不会被更新",
            ]
            if self.use_mysql or self.use_sqlite:
                choices.extend(["新增记录", "合并记录"])
                tips.extend([
                    "将本次爬取已经获取到的记录新增到数据库中，但不会删除无效数据，然后结束本次爬取",
                    "将本次爬取已经获取到的记录合并到数据库中，会删除无效数据，但可能丢失数据库中已有记录，然后结束本次爬取",
                ])

            # 弹出消息框，让用户选择接下来的操作
            operate = GetChoiceFromMessageBox(" ", "自动重连失败，请选择接下来的操作", choices, tips)
            match operate:
                case "再次重连":
                    self.run_thread.wait() # 等待Run线程结束
                    self.Continue() # 重新开始Run线程
                case "直接结束":
                    self.Finish() # 结束当前爬取任务
                case "新增记录":
                    for db in self.dbs: db.flush_new()
                    self.Finish() # 结束当前爬取任务
                case "合并记录":
                    for db in self.dbs:
                        db.remove_invalid()
                        db.flush_new()
                    self.Finish() # 结束当前爬取任务
        elif isinstance(data, str): # 其他情况下，暂停爬取并弹出消息框
            print(data)
            self.Pause() # 暂停当前爬取任务
            QMessageBox.warning(self, " ", data, QMessageBox.Ok)
        else: # data: list[item]
            match self.insert_method:
                case "合并":
                    for item in data:
                        if self.show_item: self.AddItemToTable(item)
                        for db in self.dbs: db.note(item) # 存入临时表
                case "新增":
                    for item in data:
                        if self.show_item: self.AddItemToTable(item)
                        for db in self.dbs: db.store(item) # 存入主表

    def AddItemToTable(self, item: Item):
        record = [item.name, str(item.price), str(item.origin_price), f"{'%.2f'%item.discount}", item.process_url()]
        self.table.insertRow(self.table.rowCount())
        for i in range(len(record)):
            self.table.setItem(self.table.rowCount() - 1, i, QTableWidgetItem(record[i]))
        # 表格滚动条自动滚动到底部
        self.table.scrollToBottom()

    def TestCookieExist(self):
        try:
            get_cookie()
            return True
        except Exception as e:
            QMessageBox.warning(self, " ", str(e), QMessageBox.Ok)

    def Quit(self):
        """
        退出程序时调用，终止 Run 线程，断开数据库连接
        """
        if self.run_thread: self.run_thread.quit()
        for db in self.dbs: db.disconnect()

    ############################################################################################
    ####                                以下是四个状态跳转函数                                ####
    ############################################################################################
    def Start(self):
        try:
            # 使用的数据库
            self.dbs = []
            if self.use_mysql: self.dbs.append(MySQLDB(self.item_type))
            if self.use_sqlite: self.dbs.append(SQLiteDB(self.item_type))
            # 在主线程中创建RunThread对象，并连接信号和槽
            self.run_thread = RunThread(self.item_type, self.sort, self.use_clash)
            self.run_thread.signal.connect(self.HandleSignal)
        except Exception as e:
            QMessageBox.warning(self, " ", str(e), QMessageBox.Ok)
            return

        # 显示暂停按钮，隐藏其他按钮
        self.button_start.setVisible(False)
        self.button_finish.setVisible(False)
        self.button_continue.setVisible(False)
        self.button_pause.setVisible(True)
        # 设置控制区所有控件不可用
        self.box_item_type.setEnabled(False)
        self.box_sort.setEnabled(False)
        self.box_insert_method.setEnabled(False)
        self.button_edit_cookie.setEnabled(False)
        self.box_use_mysql.setEnabled(False)
        self.box_use_sqlite.setEnabled(False)
        self.button_setup_mysql.setEnabled(False)
        self.button_test_mysql.setEnabled(False)
        self.checkbox_use_clash.setEnabled(False)
        self.button_setup_clash.setEnabled(False)
        self.button_test_clash.setEnabled(False)

        # 清空表格
        self.table.setRowCount(0)

        # 启动子线程
        self.run_thread.start()
        self.status = "running"
        # self.statusBar().showMessage("开始爬取")

    def Pause(self):
        # 发送暂停信号
        self.run_thread.pause()
        # 显示结束和继续按钮，隐藏其他按钮
        self.button_start.setVisible(False)
        self.button_pause.setVisible(False)
        self.button_finish.setVisible(True)
        self.button_continue.setVisible(True)
        # 设置控制区Clash相关控件可用
        self.checkbox_use_clash.setEnabled(True)
        self.button_setup_clash.setEnabled(True)
        self.button_test_clash.setEnabled(True)

        self.status = "pause"
        # self.statusBar().showMessage("爬取暂停")

    def Finish(self):
        # 发送暂停信号
        self.run_thread.pause()
        # 显示开始按钮，隐藏其他按钮
        self.button_pause.setVisible(False)
        self.button_finish.setVisible(False)
        self.button_continue.setVisible(False)
        self.button_start.setVisible(True)
        # 设置控制区所有控件可用
        self.box_item_type.setEnabled(True)
        self.box_sort.setEnabled(True)
        self.box_insert_method.setEnabled(True)
        self.button_edit_cookie.setEnabled(True)
        self.box_use_mysql.setEnabled(True)
        self.box_use_sqlite.setEnabled(True)
        self.button_setup_mysql.setEnabled(True)
        self.button_test_mysql.setEnabled(True)
        self.checkbox_use_clash.setEnabled(True)
        self.button_setup_clash.setEnabled(True)
        self.button_test_clash.setEnabled(True)
        
        for db in self.dbs: db.disconnect() # 断开数据库连接
        self.status = "stop"
        # self.statusBar().showMessage("爬取结束")

    def Continue(self):
        # 显示暂停按钮，隐藏其他按钮
        self.button_start.setVisible(False)
        self.button_finish.setVisible(False)
        self.button_continue.setVisible(False)
        self.button_pause.setVisible(True)
        # 设置控制区Clash相关控件不可用
        self.checkbox_use_clash.setEnabled(False)
        self.button_setup_clash.setEnabled(False)
        self.button_test_clash.setEnabled(False)

        self.run_thread.start()
        self.status = "running"
        # self.statusBar().showMessage("继续爬取")

    ############################################################################################
    ####                                以下是各种事件处理函数                                ####
    ############################################################################################
    def OnClickHideCtrl(self):
        self.group_ctrl.setVisible(not self.group_ctrl.isVisible())
        self.button_hide_ctrl.setText(">" if self.group_ctrl.isVisible() else "<")
        self.button_hide_ctrl.setToolTip("隐藏控制区" if self.group_ctrl.isVisible() else "显示控制区")

    def OnChangeItemType(self):
        self.item_type = self.box_item_type.currentText()
        print(f"item type select '{self.box_item_type.currentText()}'")

    def OnChangeSort(self):
        self.sort = self.box_sort.currentText()
        print(f"sort select '{self.box_sort.currentText()}'")

    def OnChangeInsertMethod(self):
        self.insert_method = self.box_insert_method.currentText()
        print(f"insert method select '{self.box_insert_method.currentText()}'")

    def OnClickEditCookie(self):
        print("edit cookie")
        # ...

    def OnChangeUseMySQL(self):
        self.use_mysql = self.box_use_mysql.isChecked()
        self.box_insert_method.setEnabled(self.use_mysql or self.use_sqlite)
        print("use mysql" if self.box_use_mysql.isChecked() else "not use mysql")

    def OnChangeUseSQLite(self):
        self.use_sqlite = self.box_use_sqlite.isChecked()
        self.box_insert_method.setEnabled(self.use_mysql or self.use_sqlite)
        print("use sqlite" if self.box_use_sqlite.isChecked() else "not use sqlite")

    def OnChangeUseClash(self):
        self.use_clash = self.checkbox_use_clash.isChecked()
        if self.run_thread:
            self.run_thread.use_clash = self.use_clash
        print("use clash" if self.checkbox_use_clash.isChecked() else "not use clash")
        
    def OnClickSetupMySQL(self):
        print("Setup MySQL")
        # ...

    def OnClickTestMySQL(self):
        print("Test MySQL")
        # ...

    def OnClickSetupClash(self):
        print("Setup Clash")
        # ...

    def OnClickTestClash(self):
        print("Test Clash")
        # ...

    def OnClickStart(self):
        self.Start()

    def OnClickPause(self):
        self.Pause()

    def OnClickFinish(self):
        self.Finish()

    def OnClickContinue(self):
        self.Continue()

    def OnChangeShowItem(self):
        self.show_item = self.checkbox_show_item.isChecked()
        print("show item" if self.checkbox_show_item.isChecked() else "not show item")


    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    return_val = app.exec_()
    ex.Quit()
    sys.exit(return_val)
