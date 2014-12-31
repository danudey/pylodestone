#!/usr/bin/env python
# -*- coding: utf8 -*-

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

    self.city_state = None
    self.grand_company = None
    self.grand_company_rank = None
    self.free_company = None

    self.nameday = None
    self.guardian = None

    self.levels = {}
    
    self.__parse_classes()
    self.__parse_character()

  def __parse_character(self):
    self.guardian, self.nameday = self.html_obj.xpath("//dd/div/dl/*/text()")[1::2]
    self.city_state, self.free_company = self.html_obj.xpath("//dd[5]/text()|//dd[9]/a/text()")
    self.grand_company, self.grand_company_rank = self.html_obj.xpath("//dd[7]/text()")[0].split("/")
    self.title = self.html_obj.xpath("//div[@class='chara_title']/text()")[0]
    self.species, self.race, gender = self.html_obj.xpath("//div[@class='chara_profile_title']/text()")[0].split(" / ")
    if gender == u'♀':
      self.gender = "Female"
    else:
      self.gender = "Male"

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
