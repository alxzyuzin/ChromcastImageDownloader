import time
strn = "GeeksforGeeks"
for i in range(0, len(strn)):
    print(strn[i], end="", flush = True)
    time.sleep(2)

for i in range(10):
    print(".", end = "", flush=True)
    time.sleep(1)
