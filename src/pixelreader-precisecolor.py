from PIL import Image, ImageDraw
import os
import glob

# Mystery Pic Color Matcher
# =====================================================================================================

# Searches the image dump for images that contain a list of color codes
# You can use a color picker on the Mystery Pic and grab a few significant color codes from there
# Less accurate but much faster

# =====================================================================================================

# You are free to modify this script for personal use but modified scripts must not be shared publicly without permission.
# Feel free to contact me at @mettymagic on discord for any questions or inquiries. ^^

# Trans rights are human rights ^^
# metty says hi

# =====================================================================================================

# set directories as desired
DUMP_ROOT_DIRECTORY = "./images/shops"
MATCH_DIRECTORY = "./matches"

# number between 0-1, indicates tolerance of color differences.
#   sometimes TNT fucks with image colors / blurs so it can help to increase or decrease this value
#   low: 0.02, avg: 0.04, high: 0.08
COLOR_TOLERANCE = 0.04 

# =====================================================================================================

# scans every pixel of an image for the matching colors
# if all the colors are found in said image, copy it to a match folder
def scanImage(path):
    global rgbs
    im = Image.open(path).convert("RGB")
    width, height = im.size
    need_to_find = rgbs.copy()
    
    #iterate each pixel in image
    for x in range(width):
        for y in range(height):
            rgb_found = [] # can have multiple matches as a result of color tolerance so we do this as an array
            for rgb in need_to_find:
                pixel = im.getpixel((x,y))
                # if difference in rgb values is within tolerance, add to found list
                rgb_diff = tuple(map(lambda i, j: abs(i - j), pixel, rgb))
                if all(diff <= 255*COLOR_TOLERANCE for diff in rgb_diff):
                    rgb_found.append(rgb)
            # we don't need to find found colors anymore so we can update it
            for rgb in rgb_found:
                need_to_find.remove(rgb)
            # if we don't have any colors left to find, it's a match
            if not need_to_find:
                global matchNum
                matchNum += 1
                print("MATCH #%d FOUND at %d, %d in %s." % (matchNum, x, y, path))
                # creates a little red circle at the last matching location on the image - can be helpful in some cases but its not perfect
                draw = ImageDraw.Draw(im)
                draw.ellipse((x-20, y-20, x+20, y+20), fill=None, outline="red")
                # saves image
                im.save(MATCH_DIRECTORY + "/match%d.png" % matchNum)
                return

# =====================================================================================================

# creates list of image file paths to be read
img_list = []
for root, subdirs, files in os.walk(DUMP_ROOT_DIRECTORY):
    for file in files:
        img_list.append(os.path.join(root, file))
            
if len(img_list) < 1: 
    print("Error: There's no images to scan in directory %s!")
    exit()

# parses user input hexcodes separated by spaces
print("Input color hexcodes: (multiple colors separated by spaces)")
h = input(" > ").strip().split(" ")
rgbs = []
for hex in h:
    hex = hex.lstrip("#")
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    rgbs.append(rgb)
print("Searching %d images for %d color(s) " % (len(img_list), len(rgbs)), rgbs)

# create matches directory if it doesn't exist
if not os.path.exists(MATCH_DIRECTORY):
    os.makedirs(MATCH_DIRECTORY)
    
# clears the match
files = glob.glob("%s/*" % MATCH_DIRECTORY)
for f in files:
    os.remove(f)

i = 0
matchNum = 0
# scan each image
for img in img_list:
    i += 1
    print("Scanning image %d / %d            " % (i, len(img_list)), end="\r")
    scanImage(img)

# final results displayed, can be accessed in match folder
print("%d matches were found out of %d images searched." % (matchNum, len(img_list)))
    