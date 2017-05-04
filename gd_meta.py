import urllib.request
from html.parser import HTMLParser
import datetime
import time
import json
import os
from os import listdir
from os.path import isfile, join

class GDForumParser(HTMLParser):
    global depth
    global tags
    global attrs
    global res
    global fin
    depth = -1
    res = {'Sticky':False}
    tags = []
    attrs = []
    fin = []
    def handle_starttag(self, tag, attr):
        global depth
        global tags
        depth += 1
        tags.append(tag)
        attrs.append(attr)
    def handle_endtag(self, tag):
        global depth
        global tags
        depth -= 1
        tags.pop()
        attrs.pop()
    def handle_data(self, data):
        global depth
        global tags
        global res
        data = data.strip()
        if "..." != data and "(" != data and ")" != data and "" != data:
            if data == 'Sticky:':
                res['Sticky'] = True
            if depth == 3 and tags[depth] == 'a' and "showthread" in attrs[depth][0][1]:
                res["Thread Title"] = data
            elif depth == 3 and tags[depth] == 'span' and len(attrs[depth]) >= 2:
                res["Thread Author"] = data
            elif depth == 2 and tags[depth] == 'div' and len(attrs[depth]) > 0 and data != "by":
                if data == "Yesterday":
                    data = datetime.date.fromordinal(datetime.date.today().toordinal()-1).strftime("%m-%d-%Y")
                elif data == "Today":
                    data = datetime.date.fromordinal(datetime.date.today().toordinal()).strftime("%m-%d-%Y")
                res["Day of Last Post"] = data
            elif depth == 3 and tags[depth] == 'span' and "class" in attrs[depth][0][0]:
                res["Time of Last Post"] = data
            elif depth == 3 and tags[depth] == 'a':
                res["Last Poster"] = data
            elif depth == 2 and tags[depth] == 'a':
                res["Replies"] = data
            elif depth == 1 and tags[depth] == 'td':
                res["Views"] = data
                if not res["Sticky"]:
                    fin.append(res)
                res = {'Sticky':False}
    def get_fin(self):
        return fin

def check_forum():
    fp = urllib.request.urlopen("http://www.grimdawn.com/forums/forumdisplay.php?f=17")
    bytestring = fp.read()

    html = bytestring.decode("latin-1")
    fp.close()

    forum = html[html.index("<tbody id=\"threadbits_forum_17\">") + 38:] #38 = length of string plus whitespace
    forum = forum[:forum.index("</tbody>")] #
    gdfp = GDForumParser()
    gdfp.feed(forum)
    data = gdfp.get_fin()
    stamp = time.mktime(datetime.datetime.now().timetuple())
    chunk = {stamp: data}
    jdata = json.dumps(chunk, indent=4, sort_keys=True)
    if not os.path.exists("dumps"):
        os.makedirs("dumps")
    fil = open("dumps/" + str(stamp).replace(".0","") + ".json", 'w')
    fil.write(jdata)
    fil.flush()
    fil.close()
    
def get_dumps():
    return [f for f in listdir("dumps/") if isfile(join("dumps/", f))]
        
if __name__ == "__main__":
    #check_forum()
    dumps = get_dumps()
    metafile = json.loads(open("meta.json").read())
    print(metafile)