#/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=5000

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
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:3000")
driver = webdriver.Chrome(options=chrome_options)

# Total number of pages
total_pages = 1655  # Adjust this value as per your requirement

# Base URL
base_url = "https://classie-evals.stonybrook.edu/?currentTerm=ALL&page="
base_url2 = "https://classie-evals.stonybrook.edu/?currentTerm=ALL&page=1"

columns = ["Section", "Course", "Instructor", "URL", "Overall Grade", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "P",
           "NC", "I", "W"]

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

    for page_number in range(1, total_pages + 144):
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

            try:
                course_title = tr.find_all('td')[1].text.strip()
            except:
                course_title = ""

            try:
                instructor = tr.find_all('td')[2].a.text.strip()
            except:
                instructor = ""

            # print(f"Section: {section}")
            # print(f"Course Title: {course_title}")
            # print(f"Instructor: {instructor}")

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
                scripts = soup_page.find_all('script')
                script1_content = scripts[9].string
                script2_content = scripts[10].string

                # Using regular expression to extract the grades and their counts
                pattern1 = re.compile(r"\['(.*?)', (\d+),")
                grades_list = pattern1.findall(script1_content)[0:15]
                grades = dict((name, int(grade)) for name, grade in grades_list)

                # Using regular expression to extract the overall grade with 1 response
                pattern2 = re.compile(r"\['(.*?)', (\d+),")

                try:
                    overall_grade_with_1 = pattern2.findall(script2_content)[0:5]
                    overall_grade_with_1 = max(overall_grade_with_1, key=lambda x: int(x[1]))
                except:
                    overall_grade_with_1 = ""

                row_data = {
                    "Section": section,
                    "Course": course_title,
                    "Instructor": instructor,
                    "URL": driver.current_url,
                    "Overall Grade": overall_grade_with_1
                }

                for grade in columns[5:]:
                    row_data[grade] = grades.get(grade, 0)
                if (has_non_zero_grade(grades)):
                    data.loc[len(data)] = row_data
            except:
                pass

    # Close the browser
    driver.quit()
    data.to_excel(excel_file_path, index=False, engine='openpyxl')
except Exception as e:
    print(e)
    driver.quit()
    data.to_excel(excel_file_path, index=False, engine='openpyxl')
