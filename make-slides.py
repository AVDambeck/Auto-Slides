#!python
"""00. this is 1;5Da program which inputs a set of images with a specific naming format, and outputs a pdf containing a slide show of the images with titles;
0.  the spe1;5C1;5Dcific name format is id.mm-dd-yyyy.name_of_image.jpg7;
1. impo1;5A1;5C1;5Drt and define;
2. 1;5B1;5A1;5C1;5Dvalidate image names;
3. 1;5B1;5A1;5C1;5Dcreate a slide object from each picture, including the extracted name, date, and file location;
4. for each slide, genorate HTML, and render to file;
5. unite the files;
6. exit;
"""

#1. Import and define
import argparse
import logging
import glob
import re
import os
from pyhtml2pdf import converter
import subprocess

margin = 50
page_width = 1920
page_height = 1080
page_ratio = page_width/page_height

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Increase verbosity.")
parser.add_argument("--debug", action='store_true', help="presevers some files for debugging porposus.")
parser.add_argument("-f", "--force",  action='store_true', help="Overide exiting cache.")
parser.add_argument("-d", "--dir", help="Directory to load files from.")
parser.add_argument("-o", "--output", help="Specify output file.")
parser.add_argument("-n", "--noformat", action='store_true', help="Disable reformating of text, eg display names will include underscores, lowercase letters, etc.")
parser.add_argument("-D", "--nodate", action='store_true', help="Disable date.")
parser.add_argument("-t", "--title", help='Will genorate a title page with the text "Title|Subtitle."')
parser.add_argument("-H", "--headerposition", help='"left" "right" "top" "bottom" or "auto"')
args = parser.parse_args()

if args.verbose == True:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
else:
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

ProcessFiles = True
if args.debug:
    removeProcessFiles = False

force = False
if args.force:
    force = True

if args.dir == None:
    logging.warning(f'no imgs specified. did you for get --files?')
    exit()
else:
    files = glob.glob(str(args.dir)+"*")
    dir = args.dir

output = "slides.pdf"
if args.output:
    output = args.output

text_formatting = True
if args.noformat:
    text_formatting = False

show_date = True
if args.nodate:
    show_date = False
   
show_title = False
if args.title:
    show_title = True
    string = args.title.split("|")
    title_text = string[0]
    subtitle_text = string[1]
    title_html = (f'<!DOCTYPE html>'
    '<head>'
    '<style>'
    '@page {'
    f'    size: {page_width}px {page_height}px;'
    f'    margin: {margin}px {margin}px {margin}px {margin}px;'
    '}'
    'div {'
    '     position: fixed;'
    '     top: 40%;'
    '     left: 50%;'
    '     transform: translate(-50%, -50%);'
    '}'
    'h1 {'
    '     font-size: 68pt;'
    '}'
    'h2 {'
    '     font-size: 28pt;'
    '}'
    '</style>'
    '</head>'
    '<html>'
    '  <body>'
    '     <div>'
    f'      <h1>{title_text}</h1>'
    f'      <h2>{subtitle_text}</h2>'
    '     </div'
    )

if args.headerposition in ["left", "right", "top", "bottom", "auto"]:
    header = args.headerposition
elif not args.headerposition: 
    header = "left"
else: 
    logging.warning(f'Invalid header position.')
    exit()

# Testing new html paradigm

imgCssLs = [
]

textCssLs = [
]

def makeCss(ls):
    string = ""
    for i in ls:
       string += (f"    {i}")
    return(string)

imgCss = makeCss(imgCssLs)
textCss = makeCss(textCssLs)

def floatLeft():
    global imgCssLs
    global textCssLs
    global imgCss
    global textCss

    imgCssLs = [
        f'float: right;'
    ]

    textCssLs = [
        f'float: left;'
    ]

    imgCss = makeCss(imgCssLs)
    textCss = makeCss(textCssLs)

def floatRight():
    global imgCssLs
    global textCssLs
    global imgCss
    global textCss

    imgCssLs = [
        f'float: left;'
    ]

    textCssLs = [
        f'float: right;'
    ]

    imgCss = makeCss(imgCssLs)
    textCss = makeCss(textCssLs)

