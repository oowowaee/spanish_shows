#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium.common.exceptions import NoSuchElementException, WebDriverException, ElementNotVisibleException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_helpers import element_does_not_have_text
from show_scraper import NetflixShowScraper
import data
import pdb
import dill as pickle
import config
import time
import csv

# SELENIUM CHEATSHEET
#   driver.page_source
#   driver.title

#      iframe = self._browser.find_elements_by_tag_name('iframe')[0]
#      self._browser.switch_to_frame(iframe)


class NetflixScraper:
  AUDIO_URL = 'https://www.netflix.com/browse/audio'
  BASE_URL = 'https://www.netflix.com/ca/login'                     # ROOT PAGE URL
  LINK_CONTAINER = 'a'                                              # CSS CLASS FOR SELECTING PAGE LINKS
  CATEGORY_LINKS_CONTAINER = None
  PAGINATION_SELECTOR = None                                        # CSS Class for finding 'next' link
  RECORDS_CONTAINER = '.gallery'                                    # CSS Selector for wrapping records

  def __init__(self, webdriver_instance, language):
    self._browser = webdriver_instance
    self._language = language
    self._show_scraper = NetflixShowScraper(webdriver_instance)
    self._results = []
    return
  
  def scrape(self):
    # self._load_cookies()

    self._browser.get(self.AUDIO_URL)

    # If we were redirected, then we're not logged in
    if self._browser.current_url != self.AUDIO_URL:
      self._login()
      self._browser.get(self.AUDIO_URL)
    else:
      user_container = self._browser.find_elements_by_class_name('list-profiles-container')
      # Sometimes the currently logged in user gets lost, so if the user profile selector is present on the page, first select the user
      if len(user_container):
        self._select_user()

    self._find_language_content()

    self._results = self._harvest_content(0, 0, 1)

    return self._results

  def _load_cookies(self):
    try:
      cookies = pickle.load(open("cookies.pkl", "rb"))
      for cookie in cookies:
        try:
          self._browser.add_cookie(cookie)
        except WebDriverException:
          pass
    except IOError:
      pass
    return

  def _find_language_content(self):
    container = self._browser.find_element_by_class_name('languageDropDown')
    container.find_element_by_class_name('label').click()
    container.find_element_by_link_text(self._language).click()

    # Make sure the page content has reloaded
    time.sleep(.5)
    # wait = WebDriverWait(self._browser, 5)
    # element = wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.languageDropDown .label'), self._language.upper()))
    return

  def _login(self):
    self._get_initial_page()

    self._browser.find_element_by_id('email').send_keys(config.NETFLIX_CONFIG['email'])
    self._browser.find_element_by_id('password').send_keys(config.NETFLIX_CONFIG['password'])
    self._browser.find_element_by_class_name('login-button').click()

    self._select_user()
    return

  def _select_user(self):
    self._browser.find_element_by_link_text(config.NETFLIX_CONFIG['user']).click()

    # Wait for login to complete
    wait = WebDriverWait(self._browser, 5)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'mainView')))

    pickle.dump(self._browser.get_cookies(), open("cookies.pkl","wb"))
    return

  def _get_initial_page(self):
    self._browser.get(self.BASE_URL)
    return

  def _scroll_down(self):
    self._browser.execute_script("window.scrollBy(0, 150);")
    return

  def _harvest_content(self, start_row = 0, slider_start = 0, number_to_scrape = float('inf')):
    records = []
    row_id = start_row
    row_exists = True

    while row_exists and len(records) < number_to_scrape:
      try:
        wait = WebDriverWait(self._browser, 2)
        row_container = self._browser.find_element_by_id('row-{}'.format(row_id))
      except TimeoutException:
        row_exists = False
        break

      records += self._harvest_row_content(row_container, row_id, slider_start, number_to_scrape - len(records))
      self._scroll_down()
      row_id += 1

    try:
      records = pickle.load(open('scraped_data.pkl', 'rb')) + records
    except IOError:
      pass

    pickle.dump(records, open('scraped_data.pkl', 'wb'))
    return records

  def _harvest_row_content(self, row_container, row_id, slider_start, number_to_scrape):
    records = []
    slider_id = slider_start
    slider_item_count = len(row_container.find_elements_by_class_name('slider-item'))

    while slider_id < slider_item_count and len(records) < number_to_scrape:
      time.sleep(.5)

      wait = WebDriverWait(self._browser, 2)
      slider_item = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#row-{0} .slider-item-{1}'.format(row_id, slider_id))))
      slider_item.click()

      time.sleep(.5)

      record = self._show_scraper.scrape(row_container.find_element_by_class_name('jawBone'))
      slider_id += 1
      records.append(record)

    return records


