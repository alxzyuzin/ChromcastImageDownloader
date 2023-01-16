import time
strn = "GeeksforGeeks"
for i in range(0, len(strn)):
    k = 10
    print(strn[i], end="", flush = True)
    time.sleep(2)
print(k)
for i in range(10):
    print(".", end = "", flush=True)
    time.sleep(1)
