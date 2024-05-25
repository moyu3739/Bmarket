
log_enable = True
log_path = "log.txt"

def Print(text):
    if not log_enable: return
    if log_path is None:
        print(text)
    else:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")



if __name__ == "__main__":
    Print("Hello, World!")
    Print("Hello, Python!")
