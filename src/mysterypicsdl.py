import requests
import math
import os
import glob
from bs4 import BeautifulSoup

# Mystery Pic Downloader
# =====================================================================================================

# Scrapes jellyneo for pictures that could come up in mystery pic
# Sorry Dave from Jellyneo forgive me but i cannot be ASSED to manually do this

# =====================================================================================================

# You are free to modify this script for personal use but modified scripts must not be shared publicly without permission.
# Feel free to contact me at @mettymagic on discord for any questions or inquiries. ^^

# Trans rights are human rights ^^
# metty says hi

# =====================================================================================================

# set to true to download categories that have been used waaaay in the past
FULL_DUMP = False
# set to the directory you want to download the dump to
DUMP_DIRECTORY = "./images/" 

# =====================================================================================================

# sends web request and returns response
def getResponse(url, lasturl, getSoup = True):
    # Headers spoof an actual response. I just stole the ones my browser sent in a manual visit.
    x = requests.get(url, headers = {
    "Connection":"keep-alive",
    "Cache-Control":"max-age=0",
    "sec-ch-ua":'"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    "sec-ch-ua-mobile":"?0",
    "sec-ch-ua-platform":'"Windows"',
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site":"none",
    "Sec-Fetch-Mode":"navigate",
    "Sec-Fetch-User":"?1",
    "Sec-Fetch-Dest":"document",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"en-US,en;q=0.9",
    "Referer":lasturl # we're just manually going page-by-page, right..?
    })

    if getSoup:
        soup = BeautifulSoup(x.content, "html.parser")
        return soup
    else:
        return x.content
    
# returns true if file exists within excluded list
def isExcluded(name):
    global excludelist
    for str in excludelist:
        if str in name:
            return True
    return False
        
# downloads results from a single page
def getImagesFromResponse(soup, folder, sourceurl, page, pages):
    imgs = soup.select("body > div.row > div.large-9.small-12.columns.content-wrapper > ul.no-padding.small-block-grid-2.large-block-grid-4.text-center > li > a > img")
    i = 1
    # for each image we want to download
    for img in imgs:
        # grab file name from url
        url = img.get("src")
        name = url.partition("https://images.neopets.com/")[-1].replace("/", "-")
        
        # skip work if image already exists under any file type
        if not glob.glob("%s/%s/%s.*" % (DUMP_DIRECTORY,folder,name.split(".")[0])): 
            print("[%s : %d/%d : %d/40] Downloading %s...                              " % (folder, page, pages, i, name), end="\r")

            # get image data
            img_data = getResponse(url, sourceurl, False)
            
            # saves image data as file
            with open("%s/%s/%s" % (DUMP_DIRECTORY,folder,name), 'wb') as f:
                f.write(img_data)
        elif isExcluded(name):
            print("NOTE: Image excluded, skipping %s...                              " % (name))
        else:
            print("NOTE: Image already exists, skipping %s...                              " % (name))
        i += 1 

def getIgnoreList():
    if os.path.exists("src/exclude/noscrape.txt"):
        with open("src/exclude/noscrape.txt", "r") as f:
            return f.read().split("\n")

# visits each image result page and downloads all results
def getAllPages(baseurl, category, imgnum):
    # makes category directory if it doesn't already exist
    if not os.path.exists("%s/%s/" % (DUMP_DIRECTORY,category)):
        os.makedirs("%s/%s/" % (DUMP_DIRECTORY,category))

    # calculates # of pages to visit based on 40 results per page
    # TODO: start w/ one response, use that to read # of pages
    pages = math.ceil(imgnum/40.0)
    startlist = range(pages)
    lasturl = "https://www.drsloth.com"
    print("Downloading %d images (%d pages) for category %s." % (imgnum, pages, category))
    
    # for each page 
    for start in startlist:
        url = baseurl + str(start*40) #increment start index
        getImagesFromResponse(getResponse(url, lasturl), category, url, start+1, pages) #run the work for that page
        lasturl = url #we totally manually visited this page
    print("Downloading complete, %d images downloaded." % (imgnum))

# =====================================================================================================

# to scrape more pages, simply add more function calls using the following format:
# getAllPages(<url with blank &start=>, <folder name>, <number of results the search returns>)
# example: getAllPages("https://www.drsloth.com/search/?start=0", "ddos", 147585)

# =====================================================================================================

# create root directory if it doesn't exist
if not os.path.exists(DUMP_DIRECTORY):
    os.makedirs(DUMP_DIRECTORY)
            
# should cover all shops / non-shop banners
excludelist = getIgnoreList()     
getAllPages("https://www.drsloth.com/search/?width=450&height=150&start=", "shops", 160)

# defunct / unused categories, left out by default
if(FULL_DUMP):
    getAllPages("https://www.drsloth.com/search/?category=38&start=", "shopblog", 275)
    getAllPages("https://www.drsloth.com/search/?category=10&not_in_url=t%5C_&start=", "usershop", 2301)
    getAllPages("https://www.drsloth.com/search/?category=22&start=", "neopedia", 634)
    getAllPages("https://www.drsloth.com/search/?category=23&start=", "bg", 2087)
    getAllPages("https://www.drsloth.com/search/?category=60&start=", "bg", 1482)
    getAllPages("https://www.drsloth.com/search/?category=37&start=", "world", 889)
