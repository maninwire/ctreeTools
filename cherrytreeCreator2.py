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
start="""<?xml version="1.0" ?>
<cherrytree>
    """

end="</cherrytree>"
node="""    <node custom_icon_id="0" foreground="" is_bold="False" name="{0}" prog_lang="custom-colors" readonly="False" tags="" ts_creation="1532615939.56" ts_lastsave="1532615977.51" unique_id="{2}">
                <rich_text>
                        {1}
                </rich_text>
        </node> 
"""
SCRIPTFOLDER=os.path.dirname(os.path.realpath(__file__))
class mycherrytree:
    def __init__(self,options):
        self.input=options.input
        self.output=options.output #ctd file
        self.bookName=os.path.basename(self.output)
        #self.tree=ET.ElementTree(file=self.input)
        #self.root=self.tree.getroot()
        self.separator=options.separator
        self.field=options.field
        self.removeString=options.removeString


    def create(self):
        out=start
        with open(self.input) as myfile:
            lines=myfile.readlines()
        count=0
        for l in lines:
            count+=1
            l=l.strip()
            l_array=l.split(self.separator)
            try:
                index=int(self.field)-1
                name=l_array[index]
            except: 
                print("index wrong, did you check inside of list?");exit()

            if self.removeString:
                removes=self.removeString.split(",")
                for remove in removes:
                    if name.find(remove)>0:name=name.replace(remove,"")
            content=open(l,"r").read()
            out+=node.format(name,content,str(count))

        out+=end

        with open(self.output,"w") as f:
                f.write(out)

class OptionParserWrapper(OptionParser):
    #needed in order to format the help text. sucks.
    def format_epilog(self, formatter):
	return self.epilog




from optparse import OptionParser

if __name__ == '__main__':

    USAGE = "usage: %prog [options] "
    EPILOGUE = """ 
        create ct ctb (xml) format from contents of files:
        Howto:
	Save all interesting files in list.
	Name them similarly, and separate name with a separator then use like "cut"
	Please note that cherrytree can already import a directory of files.
	This is if you need to change file names for node names
	
    
    
    """

    parser = OptionParser(usage=USAGE, epilog=EPILOGUE)
#    parser.add_option("-g", "--getnote", help="get note text")
    parser.add_option("-i", "--input", help="file containing files to open and create as nodes")
    parser.add_option("-o", "--output", help="cherry tree file save, ctd format")
    parser.add_option("-s", "--separator", help="filename separator. This is to retrieve proper node name")
    parser.add_option("-f", "--field", help="once the name is cut, select field with this")
    parser.add_option("-r", "--removeString", help="in case you need to remove additional strings from names: '.nmap,_,whatever")
    (options, args) = parser.parse_args()

    if not options.input:print("input file needed");exit()
    if not options.output:print("output file needed");exit()
    t=mycherrytree(options)
    t.create()
    
