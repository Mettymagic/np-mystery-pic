from PIL import Image, ImageDraw
import os
import numpy as np
import time
from threading import Thread
from threading import active_count
from threading import Lock

# Mystery Pic File Matcher
# =====================================================================================================

# Searches the image dump for images that contain the same color as the Mystery Pic
# Slower and can be finnicky if TNT screws with the MP colors
# But can be much more accurate

# =====================================================================================================

# You are free to modify this script for personal use but modified scripts must not be shared publicly without permission.
# Feel free to contact me at @mettymagic on discord for any questions or inquiries. ^^

# Trans rights are human rights ^^
# metty says hi

# =====================================================================================================

# set directories as desired
IMAGE_ROOT_DIRECTORY = "." # just drop the image in the same folder this file is in by default
DUMP_ROOT_DIRECTORY = "./images/shops"
MATCH_DIRECTORY = "./matches"

# number between 0-1, indicates tolerance of color differences.
#   sometimes TNT fucks with image colors / blurs so it can help to increase or decrease this value
#   low: 0.02, avg: 0.04, high: 0.08
TOLERANCE = 0.04

# how often the progress display updates, in seconds
DISPLAY_INTERVAL = 2.0

# =====================================================================================================

lock = Lock()

# converts time to readable string
def time_str(t):
    mod_t = t
    min = int(mod_t//60000)
    m_str = ""
    if min > 0: m_str = "{}m:".format(min)
    mod_t -= min*60000
    sec = int(mod_t//1000)
    s_str = ""
    if sec > 0: s_str = "{:02d}s:".format(sec)
    mod_t -= sec*1000
    return m_str+s_str+"{:03d}ms".format(int(mod_t))
    
# splits list a into n equally divided lists
def split(a, n):
    k, m = divmod(len(a), n)
    return list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)))

# gets a list of colors in the source mystery pic
def scanMysteryPic(path):
    im = Image.open(path).convert("RGB")
    width, height = im.size
    rgbs = {}
    for x in range(width):
        for y in range(height):
            pixel = im.getpixel((x,y))
            rgbs[pixel] = None
    return list(rgbs.keys())

# scans every pixel of an image for the matching colors
# if all the colors are found in said image, copy it to a match folder
def scanImage(path):
    global rgbs
    im = Image.open(path).convert("RGB")
    width, height = im.size
    colors_to_find = rgbs.copy()
    # for each pixel in image
    for x in range(width):
        for y in range(height):
            pixel = im.getpixel((x,y))
            # checks if the pixel matches any of the colors we need to find
            for rgb in colors_to_find.copy():
                rgb_diff = tuple(map(lambda i, j: abs(i - j), pixel, rgb))
                # if the color is close enough, remove it
                if all(diff <= 255*TOLERANCE for diff in rgb_diff) and rgb in colors_to_find:
                    colors_to_find.remove(rgb)
                    if not colors_to_find: #if we found all the colors
                        global matchNum
                        # critical section - only 1 thread can do this at a time
                        lock.acquire()
                        # save the file and add to # of matches
                        matchNum += 1
                        print("MATCH #%d FOUND in %s: All colors found!" % (matchNum, path))
                        im.save(os.path.join("matches", "match%d.png" % matchNum))
                        lock.release()
                        # end of critical section
                        return

# each thread runs this function
def thread_work(imglist):
    global n_complete
    # scans each image in its list
    for img in imglist:
        scanImage(img)
        # critical section - only 1 thread can do this at a time
        lock.acquire()
        n_complete += 1
        lock.release()
        # end of critical section

# creates list of image file paths to be read
img_list = []
for root, subdirs, files in os.walk(DUMP_ROOT_DIRECTORY):
    for file in files:
        img_list.append(os.path.join(root, file))
            
if len(img_list) < 1: 
    print("Error: There's no images to scan in directory %s!")
    exit()

# gets color list from user input file
print("Enter mystery pic file name: (ex pic.png)\n")
h = input(" > ")

rgbs = scanMysteryPic(h)
print("Searching %d images for %d colors found in %s with %.0f%% tolerance." % (len(img_list), len(rgbs), h, TOLERANCE*100))

#divide work across threads
n_threads = os.cpu_count()
split_list = split(img_list, n_threads)
print("Using %d threads to find results." % n_threads)

# create matches directory if it doesn't exist
if not os.path.exists(MATCH_DIRECTORY):
    os.makedirs(MATCH_DIRECTORY)

# start thread work
n_complete = 0
matchNum = 0
print("Progress: Thread 0/%d started." % (n_threads), end='\r')
for i in range(n_threads):
    t = Thread(target=thread_work, args=[split_list[i]])
    t.start()
    print("Progress: Thread %d/%d started." % ((i+1), n_threads), end='\r')
    i += 1
print("Progress: All %d threads started. Running calculations..." % (n_threads))

# display time and display progress while working
start_time = time.monotonic()
working = True
while(working):
    nt = active_count()
    if nt == 1: working = False # if our only thread is this one, the work is done!
    print("Progress: %d / %d (%.1f%%) (Time Elapsed: %s)                 " % (n_complete, len(img_list), (n_complete/len(img_list))*100, time_str((time.monotonic()-start_time)*1000)), end= '\r')
    time.sleep(DISPLAY_INTERVAL - ((time.monotonic() - start_time) % DISPLAY_INTERVAL)) # we can take a break while the other threads do their work
    
# final results displayed, can be accessed in match folder
print("%d matches were found out of %d images searched." % (matchNum, len(img_list)))
    