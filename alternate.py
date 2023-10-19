from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
from selenium.webdriver.common.by import By
import pandas as pd

bool = True

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:5000")
driver = webdriver.Chrome(options=chrome_options)

# Total number of pages
total_pages = 1655  # Adjust this value as per your requirement

# Base URL
base_url = "https://classie-evals.stonybrook.edu/?currentTerm=ALL&page="
base_url2 = "https://classie-evals.stonybrook.edu/?currentTerm=ALL&page=103"

columns = ["Section", "Good Comments","Bad Comments", "URL"]

excel_file_path = "classie_evals_data.xlsx"

def has_non_zero_grade(grades):
    for grade in columns[5:]:
        if int(grades[grade]) != 0:
            return True
    return False

try:

    try:
        # Read the existing Excel file
        data = pd.read_excel(excel_file_path, engine='openpyxl')

    except:
        # If the file does not exist, create a new DataFrame with columns
        data = pd.DataFrame(columns=columns)

    driver.get(base_url2)

    for page_number in range(103, 500):
        print(f"Page Number: {page_number}")
        print("___________________")
        # Navigate to the webpage
        section_link = base_url + str(page_number)

        # Fetching the content of the new page with AJAX
        js_script = f'''
            var callback = arguments[arguments.length - 1];
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '{section_link}', true);
            xhr.onreadystatechange = function() {{
                if (xhr.readyState == 4 && xhr.status == 200) {{
                    callback(xhr.responseText);
                }}
            }};
            xhr.send();
            '''

        page_content = driver.execute_async_script(js_script)

        soup = BeautifulSoup(page_content, 'html.parser')

        # Finding the tbody tag
        tbody = soup.find('tbody')

        # Iterating through each tr tag inside tbody
        try:
            trs = tbody.find_all('tr')
        except:
            input_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main-form-inputs"]/div[5]/button'))
            )
            input_field.click()
            sleep(5)
            trs = tbody.find_all('tr')

        for tr in trs:
            # Extracting section, course title, and instructor name
            try:
                section = tr.find_all('td')[0].a.text.strip()
            except:
                section = ""

            # Extracting the link and use AJAX to get the HTML of the linked page
            section_link = tr.find_all('td')[0].a['href']
            section_link = f"https://classie-evals.stonybrook.edu/{section_link}"  # Replace example.com with the actual domain

            # Fetching the content of the new page with AJAX
            js_script = f'''
                var callback = arguments[arguments.length - 1];
                var xhr = new XMLHttpRequest();
                xhr.open('GET', '{section_link}', true);
                xhr.onreadystatechange = function() {{
                    if (xhr.readyState == 4 && xhr.status == 200) {{
                        callback(xhr.responseText);
                    }}
                }};
                xhr.send();
                '''

            try:
                page_content = driver.execute_async_script(js_script)
                soup_page = BeautifulSoup(page_content, 'html.parser')

                ul_tag = soup_page.find('ul', id='paginate-1')
                ul_tag2 = soup_page.find('ul', id='paginate-2')

                # Extract all li elements from both ul tags
                li_tags1 = ul_tag.find_all('li') if ul_tag else []
                li_tags2 = ul_tag2.find_all('li') if ul_tag2 else []

                # Extract the text from li elements and store it in arrays
                GoodComments = [li.text.strip() for li in li_tags1]
                BadComments = [li.text.strip() for li in li_tags2]

                # print(GoodComments)
                # print(BadComments)
                # print("\n")

                row_data = {
                    "Section": section,
                    "Good Comments": GoodComments,
                    "Bad Comments": BadComments,
                    "URL":section_link
                }

                data.loc[len(data)] = row_data

            except:
                pass

except Exception as e:
    print(e)
    driver.quit()
    data.to_excel(excel_file_path, index=False, engine='openpyxl')

# Close the browser
driver.quit()
data.to_excel(excel_file_path, index=False, engine='openpyxl')
