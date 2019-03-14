import re

from lxml import html as l_html
from lxml import etree
import html
import requests
from itertools import chain

def stringify_children(node):
  # list(chain(*([c.text, etree.tostring(c), c.tail] for c in node.getchildren()))) +
  parts = []
  sup_pattern = r'\<sup\>(?P<num>.*)\</sup\>'
  sub_pattern = r'\<sup\>(?P<num>.*)\</sup\>'
  comment_pattern = r'\<!--(?P<comment>.*)--\>'
  span_pattern = r'\<span class="blt_Color"\>\s*\<strong\>\s*(?P<content>.*?)\s*\</strong\>\s*\</span\>'
  for c in node.getchildren():
      s = etree.tostring(c).decode('utf-8')
      s = html.unescape(s)
      s = ' '.join(s.split())
      s = re.sub('\t|\n|\r|\f|\v|&#13;|&#160;', '', s)

      span_match = re.compile(span_pattern).search(s)
      if span_match:
          s = re.sub(re.escape(span_match.group(0)), span_match.group('content').strip(), s)

      sup_match = re.compile(sup_pattern).search(s)
      if sup_match:
          s = s.replace(sup_match.group(0), '^{{{}}}'.format(sup_match.group('num'))).strip()

      sub_match = re.compile(sub_pattern).search(s)
      if sub_match:
          s = s.replace(sub_match.group(0), '_{{{}}}'.format(sub_match.group('num'))).strip()

      comment_match = re.compile(comment_pattern).search(s)
      if comment_match:
          s = s.replace(comment_match.group(0), '')

      parts.append(html.unescape(s).strip())

  # filter removes possible Nones in texts and tails
  return ''.join(node.text.split() + [str(x) for x in filter(None, parts)] + node.tail.split()).split(',')

def scrape(baselink, url):
  page = requests.get(url)
  tree = l_html.fromstring(page.content)
  DATA = {}
  for e in tree.xpath('//div[contains(@id, "element_name")]/a'):
      elem = e.attrib['title']
      DATA[elem] = {'short': e.text.strip()}

      print('\nInformation about {}:'.format(elem))
      link2 = baselink + e.attrib['href']
      sp = requests.get(link2)
      st = l_html.fromstring(sp.content)

      # read Fact Box
      for d in st.xpath('//div[contains(@id, "exp_factbox")]//table'):
          for k, v in zip(d.xpath('.//td[contains(@class, "miningb_border_rt")]'), d.xpath('.//td[contains(@class, "trbox_ca")]')):
              for _k, _v in zip(k.xpath('./span/strong'), v.xpath('./text()')):
                  dkey = ' '.join(stringify_children(k))
                  dval = stringify_children(v)
                  try:
                      dval = [float(dv) for dv in dval]
                  except:
                      try:
                          dval = [float(v) for v in x for x in list(dval)]
                      except:
                          print('Could not convert value {} of {}. Leaving as string.'.format(dval, dkey))
                  if len(dval) == 1:
                      dval = dval[0]
                  if not dkey == 'ChemSpider ID':
                      DATA[elem].update({dkey: dval})
      # read Atomic data
      # for d in st.xpath('//div[contains(@id, "exp_atomicdata")]//table'):

      # read Oxidation states and isotopes
      # for d in st.xpath('//div[contains(@id, "exp_oxidation")]//table'):

      # read Supply risk
      # for d in st.xpath('//div[contains(@id, "exp_mining")]//table'):

      # read Pressure and temperature data - advanced
      # for d in st.xpath('//div[contains(@id, "exp_pressure")]//table'):

      # break
  return DATA

if __name__ == '__main__':
  baselink = 'http://www.rsc.org'
  url = baselink + '/periodic-table'
  data = scrape(baselink, url)
  print(data)

  # csvFilename = "namesAndPhones.csv"  # what name you want to save your csv as
  # csv = open(csvFilename, "w")  # create or open csv, "w" to write strings
  # colNames = "Name, Phone\n"  # column titles
  # csv.write(colNames)
  #
  # for elem in data:
  #     text = elem.text_content()  # text inside each td elem
  #     splitText = text.split("\r\n")  # returns list of text between "\r\n" chars
  #     name = splitText[2].strip()  # get name and remove whitespace
  #     phone = splitText[-3].strip()  # get phone number and remove whitespace
  #     csv.write(name + "," + phone + "," + "\n")  # write to csv


