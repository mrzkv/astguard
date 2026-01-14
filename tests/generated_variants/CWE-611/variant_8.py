import xml.etree.ElementTree as ET
from lxml import etree
def cwe611_variant_8(user_input):
    ET.fromstring(user_input)

if __name__ == '__main__':
    cwe611_variant_8(input())
