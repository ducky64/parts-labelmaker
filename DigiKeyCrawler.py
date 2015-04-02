import collections
import re
import pprint
from urllib.parse import quote

from bs4 import BeautifulSoup

import httplib2

class DigiKeyCrawlerInterface(object):
  URL_PREFIX = 'http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail?name='

  def parse_table(self, soup_table):
    elements = collections.OrderedDict()
    for row in soup_table.findChildren('tr'):
      header = row.find('th')
      value = row.find('td')
      if (header is not None) and (value is not None):
        elements[header.get_text()] = value.get_text()
    return elements
    
  def get_component_parametrics(self, component):
    h = httplib2.Http('.cache')
    resp_headers, content = h.request(self.URL_PREFIX + quote(component))
    content = content.decode("utf-8")
    
    # The part attributes table has a hanging </a> tag. Fail...
    content = re.sub(r'</a>', '', content)
    content = re.sub(r'<a[^>]*>', '', content)
    content = content.replace('&nbsp;', '')
    content = content.replace('\n', '')
    content = content.replace('\t', '')

    soup = BeautifulSoup(content)
    parametrics = collections.OrderedDict()

    parametrics.update(self.parse_table(soup.find('table', 'product-details')))
    parametrics.update(self.parse_table(soup.find('td', 'attributes-table-main')))
  
    return parametrics
  
class DigiKeyRewrite(object):
  def rewrite_parametrics(self):
    pass

if __name__ == '__main__':
  # Simple demo and test script
  dksi = DigiKeyCrawlerInterface()
  pprint.pprint(dksi.get_component_parametrics('LM3940IT-3.3/NOPB'))