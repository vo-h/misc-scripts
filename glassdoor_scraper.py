"""
Introduction
A short script to scrape reviews of a particular company from Glassdoor.

To Begin
You will need:

URL of the 2nd review page of the company of interest. For example, Intel's 2nd review page looks like this: (Notice that 'P2' refers to Page number 2) https://www.glassdoor.com/Reviews/Intel-Corporation-Reviews-E1519_P2.htm?filter.iso3Language=eng
The prefix is gonna be: 'Reviews/Intel-Corporation-Reviews-E1519_P'
The suffix is gonna be: '.htm?filter.iso3Language=eng'
Name of a .xlsx file you want to save the data to.
First and last page you want to scrape data from.
Required Software:

Python packages: Selenium, Pandas, time, OS
Google Chrome and Google Chrome Driver
How It Works
The get_data() function first checks if target file exists. If it does, it loads the file, so that more entries can be added. Then it calls get_page() for each page from first and last page.
The get_page() function opens up a Google Chrome browser in the background and search for the desired information, then close the browser. Keeping the same browser, and changing the URL only will trigger the Glassdoor's sign-in pop-up. So, I've written the script to open a new window for each page and close it instead. It takes about 20 seconds to scrape a page if the page contains all the information Selenium is tasked to find. It takes longer if information is missing.
End Result
The final .xlsx file will have the following columns:

Index
Date
Position
Location
Pros
Cons
Work/Life Balance Rating
Culture Rating
Diversity & Inclusion Rating
Career Opportunities Rating
Benefits Rating
Management Rating
Page Number
"""

from selenium import webdriver
import pandas as pd
import time
import os.path
from webdriver_manager.chrome import ChromeDriverManager


def get_page(prefix, suffix, pg_number, columns):

    # initiate chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # go to specified url
    driver.get('https://www.glassdoor.com/' + prefix + str(pg_number) + suffix)

    # wait for a bit for page to load and to not set off red flag
    driver.implicitly_wait(2)

    # Find all the review blocks
    elements = driver.find_elements_by_xpath(
        '//li[@class="noBorder empReview cf pb-0 mb-0"]'
    )

    data = pd.DataFrame(columns=columns)

    for element in elements:

        # Get user id for each post
        user_id = element.get_attribute("id")

        # Some of these information might by missing like position and location
        try:
            row = []

            # Get text data in order: date, position, location, pros, cons
            row.append(
                driver.find_element_by_xpath(
                    f"//*[@id='{user_id}']//div[2]//div[1]//span[1]"
                ).text.split("-")[0]
            )
            row.append(
                driver.find_element_by_xpath(
                    f"//*[@id='{user_id}']//div[2]//div[1]//span[contains(@class, 'authorJobTitle')]"
                ).text.split("-")[1]
            )
            row.append(
                driver.find_element_by_xpath(
                    f"//*[@id='{user_id}']//div[2]//div[1]//span[2]/span"
                ).text
            )       
            row.append(
                driver.find_element_by_xpath(
                    f"//*[@id='{user_id}']//div[2]//div[2]/div[1]/p[2]/span"
                ).text
            )
            row.append(
                driver.find_element_by_xpath(
                    f"//*[@id='{user_id}']//div[2]//div[2]/div[2]/p[2]/span"
                ).text
            )

            # Get ratings data in order:
            # work_life, culture, inclusion, career_op, benefits, management
            ratings = {
                "css-152xdkl": 1,
                "css-19o85uz": 2,
                "css-1ihykkv": 3,
                "css-1c07csa": 4,
                "css-1dc0bv4": 5,
            }

            for item in [
                "Work/Life Balance",
                "Culture & Values",
                "Diversity & Inclusion",
                "Career Opportunities",
                "Compensation and Benefits",
                "Senior Management",
            ]:
                try:
                    xpath = f'//*[@id="{user_id}"]//div[1]//li/div[text()="{item}"]//following-sibling::div[1]'
                    rating_key = driver.find_element_by_xpath(xpath).get_attribute(
                        "class"
                    )
                    row.append(ratings[rating_key])
                except:
                    row.append("")

            # Add row to data
            row.append(pg_number)
            data = data.append(pd.Series(row, index=data.columns), ignore_index=True)
        except:
            None

    return data


def get_data(prefix, suffix, target_file, min_page, max_page):
    
    # The columns we are interested in
    columns = [
        "date",
        "position",
        "location",
        "pros",
        "cons",
        "work_life",
        "culture",
        "inclusion",
        "career_op",
        "benefits",
        "management",
        "page",
    ]

    # Check if target_file exists. If it does, load it. 
    if os.path.isfile(target_file):
        reviews = pd.read_excel(target_file, usecols=columns)
    else:
        reviews = pd.DataFrame(columns=columns)
    
    # Record start time to get a sense of how long things are taking
    start_time = time.time()
    
    
    for page in range(min_page, max_page):
        try:
            data = get_page(prefix=prefix, suffix=suffix, pg_number=page, columns=columns)
            reviews = reviews.append(data, ignore_index=True)
            print(f"""
     Done with page {page}, {int(time.time() - start_time)} seconds have passed.
     """)
        except:
            None
    
    reviews.to_excel(target_file)



if __name__ == '__main__':
    # add option to not pop up browser
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    # Structure of glassdoor url: prefix + page number + suffix
    prefix = "Reviews/Insight-Global-US-Reviews-EI_IE152783.0,14_IL.15,17_IN1_IP"
    suffix = ".htm?filter.iso3Language=eng&filter.employmentStatus=REGULAR&filter.employmentStatus=PART_TIME"


    get_data(prefix, suffix, 'data/test.xlsx', 1, 2)
