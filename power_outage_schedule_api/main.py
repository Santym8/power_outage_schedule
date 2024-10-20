from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PowerOutgeTime(BaseModel):
    start_time_utc: str
    end_time_utc: str

def extract_data(html: str) -> list[PowerOutgeTime]:
    soup = BeautifulSoup(html, 'lxml')
    
    table_body = soup.find('tbody', {'id': 'j_idt9:j_idt71:0:j_idt77_data'})
    
    result = []
    date_data = None
    
    # Timezone info (assuming it's Ecuador timezone UTC-5)
    local_timezone = pytz.timezone('America/Guayaquil')
    utc_timezone = pytz.UTC
    
    for row in table_body.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) == 3:
            date_data = columns[0].find('label').text.strip()
            start_time = columns[1].find('label').text.strip()
            end_time = columns[2].find('label').text.strip()
        else:
            start_time = columns[0].find('label').text.strip()
            end_time = columns[1].find('label').text.strip()
        
        # Combine date and time
        start_datetime_str = f"{date_data} {start_time}"
        end_datetime_str = f"{date_data} {end_time}"
        
        # Parse the datetime strings
        start_datetime = datetime.strptime(start_datetime_str, '%d/%m/%Y %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime_str, '%d/%m/%Y %H:%M:%S')
        
        # Localize to the local timezone and convert to UTC
        start_datetime_local = local_timezone.localize(start_datetime)
        end_datetime_local = local_timezone.localize(end_datetime)
        
        start_time_utc = start_datetime_local.astimezone(utc_timezone).isoformat()
        end_time_utc = end_datetime_local.astimezone(utc_timezone).isoformat()
        
        result.append(
            PowerOutgeTime(
                start_time_utc=start_time_utc,
                end_time_utc=end_time_utc
            )
        )
    
    return result

@app.get("/get_power_outage/{text_input}")
async def submit_form(text_input: str) -> list[PowerOutgeTime]:
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        driver.get("https://www3.emelnorte.com/ConsultaCuentaContrato/suspension.xhtml")

        # Input the data
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'j_idt9:identif')))
        input_field = driver.find_element(By.ID, 'j_idt9:identif')
        input_field.send_keys(text_input)

        # Submit the form
        submit_button = driver.find_element(By.NAME, 'j_idt9:j_idt64')
        submit_button.click()
        
        # Wait for the response
        time.sleep(5)

        # Get the response
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        response_element = driver.find_element(By.TAG_NAME, 'body')
        response_html = response_element.get_attribute('innerHTML')
        driver.quit()
        
        return extract_data(response_html)

    except Exception as e:
        print(e)
        if driver:
            driver.quit()
        raise HTTPException(status_code=500, detail=str(e))
