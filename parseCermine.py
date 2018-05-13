# -*- coding: UTF-8 -*-

import mysql.connector
import os
from lxml import etree
from rake_nltk import Rake
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def nodeList2str(nodeList):
    str = ""
    for i in range(len(nodeList)):
        str += nodeList[i].text + ";"
    return str


def generateKeywords(title, abstract):
    keywordStr = ""

    r = Rake()
    r.extract_keywords_from_text(title)
    for phrase in r.get_ranked_phrases():
        keywordStr += phrase.encode('utf-8') + ";"

    r.extract_keywords_from_text(abstract)
    for phrase in r.get_ranked_phrases():
        keywordStr += phrase.encode('utf-8') + ";"

    return keywordStr


def printInfo(text, context, f, intoDB):
    tree = etree.parse(text)
    docTree = tree.getroot()

    authorNames = docTree.xpath('//contrib-group//contrib//string-name')
    authorStr = nodeList2str(authorNames)

    institutionNames = docTree.xpath('//contrib-group//aff//institution')
    institutionStr = nodeList2str(institutionNames)

    title = docTree.xpath('//article-meta//article-title')[0].text

    abstract = docTree.xpath('//abstract//p')[0].text

    kwdGroup = docTree.xpath('//kwd-group//kwd')
    if len(kwdGroup) == 0:
        keywordStr = generateKeywords(title, abstract)
    else:
        keywordStr = nodeList2str(kwdGroup)

    journal = docTree.xpath('//journal-meta//journal-title')[0].text

    year = docTree.xpath('//pub-date//year')[0].text

    volume = docTree.xpath('//volume')[0].text

    fpage = docTree.xpath('//fpage')[0].text
    lpage = docTree.xpath('//lpage')[0].text
    pageStr = fpage + "-" + lpage

    # RT Journal Article
    print >> f, ("RT Journal Article")

    # SR 1
    print >> f, ("SR 1")

    # A1 戴建春;
    print >> f, ("A1 %s" % authorStr.encode('utf-8'))

    # AD 温州医科大学外国语学院;上海外国语大学研究生部;
    print >> f, ("AD %s" % institutionStr.encode('utf-8'))

    # T1 认知语言学视角下幽默话语中本源概念的英译——以《围城》为例
    print >> f, ("T1 %s" % title.encode('utf-8'))

    # JF 淮海工学院学报(人文社会科学版)
    print >> f, ("JF %s" % journal.encode('utf-8'))

    # YR 2018
    print >> f, ("YR %s" % year.encode('utf-8'))

    # IS 04
    print >> f, ("IS %s" % volume.encode('utf-8'))

    # OP 58-63
    print >> f, ("OP %s" % pageStr.encode('utf-8'))

    # K1 本源概念;翻译;幽默;认知语言学;《围城》 indigenous information;translation;humor;cognitive linguistics;Fortress Besieged
    print >> f, ("K1 %s" % keywordStr.encode('utf-8'))

    # AB 基于对《围城》英译本中含有本源概念的幽默话语的理解度和幽默度的调查,并从认知语言学视角对典型译文进行评析,认为本源概念的翻译对目标语读者理解话语的幽默影响很大。翻译时,译者可以使用任何翻译方法,但相比较而言,
    # 不加注的直译较难以有效传达幽默。翻译中应允许译者有适度的创造性。
    print >> f, ("AB %s" % abstract.encode('utf-8'))

    print >> f, ("CL %s" % context.encode('utf-8'))

    print >> f, ("\n")

    if intoDB:
        putIntoDB(authorStr, institutionStr, title, journal, year, volume, fpage, lpage, keywordStr, abstract, context)


def putIntoDB(authorStr, institutionStr, title, journal, year, volume, fpage, lpage, keywordStr, abstract, context):
    cnx = mysql.connector.connect(user='root', password='123456', host='127.0.0.1', database='linguistics')
    add_paper = ("INSERT INTO paper "
                 "(author, institution, title, journal, year, volume, fpage, lpage, keywords, abstract, field)"
                 "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    paper_data = (authorStr, institutionStr, title, journal, year, volume, fpage, lpage, keywordStr, abstract, context)
    cursor = cnx.cursor()
    cursor.execute(add_paper, paper_data)
    cnx.commit()

    cursor.close()
    cnx.close


def getAllFile(path, allfile):
    allfilelist = os.listdir(path)
    for file in allfilelist:
        filepath = os.path.join(path, file)
        if os.path.isdir(filepath):
            getAllFile(filepath, allfile)
        if os.path.splitext(filepath)[1] == '.cermxml':
            allfile.append(filepath)


path = "test"
allfile = []
getAllFile(path, allfile)
f = open("final/download_1234.txt", 'w')

for file in allfile:
    text = open(file)
    context = file.split('/')[1]
    intoDB = False

    printInfo(text, context, f, intoDB)
    text.close()
