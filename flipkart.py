from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time 
import bs4
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas
import hashlib, io, requests, pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from pathlib import Path
from PIL import Image
import concurrent.futures
import os
import random


"""iF YOU ARE OPENING OR RUNNNG THIS CODE AFTER A MONTH THIS CODE WILL NOT WORK BECAUSE WEBSITE WOULD HAVE UPDATE THERE TAGS"""


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
"""This part of the code will first go on google chrome search flipkart and then open flipkart and search mobile on it """
driver.get("https://www.google.com/")

search = driver.find_element(By.XPATH,("/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea"))
search.send_keys("flipkart")
search.send_keys(Keys.ENTER)
time.sleep(5)

link = driver.find_element(By.XPATH,("""/html/body/div[4]/div/div[12]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/span/a""")).click()
time.sleep(2)

input=driver.find_element(By.XPATH,"""/html/body/div[1]/div/div[1]/div/div/div/div/div[1]/div/div[1]/div/div[1]/div[1]/header/div[1]/div[2]/form/div/div/input""")
input.send_keys("mobile")
input.send_keys(Keys.ENTER)


def download_image(img_url, folder_path, phone_name):
    try:
        image_content = requests.get(img_url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert("RGB")
        random_number = random.randint(10000, 99999)
        image_name = f"{phone_name}_{random_number}.png"
        file_path = Path(folder_path, image_name)
        image.save(file_path, "PNG", quality=80)
        print(f"Downloaded: {file_path}")
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")

def scrap_image(images, phone_name):
    """Folder creation code"""
    random_number = random.randint(10000, 99999)
    directory_path = "/home/to23/Work/Learning/webscraping/image"
    folder_name = f"{phone_name}_{random_number}"
    folder_path = os.path.join(directory_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    """Download images concurrently"""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        """calling download_image """
        futures = [executor.submit(download_image, img.get('src'), folder_path, phone_name) for img in images]
        for future in concurrent.futures.as_completed(futures):
            try:
                _ = future.result()
            except Exception as e:
                print(f"Error in future {e}")

all_data = pandas.DataFrame(columns=['Name', 'Higlights', 'Description','Image','Url'])
def scrap_text_data():
    global all_data 
    """pagination and data extraction function where using for loop we are changing the page number &page="+str(i) so that after 
    every iterartion we can acces new page"""
    for i in range(1,3):
        url="https://www.flipkart.com/search?q=mobile&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="+str(i)

        driver.get(url)

        time.sleep(3) 

        response = driver.page_source   

        soup = bs4.BeautifulSoup(response,'html.parser')    
        boxes = soup.find_all('a',class_="CGtC98")

        list_of_names = []
        list_of_higlights = []
        list_of_description = []
        list_of_url = []
        list_of_img = []
        """Here Boxes contain all the box present on the page which we will access one by one using for loop"""
        for box in boxes:
            sub_link="https://www.flipkart.com"+str(box.get("href"))
            driver.get(sub_link)

            response = driver.page_source   
            """By this part of the code we are accessing data from the box"""
            soup = bs4.BeautifulSoup(response,'html.parser')    
            container = soup.find('div',class_="DOjaWF YJG4Cf")
            name = container.find('h1',class_="_6EBuvT")
            higlights = container.find('div',class_="xFVion")
            description = container.find('div',class_="yN+eNk w9jEaj")
            image_container = container.find('ul',class_="ZqtVYK")
            images = image_container.find_all('img') if image_container else []
            
            scrap_image(images,name.text)
            """If data is True then store dat else if none then store Na"""
            try:
                list_of_img.append(images)
            except AttributeError:
                list_of_img.append("Na")

            try:
                list_of_names.append(name.text)
            except AttributeError:
                list_of_names.append("Na")

            try:
                list_of_higlights.append(higlights.text )
            except AttributeError:
                list_of_higlights.append("Na")

            try:
                list_of_description.append(description.text)
            except AttributeError:
                list_of_description.append("Na")

            try:
                list_of_url.append(sub_link)
            except AttributeError:
                list_of_url.append("Na")
      
        """storing data in Excel format"""
        page_data = pandas.DataFrame({
            'Name': list_of_names,
            'Higlights': list_of_higlights,
            'Description': list_of_description,
            'Image': list_of_img,
            'Url': list_of_url
        })

        all_data = pandas.concat([page_data, all_data], ignore_index=True)
        print(all_data)
scrap_text_data()

driver.quit()

all_data.to_csv('flipkart_50000_all_pages.csv', index=False)





    

