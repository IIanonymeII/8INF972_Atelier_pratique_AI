# -*- coding: utf-8 -*-

import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

month_mapping = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

def write_csv(data, filename):
    """Writes a list of data to a CSV file.

    Args:
      data: A list of lists or tuples.
      filename: The name of the CSV file to write to.
    """

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)


def create_driver():
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.set_preference("javascript.enabled", False)
    driver = webdriver.Firefox(executable_path='geckodriver.exe', options=firefox_options)
    return driver

def scrape_year(driver, year, nbMovies = 200):
    url = "https://www.the-numbers.com/market/" + str(year) + "/top-grossing-movies"
    
    driver.get(url)
    data = []

    # Find all tables in the webpage
    tables = driver.find_elements(By.TAG_NAME, "table")
    for table in tables:
        # Find all rows in the table
        rows = table.find_elements(By.TAG_NAME, "tr")
        rows = rows[1:nbMovies + 1]
        for row in rows:
            current = []
            # Find all columns in the row
            cols = row.find_elements(By.TAG_NAME, "td")

            if cols:
                link = cols[1].find_element(By.CSS_SELECTOR, "a[href]")
                
                if link:
                    title = link.text
                    current.append(title)
                    href = link.get_attribute("href")
                    movie_url = href
                    result = getMovieInfo(movie_url)
                    current = current + result
                    data.append(current)
    
    write_csv(data, "movies.csv")
    return data

def extractNumberFromDollar(priceStr):
    priceInt = re.sub(r'\D', '', priceStr)
    return int(priceInt)

def getMovieInfo(url):
    driver = create_driver()
    driver.get(url)
    result = []
    
    list_h2 = driver.find_elements(By.TAG_NAME, "h2")
    for h2 in list_h2:
        if h2.text == "Metrics":
            table = h2.find_element(By.XPATH , "./following-sibling::table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    col1 = cols[0].find_element(By.TAG_NAME, "b").text
                    col2 = cols[1].text
 
                    if col1 == "Production Budget:":
                        priceStr = re.search(r'\$[\d,]+', col2)
                        if priceStr:
                            extracted_value = priceStr.group(0)
                            extracted_value = extractNumberFromDollar(extracted_value)
                        else:
                            extracted_value = None
                        result.append(extracted_value)
                    if col1 == "Infl. Adj. Dom. BO":
                        result.append(extractNumberFromDollar(col2))
            
        elif (h2.text == "Movie Details"):
            table = h2.find_element(By.XPATH , "./following-sibling::table")
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    header = cols[0].text
                    col2 = cols[1]
    
                    if header in ("MPAA Rating:", "Genre:", "Source:", "Production Method:",
                                  "Creative Type:",):
                        result.append(col2.find_element(By.TAG_NAME, "a").text)
                    elif header in ("Keywords:", "Production/Financing Companies:", 
                                    "Production Countries:", "Languages:"):
                        words = col2.find_elements(By.TAG_NAME, "a")
                        word_list = []
                        for word in words:
                            word_list.append(word.text)
                        result.append(word_list)
                    elif header == "Running Time:":
                        runningTime = re.search(r'[\d]+', col2.text)
                        if priceStr:
                            runningTime = runningTime.group(0)
                        else:
                            runningTime = None
                        result.append(runningTime)
                    elif header == "Domestic Releases:":
                        date_pattern = r"(\w+ \d{1,2}(?:st|nd|rd|th), \d{4})"
                        
                        # Search for the first date in the text
                        match = re.search(date_pattern, col2.text)
                        
                        if match:
                            first_date = match.group(0)
                            split_result = first_date.split()
                            numeric_month = month_mapping[split_result[0]]
                            numeric_year = split_result[-1]
                        else:
                            numeric_month = None
                            numeric_year = None
                        result.append(numeric_year)
                        result.append(numeric_month)
            driver.quit()
            return result

driver = create_driver()
for year in reversed(range(2020, 2024, 1)):
    scrape_year(driver, year, 1)
driver.quit()