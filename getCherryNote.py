#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
from optparse import OptionParser
import os
from os.path import basename,exists,dirname,isdir
#~ from subprocess import check_output
#~ import subprocess
import re
from bs4 import BeautifulSoup
import codecs
import xml.etree.cElementTree as ET


class mycherrytree:
    def __init__(self,book):
        self.book=book
        self.path=""
        self.tree=ET.ElementTree(file=self.book)
    def getXpathToNote(self,notepath):
        arr=notepath.split("/")
        out=""
        folders=arr[1:]
        for i in folders:
                out+="node[@name='{}']/".format(i)
        out+="rich_text"
        return out

    def getRichText(self,notepath):
        for elem in self.tree.iterfind(self.getXpathToNote(notepath)):
            a=elem
            text=[i for i in a.itertext()]
        return text

from optparse import OptionParser

if __name__ == '__main__':

    USAGE = "usage: %prog [options] "
    EPILOGUE = """ cherry tree utilities"""

    parser = OptionParser(usage=USAGE, epilog=EPILOGUE)
    parser.add_option("-g", "--getnote", help="/path/to/note")
    parser.add_option("-b", "--book", help="cherry tree notebook")
    (options, args) = parser.parse_args()

    if not options.getnote or not options.book:print("need options");exit()
    t=mycherrytree(options.book)
    if options.getnote:
        print(t.getRichText(options.getnote))
        


