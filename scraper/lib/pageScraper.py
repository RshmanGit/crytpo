from bs4 import BeautifulSoup as bs
import urllib.request as ur
import pymongo
from pymongo import MongoClient
import pprint
import time
import datetime
import optparse

##################################
#Main Functions
##################################
def main():
  boardlist = ['https://bitcointalk.org/index.php?board=1.0', 'https://bitcointalk.org/index.php?board=8.0']
  headers = {'User-Agent' : "Magic Browser"}
  
  #pymongo configurations
  client = MongoClient("localhost",27017)
  db = client.scrape
  collection = db.threadlinks
  
  for board in boardlist:
    scrapeBoard(board, headers,collection)
  
  return(0) 

####################################
#Finds number of pages in each board
#stores them in a list ans passes to 
#a function which will scrape all
#pages for the content
####################################
def scrapeBoard(board, head, posts):
  iter = 40
  
  try:
    pagelist = []
    baseurl = board[:-1]
    
    #find the last page index
    req = ur.Request(board,headers = head)
    con = ur.urlopen(req)
    page = con.read()
    soup = bs(page,"html.parser")
    divs = soup.find_all('div')
    caught = divs[1]
    numtable = caught.find_all('table')[1]
    last_number = numtable.find_all('b')[1].next_sibling
    last_page = (int(last_number.string) * iter) - iter
    
    i=0
    while(i <= last_page):
      new_url = baseurl + str(i)
      #print(new_url)
      pagelist.append(new_url)
      i = i + iter
    
    xntr = 0
    for page in pagelist:
      #print("[+]-------\n")
      scrapePage(page, head, xntr, posts)
      xntr = xntr + 1
    
  except Exception as e:
    print(e)
    
##########################################
#finds the href url from the tables of each
#page and the dumps em in Mongo
##########################################
def scrapePage(url, head, ad, posts):
  threadlist = []
  try:
    time.sleep(0.2)
    print("[+]Scraping page: "+str(url))
    req = ur.Request(url,headers = head)
    con = ur.urlopen(req)
    page = con.read()
    soup = bs(page, "html.parser")
    
    divs = soup.find_all('div')
    caught = divs[1]
    
    if(ad == 0):
      posttable = caught.find_all("div","tborder")[1].find("table")
    else:
      posttable = caught.find_all("div","tborder")[0].find("table")
      
    for post in posttable:
      try:
        subject = post.find("span").a.get("href")
        print(subject)
        threadlist.append(subject)
        post = {
          "url" : subject
        }
        posts.insert_one(post)
     
      except Exception as e:
        print("[-]No post found int row")
  
  except Exception as e:
    print(e)

###########################################
if __name__ == "__main__":
  main()
