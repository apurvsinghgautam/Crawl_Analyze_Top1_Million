import sys
import threading
from check_tls import check_tls


with open("drive/My Drive/tranco_list.csv") as f:
    mill = f.readlines()

mill = [dd.split('\n')[0].split(',')[1] for dd in mill]

def tfunc(kk):
    f = open("drive/My Drive/tls_ver_check_results/result_" + str(kk), "a+")
    g = open("drive/My Drive/tls_ver_check_results/error_" + str(kk), "a+")
    for dom in mill[kk*1000:(kk+1)*1000]:
        tls_ver = check_tls(dom)
        if tls_ver == "error":
            g.write(str(dom))
            g.write("\n") 
            print("-", end="")
            continue
        f.write(str(dom))
        f.write(" ")
        f.write(str(tls_ver))
        f.write("\n")
    f.close()
    g.close()

threads = []

for i in range(1000):
    thread = threading.Thread(target=tfunc, args=(i,))
    threads.append(thread)
    thread.start()

for t in threads:
    t.join()
    
values = []
for i in range(1000):
    f = open("drive/My Drive/tls_ver_check_results/error_" + str(i), "r")
    x = f.readlines()
    values += [dd for dd in x]
    f.close()

print(len(values))
values = [dd.split('\n')[0] for dd in values]

f = open("drive/My Drive/allerror", "a+")
for i in values:
    f.write(i)
    f.write('\n')

values = []
for i in range(1000):
    f = open("drive/My Drive/tls_ver_check_results/result_" + str(i), "r")
    x = f.readlines()
    values += [dd for dd in x]
    f.close()

print(len(values))
values = [dd.split('\n')[0] for dd in values]

f = open("drive/My Drive/allresult", "a+")
for i in values:
    f.write(i)
    f.write('\n')