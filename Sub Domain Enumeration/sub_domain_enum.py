import re
import time
import os
import requests
import ssl
import OpenSSL as openssl
import urllib.parse as up
import threading
import sys
import hashlib
import concurrent.futures
import dns.resolver

usragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    if sys.platform.startswith('win'):
        try:
            import win_unicode_console , colorama
            win_unicode_console.enable()
            colorama.init()
        except:
            HEADER = OKBLUE = OKGREEN = WARNING = FAIL = ENDC = ''

def sereq(url):
    resp = requests.get(url, headers={'User-Agent': usragent, 'Connection': 'Close'}, timeout=30)
    resp.encoding = 'utf-8'
    return resp

def crtsh_enum(domain):
    # certificate logs search crt.sh
    subdomains = []
    start = time.time()
    try:
        r = requests.get("https://crt.sh/?q=" + domain, headers={'User-Agent': usragent, 'Connection': 'Close'}, timeout=30)
        r.encoding = 'utf-8'
        for dom in re.findall("<BR>([^ \.]+\." + re.escape(domain) + ")", r.text):
            subdomains.append(dom)
        subdomains = list(set(subdomains))
        if len(subdomains) == 0 and "Too Many Requests" in r.text:
            print("Too Many Requests for CRT.SH")
        print(bcolors.FAIL + "Cert log from crt.sh for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    except requests.exceptions.Timeout:
        print(bcolors.WARNING + "CRT.SH timeout for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    except:
        print(bcolors.WARNING + "Unknown error in crt.sh for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    return subdomains

def virustotal_enum(domain):
    # virus total enumeration
    subdomains = []
    start = time.time()
    try:
        r = requests.get(url = "https://www.virustotal.com/ui/domains/{0}/subdomains?limit=40".format(domain), headers={'Connection': 'Close'}, timeout=20)
        for i, entry in enumerate(r.json()['data']):
            subdomains.append(entry['id'])
        subdomains = list(set(subdomains))
        print(bcolors.FAIL + "Virustotal for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    except requests.exceptions.Timeout:
        print(bcolors.WARNING + "Virustotal timeout for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    except:
        print(bcolors.WARNING + "Unknown error in virustotal for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    return subdomains

def threatcrowd_enum(domain):
    # threat crowd enumeration
    subdomains = []
    start = time.time()
    try:
        r = requests.get(url = "https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={0}".format(domain), headers={'Connection': 'Close'}, timeout=20)
        for entry in r.json()['subdomains']:
            subdomains.append(entry)
        subdomains = list(set(subdomains))
        print(bcolors.FAIL + "ThreatCrowd for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    except requests.exceptions.Timeout:
        print(bcolors.WARNING + "ThreatCrowd timeout for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    except:
        print(bcolors.WARNING + "Unknown error in ThreatCrowd for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    return subdomains

def contentdict_enum(domain):
    # direct directory dictionary from web page
    subdomains = []
    start = time.time()
    try:
        session = requests.Session()
        session.headers = {'User-Agent': usragent, 'Connection': 'Close'}
        r = session.get("http://" + domain, timeout=20)
        session.close()
        r.encoding = 'utf-8'
        aa = list(set(re.findall("htt.{2,20}" + domain, r.text)))
        if not len(aa) == 0:
            x = [up.unquote(i).split("//")[1] for i in aa if "//" in up.unquote(i)]
            y = list(set(x))
            for jj in y:
                try:
                    r = session.get("http://" + jj, timeout=3)
                    session.close()
                    r.encoding = 'utf-8'
                except:
                    continue
                bb = list(set(re.findall("htt.{2,20}" + domain, r.text)))
                if not len(bb) == 0:
                    x += [up.unquote(i).split("//")[1] for i in bb if "//" in up.unquote(i)]
            subdomains = list(set(subdomains + x))
        print(bcolors.FAIL + "Content dictionary level 2 BFS for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    except requests.exceptions.ConnectionError:
        print(bcolors.WARNING + "Webpage Dcitionary Connection Error for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    except:
        print(bcolors.WARNING + "Unknown error in webpage dictionary for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    return subdomains

def san_enum(domain):
    # subject alternate name in x.509 certs
    subdomains = []
    start = time.time()
    try:
        cert = ssl.get_server_certificate((domain, 443))
        x509 = openssl.crypto.load_certificate(openssl.crypto.FILETYPE_PEM, cert)
        for i in range(0, x509.get_extension_count()):
            ext = x509.get_extension(i)
            if "subjectAltName" in str(ext.get_short_name()):
                content = ext.__str__()
                for d in content.split(","):
                    subdomains.append(d.strip()[4:])
        subdomains = list(set(subdomains))
        print(bcolors.FAIL + "SAN for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    except:
        print(bcolors.WARNING + "Unknown error in san for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    return subdomains

def se_enum(domain):
    # search engine result - Yahoo and Netcraft
    subdomains = []
    start = time.time()
    try:
        x1 = []
        r1 = requests.get(url = "https://search.yahoo.com/search?p=site%3A{0}".format(domain), headers={'User-Agent': usragent, 'Connection': 'Close'}, timeout=30)
        r1.encoding = 'utf-8'
        x1 += re.findall('http.{3,15}\.' + re.escape(domain), r1.text)
        if not len(x1) == 0:
            limpage = (re.findall('<span>.{2,20} results<', r1.text)[0]).split(' results')[0].split('<span>')[1]
        else:
            limpage = '10'
        limpage = min(200, int(limpage.replace(',', '')))
        urls = ["https://search.yahoo.com/search?p=site%3A{0}&b={1}".format(domain, pages) for pages in range(10, limpage, 10)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=limpage//10) as pool:
            responses = pool.map(sereq, urls)
        for rr in responses:
            x1 += re.findall('http.{3,15}\.' + re.escape(domain), rr.text)

        link = "https://searchdns.netcraft.com/?restriction=site+contains&host={0}".format(domain)
        x2 = []
        cookies = {}
        r3 = requests.get(url = link, headers={'User-Agent': usragent, 'Connection': 'Close'}, timeout=(10, None), cookies=cookies)
        r3.encoding = 'utf-8'
        if 'set-cookie' in r3.headers:
            cook = r3.headers['set-cookie']
            cook_list = cook[0:cook.find(';')].split("=")
            cookies[cook_list[0]] = cook_list[1]
            cookies['netcraft_js_verification_response'] = hashlib.sha1(up.unquote(cook_list[1]).encode('utf-8')).hexdigest()
        while True:
            try:
                r3 = requests.get(url = link, headers={'User-Agent': usragent, 'Connection': 'Close'}, timeout=(10, None), cookies=cookies)
                r3.encoding = 'utf-8'
                x2 += re.findall('http.{3,15}\.' + re.escape(domain), r3.text)
                if 'Next Page' not in r3.text:
                    break
                text = re.findall('.a.+?..Next Page', r3.text)
                link = "https://searchdns.netcraft.com" + (text[0].split("href=\"")[1]).split("\">Next")[0]
            except requests.exceptions.Timeout:
                break
        x1 = list(set(x1 + x2))
        x1 = [up.unquote(i).split("//")[1] for i in x1 if "//" in up.unquote(i) and not "<" in up.unquote(i)]

        subdomains = list(set(x1))
        print(bcolors.FAIL + "SE result for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    except requests.exceptions.Timeout:
        print(bcolors.WARNING + "SE result timeout for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    except:
        print(bcolors.WARNING + "Unknown error in se result for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
    return subdomains

def dnsmx_enum(domain):
    # DNS resolve in x.509 certs
    subdomains = []
    flag = True
    start = time.time()
    try:
        result = dns.resolver.query(domain, 'MX')
        for exdata in result:
            subdomains.append(exdata.exchange.to_text())
    except:
        print(bcolors.WARNING + "Unknown error in dns resolver for " + domain + " - ", "%.2f" %(time.time() - start), bcolors.ENDC)
        flag = False
    subdomains = list(set(subdomains))
    if flag:
    	print(bcolors.FAIL + "DNS MX Resolver for domain " + domain + " - ", "%.2f" %(time.time() - start), len(subdomains), bcolors.ENDC)
    return subdomains

def combined_enum(domain):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        crtsh_res = executor.submit(crtsh_enum, domain)
        virustotal_res = executor.submit(virustotal_enum, domain)
        threatcrowd_res = executor.submit(threatcrowd_enum, domain)
        contentdict_res = executor.submit(contentdict_enum, domain)
        san_res = executor.submit(san_enum, domain)
        se_res = executor.submit(se_enum, domain)
        dnsmx_res = executor.submit(dnsmx_enum, domain)
        subdlist = [crtsh_res.result(), virustotal_res.result(), threatcrowd_res.result(), contentdict_res.result(), san_res.result(), se_res.result(), dnsmx_res.result()]
    subd = []
    for res in subdlist:
        subd += res
    subd = list(set(subd))
    return subd

starttime = time.time()

if len(sys.argv) < 2:
    print(bcolors.WARNING + "Usage: python sub_domain_enum.py <domain> [-s/--save]" +bcolors.ENDC)
    sys.exit()
user_dom = sys.argv[1]
data = combined_enum(user_dom)
print(bcolors.OKGREEN + "---------------------------------")
print("Number of unique entries found :", len(data))
print("---------------------------------" + bcolors.ENDC)
if len(sys.argv) > 2 and (sys.argv[2] == "-s" or "--save"):
    f = open(user_dom.replace('.', '-'), "a+")
    for subdomain in data:
        f.write(subdomain)
        f.write("\n")
    f.close()
    print(bcolors.HEADER + "Data stored in file " + bcolors.OKGREEN + user_dom.replace('.', '-') + bcolors.HEADER + " in current directory." + bcolors.ENDC)
else:
    for subdomain in sorted(data):
        print(bcolors.OKBLUE + subdomain)

print(bcolors.WARNING + "---------------------------------\nTotal Time taken", "%.2f" %(time.time() - starttime), bcolors.ENDC)