def floatTop():
    global imgCssLs
    global textCssLs
    global imgCss
    global textCss

    imgCssLs = [
        f'margin: auto;',
        f'display: block;'
    ]

    textCssLs = [
        f'text-align: center;'
    ]

    imgCss = makeCss(imgCssLs)
    textCss = makeCss(textCssLs)

def floatBottom():
    logging.warning(f'bottom position not yet implemented. Falling back to top')
    floatTop()

if header == "left":
    floatLeft()
    
if header == "right":
    floatRight()

if header == "top":
    floatTop()
    
if header == "bottom":
    floatBottom()
    
if header == "auto":
    logging.warning(f'Auto position not yet implemented. Falling back to left')
    floatLeft()
    # see slide class def(heml) function.
    #pass

class slide:
    def __init__(self, file):
        self.file = str(dir) + str(file)
        string = str(file).split(".")
        self.id = string[0]
        self.date = string[1]
        self.name = string[2]
        self.format = string[3]
        if text_formatting:
            self.display_name = self.name.replace('_', ' ').replace('_slash_', '/').replace('_plus_', '+').title()
            self.display_date = self.date.replace('-', '/')
        else:
            self.display_name = self.name
            self.display_date = self.date
        if show_date == False:
            self.display_date=""
        self.page_name = str(self.date + "." + self.name)
        
    def html(self):
        #extra 4 px buffer makes the page setting happy. idk why
        img_height = 1080 - ((margin+4)*2)
        return(
f'<!DOCTYPE html>'
f'<head>'
f'<style>'
'@page {'
f'    size: {page_width}px {page_height}px;'
f'    margin: {margin}px {margin}px {margin}px {margin}px;'
'}'
'img {'
f'{imgCss}'
'}'
'.text {'
f'{textCss}'
'}'
f'</style>'
f'</head>'
f'<html>'
f'  <body>'
f'    <div class=text>'
f'      <h1>{self.display_name}</h1>'
f'      <h2>{self.display_date}</h2>'
f'    </div>'
f'    <img src="../{self.file}" width="auto" height="{img_height}px">'
)


def slide_sort_value(slide):
        return(str(slide.id) + str(slide.date))

    
cache_path = 'cache/' 
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
    pass
elif force == True:
    cache_files = glob.glob(f'{cache_path}*')
    for file in cache_files:
        os.remove(file)
else:
    logging.warning(f'Existing cache found. Aborting. Try removing cache/ or using --force')
    exit()

    
#2. validate image names

imgs = []

for f in files:
    string = (f.removeprefix(dir))
    pattern = re.compile("[0-9]{2}.[0-9]{2}-[0-9]{2}-[0-9]{4}.\w+.(?:jpg|gif|png|JPG)")
    if pattern.match(string):
        imgs.append(string)
    else:
        logging.info(f'Skipping {string}. Does not match namespace pattern ID.MM-DD-YYYY.NAME.FMT')

if imgs == []:
    logging.warning(f'No valid files found. Are your filenames ID.MM-DD-YYYY.NAME.FMT?')
    exit()

#3 create slide oject from each picture
slides = []
for i in imgs:
    foo = slide(i)
    slides.append(foo)
slides.sort(key=slide_sort_value)
    
#4 for each slide, generate HTML and render to file

#4.1 if theres a title make that

if show_title:
    logging.info(f'begining title slide')
    html_file = open(f'{cache_path}slide.html', "w+")
    html_file.write(title_html)
    html_file.close()
    html_path = str(os.path.abspath(f'{cache_path}slide.html'))
    converter.convert(f'file:///{html_path}', f'{cache_path}000-title.pdf', print_options={}, compress=True, power=2)



for s in slides:
    logging.info(f'begining {s.name}, slide number {s.id}')
    html_file = open(f'{cache_path}slide.html', "w+")
    html_file.write(s.html())
    html_file.close()
    html_path = str(os.path.abspath(f'{cache_path}slide.html'))
    converter.convert(f'file:///{html_path}', f'{cache_path}{slide_sort_value(s)}{s.page_name}.pdf', print_options={}, compress=True, power=2)


#5 unite pages
subprocess.run(f'pdfunite {cache_path}*.pdf {output}', shell=True)

#6 exit
if removeProcessFiles:
    cache_files = glob.glob(f'{cache_path}*')
    for file in cache_files:
        os.remove(file)
    os.rmdir(cache_path)
