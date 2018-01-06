from selenium.common.exceptions import NoSuchElementException, WebDriverException, ElementNotVisibleException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_helpers import element_does_not_have_text
import pdb
import config
import time
import csv

# Handles scraping of the data from a show resource
class NetflixShowScraper:
  def __init__(self, browser):
    self._browser = browser
    return

  def scrape(self, page_element):
    # number of seasons
    wait = WebDriverWait(self._browser, 2)
    page_element = wait.until(element_does_not_have_text(page_element, 'Loading...'))
    description = page_element.text.replace('\n', '\\n')
    name = self._get_name(page_element)

    try:
      time.sleep(.5)
      menu = page_element.find_element_by_class_name('menu')
      # TODO: Just check for the presence of seasons text
      if 'Parts' in description or 'Collection' in description or 'Season' in description:
        el = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'EPISODES')))
        el.click()
        text = self._harvest_episode_text(page_element)
      else:
        text = []

      self._close()
    except (NoSuchElementException, WebDriverException) as e:
      print menu.text
      pdb.set_trace()
    return [name, description, text]

  # Click the close button
  def _close(self):
    wait = WebDriverWait(self._browser, 2)
    element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'close-button')))
    element.click()
    return

  # Some titles have images for their name, others have text
  def _get_name(self, page_element):
    wait = WebDriverWait(self._browser, 2)
    try:
      element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.jawBone h3 img')))
      name = element.get_attribute('alt')
    except TimeoutException:
      name = page_element.find_element_by_class_name('text').text
    return name

  # Navigate through all the seasons, and scroll right while we still can appending the episode data
  def _harvest_episode_text(self, el):
    text = []
    season_dropdown = el.find_element_by_css_selector('.nfDropDown')
    time.sleep(.5)
    season_dropdown.find_element_by_class_name('label').click()
    number_of_seasons = len(season_dropdown.find_elements_by_tag_name('a')) - 1
    season_dropdown.find_element_by_class_name('label').click()
    current_season = 1

    while current_season <= number_of_seasons:
      season_dropdown.find_element_by_class_name('label').click()
      # Stupid La Mante has the seasons listed in french
      season_dropdown.find_elements_by_css_selector('.sub-menu-list .sub-menu-link')[current_season - 1].click()
      time.sleep(.5)
      season_text = season_dropdown.text + '\n'
      try:
        while True:
          season_text += el.find_element_by_class_name('episodeWrapper').text + '\n'

          wait = WebDriverWait(self._browser, 2)
          caret = el.find_element_by_class_name('icon-rightCaret')
          #caret = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'icon-rightCaret')))
          caret.click()
          time.sleep(1)
      except (NoSuchElementException, ElementNotVisibleException, IndexError) as e:
        current_season += 1
        text.append(season_text)
        season_text = ''
      except WebDriverException as e:
        pass

    return text