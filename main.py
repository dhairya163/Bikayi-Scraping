# import requests
print('new')
from selenium import webdriver

##
import sys
import time
import warnings
warnings.filterwarnings("ignore")
##

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
header = {"authorization": "MzM2Mjc3OTM0NTcyNTY4NTc4.X3EwXw.OF4fUdtM0PZM5uImuAqd5JVYAy8"}

options = webdriver.ChromeOptions()
# options.headless = True
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--window-size=1920,1080")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

def scroll_to_bottom(driver):

    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(1)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))

originurl = input("Enter categorical url to scrape: ")
driver.get(originurl)
time.sleep(5)
scroll_to_bottom(driver)
time.sleep(5)


products = driver.find_elements_by_xpath('//*[@class="px-0 item"]')

ids = []

for product in products:
  ids.append(product.get_attribute("id"))

tempnames = driver.find_elements_by_xpath('//*[@class="item__details-description"]')

names = []
for i in tempnames:
  names.append(i.text)

if len(ids)==len(names):
  print("import sucess")


print("Number of products available are - " + str(len(names)))
start = input("Enter starting range to scrape (it starts with zero) ")
end = input("Enter ending range to scrape (it can be maximum number of products) ")

if(int(end) > len(names)):
  print("You entered more number of products than available...")
  sys.exit(50)

urls = []

import re
for i in range(int(start),int(end)):
  url = originurl + "/"
  regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
  splitnames = names[i].split()
  counter = 0
  for j in splitnames:
    if(regex.search(j) == None):
      if counter == 0:
        url = url + j
        counter=1
      else:
        url = url + "-" + j
  url = url+"_"+str(ids[i])

  urls.append(url)

print(urls)


title = []
description = []
price = []
imgurl = [[]]
varname = []
varvalue = []

########################################################
countscaping = int(start)
for url in urls:
  driver.get(url)
  time.sleep(4)
  # scroll_to_bottom(driver)
  time.sleep(12)
  try:
    title.append(driver.find_element_by_xpath('//*[@class="name"]').text)
  except:
    title.append("")
  description.append(driver.find_element_by_xpath('//*[@class="sub-block__body product-description"]').text)
  try:
    price.append(driver.find_element_by_xpath('//*[@class="price align-baseline"]').text)
  except:
    price.append(driver.find_element_by_xpath('//*[@class="align-baseline price"]').text)    
  try:
    tempimgurl = []
    photoblock = driver.find_element_by_xpath('//*[@id="photoBlock"]')
    tempimgs = photoblock.find_elements_by_tag_name("img")
    for tempimg in tempimgs:
      tempimgurl.append(tempimg.get_attribute("src"))
    imgurl.append(tempimgurl)
  except:
    tempimgurl = []
    imgurl.append(tempimgurl)
    print("failed to get image for this product - " + str(url))
  try:
    tempvarname = driver.find_element_by_xpath('//div[@class="header d-flex"]').text
    varname.append(tempvarname)
  except:
    print("no variation found for this product")
    varname.append("")
    varvalue.append("")
    print("Product {} scraped successfully".format(str(countscaping)))
    countscaping = countscaping + 1
    continue
  try:
    tempvarvaluess = driver.find_elements_by_xpath('//div[@class="input-dropdown d-flex"]')
    tempvarvaluess[0].click()
    time.sleep(1)
    tempvarvalues = driver.find_elements_by_xpath('//li//div//div[@class="my-auto"]')
    ttvarvalue = ""
    countervalue = 0
    for tempvarvalue in tempvarvalues:
      if(countervalue == 0):
        ttvarvalue = ttvarvalue + tempvarvalue.text
      else:
        ttvarvalue = ttvarvalue + "|" + tempvarvalue.text
      countervalue = countervalue + 1
    varvalue.append(ttvarvalue)
  except:
    time.sleep(1)
    ttvarvalue = driver.find_element_by_xpath('//span[@class="m-auto"]').text
    varvalue.append(ttvarvalue)
  print("Product {} scraped successfully".format(str(countscaping)))
  countscaping = countscaping + 1
  time.sleep(1)
###########################################################

import urllib.request
import os
import uuid
import cloudinary.uploader
from PIL import Image

cloudinary.config( 
  cloud_name = "dhairya", 
  api_key = "946911894239634", 
  api_secret = "SoMeM_G8C0gbDZ1-U5-JDWDrhtY" 
)

finalimgurls = []

for j in range(1,len(imgurl)):
  finalimgurl = ""
  for i in range(len(imgurl[j])):
    filename =  str(uuid.uuid4().hex) + ".jpg"
    urllib.request.urlretrieve(imgurl[j][i],filename)
    im = Image.open(filename)

    rgb_im = im.convert("RGB")

    rgb_im.save(filename)

    xd = cloudinary.uploader.upload(filename)
    if(i == 0):
      finalimgurl = finalimgurl + xd['url']
    else:
      finalimgurl = finalimgurl + "," + xd['url']
    os.remove(filename)
  finalimgurls.append(finalimgurl)



import pandas as pd

args = [title,price,description,finalimgurls,varname,varvalue]

df = pd.DataFrame(args)

df= df.T
df.columns = ["title","price","description","finalimgurls","varname","varvalues"]


df.to_csv("final.csv")
print(df)
print("Scraping done successfully")