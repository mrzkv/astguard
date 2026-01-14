import xml.etree.ElementTree as ET
from lxml import etree
def cwe611_variant_9(user_input):
    etree.fromstring(user_input)

if __name__ == '__main__':
    cwe611_variant_9(input())
