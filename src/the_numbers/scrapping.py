# -*- coding: utf-8 -*-

import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
import cpi

def extractNumberFromDollar(priceStr):
    priceInt = re.sub(r'\D', '', priceStr)
    return int(priceInt)

def create_driver():
    firefox_options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=firefox_options)
    return driver

def waitForOneElement(driver, by, name):
    try:
        return WebDriverWait(driver, 5, ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((by, name)))
    except TimeoutException:
        return None
    

def waitForMultipleElements(driver, by, name):
    try:
        return WebDriverWait(driver, 3, ignored_exceptions=ignored_exceptions)\
            .until(EC.presence_of_all_elements_located((by, name)))
    except TimeoutException:
        return []

def getInflationRate(year):
    return cpi_current / cpi.get(year)

def adjustToInflation(amount, year):
    return round(amount * getInflationRate(year))

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

def scrape_year(driver, year, nbMovies = 200):
    url = "https://www.the-numbers.com/market/" + str(year) + "/top-grossing-movies"
    driver.get(url)
    data = []
    table = waitForOneElement(driver, By.TAG_NAME, "table")
    rows = waitForMultipleElements(table, By.TAG_NAME, "tr")
    nbMovies = min(nbMovies, len(rows) - 2)
    rows = rows[1:nbMovies]
    for row in rows:
        current = [None] * ARRAY_SIZE
        # Find all columns in the row
        cols = waitForMultipleElements(row, By.TAG_NAME, "td")
        if cols:
            link = waitForOneElement(cols[1], By.CSS_SELECTOR, "a[href]")
            if link:
                movie_url = link.get_attribute("href")
                current = getMovieInfo(driver, movie_url, year, current)
                if current != None:
                    data.append(current)
    
    write_csv(data, "movies" + str(year) + ".csv")
    return data


def getMovieInfo(driver, url, year, data):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1]) 
    driver.get(url)
    data[TITLE_POS] = getTitle(driver)
    if data[TITLE_POS] == None:
        return None
    data = getPerformance(driver, data, year)
    list_h2 = waitForMultipleElements(driver, By.TAG_NAME, "h2")
    for h2 in list_h2:
        match h2.text:
            case "Metrics":
                data = getBudget(driver, data[TITLE_POS], h2, year, data)
            case "Movie Details":
                table = waitForOneElement(h2, By.XPATH , "./following-sibling::table")
                rows = waitForMultipleElements(table, By.TAG_NAME, "tr")
                for row in rows:
                    cols = waitForMultipleElements(row, By.TAG_NAME, "td")
                    if cols:
                        header = cols[0].text
                        col2 = cols[1]
                        match header:
                            case "MPAA Rating:" | "Genre:" | "Source:" | "Production Method:" \
                                      | "Creative Type:":
                                data[pos_mapping_1[header]] = waitForOneElement(col2, By.TAG_NAME, "a").text
                            case "Keywords:" | "Production/Financing Companies:" \
                                        | "Production Countries:" | "Languages:":
                                words = waitForMultipleElements(col2, By.TAG_NAME, "a")
                                word_list = []
                                for word in words:
                                    word_list.append(word.text)
                                data[pos_mapping_2[header]] = word_list
                            case "Running Time:":
                                runningTime = re.search(r'[\d]+', col2.text)
                                if runningTime:
                                    runningTime = runningTime.group(0)
                                    data[DURATION_POS] = runningTime
                            case "Domestic Releases:":
                                date_pattern = r"(\w+ \d{1,2}(?:st|nd|rd|th), \d{4})"
                                
                                # Search for the first date in the text
                                match = re.search(date_pattern, col2.text)
                                
                                if match:
                                    first_date = match.group(0)
                                    split_result = first_date.split()
                                    numeric_month = month_mapping[split_result[0]]
                                    numeric_year = split_result[-1]
                                    if numeric_year != str(year):
                                        driver.close()
                                        driver.switch_to.window(driver.window_handles[-1])
                                        return None
                                    data[YEAR_RELEASE_POS] = numeric_year
                                    data[MONTH_RELEASE_POS] = numeric_month
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])
    return data

