from time import sleep
from click import command, option, Choice
from item import Item
import mysql_database
import sqlite_database
from access import access
from clashAPI import Selector, Mode, clashAPI
from proxy import proxy

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

    bmarket = access()
    if use_proxy: pxy = proxy(Selector.PAYPAL)

    match db_type:
        case "sqlite": dbs = [sqlite_database.DB(category, "Bmarket.db")]
        case "mysql": dbs = [mysql_database.DB(category, "./dbconfig.txt")]
        case "both": dbs = [sqlite_database.DB(category, "Bmarket.db"), mysql_database.DB(category, "./dbconfig.txt")]

    while True:
        try:
            next_id, fetched = bmarket.fetch(next_id, category2id(category), sort2type(sort), keywords, shieldwords)
            for item in fetched:
                # flag = db.store(item, False)
                for db in dbs: db.store(item, False)
                if not flag: break
                if show_item_info: print(item.info())
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
                print("可能触发风控，尝试自动重连...")
                count_reconnect = count
                reconnect_try = 0
                if use_proxy: pxy.change_proxy() # 更换代理
            else: # 连续出现重连失败
                reconnect_try += 1
            if reconnect_try >= reconnect:
                while True:
                    print("可能触发了风控，请选择接下来的操作...")
                    print("c  手动重置网络连接，然后继续获取数据")
                    print("q  退出程序，不执行任何操作")
                    s = input()
                    match s:
                        case "c":
                            print("继续获取数据...")
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

    bmarket = access()
    if use_proxy: pxy = proxy(Selector.PAYPAL)

    match db_type:
        case "sqlite": dbs = [sqlite_database.DB(category, "Bmarket.db")]
        case "mysql": dbs = [mysql_database.DB(category, "./dbconfig.txt")]
        case "both": dbs = [sqlite_database.DB(category, "Bmarket.db"), mysql_database.DB(category, "./dbconfig.txt")]

    while True:
        try:
            next_id, fetched = bmarket.fetch(next_id, category2id(category), sort2type(sort), keywords, shieldwords)
            for item in fetched:
                for db in dbs: db.note(item)
                if show_item_info: print(item.info())
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
                print("可能触发风控，尝试自动重连...")
                count_reconnect = count
                reconnect_try = 0
                if use_proxy: pxy.change_proxy() # 更换代理
            else: # 连续出现重连失败
                reconnect_try += 1
            if reconnect_try >= reconnect:
                while True:
                    print("自动重连失败，请选择接下来的操作...")
                    print("c  手动重置网络连接，然后继续运行程序")
                    print("q  退出程序，不执行任何操作（警告：此操作将不会保存本次获取到的新记录）")
                    print("f  保存新获取到的记录，然后退出程序（警告：此操作将会保留部分已失效记录）")
                    print("m  合并原有记录和新记录，然后退出程序（警告：此操作将会丢失部分原有记录）")
                    s = input()
                    match s:
                        case "c":
                            print("继续获取数据...")
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
    prompt="请选择分类",
    type=Choice(["all", "fig", "model", "peri", "3C", "gacha"]),
    default="fig",
)
@option(
    "--sort",
    prompt="请选择排序方式",
    type=Choice(["时间降序", "价格升序", "价格降序"]),
    default="时间降序",
)
@option(
    "--operator",
    prompt="请选择获取数据的方式",
    type=Choice(["pull", "merge"]),
    default="merge",
)
@option(
    "--db_type",
    prompt="请选择使用的数据库",
    type=Choice(["sqlite", "mysql", "both"]),
    default="sqlite",
)
@option(
    "--use_proxy",
    prompt="重连失败时是否自动使用代理",
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
    input("按任意键退出程序...")