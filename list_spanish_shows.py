#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
from netflix_scraper import NetflixScraper
from selenium import webdriver
import argparse

import csv

def main():
  records = []
  command_args = _get_args()

  if command_args.chrome:
    path_to_chromedriver = '/home/tally/projects/chromedriver_27'
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=/home/tally/.config/google-chrome/selenium")
    browser = webdriver.Chrome(executable_path = path_to_chromedriver, chrome_options=options)
  else:
    browser = webdriver.PhantomJS()

  scraper = NetflixScraper(browser, 'Spanish')
  records = scraper.scrape()

  browser.close()

  # outfile = 'csv/' + scraper.__class__.__name__ + '.csv'

  # with open(outfile, 'wb') as csvfile:
  #   writer = csv.writer(csvfile,
  #                       delimiter=',',
  #                       quoting=csv.QUOTE_MINIMAL)

  #   writer.writerow(FIELDS)

  #   for record in records:
  #     writer.writerow([unicode(s).encode('utf-8') for s in record])

def _get_args():
  help_text = "{}"
  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--chrome", action='store_true',
                      help=help_text.format("flag to use chrome browser"))

  return parser.parse_args()

if __name__ == '__main__':
  main()
