"""
This script automatically plays the game Set on GatherTown at the user's prompt.
"""


from itertools import combinations
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_cards():

    """
    This function first finds the card elements on the website,
    then get infromation on the shape, color, pattern, and count.
    How it finds these data is very specific to the
    website where set is hosted.
    """

    # All the cards fall into this block
    elements = driver.find_elements_by_xpath(
        "//*[@id='root']/div/div/div[2]/div[2]/div[contains(@style, 'opacity: 1')]"
    )

    cards = []

    for ind, element in enumerate(elements):

        card = dict.fromkeys(["ind", "shape", "color", "pattern", "count"])

        # index the card so that it can be called later
        card["ind"] = ind

        card["shape"] = str(
            element.find_element_by_tag_name("use").get_attribute("href")
        )[1:]

        card["color"] = element.find_element_by_css_selector(
            "svg use:nth-of-type(2)"
        ).get_attribute("stroke")

        if str(element.find_element_by_tag_name("use").get_attribute("mask")) == "":
            if (
                str(element.find_element_by_tag_name("use").get_attribute("fill"))
                != "transparent"
            ):
                card["pattern"] = "filled"
            else:
                card["pattern"] = "transparent"
        else:
            card["pattern"] = "striped"

        card["count"] = len(element.find_elements_by_tag_name("svg"))

        cards.append(card)

    return elements, cards


def get_set(cards):
    """
    This function reads the card attributes and go through the combination
    of 3 cards to find the set that fits the bill.
    """
    for pot_set in combinations(cards, 3):
        passes = 0
        for test_type in ["shape", "color", "pattern", "count"]:
            array = [
                pot_set[0][test_type],
                pot_set[1][test_type],
                pot_set[2][test_type],
            ]
            if len(set(array)) in [1, 3]:
                passes += 1
        if passes == 4:
            return pot_set


def click_buttons(elements, the_set):
    """
    Click the appropriate 3 cards.
    """
    for card in the_set:
        elements[card["ind"]].click()


# Open webpage
url = input("Please enter custom Gather.Town URL: ")
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get(url)

# The script stalls until we are in game.
while (signal := input("Enter 'yes' when the game begins: ")) != "yes":
    None


# Unique to gather.town since the the game is embdded.
driver.switch_to.frame(0)


while (signal := input("Keep going? ")) != "no":
    buttons, current_cards = get_cards()
    current_set = get_set(current_cards)
    click_buttons(buttons, current_set)
    time.sleep(2)  # allow website to re-load.

driver.close()
