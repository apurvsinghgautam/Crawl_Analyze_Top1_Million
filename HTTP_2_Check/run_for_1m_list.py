from check_http2 import check_http2

with open("tranco_list.csv") as f:
    mill = f.readlines()

mill = [dd.split('\n')[0].split(',')[1] for dd in mill]

def tfunc(kk):
    f = open("drive/My Drive/http2_domains/result_" + str(kk), "a+")
    g = open("drive/My Drive/http2_domains/error_" + str(kk), "a+")
    for dom in mill[kk*1000:(kk+1)*1000]:
        http2_res = check_http2(dom)
        if http2_res == "error":
            g.write(dom)
            g.write("\n") 
            # print("-", end="")
            continue
        f.write(dom)
        f.write(" ")
        f.write(http2_res)
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
    f = open("http2_domains/error_" + str(i), "r")
    x = f.readlines()
    values += [dd for dd in x]
    f.close()

print(len(values))
values = [dd.split('\n')[0] for dd in values]

f = open("allerror", "a+")
for i in values:
    f.write(i)
    f.write('\n')

values = []
for i in range(1000):
    f = open("http2_domains/result_" + str(i), "r")
    x = f.readlines()
    values += [dd for dd in x]
    f.close()

print(len(values))
values = [dd.split('\n')[0] for dd in values]

f = open("allresult", "a+")
for i in values:
    f.write(i)
    f.write('\n')
