from time import sleep
from click import command, option, Choice
import mysql_database
import sqlite_database
from access import access
from clash_proxy import proxy
from Log import *

CATEGORY_MAP = {
    "all": "",
    "fig": "2312",
    "model": "2066",
    "peri": "2331",
    "3C": "2273",
    "gacha": "fudai_cate_id",
}

SORT_MAP = {
    "时间降序": "TIME_DESC",
    "价格升序": "PRICE_ASC",
    "价格降序": "PRICE_DESC",
}

dbs = []

def category2id(category: str):
    return CATEGORY_MAP.get(category, "")

def sort2type(sort: str):
    return SORT_MAP.get(sort, "TIME_DESC")

def pull(category: str, sort: str, db_type: str, use_proxy = False, show_item_info = False, keywords = [], shieldwords = []):
    next_id = None
    count = 0
    count_item = 0
    flag = True # 表示当前商品是否为本地数据库中没有的新商品
    count_reconnect = -1 # 上一次重连时的 count
    reconnect = 5 # 尝试重连的次数
    cont = True # 是否继续运行

    # 选择数据库类型
    match db_type:
        case "sqlite": dbs = [sqlite_database.DB(category, "Bmarket.db")]
        case "mysql": dbs = [mysql_database.DB(category, "./config.txt")]
        case "both": dbs = [sqlite_database.DB(category, "Bmarket.db"), mysql_database.DB(category, "./config.txt")]

    # 初始化与市集的连接
    bmarket = access()
    # 初始化代理
    if use_proxy: pxy = proxy("./config.txt")

    print("开始获取商品信息...")
    while True:
        try:
            next_id, fetched = bmarket.fetch(next_id, category2id(category), sort2type(sort), keywords, shieldwords)
            for item in fetched:
                for db in dbs.copy():
                    success = db.store(item, error_echo=False) # 存入主表
                    if not success: # 如果记录已经在当前数据库中存在
                        dbs.remove(db) # 把当前数据库从数据库列表中删除，即之后新记录不会再存入当前数据库
            if len(dbs) == 0: break # 如果所有数据库都已经存在相同记录，则结束当前爬取任务

            count_item += len(fetched)
            if count_item % 100 == 0:
                print(f"已获取 {count_item} 条记录")
            if not flag:
                print("没有新商品了...")
                break
            if not next_id:
                if count == 0: print("Cookie 无效，请更新 Cookie...")
                else: print("没有更多商品了...")
                break
            count += 1
        except Exception as e:
            if count_reconnect != count: # 如果上次重连后有获取到数据
                print("连接断开，可能触发风控，尝试自动重连...")
                count_reconnect = count
                reconnect_try = 0
                # if use_proxy: pxy.change_proxy() # 更换代理
            else: # 连续出现重连失败
                reconnect_try += 1
            if reconnect_try >= reconnect:
                if use_proxy:
                    print("自动重连失败，尝试切换代理...")
                    msg = pxy.change_proxy() # 更换代理
                    if msg == "ok":
                        print(f"切换到代理 '{pxy.now_proxy}'")
                        continue
                    else: print(msg)
                while True:
                    if use_proxy: print("切换代理失败，请选择接下来的操作...")
                    else: print("自动重连失败，请选择接下来的操作...")
                    print("c  再次尝试连接")
                    print("q  退出程序，不执行任何操作")
                    s = input()
                    match s:
                        case "c":
                            print("继续获取商品信息...")
                            cont = True
                            break
                        case "q":
                            print("退出程序...")
                            cont = False
                            break
            if not cont: break # 结束外层循环
            sleep(1) # 重连间隔，等待1秒后重连
    for db in dbs: db.disconnect()

