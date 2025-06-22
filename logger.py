def log(txt):
    with open("logs.txt", "a") as f:
        f.write(txt + "\n")
