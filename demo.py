import lxml
from lxml import html
import requests

link = "http://sdirwmp.org/contact-us"
response = requests.get(link) #get page data from server, block redirects
sourceCode = response.content #get string of source code from response
htmlElem = html.document_fromstring(sourceCode) #make HTML element object
tdElems = htmlElem.cssselect("[valign=top]") #list of all td elems

# for elem in tdElems:
#   text = elem.text_content() #text inside each td elem
#   tdElem1 = htmlElem.cssselect("[valign=top]")[0]  # first td elem
#   text = elem.text_content()
#   splitText = text.split("\r\n")  # returns list of text in between "\r\n" chars
#   print(splitText)

csvFilename = "namesAndPhones.csv" #what name you want to save your csv as
csv = open(csvFilename, "w") #create or open csv, "w" to write strings
colNames = "Name, Phone\n" #column titles
csv.write(colNames)

tdElems = htmlElem.cssselect("[valign=top]") #list of all td elems

for elem in tdElems:
  text = elem.text_content() #text inside each td elem
  splitText = text.split("\r\n") #returns list of text between "\r\n" chars
  name = splitText[2].strip() #get name and remove whitespace
  phone = splitText[-3].strip() #get phone number and remove whitespace
  csv.write(name + "," + phone + "," + "\n") #write to csv