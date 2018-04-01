from bs4 import BeautifulSoup as bs
from bs4.element import NavigableString, Tag
import urllib.request as ur
from pymongo import MongoClient
import time
import datetime 
from pprint import pprint

########################################
#Find the number of pages available in a
#thread and forms links for the in a list
#and returns them
########################################
def pagefinder(div, baseurl):
  found = div.find_next("table")
  tds = found.find_all("td")[0]
  
  try:
    last_page = int(tds.find_all("a")[-2].string)
    iter = 20
    pagelist = []
    u = 0
  
    for i in range(0,last_page):
      pagelist.append(baseurl + str(u))
      u = u + iter
  except Exception as e:
    return baseurl+"0"
  
  return pagelist;
  
##############################################
#It scrapes all the pages for the contents and
#dumps into mongo
##############################################
def scrapePage(link, head, posts):
  req = ur.Request(link, headers = head)
  con = ur.urlopen(req)
  page = con.read()
  soup = bs(page, "html.parser")
  time.sleep(0.4)
  
  form = soup.find_all("form",id = "quickModForm")[0]
  table = form.find_all("table")[0]
  
  x = 0

  for child in table.contents:
    try:
      temp = child
      caughttable = temp.find("table")
      for tr in caughttable.contents:
        
        results = tr.find("td")
        try:
          
          tds = results.find("table").find("tr").find_all("td")
          poster_infostrings = extractNavigableStrings(tds[0])
          HPstrings = extractNavigableStrings(tds[1])
          
          x = 0
          for info in poster_infostrings:
            print(x)
            x = x + 1
            print(info)
            
          #fucking commit already
          print("Extracted")
          
          post = {}

          try:
            post['name'] = poster_infostrings[1]
            post['activity'] = poster_infostrings[7].split(":")[1]
            post['merit'] = poster_infostrings[8].split(":")[1] 
          except Exception as e:
            print('[-]-----------------')

          try:
            date = HPstrings[8].split(',')
            day = date[0].split()
            post['date'] = str(day[0]+ " "+ day[1] + " " +date[1])
            strings = HPstrings[17:-1]

            postdata = ""
            for s in strings:
              postdata += s

            post['postdata'] = s
          except Exception as e:
            print("[-]------------------")

          #pprint(post)
          print(x)
          x = x + 1   
          posts.insert_one(post)      

          print("------------------------")
          
        except Exception as e:
         
          pass
          
        print(link)
        print("-=-=-=-=-=-==--=")
    except Exception as e:
      print("***********")
  print(link)
  print("----------------------------------")
  
##############################################
#Function to extract all navigable strings from
#the headerpost and user banner
##############################################
def extractNavigableStrings(context):
    strings = []
    for e in context.children:
        if isinstance(e, NavigableString):
            strings.append(e)
        if isinstance(e, Tag):
            strings.extend(extractNavigableStrings(e))
    return strings

##############################################
#controller function for scraping operation
#first calls pagefinder function 
#second it calls scrapePage function
##############################################
def scrapeThread(thread, head, posts):
  req = ur.Request(thread, headers = head)
  con = ur.urlopen(req)
  page = con.read()
  soup = bs(page, "html.parser")
  
  div = soup.find_all('div')[1]
  
  #links to all pages in the thread
  baseurl = thread[:-1]
  allpagelinks = pagefinder(div, baseurl)
  
  for link in allpagelinks:
    scrapePage(link, head, posts)  
  
  print("---------------------------------\n")
    
###############################################
#Main function
##############################################
def main():
  
  headers = {'User-Agent' : 'Magic Browser'}
  
  try:
    client = MongoClient("localhost",27017)
    db = client.scrape
    collection = db.threadlinks
    results = collection.find()
    posts = db.postData
  
    #for result in results:
    for i in range(0,4):
      try:
        scrapeThread(results[i]['url'],headers,posts)
      except Exception as e:
        pass
  
  except Exception as e:
    print(e)
  
if(__name__ == '__main__'):
  main()
