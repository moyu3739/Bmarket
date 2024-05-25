import sys
import webbrowser
import PyQt5

from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

from EasyPyQt import *
from EditWindow import *
from Log import *

from item import Item, Filter, NameFilter
from Bmarket import Bmarket
from mysql_database import DB as MySQLDB
from sqlite_database import DB as SQLiteDB
from clash_proxy import proxy as ClashProxy, read_proxy_config


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
            self.emit("status", "正在连接 Clash...")
            self.clash = ClashProxy() if self.use_clash else None
            self.emit("status", "正在爬取")
        except Exception as e:
            self.interrupt("msg", str(e)) # 发送错误信息
            return

        while self.running:
            fetched = self.bmarket.Fetch()
            if fetched == "no more":
                self.interrupt("msg", "no more")
            elif fetched == "invalid cookie":
                self.interrupt("msg", "invalid cookie")
            elif fetched == "reconnect failed":
                if self.use_clash:
                    Print("自动重连失败，正在切换代理...")
                    self.emit("status", "自动重连失败，正在切换代理...")
                    msg = self.clash.change_proxy() # 更换代理
                    if msg == "ok":
                        Print(f"切换到代理 '{self.clash.now_proxy}'")
                        self.emit("status", f"已切换到代理 '{self.clash.now_proxy}'")
                        continue
                    else: self.interrupt("msg", msg)
                else:
                    self.interrupt("msg", "reconnect failed")
            else: # have fetched items successfully
                self.emit("record", fetched)

    def emit(self, type, data):
        self.signal.emit([type, data])

    def interrupt(self, type, data):
        self.running = False
        self.signal.emit([type, data])

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
            

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Bmarket"
        self.left = 100
        self.top = 100
        self.width = 1230
        self.height = 900
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
        self.auto_scroll = True
        self.run_thread = None
        self.dbs = []
        self.status = "stop"
        self.all_items = []
        self.filter = NameFilter("")
    
    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # 图标
        self.setWindowIcon(QIcon("icon.png"))
    
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
        # 搜索框和搜索按钮
        self.textbox_search = Textbox(self, placeholder="搜索商品", h=30, w=300)
        self.textbox_search.setClearButtonEnabled(True)
        self.button_search = Button(self, "🔍", h=30, w=30, on_click=self.OnClickSearch)
        self.layout_search = WrapLayout([self.textbox_search, self.button_search], "H", align="left")
        # 表格选项
        self.checkbox_show_item = CheckBox(self, "实时显示商品", on_change=self.OnChangeShowItem)
        self.checkbox_show_item.setChecked(True)
        self.checkbox_auto_scroll = CheckBox(self, "自动滚动到底部", on_change=self.OnChangeAutoScroll)
        self.checkbox_auto_scroll.setChecked(True)
        self.layout_table_options = WrapLayout([self.checkbox_show_item, self.checkbox_auto_scroll], "H", align="left")
        """
        这里设计了两个表格分别用于显示完整数据和搜索结果
        目的：提高搜索框为空时的搜索（即显示全部记录）速度，避免表格的插入操作对所有记录都执行一遍
        方法：获取到记录时，无条件插入 `table` 表格，根据搜索框条件过滤后插入 `table_search` 表格。
            搜索时，如果搜索框为空，将 `table_search` 表格设为隐藏状态，将 `table` 表格设为显示状态即可；
            如果搜索框不为空，根据搜索框条件过滤全部记录 `all_items` 放进 `table_search` 表格，
            并将 `table` 表格设为隐藏状态，将 `table_search` 表格设为显示状态。
        """
        # 显示完整数据的表格（在搜索框中有内容时隐藏，为空时显示）
        self.table = Table(
            self, header=["商品", "市集价", "原价", "市集折扣", "链接（双击用浏览器打开）"],
            columns_width=[400, 80, 80, 80, 200],
            edit_enable=False,
        )
        self.table.cellDoubleClicked.connect(self.OnCellDoubleClick)
        # 显示搜索结果的表格（在搜索框中有内容时显示，为空时隐藏）
        self.table_search = Table(
            self, header=["商品", "市集价", "原价", "市集折扣", "链接（双击用浏览器打开）"],
            columns_width=[400, 80, 80, 80, 200],
            edit_enable=False,
        )
        self.table_search.cellDoubleClicked.connect(self.OnCellDoubleClickSearch)
        self.table_search.setVisible(False)
        # 表格区布局
        self.layout_table = WrapLayout([self.layout_search, self.table, self.table_search, self.layout_table_options])

        # 整体布局
        self.layout = WrapLayout([self.layout_table, self.button_hide_ctrl, self.group_ctrl], "H")

        # 状态栏
        self.status_bar = QStatusBar(self)
        self.status_bar.setStyleSheet("background-color: #ccc;")
        self.SetStatus("准备就绪")

        # 窗体布局
        self.layout_main = WrapLayout([self.layout, self.status_bar], "V")
        self.setLayout(self.layout_main)

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
        self.button_test_cookie = Button(self, "测试Cookie", h=40, on_click=self.OnClickTestCookie)
        self.group_edit_cookie = WrapGroup(self, "Cookie", [self.button_edit_cookie, self.button_test_cookie], "H")
        
        # 选择使用的数据库
        self.box_use_mysql = CheckBox(self, "MySQL", on_change=self.OnChangeUseMySQL)
        self.box_use_sqlite = CheckBox(self, "SQLite", on_change=self.OnChangeUseSQLite)
        self.group_dbs_used = WrapGroup(self, "将记录插入数据库", [self.box_use_mysql, self.box_use_sqlite])
        
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
    def HandleSignal(self, signal):
        """
        在主线程中定义一个槽函数，用于处理信号
        """
        if self.block_signal: return
        [type, data] = signal

        if type == "msg":
            match data:
                case "no more":
                    Print("没有更多商品了")

                    # 如果插入数据库方式为“合并”，则删除无效数据并将临时表数据合并到主表
                    if self.insert_method == "合并": self.MergeDB()
                    self.Finish() # 结束当前爬取任务
                    QMessageBox.information(self, " ", "没有更多商品了", QMessageBox.Ok)
                case "invalid cookie":
                    Print("Cookie 无效，请更新 Cookie")
                    self.Finish() # 结束当前爬取任务
                    QMessageBox.critical(self, " ", "Cookie 无效，请更新 Cookie", QMessageBox.Ok)
                case "reconnect failed":
                    Print("自动重连失败，请选择接下来的操作...")

                    choices_simple = ["再次重连", "直接结束"]
                    tips_simple = [
                        "再次尝试连接市集，程序会继续运行，本次爬取已经获取到的记录不会丢失",
                        "本次爬取已经获取到的记录将被丢弃，数据库不会被更新",
                    ]
                    choices_complex = ["再次重连", "直接结束", "新增记录", "合并记录"]
                    tips_complex = [
                        "再次尝试连接市集，程序会继续运行，本次爬取已经获取到的记录不会丢失",
                        "本次爬取已经获取到的记录将被丢弃，数据库不会被更新",
                        "将本次爬取已经获取到的记录新增到数据库中，但不会删除无效数据，然后结束本次爬取",
                        "将本次爬取已经获取到的记录合并到数据库中，会删除无效数据，但可能丢失数据库中已有的有效记录，然后结束本次爬取",
                    ]
                    
                    # 选择接下来的操作
                    # 如果使用数据库且插入数据库方式为“合并”，则增加两个选项：新增记录、合并记录
                    if self.insert_method == "合并" and (self.use_mysql or self.use_sqlite):
                        choices = choices_complex
                        tips = tips_complex
                    else:
                        choices = choices_simple
                        tips = tips_simple

                    # 弹出消息框，让用户选择接下来的操作
                    operate = GetChoiceFromMessageBox(" ", "自动重连失败，请选择接下来的操作", choices, tips)
                    match operate:
                        case "再次重连":
                            self.run_thread.wait() # 等待Run线程结束
                            self.Continue() # 重新开始Run线程
                        case "直接结束":
                            self.Finish() # 结束当前爬取任务
                        case "新增记录":
                            self.UpdateDB()
                            self.Finish() # 结束当前爬取任务
                        case "合并记录":
                            self.MergeDB()
                            self.Finish() # 结束当前爬取任务
                case _: # 其他消息，暂停爬取并弹出消息框
                    Print(data)
                    self.Pause() # 暂停当前爬取任务
                    QMessageBox.critical(self, " ", data, QMessageBox.Ok)

        elif type == "status":
            self.SetStatus(data)
            if data.startswith("已切换到代理"): # 若状态信息为切换到新代理，则3秒后将状态设为“准备就绪”
                def SetStatusReady():
                    if self.status == "running": self.SetStatus("正在爬取")
                QTimer.singleShot(3000, SetStatusReady) # 定时3秒之后将状态设为“准备就绪”
                    
        elif type == "record": # data: list[item]
            self.all_items.extend(data)
            match self.insert_method:
                case "合并":
                    for item in data:
                        if self.show_item: self.AddItemToTwoTable(item)
                        for db in self.dbs: db.note(item) # 存入临时表
                case "新增":
                    for item in data:
                        if self.show_item: self.AddItemToTwoTable(item)
                        for db in self.dbs.copy():
                            success = db.store(item, error_echo=False) # 存入主表
                            if not success: # 如果记录已经在当前数据库中存在
                                self.dbs.remove(db) # 把当前数据库从数据库列表中删除，即之后新记录不会再存入当前数据库
                    if len(self.dbs) == 0: # 如果所有数据库都已经存在相同记录，则结束当前爬取任务
                        self.Finish()
                        self.block_signal = True
                        QMessageBox.information(self, " ", "没有更多新商品了", QMessageBox.Ok)
                        
    def MergeDB(self):
        """
        合并临时表记录到主表中
        """
        for db in self.dbs:
            db.remove_invalid()
            db.flush_new()

    def UpdateDB(self):
        """
        将临时表记录新增到主表中（不删除无效数据）
        """
        for db in self.dbs: db.flush_new()

    def FilterItem(self, item: Item):
        return self.filter.filtrate(item)
    
    def FilterWholeTableSearch(self):
        self.table_search.setRowCount(0)
        for item in self.all_items:
            self.AddItemToTableSearch(item)

    def AddItemToTwoTable(self, item: Item):
        self.AddItemToTable(item)
        self.AddItemToTableSearch(item)

    def AddItemToTable(self, item: Item):
        record = [item.name, str(item.price), str(item.origin_price), f"{'%.2f'%item.discount}", item.process_url()]
        self.table.insertRow(self.table.rowCount())
        for i in range(len(record)):
            self.table.setItem(self.table.rowCount() - 1, i, QTableWidgetItem(record[i]))
        # 表格滚动条自动滚动到底部
        if self.auto_scroll: self.table.scrollToBottom()

    def AddItemToTableSearch(self, item: Item):
        if not self.FilterItem(item): return # 如果不符合过滤条件，则不显示
        record = [item.name, str(item.price), str(item.origin_price), f"{'%.2f'%item.discount}", item.process_url()]
        self.table_search.insertRow(self.table_search.rowCount())
        for i in range(len(record)):
            self.table_search.setItem(self.table_search.rowCount() - 1, i, QTableWidgetItem(record[i]))
        # 表格滚动条自动滚动到底部
        if self.auto_scroll: self.table_search.scrollToBottom()

    def SetStatus(self, status: str):
        self.status_bar.showMessage("当前状态：" + status)

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
            # 检查Clash配置是否正确
            if self.use_clash: read_proxy_config()
        except Exception as e:
            QMessageBox.critical(self, " ", str(e), QMessageBox.Ok)
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
        self.button_test_cookie.setEnabled(False)
        self.box_use_mysql.setEnabled(False)
        self.box_use_sqlite.setEnabled(False)
        self.button_setup_mysql.setEnabled(False)
        self.button_test_mysql.setEnabled(False)
        self.checkbox_use_clash.setEnabled(False)
        self.button_setup_clash.setEnabled(False)
        self.button_test_clash.setEnabled(False)

        # 清空表格
        self.table.setRowCount(0)
        self.table_search.setRowCount(0)
        self.all_items = []

        # 启动子线程
        self.block_signal = False
        self.status = "running"
        self.run_thread.start()
        self.SetStatus("正在爬取")

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
        self.SetStatus("已暂停")

    def FinishUserOperate(self):
        """
        结束当前爬取任务后，根据用户选择的操作进行相应的操作
        `return`: 是否结束当前爬取任务
        """
        choices_simple = ["直接结束", "取消"]
        tips_simple = ["本次爬取已经获取到的记录将被丢弃，数据库不会被更新"]
        choices_complex = ["直接结束", "新增记录", "合并记录", "取消"]
        tips_complex = [
            "本次爬取已经获取到的记录将被丢弃，数据库不会被更新",
            "将本次爬取已经获取到的记录新增到数据库中，但不会删除无效数据",
            "将本次爬取已经获取到的记录合并到数据库中，会删除无效数据，但可能丢失数据库中已有的有效记录",
        ]

        # 选择接下来的操作
        choices = []
        tips = []
        # 如果使用数据库且插入数据库方式为“合并”，则增加两个选项：新增记录、合并记录
        if self.insert_method == "合并" and (self.use_mysql or self.use_sqlite):
            choices = choices_complex
            tips = tips_complex
        else:
            choices = choices_simple
            tips = tips_simple

        # 弹出消息框，让用户选择接下来的操作
        operate = GetChoiceFromMessageBox(" ", "你结束了当前爬取任务，请选择接下来的操作", choices, tips)
        match operate:
            case "新增记录":
                self.UpdateDB()
                self.Finish() # 结束当前爬取任务
                return True
            case "合并记录":
                self.MergeDB()
                self.Finish() # 结束当前爬取任务
                return True
            case "直接结束":
                self.Finish() # 结束当前爬取任务
                return True
            case "取消":
                return False

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
        self.button_test_cookie.setEnabled(True)
        self.box_use_mysql.setEnabled(True)
        self.box_use_sqlite.setEnabled(True)
        self.button_setup_mysql.setEnabled(True)
        self.button_test_mysql.setEnabled(True)
        self.checkbox_use_clash.setEnabled(True)
        self.button_setup_clash.setEnabled(True)
        self.button_test_clash.setEnabled(True)
        
        for db in self.dbs: db.disconnect() # 断开数据库连接
        self.status = "stop"
        self.SetStatus("爬取结束")
        def SetStatusReady():
            if self.status == "stop": self.SetStatus("准备就绪")
        QTimer.singleShot(3000, SetStatusReady) # 定时3秒之后将状态设为“准备就绪”

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

        self.status = "running"
        self.run_thread.start()
        self.SetStatus("正在爬取")

    ############################################################################################
    ####                                以下是各种事件处理函数                                ####
    ############################################################################################
    def OnCellDoubleClick(self, row, col):
        if self.table.horizontalHeaderItem(col).text() == "链接（双击用浏览器打开）":
            url = self.table.item(row, col).text()
            webbrowser.open(url)

    def OnCellDoubleClickSearch(self, row, col):
        if self.table_search.horizontalHeaderItem(col).text() == "链接（双击用浏览器打开）":
            url = self.table_search.item(row, col).text()
            webbrowser.open(url)

    def OnClickHideCtrl(self):
        self.group_ctrl.setVisible(not self.group_ctrl.isVisible())
        self.button_hide_ctrl.setText(">" if self.group_ctrl.isVisible() else "<")
        self.button_hide_ctrl.setToolTip("隐藏控制区" if self.group_ctrl.isVisible() else "显示控制区")

    def OnChangeItemType(self):
        self.item_type = self.box_item_type.currentText()
        Print(f"item type select '{self.box_item_type.currentText()}'")

    def OnChangeSort(self):
        self.sort = self.box_sort.currentText()
        Print(f"sort select '{self.box_sort.currentText()}'")

    def OnChangeInsertMethod(self):
        self.insert_method = self.box_insert_method.currentText()
        Print(f"insert method select '{self.box_insert_method.currentText()}'")

    def OnClickEditCookie(self):
        Print("edit cookie")
        edit_window = CookieEditWindow()
        edit_window.exec_()

    def OnClickTestCookie(self):
        Print("test cookie")
        try:
            bmarket_test = Bmarket("全部", "时间降序（推荐）") # 其中会尝试打开 cookie.txt 文件，若文件不存在会抛出异常
            res = bmarket_test.Fetch() # 会使用 cookie.txt 文件中的 Cookie 访问市集
            if res == "invalid cookie": raise Exception() # 若返回 "invalid cookie" 则抛出异常
            QMessageBox.information(self, " ", "Cookie 有效，市集连接成功", QMessageBox.Ok)
        except:
            QMessageBox.critical(self, " ", "Cookie 缺失或已失效，请重新配置 Cookie", QMessageBox.Ok)

    def OnChangeUseMySQL(self):
        self.use_mysql = self.box_use_mysql.isChecked()
        self.box_insert_method.setEnabled(self.use_mysql or self.use_sqlite)
        Print("use mysql" if self.box_use_mysql.isChecked() else "not use mysql")

    def OnChangeUseSQLite(self):
        self.use_sqlite = self.box_use_sqlite.isChecked()
        self.box_insert_method.setEnabled(self.use_mysql or self.use_sqlite)
        Print("use sqlite" if self.box_use_sqlite.isChecked() else "not use sqlite")

    def OnChangeUseClash(self):
        self.use_clash = self.checkbox_use_clash.isChecked()
        if self.run_thread:
            self.run_thread.use_clash = self.use_clash
        Print("use clash" if self.checkbox_use_clash.isChecked() else "not use clash")
        
    def OnClickSetupMySQL(self):
        Print("Setup MySQL")
        edit_window = MySQLConfigEditWindow()
        edit_window.exec_()

    def OnClickTestMySQL(self):
        Print("Test MySQL")
        try:
            _ = MySQLDB()
            QMessageBox.information(self, " ", "MySQL 连接成功", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, " ", str(e), QMessageBox.Ok)

    def OnClickSetupClash(self):
        Print("Setup Clash")
        edit_window = ClashConfigEditWindow()
        edit_window.exec_()

    def OnClickTestClash(self):
        Print("Test Clash")
        try:
            _ = ClashProxy()
            QMessageBox.information(self, " ", "Clash 连接成功", QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, " ", str(e), QMessageBox.Ok)

    def OnClickStart(self):
        self.Start()

    def OnClickPause(self):
        self.Pause()

    def OnClickFinish(self):
        if self.FinishUserOperate():
            self.Finish()

    def OnClickContinue(self):
        self.Continue()

    def OnClickSearch(self):
        self.filter.SetFilter(self.textbox_search.text())
        if self.filter.text == "": # 如果搜索框为空，则显示完整数据表
            self.table.setVisible(True)
            self.table_search.setVisible(False)
        else: # 否则显示搜索结果表
            self.FilterWholeTableSearch()
            self.table.setVisible(False)
            self.table_search.setVisible(True)

    def OnChangeShowItem(self):
        self.show_item = self.checkbox_show_item.isChecked()
        Print("show item" if self.checkbox_show_item.isChecked() else "not show item")

    def OnChangeAutoScroll(self):
        self.auto_scroll = self.checkbox_auto_scroll.isChecked()
        Print("auto scroll" if self.checkbox_auto_scroll.isChecked() else "not auto scroll")

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    return_val = app.exec_()
    ex.Quit()
    sys.exit(return_val)
