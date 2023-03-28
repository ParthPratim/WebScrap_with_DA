import time, os, argparse,sys, csv, re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import bs4
import numpy as np
from selenium.webdriver.chrome.options import Options


chrome_options = None
homedir = os.path.expanduser("~")
webdriver_service = Service("./chromedriver/stable/chromedriver")
DOM_stack = []

def initial_setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")

def browser_setup():
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    return browser

def open_page(browser,url):
    browser.get(url)


"""
Important features in the model:
1. Text size
2. Text color
3. Text bold 
4. Text italisize
5. Text underline
6. Actual contained text
"""

parser = argparse.ArgumentParser("dataset_generator")
parser.add_argument("--url", dest="url", help="URL to Scrapp", nargs='?' , type=str,
                    default="http://wikipedia.org")
parser.add_argument("--main-class", dest="main_class",  nargs='?' ,help="class name of the main content section", type=str, default=None)
parser.add_argument("--main-id", dest="main_id", nargs='?', help="id name of the main content section", type=str, default=None)
parser.add_argument("--tag", dest="tag", help="what should the cell be tagged with", type=str, default=None)
args = parser.parse_args()

if args.main_class == None and args.main_id == None:
    print("Specify atleast one of class or id")
    sys.exit(1)

initial_setup_selenium()

browser = browser_setup()

open_page(browser,args.url)

print("Waiting for 10 secons for the page to get loaded...")
time.sleep(7)
print("Page is assumed to have been loaded now...")

if args.main_class:
    main_section = browser.find_element(By.CLASS_NAME, args.main_class)
else: 
    main_section = browser.find_element(By.ID, args.main_id)


html_content = main_section.get_attribute('innerHTML')
html_bs4 = bs4.BeautifulSoup(html_content,features="lxml")
DOM_stack.extend(html_bs4.findChildren(recursive=True))

DUMP_DATA = []

for element in DOM_stack:
    text = element.find_all(text = True, recursive = False)
    if len(text) == 0:
        continue
        
    combined = ' '.join([a.strip() for a in text])
    combined = combined.strip()
    if len(combined) == 0 or any(chr.isdigit() for chr in combined) or not combined.isascii() or len(combined) < 5:
        continue
    classes = []
    if 'class' in element.attrs:
        classes = element.attrs['class']
    try:
        lx = None
        if len(classes) != 0:
            class_names = ' '.join(classes)
            lx = browser.find_element(By.XPATH, "//%s[@class='%s']" % (element.name ,class_names))
        else:
            lx = browser.find_element(By.TAG_NAME, element.name)
        
        f_size = lx.value_of_css_property("font-size")[:-2]
        f_color_r , f_color_g, f_color_b, f_color_a  = (color.strip() for color in lx.value_of_css_property("color")[5:-1].split(',') )
        f_weight = lx.value_of_css_property("font-weight")
        if len(f_weight) == 0:
            f_weight = "normal"
        combined = re.sub("/^[A-Z ]*$/", "", combined,0,re.IGNORECASE)
        DUMP_DATA.append([combined, f_size, f_color_r , f_color_g, f_color_b, f_color_a , f_weight,args.tag])

    except:
        pass


#DUMP_DATA = np.unique(DUMP_DATA)
with open('scrap_dataset.csv','a', newline='') as dfile:
    writer = csv.writer(dfile)

    #writer.writerow(["text","font_size","font_color_red" , "font_color_green", "font_color_blue", "font_color_alpha" ,"font_weight","output"])
    writer.writerows(DUMP_DATA)


browser.quit()