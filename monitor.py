import requests
from bs4 import BeautifulSoup as soup
import time
import json
import datetime
from random import randint

#Set the refresh rate in seconds
interval = 60
#Choose either UK, US or CA
region = "UK"
#Enter your discord webhook here
webhook = ""
#If you want to use proxies, set useproxies to True and enter your proxies on individual lines in a file in the same relative directory called proxies.txt
useproxies = False

if region.lower() == "uk":
    map = "http://www.adidas.co.uk/static/on/demandware.static/-/Sites-CustomerFileStore/default/adidas-GB/en_GB/sitemaps/product/adidas-GB-en-gb-product.xml"
    suggestionsbase = "https://www.adidas.co.uk/api/suggestions/"
if region.lower() == "us":
    map = "https://www.adidas.com/static/on/demandware.static/-/Sites-CustomerFileStore/default/adidas-US/en_US/sitemaps/product/adidas-US-en-us-product.xml"
    suggestionsbase = "https://www.adidas.com/api/suggestions/"
if region.lower() == "ca":
    map = "http://www.adidas.ca/static/on/demandware.static/-/Sites-CustomerFileStore/default/adidas-CA/en_CA/sitemaps/product/adidas-CA-en-ca-product.xml"
    suggestionsbase = "https://www.adidas.ca/api/suggestions/"

headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'en-US,en;q=0.9',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'}

def proxyforreq(proxy):

    try:
        proxy.split(":")[2]
        ip = proxy.split(":")[0]
        port = proxy.split(":")[1]
        userpassproxy = '%s:%s' % (ip, port)
        proxyuser = proxy.split(":")[2].rstrip()
        proxypass = proxy.split(":")[3].rstrip()
        proxies = {'http': 'http://%s:%s@%s' % (proxyuser, proxypass, userpassproxy),
                   'https': 'http://%s:%s@%s' % (proxyuser, proxypass, userpassproxy)}

    except:
        proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}

    return proxies



def gettitle(url, region):
    if region.lower() == "uk":
        base = url.split("/")[3]
    if region.lower() == "us" or region.lower() == "ca":
        base = url.split("/")[4]
    words = base.split("-")
    baretitle = ""
    for word in words:
        word = word[0].capitalize() + word[1:]
        baretitle = baretitle + " %s"%word
    title = baretitle[1:]
    return title


def getdata(pid,suggestionsbase,useproxies,proxies):
    suggestionspage = suggestionsbase + pid
    if useproxies == False:
        sug = requests.get(suggestionspage, headers)
    else:
        sug = requests.get(suggestionspage, proxies=proxies, headers=headers)
    sugtext = json.loads(sug.text)
    prod = sugtext['products']
    prods = prod[0]
    price = prods['standardPrice']
    price = price.replace(" ", "")
    url = prods['image']
    return price, url


def discordpost(title,data,url,webhook,useproxies,proxies):
    footer1 = {
        "icon_url": "https://i.imgur.com/RKaFd4O.png",
        "text": "Developed by @SoleSorcerer"
        ""}
    thumbnail1 = {
        "url": data[1]}
    fields1 = [
        {
            "name": "Price:",
            "value": data[0],
            "inline": "true"
        },
        {
            "name": "Region:",
            "value": region.upper(),
            "inline": "false"
        },
    ]

    embed = {
        "title": title,
        "url": url,
        "color": 5305409,
        "timestamp": str(datetime.datetime.now()),
        "footer": footer1,
        "thumbnail": thumbnail1,
        "fields": fields1
    }

    embed = [embed]
    discordjson = {"embeds": embed, "username": "New Adi Item"}
    if useproxies == False:
        requests.post(webhook, json=discordjson)
    else:
        requests.post(webhook, proxies=proxies, json=discordjson)


links = []

if useproxies == True:
    rawproxies = open('proxies.txt','r').read().splitlines()
else:
    rawproxies = ""

def loop(index,links,map,useproxies,rawproxies,region):
    foundnewlink = False
    if useproxies == False:
        html = requests.get(map, headers)
    else:
        if len(rawproxies) == 0:
            print("Enter some proxies to use proxies")
        if len(rawproxies) == 1:
            num = 0
        if len(rawproxies) > 1:
            num = randint(0, len(rawproxies))

        proxies = proxyforreq(rawproxies[num])
        html = requests.get(map, proxies=proxies, headers=headers)
    pagesoup = soup(html.text, "html.parser")
    for item in pagesoup.find_all('loc'):
        link = item.text
        if link in links:
            pass
        else:
            if index != 10:
                if region.lower() == "uk" :
                    pid = link.split("/")[4].split(".html")[0]
                if region.lower() == "us" or region.lower() == "ca":
                    pid = link.split("/")[5].split(".html")[0]
                title = gettitle(link, region)
                if useproxies == False:
                    data = getdata(pid, suggestionsbase, False, "")
                    try:
                        discordpost(title, data, link, webhook, False, "")
                    except:
                        print("Error posting to discord, make sure you have entered your webhook")
                else:
                    data = getdata(pid, suggestionsbase, True, proxies)
                    try:
                        discordpost(title, data, link, webhook, True, proxies)
                    except:
                        print("Error posting to discord, make sure you have entered your webhook")

                print("--------------\nFound new item: \nTitle: %s\nPrice: %s\nLink: %s\n---------------\n" %(title,data[0],link))
            links.append(link)
            foundnewlink = True
    if index == 0:
        print("Loaded products")
    if foundnewlink == False:
        print("No new links found")
    time.sleep(interval)
    index += 1
    loop(index,links,map,useproxies,rawproxies,region)

loop(0,links,map,useproxies,rawproxies,region)