def getTitle(driver):
    main = waitForOneElement(driver, By.ID, "main")
    if main == None:
        return None
    list_h1 = waitForMultipleElements(main, By.TAG_NAME, "h1")
    h1 = list_h1[0]
    return h1.text.rsplit(' ', 1)[0]

def getPerformance(driver, data, year):
    table = waitForOneElement(driver, By.ID, "movie_finances")
    rows = waitForMultipleElements(table, By.TAG_NAME, "tr")
    for row in rows:
        cols = waitForMultipleElements(row, By.TAG_NAME, "td")
        if cols and (len(cols) > 1):
            col1 = cols[0].text
            col2 = cols[1].text
            match col1:
                case "Domestic Box Office":
                    if (col2 == "n/a"):
                        data[BOXOFFICE_DOMESTIC_ORIGINAL_POS] = 0
                        data[BOXOFFICE_DOMESTIC_ADJUSTED_POS] = 0
                    else:
                        box_office = int(extractNumberFromDollar(col2))
                        adjusted_box_office = adjustToInflation(box_office, year)
                        data[BOXOFFICE_DOMESTIC_ORIGINAL_POS] = box_office
                        data[BOXOFFICE_DOMESTIC_ADJUSTED_POS] = adjusted_box_office
                case "International Box Office":
                    if (col2 == "n/a"):
                        data[BOXOFFICE_INTERNATIONAL_ORIGINAL_POS] = 0
                        data[BOXOFFICE_INTERNATIONAL_ADJUSTED_POS] = 0
                    else:
                        box_office = int(extractNumberFromDollar(col2))
                        adjusted_box_office = adjustToInflation(box_office, year)
                        data[BOXOFFICE_INTERNATIONAL_ORIGINAL_POS] = box_office
                        data[BOXOFFICE_INTERNATIONAL_ADJUSTED_POS] = adjusted_box_office
    return data

def findMovie(driver, year, title):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1]) 
    # Search for movie
    driver.get("https://en.wikipedia.org/wiki/Main_Page")
    
    success = False
    attempts = 0;
    while((attempts < 4) and (success == False) ):
        try:
            form = waitForOneElement(driver, By.ID, "searchform")
            searchInput = waitForMultipleElements(form, By.TAG_NAME, "input")[0]
            if (attempts > 0):
                searchInput.send_keys(Keys.CONTROL + "a")
                searchInput.send_keys(Keys.DELETE)
                time.sleep(1)
            searchInput.send_keys(title + " " + str(year) +" film ")
            searchInput.submit()
            
            success = True;
            break;
        except StaleElementReferenceException:
            time.sleep(2)
            attempts += 1
        
    return success

def scrapWikipedia(title, year, data, driver):
    success = findMovie(driver, year, title)
    if not success:
        print(f"wikipedia: {title} not found")
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        return data
    
    # Get movie page
    waitForMultipleElements(driver, By.CLASS_NAME, "searchresults")
    pageTitle = waitForOneElement(driver, By.ID, "firstHeading").text
    if pageTitle.strip() == "Search results":
        results = waitForMultipleElements(driver, By.CLASS_NAME, "mw-search-result-heading")
        if len(results) == 0:
            print(f"wikipedia: {title}: No results for search")
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            return data
        link = waitForMultipleElements(results[0], By.CSS_SELECTOR, "a[href]")[0]
        driver.get(link.get_attribute("href"))
    table = waitForMultipleElements(driver, By.CLASS_NAME, "infobox")
    if len(table) == 0:
        print(f"wikipedia: {title} not found (no table on right)")
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
        return data
    rows = waitForMultipleElements(table[0], By.TAG_NAME, "tr")
    budget = None
    for row in rows:
        col = waitForMultipleElements(row, By.TAG_NAME, "th")
        if len(col) > 0:
            col = col[0]
            content = col.text
            if content == "Budget":
                contentTDOriginal = waitForOneElement(row, By.TAG_NAME, "td").text
                pattern = r'\[.*?\]'
                contentTD = re.sub(pattern, '', contentTDOriginal).replace("$", "")
                budget = None
                if (contentTD.find("million") != -1):
                    pattern = r'\d+(?:[,.]\d{0,4})? million'
                    matches = re.search(pattern, contentTD)
                    if matches:
                        matched_text = matches.group()
                        cleaned_text = matched_text.replace(" million", "")
                        array = cleaned_text.split()
                        if len(array) > 1:
                            cleaned_text = array[-1]
                        else:
                            cleaned_text = array[0]
                        # Convert the cleaned text to a float and multiply it by 1,000,000
                        try:
                            budget = round(float(cleaned_text) * 1000000)
                        except ValueError:
                            print(f"Error for conversion of price ({cleaned_text}) for {title} ({year})")
                            budget = None
                        
                    else:
                        if(contentTD.find("–")):
                            budget = contentTD.split("–")[-1].split()[0]
                            try:
                                budget = round(float(budget) * 1000000)
                            except ValueError:
                                print(f"Error for conversion of price ({budget}) for {title} ({year})")
                                budget = None
                        elif(contentTD.find("-")):
                            budget = contentTD.split("-")[-1].split()[0]
                            try:
                                budget = round(float(budget) * 1000000)
                            except ValueError:
                                print(f"Error for conversion of price ({budget}) for {title} ({year})")
                                budget = None
                            
                else:
                    filtered_text = ''.join(re.findall(r'[\d\s]+', contentTD))
                    array = filtered_text.split()
                    if len(array) != 0:
                        if len(array) > 1:
                            cleaned_text = array[-1]
                        else:
                            cleaned_text = array[0]
                        budget = int(cleaned_text)
                # print(f"wikipedia: {title} (({year})) Budget in div: {contentTDOriginal}; Extracted: {budget}")
    data[BUDGET_ORIGINAL_POS] = budget
    if budget == None:
        adjusted_budget = None
    else:
        adjusted_budget = adjustToInflation(budget, year)
    data[BUDGET_AJUSTED_POS] = adjusted_budget
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])
    return data

