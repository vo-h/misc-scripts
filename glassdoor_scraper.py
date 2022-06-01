# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 19:39:45 2021
@author: hienv
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
