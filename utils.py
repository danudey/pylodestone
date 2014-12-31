import lxml.html
import requests

url_cache = {}

def url_to_html_obj(url, clean=True):
  """
  Takes a url and returns a lxml.html-parsed object;
  url objects are cached
  """
  try:
    return url_cache[url]
  except KeyError:
    data = requests.get(url).text
    url_cache[url] = lxml.html.fromstring(data)
    url_cache[url].make_links_absolute(url)
    return url_cache[url]

def xpath_from_url(url, xpath):
  """
  One-shot convenience function to return the result of an
  xpath query on the contents of a URL. Highly inefficient.
  """
  html_obj = url_to_html_obj(url)
  return html_obj.xpath(xpath) 