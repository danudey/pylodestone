#!/usr/bin/env python

# Standard library
import sys
import codecs
import datetime

# Extra libraries
import pytz
import requests
import lxml.html
from lxml.html.clean import clean_html

# Our libraries
import lodestone

# Official FFXIV North American timezone is PST
TIMEZONE = "America/Los_Angeles"
TZ = pytz.timezone(TIMEZONE)

class Character(lodestone.LodestoneObject):
  def __init__(self, html_obj):
    super(Character, self).__init__(html_obj)
    
    self.title = None
    self.species = None
    self.race = None
    self.gender = None
    self.grand_company = None
    self.free_company = None

    self.levels = {}
    
    self.__parse_classes()

  def __parse_classes(self):
    class_data = map(str.strip,self.html_obj.xpath("//table[@class='class_list']/tr/td/text()"))
    
    while class_data:
      class_name,class_level,class_xp = class_data[:3]
      del([class_data[:3]])

      class_name = class_name.lower()

      try:
        class_level = int(class_level)
      except ValueError:
        class_level = 0

      try:
        class_xp = map(int,class_xp.split(" / ")) 
      except ValueError, e:
        class_xp = [0,0]

      data = {
        class_name.lower(): {
          'level': class_level,
          'xp': class_xp
        }
      }
      self.levels.update(data)

  @classmethod
  def fromLodestoneHTML(cls, html):
    html_obj = lxml.html.fromstring(html)
    obj = cls(html_obj)
    return obj

  @classmethod
  def fromLodestoneURL(cls, url):
    response = requests.get(url)
    if response.status_code == 200:
      return cls.fromLodestoneHTML(response.text)
