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
FOLDERCONTENT="""<?xml version="1.0" encoding="UTF-8"?>
<node>
<version>6</version>
<dict>
  <key>title</key><string>changenodename</string>
  <key>version</key><integer>6</integer>
  <key>content_type</key><string>application/x-notebook-dir</string>
</dict>
</node>
"""
LEAFCONTENT="""<?xml version="1.0" encoding="UTF-8"?>
<node>
<version>6</version>
<dict>
  <key>title</key><string>changenodename</string>
  <key>version</key><integer>6</integer>
  <key>content_type</key><string>text/xhtml+xml</string>
</dict>
</node>
"""
LEAFMAINCONTENT="""<?xml version="1.0" encoding="UTF-8"?>
<node>
<version>6</version>
<dict>
  <key>title</key><string>changenodename</string>
  <key>version</key><integer>6</integer>
  <key>content_type</key><string>text/xhtml+xml</string>
  <key>order</key><integer>0</integer>
</dict>
</node>
"""
PAGECONTENT="""!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>hoja1</title>
</head><body>changethistext</body></html>
"""
class mycherrytree:
    def __init__(self,options):
        self.input=options.input
        self.output=options.output
        self.bookName=os.path.basename(self.output)
        self.tree=ET.ElementTree(file=self.input)
        self.root=self.tree.getroot()
        if not os.path.isdir(self.output): os.mkdir(self.output)

    def getSafeName(self,name):
        escape_these=' /=([$!#&"()|<>`\;'+"'])"
        for i in escape_these:
            try:
                name=name.replace(i,"_")
            except:
                pass
        return name

    def makeLeaf(self,path,name,richtext,images=[]):
        insidepath=path+"/"+name
        if not os.path.isdir(insidepath):os.mkdir(insidepath)
        #create node.xml
        with open(insidepath+"/node.xml","w") as f:
            if name=="__main__":
                f.write(LEAFMAINCONTENT.replace("changenodename",name))
            else:
                f.write(LEAFCONTENT.replace("changenodename",name))

        if images:
            count=0 # counter for image name creation
            #images come with char offset as a way to place imgs inside text
            offsetIncrement=4
            for img in images:
                imgString=img["imgString"] #img in base64
                #offset will be incremented by our own img tags:
                imgOffset=img["offset"]+offsetIncrement
                count+=1
                imgfile=insidepath+"/image"+str(count)+".png"
                imgHtml='<img src="image{0}.png"/>'.format(str(count))
                offsetIncrement+=len(imgHtml)
                #write img tag in offset position among richtext
                richtext=richtext[:imgOffset]+imgHtml+richtext[imgOffset:]
                #write base64 image to file in same folder
                imgdata=base64.b64decode(imgString)
                with open(imgfile, 'wb') as f:
                    f.write(imgdata)

        #create page.html
        richtext=richtext.replace("\n","<br/>")
        with open(insidepath+"/page.html","w") as f:
            f.write(PAGECONTENT.replace("changethistext",richtext))

    def makeFolder(self,path,name,richtext,images=[]):
        insidepath=path+"/"+name
        if not os.path.isdir(insidepath):os.mkdir(insidepath)
        #create node.xml inside
        with open(insidepath+"/node.xml","w") as f:
            f.write(FOLDERCONTENT.replace("changenodename",name))
        #dont create page.xml here
        if richtext:
        #create leaf main as a substitute for cherrynote folder node content
            self.makeLeaf(insidepath,"__main__",richtext)

    def process(self,node,path):
        #receives a node type node and path
        #creation
        name=node.get("name")
        name=self.getSafeName(name)
        #texts:
        richtext=""
        for text in node.findall("rich_text"):
            richtext+=text.text
        images=[]
        for img in node.findall("encoded_png"):
            imgDict={"imgString":img.text.strip(),"offset":int(img.attrib["char_offset"])}
            images.append(imgDict)

        #recursivity
        children=node.findall("node")
        #children=node.getchildren()
        if not children:
            #default case
            #its a leaf
            self.makeLeaf(path,name,richtext,images)
        else:
            #self.createNode(node)
            self.makeFolder(path,name,richtext,images)
            for child in children:
                self.process(child,path+"/"+name)


    def createBasicStruct(self):
        dir1=self.output+"/__NOTEBOOK__"
        if not os.path.isdir(dir1): os.mkdir(dir1)
        file1=self.output+"/node.xml"
        if not os.path.isfile(file1):
            from shutil import copyfile
            copyfile(SCRIPTFOLDER+"/booknode.xml",file1)
            with open(file1,"rU") as f:
                text=f.read().replace("changethisname",self.bookName)
            with open(file1,"w") as f:
                f.write(text)
        file2=self.output+"/notebook.nbk"
        if not os.path.isfile(file2):
            from shutil import copyfile
            copyfile(SCRIPTFOLDER+"/notebook.nbk",file2)

    def start(self):
        #this is where it all starts
        self.createBasicStruct()
        for child in self.root.findall("node"):
            self.process(child,self.output)


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
    EPILOGUE = """ cherrytree to keepnote converter """

    parser = OptionParser(usage=USAGE, epilog=EPILOGUE)
#    parser.add_option("-g", "--getnote", help="get note text")
    parser.add_option("-i", "--input", help="cherry tree file, ctd format")
    parser.add_option("-o", "--output", help="output keepnote folder")
    (options, args) = parser.parse_args()

    if not options.input:print("input file needed");exit()
    if not options.output:print("output file needed");exit()
    t=mycherrytree(options)
    t.start()
