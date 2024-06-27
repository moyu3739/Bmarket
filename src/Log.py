class Log:
    log_enable = True
    log_path = "log.txt"

    @staticmethod
    def SetEnable(enable):
        Log.log_enable = enable

    @staticmethod
    def SetPath(path):
        Log.log_path = path

    @staticmethod
    def Print(text):
        if not Log.log_enable: return
        if Log.log_path is None:
            print(text)
        else:
            with open(Log.log_path, "a", encoding="utf-8") as f:
                f.write(text + "\n")



if __name__ == "__main__":
    Log.Print("Hello, World!")
    Log.SetEnable(False)
    Log.SetPath("log2.txt")
    Log.Print("Hello, Python!")
