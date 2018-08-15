#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
import base64
from optparse import OptionParser
import os
from os.path import basename,exists,dirname,isdir
import re
from bs4 import BeautifulSoup
import codecs
import xml.etree.cElementTree as ET

SCRIPTFOLDER=os.path.dirname(os.path.realpath(__file__))
class mycherrytree:
    def __init__(self,options):
        self.input=options.input
        self.output=options.output
        self.bookName=os.path.basename(self.output)
        self.tree=ET.ElementTree(file=self.input)
        self.root=self.tree.getroot()


    def process(self,node):
        #receives a node to fix
        #texts:
        for text in node.findall("rich_text"):
            #if text.text.find("OSCP-Survival")>=0:
            #        from ipdb import set_trace
            #        set_trace()
            textOri=text.text
            text.text=re.sub(r"\n{3,}","\n\n",text.text) #  more than 3 eofs, reduce to 2
            text.text=text.text.strip() #before and after the text, delete
            text.text="\n"+text.text
            if text.text.find("\t")>=0:
                print("[i] Tabs found\n")
                print("[i] Printing text:\n")
                print("\n")
                print(text.text)
                print("\n")
                print("\n")
                userInput=input("[?] Replace tabs?[Y/n]")
                if userInput in ["\n","Y\n","y\n"]:
                    print("Replacing")
                    text.text=re.sub(r"\t{1,},"",text.text")



        #recursivity
        children=node.findall("node")
        #children=node.getchildren()
        if not children:
            #default case
            #its a leaf
            pass
        else:
            for child in children:
                self.process(child)


    def start(self):
        #this is where it all starts
        #self.createBasicStruct()
        for child in self.root.findall("node"):
            self.process(child)
        self.tree.write(self.output)


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
    EPILOGUE = """ cherrytree fixer\n\n
    
    When working with xml, sometimes cherry tree corrupts data on some computers, adding extra spaces and lines and tabs. This is a hack to clean that  
    
    
    """

    parser = OptionParser(usage=USAGE, epilog=EPILOGUE)
#    parser.add_option("-g", "--getnote", help="get note text")
    parser.add_option("-i", "--input", help="cherry tree file, ctd format")
    parser.add_option("-o", "--output", help="cherry tree file save, ctd format")
    (options, args) = parser.parse_args()

    if not options.input:print("input file needed");exit()
    if not options.output:print("output file needed");exit()
    t=mycherrytree(options)
    t.start()
    
