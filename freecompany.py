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
from utils import url_to_html_obj, xpath_from_url

# Official FFXIV North American timezone is PST
TIMEZONE = "America/Los_Angeles"
TZ = pytz.timezone(TIMEZONE)

class FreeCompany(lodestone.LodestoneObject):
  def __init__(self, html_obj):
    super(FreeCompany, self).__init__(html_obj)
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

    self.member_list = []
    
    self.html_obj = html_obj

    self.__parse_url()
    self.__parse_header()
    self.__parse_tables()
    self.__parse_estate()

  @property
  def members(self):
    if self.member_list:
      return self.member_list
    else:
      self.memberslisthtml = self.__get_member_list()
      return self.member_list

  def __get_member_list(self):
    base_members_url = self.url + "/member/?page=1"
    members_html_obj = url_to_html_obj(base_members_url)
    members_urls = list(set(members_html_obj.xpath("//div[@class='pagination clearfix']//a/@href")))

    for members_url in members_urls:
      print "Processing members url %s" % members_url
      members_obj = url_to_html_obj(members_url)
      for player in members_obj.xpath("//div[@class='player_name_area']"):
        data = self._clean_xpath(player,"h4/div/a/text() | h4/div/a/@href | div/text()")
        self.member_list.append(dict(zip(("url","name","rank"),data)))

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

  def __parse_url(self):
    self.url = ''.join(self._extract_text("string(//meta[@property='og:url']/@content)"))

  def __parse_gc(self):
    """parse out GC"""
    self.gc, = self._extract_text("//div[@class='crest_id centering_h']/text()")

  def __parse_gc_rank(self):
    """parse out gc_rank"""
    self.gc_rank, = self._extract_text("//div[@class='crest_id centering_h']/span[@class='friendship_color']/text()")

  def __parse_gc_tag(self):
    """parse out gc tag"""
    self.tag, = self._extract_text("//table[@class='table_style2']/tr[1]/td/text()")

  def __parse_gc_name(self):
    """parse out gc name"""
    self.name, = self._extract_text("//table[@class='table_style2']/tr[1]/td/span[@class='txt_yellow']/text()")

  def __parse_server(self):
    """parse out GC server"""
    self.server, = self._extract_text("//div[@class='crest_id centering_h']/span[3]/text()")

  def __parse_formed(self):
    """parse out formation date"""
    date, = self._extract_text("//table[@class='table_style2']/tr[2]/td/script/text()")
    unixtime = int(''.join([m for m in date.split('=')[1] if m.isnumeric()]))
    self.formed = datetime.datetime.fromtimestamp(unixtime, TZ)

  def __parse_active_members(self):
    """parse active members count"""
    active_members, = self._extract_text("//table[@class='table_style2']/tr[3]/td/text()")
    self.active_members = int(active_members)

  def __parse_rank(self):
    """parse FC rank"""
    rank, = self._extract_text("//table[@class='table_style2']/tr[4]/td/text()")
    self.rank = int(rank)

  def __parse_slogan(self):
    """parse company slogan"""
    self.company_slogan, = self._extract_text("//table[@class='table_style2']/tr[6]/td/text()")

  def __parse_focus(self):
    """parse focus"""
    self.focus = self._extract_text("//table[@class='table_style2']/tr[7]/td/ul/li[not(@class)]/img/@title")

  def __parse_seeking(self):
    """parse soughtclasses"""
    self.seeking = self._extract_text("//table[@class='table_style2']/tr[8]/td/ul/li/img/@title")

  def __parse_active_times(self):
    """parse company active times"""
    self.active_times, = self._extract_text("//table[@class='table_style2']/tr[9]/td/text()")

  def __parse_recruitment(self):
    """parse company recruitment status"""
    self.recruitment, = self._extract_text("//table[@class='table_style2']/tr[10]/td/text()")

  def __parse_estate_name(self):
    """parse company recruitment status"""
    self.estate_name, = self._extract_text("//table[@class='table_style2']/tr[11]/td/div[@class='txt_yellow mb10']/text()")

  def __parse_estate_address(self):
    """parse company recruitment status"""
    self.estate_address, = self._extract_text("//table[@class='table_style2']/tr[11]/td/p[@class='mb10'][1]/text()")

  def __parse_estate_greeting(self):
    """parse company recruitment status"""
    greeting = self._extract_text("//table[@class='table_style2']/tr[11]/td/p[@class='mb10'][2]/text()")
    self.estate_greeting = ' '.join(greeting)

  def __check_estate(self):
    """
    check to see if there's an estate at all
    """
    data, = self._extract_text("//table[@class='table_style2']/tr[11]/td/text()")
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