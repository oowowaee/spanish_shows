#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
from netflix.data import NetflixDataConverter
from netflix.scraper import NetflixScraper
from selenium import webdriver
import argparse
import dill as pickle

import csv

def main():
  command_args = _get_args()

  records = _get_records(command_args)

  if command_args.convert or not command_args.scrape:
    _convert_records(records)

  return

def _convert_records(records):
  records = NetflixDataConverter().convert_to_show_data(records)
  pdb.set_trace()
  pickle.dump(records, open('show_data.pkl', 'wb'))
  return

def _get_records(command_args):
  records = []

  if command_args.scrape or not command_args.convert:
    return _scrape_records(command_args)

  if command_args.convert or not command_args.scrape:
    records = pickle.load(open('scraped_data.pkl', 'rb'))
  return records

def _scrape_records(command_args):
  #csv_options = { 'delimiter': ',', 'quoting': csv.QUOTE_MINIMAL }

  if command_args.browser:
    path_to_chromedriver = '/home/tally/projects/chromedriver_27'
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=/home/tally/.config/google-chrome/selenium")
    browser = webdriver.Chrome(executable_path= path_to_chromedriver, chrome_options= options)
    browser.maximize_window()
  else:
    browser = webdriver.PhantomJS()

  browser.implicitly_wait(2)
  scraper = NetflixScraper(browser, 'Spanish')
  records = scraper.scrape()
  browser.close()
  return records

def _get_args():
  help_text = "{}"
  parser = argparse.ArgumentParser()
  parser.add_argument("-b", "--browser", action='store_true',
                      help=help_text.format("flag to use chrome browser"))
  parser.add_argument("-s", "--scrape", action='store_true',
                      help=help_text.format("flag to only scrape data"))
  parser.add_argument("-c", "--convert", action='store_true',
                      help=help_text.format("flag to only convert existing data"))
  return parser.parse_args()

if __name__ == '__main__':
  main()
