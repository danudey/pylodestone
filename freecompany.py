#!/usr/bin/env python

import sys
import codecs
import requests
import lxml.html

from lxml.html.clean import clean_html

class FreeCompany(object):
  def __init__(self, html_obj):
    self.name = None
    self.url = None
    self.tag = None
    self.formed = None
    self.server = None
    
    self.active_members = None
    self.rank = None
    self.gc = None
    self.gc_rank = None
    self.company_slogan = None
    self.focus = None
    self.seeking = None
    self.active_times = None
    self.recruitment = None
  
    self.estate_name = None
    self.estate_address = None
    self.estate_greeting = None
    
    self.html_obj = html_obj
    
    self.__parse_url()
    self.__parse_header()
    self.__parse_tables()
    self.__parse_estate()

  def __repr__(self):
    return "<FreeCompany {name} <{tag}> ({server})>".format(name=self.name, tag=self.tag, server=self.server)

  def __parse_header(self):
    self.__parse_gc()
    self.__parse_gc_rank()
    self.__parse_server()

  def __parse_tables(self):
    self.__parse_formed()
    self.__parse_active_members()
    self.__parse_rank()
    self.__parse_slogan()
    self.__parse_focus()
    self.__parse_active_times()
    self.__parse_recruitment()
    self.__parse_gc_tag()
    self.__parse_gc_name()
  
  def __parse_estate(self):
    try:
      self.__check_estate()
      self.__parse_estate_name()
      self.__parse_estate_address()
      self.__parse_estate_greeting()
    except ValueError:
      pass

  def __extract_text(self, xpath):
    return [m for m in map(lambda x: x.strip().strip(u"<>()\xc2\xab\xc2\xbb"), self.html_obj.xpath(xpath)) if m]

  def __extract_attr(self, xpath, attr):
    return self.html_obj.xpath(xpath)

  def __parse_url(self):
    self.url = ''.join(self.__extract_text("string(//meta[@property='og:url']/@content)"))

  def __parse_gc(self):
    """parse out GC"""
    self.gc, = self.__extract_text("//div[@class='crest_id centering_h']/text()")

  def __parse_gc_rank(self):
    """parse out gc_rank"""
    self.gc_rank, = self.__extract_text("//div[@class='crest_id centering_h']/span[@class='friendship_color']/text()")

  def __parse_gc_tag(self):
    """parse out gc tag"""
    self.tag, = self.__extract_text("//table[@class='table_style2']/tr[1]/td/text()")

  def __parse_gc_name(self):
    """parse out gc name"""
    self.name, = self.__extract_text("//table[@class='table_style2']/tr[1]/td/span[@class='txt_yellow']/text()")

  def __parse_server(self):
    """parse out GC server"""
    self.server, = self.__extract_text("//div[@class='crest_id centering_h']/span[3]/text()")

  def __parse_formed(self):
    """parse out formation date"""
    date, = self.__extract_text("//table[@class='table_style2']/tr[2]/td/script/text()")
    self.formed = int(''.join([m for m in date.split('=')[1] if m.isnumeric()]))

  def __parse_active_members(self):
    """parse active members count"""
    active_members, = self.__extract_text("//table[@class='table_style2']/tr[3]/td/text()")
    self.active_members = int(active_members)

  def __parse_rank(self):
    """parse FC rank"""
    rank, = self.__extract_text("//table[@class='table_style2']/tr[4]/td/text()")
    self.rank = int(rank)

  def __parse_slogan(self):
    """parse company slogan"""
    self.company_slogan, = self.__extract_text("//table[@class='table_style2']/tr[6]/td/text()")

  def __parse_focus(self):
    """parse focus"""
    self.focus = self.__extract_text("//table[@class='table_style2']/tr[7]/td/ul/li[not(@class)]/img/@title")

  def __parse_seeking(self):
    """parse soughtclasses"""
    self.seeking = self.__extract_text("//table[@class='table_style2']/tr[8]/td/ul/li/img/@title")

  def __parse_active_times(self):
    """parse company active times"""
    self.active_times, = self.__extract_text("//table[@class='table_style2']/tr[9]/td/text()")

  def __parse_recruitment(self):
    """parse company recruitment status"""
    self.recruitment, = self.__extract_text("//table[@class='table_style2']/tr[10]/td/text()")

  def __parse_estate_name(self):
    """parse company recruitment status"""
    self.estate_name, = self.__extract_text("//table[@class='table_style2']/tr[11]/td/div[@class='txt_yellow mb10']/text()")

  def __parse_estate_address(self):
    """parse company recruitment status"""
    self.estate_address, = self.__extract_text("//table[@class='table_style2']/tr[11]/td/p[@class='mb10'][1]/text()")

  def __parse_estate_greeting(self):
    """parse company recruitment status"""
    greeting = self.__extract_text("//table[@class='table_style2']/tr[11]/td/p[@class='mb10'][2]/text()")
    self.estate_greeting = ' '.join(greeting)

  def __check_estate(self):
    """
    check to see if there's an estate at all
    """
    data, = self.__extract_text("//table[@class='table_style2']/tr[11]/td/text()")
    if data == u'No Estate or Plot':
      raise ValueError("No estate or plot")

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