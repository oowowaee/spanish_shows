#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium.common.exceptions import NoSuchElementException
import pdb
import dill as pickle

# SELENIUM CHEATSHEET
#   driver.page_source
#   driver.title

#      iframe = self._browser.find_elements_by_tag_name('iframe')[0]
#      self._browser.switch_to_frame(iframe)

class Scraper:
  BASE_URL = ''                     # ROOT PAGE URL
  LINK_CONTAINER = 'a'              # CSS CLASS FOR SELECTING PAGE LINKS
  CATEGORY_LINKS_CONTAINER = None
  NAVIGATE_TO_LINKS = True          # True iff we need to harvest the information from the linked pages
  PAGINATION_SELECTOR = None           # CSS Class for finding 'next' link
  RECORDS_CONTAINER = '#unsolved'   # CSS Selector for wrapping records

  def __init__(self, webdriver_instance, required_fields):
    self._browser = webdriver_instance
    self._records = []
    self._required_fields = required_fields
    return

  @property
  def pickle_file(self):
    return 'pickle/' + self.__class__.__name__ + '.pickle'

  @property
  def records(self):
    return [record.to_array(self._required_fields) for record in self._records]
  
  def scrape(self):
    self._get_initial_page()

    if self.NAVIGATE_TO_LINKS:
      links = self._get_all_record_links()
      self._build_records_from_links(links)

    self._browser.close()
    return

  def pickle(self):
    picklefile = open(self.pickle_file, 'wb')
    pickle.dump(self._records, picklefile)
    picklefile.close()
    return

  def unpickle(self):
    picklefile = open(self.pickle_file, 'rb')
    self._records = pickle.load(picklefile)
    picklefile.close()
    return

  def _scroll_up_from_element(self, el):
    el.location_once_scrolled_into_view
    self._browser.execute_script("window.scrollBy(0, -150);")
    return

  def _navigate_to_next_page(self, scroll_up = False):
    try:
      # Sticky headers are dicks.  If scroll_up flag is passed, navigate to the nav
      # links and scroll up a bit.
      el = self._browser.find_element_by_css_selector(self.PAGINATION_SELECTOR)
      if scroll_up:
        self._scroll_up_from_element(el)
      el.click()
      return True
    except NoSuchElementException:
      return False

  def _get_initial_page(self):
    self._browser.get(self.BASE_URL)
    return

  def _build_records_from_links(self, links):
    for link in links:
      print 'Scraping ' + link
      self._browser.get(link)
      self._add_record(link)

  def _add_record(self, link = ''):
    element = self._browser.find_element_by_css_selector(self.RECORD_CLASS.RECORD_CONTAINER)
    try:
      record = self.RECORD_CLASS.from_element(element, source = link)
      if record:
        self._records.append(record)
    except NoSuchElementException as e:
      # print e
      if link:
        print 'Could not find element in ' + link
      else:
        print 'Could not find element for record'
      return

  def _get_all_record_links(self):
    links = self._get_page_links()

    if self.PAGINATION_SELECTOR:
      while self._navigate_to_next_page():
        links += self._get_page_links()

    return links

  def _get_page_links(self):
    page_links = self._browser.find_elements_by_css_selector(self.LINK_CONTAINER)
    return [link.get_attribute('href') for link in page_links]

