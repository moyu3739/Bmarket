from os import path as os_path, mkdir
from sqlite3 import connect
from time import strftime, localtime
from Item import Item
from Log import *


def GetTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())

class DB:
    connect_on: bool
    conn: connect
    main_table = "main"
    tmp_table = "tmp_main"

    def __init__(self, main_table = "main", db_file = "Bmarket.db"):
        self.tmp_table = "tmp_" + main_table
        if not os_path.exists("db"): mkdir("db") # 创建目录 db
        self.conn = connect("db/" + db_file)
        self.connect_on = True
        self.main_table = main_table
        self.create_table(self.main_table, False)
        self.drop_table(self.tmp_table, False)
        self.create_table(self.tmp_table, False)

    def disconnect(self):
        if not self.connect_on: return
        try:
            self.drop_table(self.tmp_table, False)
            self.conn.close()
        finally:
            self.connect_on = False

    def count_table(self):
        # 创建游标对象
        cursor = self.conn.cursor()
        try:
            # 查询表的数量
            cursor.execute("SHOW TABLES")
            return len(cursor.fetchall())
        except Exception as e:
            Log.Print("错误信息:", str(e))
        finally:
            cursor.close()
        return -1
        
    def create_table(self, table_name: str, exist_echo = True):
        # 创建游标对象
        cursor = self.conn.cursor()
        try:
            # 创建表
            sql = f"CREATE TABLE {'' if exist_echo else 'IF NOT EXISTS'} `{table_name}` ("\
                   "`id` VARCHAR(16) PRIMARY KEY,"\
                   "`name` VARCHAR(128),"\
                   "`time` DATETIME,"\
                   "`price` DECIMAL(8,2),"\
                   "`o_price` DECIMAL(8,2),"\
                   "`discount` DECIMAL(3,2),"\
                   "`url` VARCHAR(128));"
            cursor.execute(sql)
        except Exception as e:
            Log.Print("错误信息:", str(e))
        finally:
            cursor.close()

    def drop_table(self, table_name: str, nonexist_echo = True):
        # 创建游标对象
        cursor = self.conn.cursor()
        try:
            # 创建表
            sql = f"DROP TABLE {'' if nonexist_echo else 'IF EXISTS'} `{table_name}`"
            cursor.execute(sql)
        except Exception as e:
            Log.Print("错误信息:", str(e))
        finally:
            cursor.close()
    
    # 返回是否插入成功
    def insert(self, table: str, item: Item, error_echo = True):
        # 创建游标对象
        cursor = self.conn.cursor()
        try:
            # 新增操作
            sql = f"INSERT INTO `{table}` (`id`, `name`, `time`, `price`, `o_price`, `discount`, `url`) "\
                f"VALUES ("\
                f"'{item.id}', '{item.name.replace("'", "''")}', '{GetTime()}', {item.price}, {item.origin_price}, {item.discount}, '{item.GetItemURL()}')"
            cursor.execute(sql)
            # COMMIT命令用于把事务所做的修改保存到数据库
            self.conn.commit()
            flag = True
        except Exception as e:
            if error_echo: Log.Print("错误信息:", str(e))
            # 发生错误时回滚
            self.conn.rollback()
            flag = False
        finally:
            cursor.close()
            return flag

    # 将新记录存入主表
    def store(self, item: Item, error_echo = True):
        return self.insert(self.main_table, item, error_echo)

    # 将记录存入临时表
    def note(self, item: Item, error_echo = True):
        return self.insert(self.tmp_table, item, error_echo)

    # 将临时表中新id的记录插入主表中 
    def flush_new(self):
        cursor = self.conn.cursor()
        try:
            # 将临时表中的id不重复的记录插入主表
            sql = f"INSERT INTO `{self.main_table}` SELECT * FROM `{self.tmp_table}`"\
                  f"WHERE NOT EXISTS ("\
                  f"SELECT id FROM `{self.main_table}` WHERE `{self.main_table}`.id = `{self.tmp_table}`.id)"
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            Log.Print("错误信息:", str(e))
            self.conn.rollback()
        finally:
            cursor.close()

    # 将主表表中已失效的记录删除
    def remove_invalid(self):
        cursor = self.conn.cursor()
        try:
            # 将主表中已经失效的记录删除（失效，即在临时表不存在相同id的记录）
            sql = f"DELETE FROM `{self.main_table}`"\
                  f"WHERE NOT EXISTS ("\
                  f"SELECT id FROM `{self.tmp_table}` WHERE `{self.main_table}`.id = `{self.tmp_table}`.id)"
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            Log.Print("错误信息:", str(e))
            self.conn.rollback()
        finally:
            cursor.close()