def merge(category: str, sort: str, db_type: str, use_proxy = False, show_item_info = False, keywords = [], shieldwords = []):
    next_id = None
    count = 0
    count_item = 0
    count_reconnect = -1 # 上一次重连时的 count
    reconnect = 5 # 尝试重连的次数
    cont = True # 是否继续运行

    # 选择数据库类型
    global dbs
    match db_type:
        case "sqlite": dbs = [sqlite_database.DB(category, "Bmarket.db")]
        case "mysql": dbs = [mysql_database.DB(category, "./config.txt")]
        case "both": dbs = [sqlite_database.DB(category, "Bmarket.db"), mysql_database.DB(category, "./config.txt")]

    # 初始化与市集的连接
    bmarket = access()
    # 初始化代理
    if use_proxy: pxy = proxy("./config.txt")

    print("开始获取商品信息...")
    while True:
        try:
            next_id, fetched = bmarket.fetch(next_id, category2id(category), sort2type(sort), keywords, shieldwords)
            for item in fetched:
                for db in dbs: db.note(item)
                if show_item_info: print(item.GetInfo())
            count_item += len(fetched)
            if count_item % 100 == 0:
                print(f"已获取 {count_item} 条记录")
            if not next_id:
                if count == 0: print("Cookie 无效，请更新 Cookie...")
                else:
                    print("没有更多了...")
                    for db in dbs:
                        db.remove_invalid()
                        db.flush_new()
                break
            count += 1
        except Exception as e:
            if count_reconnect != count: # 如果上次重连后有获取到数据
                print("连接断开，可能触发风控，尝试自动重连...")
                count_reconnect = count
                reconnect_try = 0
                # if use_proxy: pxy.change_proxy() # 更换代理
            else: # 连续出现重连失败
                reconnect_try += 1
            if reconnect_try >= reconnect:
                if use_proxy:
                    print("自动重连失败，尝试切换代理...")
                    msg = pxy.change_proxy() # 更换代理
                    if msg == "ok":
                        print(f"切换到代理 '{pxy.now_proxy}'")
                        continue
                    else: print(msg)
                while True:
                    if use_proxy: print("切换代理失败，请选择接下来的操作...")
                    else: print("自动重连失败，请选择接下来的操作...")
                    print("c  再次尝试连接")
                    print("q  退出程序，不执行任何操作（警告：此操作将不会保存本次获取到的新记录）")
                    print("f  保存新获取到的记录，然后退出程序（警告：此操作将会保留部分已失效记录）")
                    print("m  合并原有记录和新记录，然后退出程序（警告：此操作将会丢失部分原有记录）")
                    s = input()
                    match s:
                        case "c":
                            print("继续获取商品信息...")
                            cont = True
                            break
                        case "q":
                            print("退出程序...")
                            cont = False
                            break
                        case "f":
                            print("保存已经获取到的记录...")
                            for db in dbs: db.flush_new()
                            cont = False
                            break
                        case "m":
                            print("合并已有记录和新记录...")
                            for db in dbs:
                                db.remove_invalid()
                                db.flush_new()
                            cont = False
                            break
            if not cont: break # 结束外层循环，退出程序
            sleep(1) # 重连间隔，等待1秒后重连
    for db in dbs: db.disconnect()


@command()
@option(
    "--category",
    prompt="商品类别",
    type=Choice(["all", "fig", "model", "peri", "3C", "gacha"]),
    default="fig",
)
@option(
    "--sort",
    prompt="排序方式",
    type=Choice(["时间降序", "价格升序", "价格降序"]),
    default="时间降序",
)
@option(
    "--operator",
    prompt="处理新记录的方式",
    type=Choice(["pull", "merge"]),
    default="merge",
)
@option(
    "--db_type",
    prompt="使用的数据库",
    type=Choice(["sqlite", "mysql", "both"]),
    default="sqlite",
)
@option(
    "--use_proxy",
    prompt="重连失败时是否自动切换代理",
    type=Choice(["y", "n"]),
    default="n",
)
def main(category: str, sort: str, operator: str, db_type: str, use_proxy: str):
    match operator:
        case "pull":
            pull(category, sort, db_type, use_proxy == "y")
        case "merge":
            merge(category, sort, db_type, use_proxy == "y")

try:
    main()
except Exception as e:
    print(e)
finally:
    for db in dbs: db.disconnect()
    input("按任意键退出程序...")
