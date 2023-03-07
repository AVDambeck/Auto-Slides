#!python
"""00. this is a program which inputs a set of images with a specific naming format, and outputs a pdf containing a slide show of the images with titles;
0.  the specific name format is ##.mm-dd-yyyy.name_of_image.jpg7;
1. import and define;
2. validate image names;
3. create a slide object from each picture, including the extracted name, date, and file location;
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

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose",  action='store_true', help="Increase verbosity.")
parser.add_argument("-f", "--force",  action='store_true', help="Overide exiting cache.")
parser.add_argument("-d", "--dir", help="Directory to load files from.")
parser.add_argument("-o", "--output", help="Specify output file.")
args = parser.parse_args()


if args.verbose == True:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
else:
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

force = False
if args.force:
    force = True

if args.dir == None:
    logging.warning(f'no imgs specified. did you for get --files?')
    exit()
else:
    files = glob.glob(str(args.dir)+"*")
    dir = args.dir

if args.output == None:
    output = "slides.pdf"
else:
    output = args.output
    
class slide:
    def __init__(self, file):
        self.file = str(dir) + str(file)
        string = str(file).split(".")
        self.id_number = string[0]
        self.date = string[1]
        self.name = string[2]
        self.format = string[3]
        self.page_name = str(self.date + "." + self.name)
        
    def html(self):
        margin = 50
        #extra 4 px buffer makes the page setting happy. idk why
        img_height = 1080 - ((margin+4)*2)
        return(
f'<!DOCTYPE html>'
f'<head>'
f'<style>'
'@page {'
'    size: 1920px 1080px;'
f'    margin: {margin}px {margin}px {margin}px {margin}px;'
'}'
'img {'
'    float: right;'
'}'
'.text {'
'    float: left'
'}'
f'</style>'
f'</head>'
f'<html>'
f'  <body>'
f'    <div class=text>'
f'      <h1>{self.name}</h1>'
f'      <h2>{self.date}</h2>'
f'    </div>'
f'    <img src="../{self.file}" width="auto" height="{img_height}px">'
)

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

if imgs == []:
    logging.warning(f'No valid files found. Are your filenames MM-DD-YYYY.NAME.FMT?')
    exit()

#3 create slide oject from each picture
slides = []
for i in imgs:
    foo = slide(i)
    slides.append(foo)
    
#4 for each slide, generate HTML and render to file
for s in slides:
    logging.info(f'begining {s.name}, slide number {self.id_number}')
    html_file = open(f'{cache_path}slide.html', "w+")
    html_file.write(s.html())
    html_file.close()
    html_path = str(os.path.abspath(f'{cache_path}slide.html'))
    converter.convert(f'file:///{html_path}', f'{cache_path}{s.page_name}.pdf', print_options={})


#5 unite pages
subprocess.run(f'pdfunite {cache_path}*.pdf {output}', shell=True)

#6 exit
cache_files = glob.glob(f'{cache_path}*')
for file in cache_files:
    os.remove(file)
os.rmdir(cache_path)
