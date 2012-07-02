import urllib
import re
from lxml import etree
import lxml.html

def scrapetop(y,m,d):
    if (y<20):
        y = y+2000
    elif (y<100):
        y = y+1900        
    url = "http://thomas.loc.gov/cgi-bin/query/B?r112:@FIELD(FLD003+s)+@FIELD(DDATE+{year}{month:02d}{day:02d})".format(year=y,month=m,day=d)    
    print url
    itemnum = 0
    parser = etree.HTMLParser()
    u = urllib.urlopen(url)
    tree   = etree.parse(u, parser)
    links = tree.xpath('.//a')    
    for l in links:
        if (l.text) and len(l.text)>1:
            # text is matchable
            if re.match('\(Senate',l.text):
                itemnum+=1
                print itemnum
                prefix = "{year}{month:02d}{day:02d}_senate({item:03d})".format(year=y,month=m,day=d,item=itemnum)
                print l.text
                print l.get('href')
                scrapesingle(l.get('href'),prefix)
    u.close()

def scrapesingle(singleurl,prefix):
    speakernum = 0
    parser = etree.HTMLParser()
    u = urllib.urlopen("http://thomas.loc.gov/"+singleurl)
    tree   = etree.parse(u, parser)
    u.close()
    links = tree.xpath('.//a/em')
    if len(links)>0:
        l = links[0]
        pfurl = l.getparent().get('href')
        print pfurl
        u = urllib.urlopen("http://thomas.loc.gov/"+pfurl)    
        t = lxml.html.fromstring(u.read())
    else:
        print "Error trying to scrape: " + prefix
    # just get the text from the printer friendly version
    # first remove the tags.
    singletext = etree.tostring(t)    
    print singletext
    singletext = re.sub('<.?p>','\n',singletext)
    singletext = re.sub('<.*?>','',singletext)    
    # then, remove the pagination
    singletext = re.sub('\[Page:.*?\]','',singletext)
    # then remove the goofy formatting of spaces
    singletext = re.sub('&#160;','',singletext)       
    f = None
    for line in singletext.split('\n'):
        if line=="END":
            if f:
                f.close()
            break
        presiding =  re.match("The PRESIDING OFFICER",line) # presiding officer
        speaker =  re.match("\s*(\w\w+)\.\s((Mc)?[A-Z]+[A-Z])(\s(of)((\s\w+)?\s(\w+)))?\.",line) # two or more letters in a last name
        bill =  re.match("\s*S\. \d*",line) # eg, S. 2333
        if presiding or bill:
            if f:
                f.close()
                f = None
        if speaker:
            if f:
                f.close()
            speakernum += 1
            #                      Mr.           BROWN
            currentspeaker = speaker.group(1)+speaker.group(2)
            if speaker.group(6):
                #                 Massachusetts
                currentspeaker += re.sub(' ','',speaker.group(6))
            print line[0:50]+'...'                            
            fname = prefix + "[" + str.zfill(str(speakernum),4) + "]" + currentspeaker
            print fname
            f = open(fname+'.txt','w')
        if f:
            f.write(line)
