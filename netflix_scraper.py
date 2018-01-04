#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium.common.exceptions import NoSuchElementException, WebDriverException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pdb
import dill as pickle
import config
import time

# SELENIUM CHEATSHEET
#   driver.page_source
#   driver.title

#      iframe = self._browser.find_elements_by_tag_name('iframe')[0]
#      self._browser.switch_to_frame(iframe)

class NetflixShowData:
  def __init__(self, **kwargs):
    self._episode_data = kwargs.get(episode_data, '')
    self._seasons = ''
    self._name = kwargs.get(name, '')
    return


class NetflixShowScraper:
  def __init__(self, browser):
    self._browser = browser
    return

  def scrape(self, page_element):
    try:
      wait = WebDriverWait(self._browser, 5)
      element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.jawBone h3 img')))
      name = element.get_attribute('alt')
      menu = page_element.find_element_by_class_name('menu')
      menu.find_element_by_link_text('EPISODES').click()
    except NoSuchElementException:
      print page_element.text
      pdb.set_trace()

    episodes_text = self._harvest_episode_text(page_element)

    return [name, episodes_text]

  # Navigate through all the seasons, and scroll right while we still can appending the episode data
  def _harvest_episode_text(self, el):
    text = []
    season_text = ''
    season_dropdown = el.find_element_by_css_selector('.nfDropDown')
    time.sleep(1)
    season_dropdown.find_element_by_class_name('label').click()
    number_of_seasons = len(season_dropdown.find_elements_by_tag_name('a')) - 1
    season_dropdown.find_element_by_class_name('label').click()
    current_season = 1

    while current_season <= number_of_seasons:
      season_dropdown.find_element_by_class_name('label').click()
      season_dropdown.find_element_by_link_text('Season {}'.format(current_season)).click()
      time.sleep(1)
      try:
        while True:
          season_text += el.text

          caret = el.find_element_by_class_name('icon-rightCaret')
          caret.click()
      except (NoSuchElementException, ElementNotVisibleException) as e:
        current_season += 1
        text.append(season_text)
        season_text = ''

    return text


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
    self._results = []
    return
  
  def scrape(self):
    self._load_cookies()

    self._browser.get(self.AUDIO_URL)

    if self._browser.current_url != self.AUDIO_URL:
      self._login()
      self._browser.get(self.AUDIO_URL)
    else:
      user_container = self._browser.find_elements_by_class_name('list-profiles-container')
      if len(user_container):
        self._select_user()

    self._find_language_content()

    self._results = self._harvest_content()

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
    time.sleep(1)
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

    pickle.dump( self._browser.get_cookies() , open("cookies.pkl","wb"))
    return

  def _get_initial_page(self):
    self._browser.get(self.BASE_URL)
    return

  def _row_container(self, id):
    self._browser.find_element_by_id('row-{}'.format(id))
    return

  def _harvest_content(self, start_row = 0, start_slider = 0, number_to_scrape = float('inf')):
    row_id = start_row
    slider_id = start_slider

    row_container = self._browser.find_element_by_id('row-{}'.format(row_id))
    wait = WebDriverWait(self._browser, 5)
    slider = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'slider-item-{}'.format(slider_id))))
    slider.click()
    record = NetflixShowScraper(self._browser).scrape(row_container.find_element_by_class_name('jawBone'))
    print record
    
    return