def getBudget(driver, title, h2, year, data):
    table = waitForOneElement(h2, By.XPATH , "./following-sibling::table")
    rows = waitForMultipleElements(table, By.TAG_NAME, "tr")
    for row in rows:
        cols = waitForMultipleElements(row, By.TAG_NAME, "td")
        if cols:
            col1 = cols[0].text
            col2 = cols[1].text
            
            if col1 == "Production Budget:":
                priceStr = re.search(r'\$[\d,]+', col2)
                if priceStr:
                    budget = priceStr.group(0)
                    budget = int(extractNumberFromDollar(budget))
                    adjusted_budget = adjustToInflation(budget, year)
                    data[BUDGET_ORIGINAL_POS] = budget
                    data[BUDGET_AJUSTED_POS] = adjusted_budget
    if data[BUDGET_ORIGINAL_POS] == None:
        data = scrapWikipedia(title, year, data, driver)
        
    return data

month_mapping = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}
ARRAY_SIZE = 19
TITLE_POS = 0
YEAR_RELEASE_POS = 1
MONTH_RELEASE_POS = 2
PUBLIC_POS = 3
BOXOFFICE_DOMESTIC_ORIGINAL_POS = 4
BOXOFFICE_INTERNATIONAL_ORIGINAL_POS = 5
BOXOFFICE_DOMESTIC_ADJUSTED_POS = 6
BOXOFFICE_INTERNATIONAL_ADJUSTED_POS = 7
BUDGET_ORIGINAL_POS = 8
BUDGET_AJUSTED_POS = 9
DURATION_POS = 10
KEYWORDS_POS = 11
SOURCE_POS = 12
GENRE_POS = 13
PROD_METH_POS = 14
CREATIVE_TYPE_POS = 15
STUDIOS_POS = 16
COUNTRIES_POS = 17
LANGUAGES_POS = 18

ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

pos_mapping_1 = {
    'MPAA Rating:': PUBLIC_POS, 'Genre:': GENRE_POS, 'Source:': SOURCE_POS,
    'Production Method:': PROD_METH_POS, 'Creative Type:': CREATIVE_TYPE_POS
}
pos_mapping_2 = {
    'Keywords:': KEYWORDS_POS, 'Production/Financing Companies:': STUDIOS_POS, 
    'Production Countries:': COUNTRIES_POS, 'Languages:': LANGUAGES_POS
}
current_year = 2022
cpi_current = cpi.get(current_year)
driver = create_driver()
#cpi.update()
for year in range(2019, 2023, 1):
    scrape_year(driver, year, 400)
driver.quit()