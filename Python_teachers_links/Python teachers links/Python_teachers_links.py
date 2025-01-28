import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build


AIESEC_URL = 'https://aiesec.org/search?earliest_start_date=2025-01-28&programmes=9&home_mcs=1559'

SHEET_ID = '11PNSM5_VD-heLjQwCqRsY9BpTMI41AupNeXrTMSduuo'
RANGE_NAME = 'Tunisia!O2:O'  

def scrape_links():
    links = []

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(AIESEC_URL)

    time.sleep(5) 

    
    try:
       
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ant-modal-content"))
        )
        print("Cookies modal found.")

       
        accept_cookies_button = modal.find_element(By.CLASS_NAME, 'ant-btn-primary')
        accept_cookies_button.click()
        print("Accepted cookies.")
    except Exception as e:
        print("No cookie prompt appeared or there was an issue clicking:", e)

       
    def click_load_more():
        try:
           
            load_more_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex"))
            )


            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_area)
            time.sleep(2) 

           
            load_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'ant-btn ant-btn-primary') and contains(., 'Load more')]")

            if load_more_button.is_displayed() and load_more_button.is_enabled():
               
                driver.execute_script("arguments[0].click();", load_more_button)
                print("Clicked 'Load More' button.")
                time.sleep(10)  
                return True  
            else:
                print("Load More button is not displayed or enabled.")
                return False  
        except Exception as e:
            print("Error while trying to click 'Load More':", e)
            return False  

    while click_load_more():
        pass  

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()  
  
    opportunity_tags = soup.find_all('a', href=True)
    
    for tag in opportunity_tags:
        href = tag['href']
        if 'opportunity' in href:  
            links.append(f"https://aiesec.org{href}")

    links = list(set(links))  
    print(f'Total links collected: {len(links)}')  
    return links


def update_google_sheet(links):
    
    creds = service_account.Credentials.from_service_account_file(
        r'C:\Users\genge\OneDrive\Desktop\teacher_cridentials\teacher-links-c9f906293ad0.json', 
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )

    service = build('sheets', 'v4', credentials=creds)
    
    values = [[link] for link in links]  

   
    body = {
        'values': values
    }

    try:
       
        service.spreadsheets().values().clear(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()

        
        result = service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f'{result.get("updatedCells")} cells updated.')
    except Exception as e:
        print(f'An error occurred: {e}')


def main():
    
    links = scrape_links()
    
    
    if links:
        update_google_sheet(links)
    else:
        print('No links found to import.')

if __name__ == '__main__':
    main()

  
