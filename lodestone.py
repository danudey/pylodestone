class LodestoneObject(object):

  STRIPCHARS = u"<>()\xc2\xab\xc2\xbb"

  def __init__(self, html_obj):
    self.html_obj = html_obj

  def _extract_text(self, xpath):
    return [m for m in map(lambda x: x.strip().strip(self.STRIPCHARS), self.html_obj.xpath(xpath)) if m]

  def _extract_attr(self, xpath, attr):
    return self.html_obj.xpath(xpath)

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
