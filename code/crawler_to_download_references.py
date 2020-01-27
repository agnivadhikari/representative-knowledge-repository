import requests
import bs4
from bs4 import BeautifulSoup
import time
import re
def read_and_download_files():
  beginning_year = 2013
  beginning_range = 5
  for i in range(beginning_range):
    yearwise_file = 'paper_dois/'+str(beginning_year+i)+'.txt'
    year_str = str(beginning_year+i)
    with open(yearwise_file,"r") as f:
      for doi in f.readlines():
        #request_str = 'http://ieeexplore.ieee.org/document/'+str(paper_identifier)+'/references#references'
        url = 'https://ieeexplore.ieee.org/xpl/dwnldReferences?arnumber='+str(doi)
        print(url)
        downloaded_file_name = ('downloaded_references/'+year_str+'/'+str(doi)).strip()
        print(downloaded_file_name)
        page = requests.get(url) # for web crawling and saving the files to be processed later
        
        #print(page.text)
        #text = page.text.replace('\n\t\t\n\t\t',',').replace('\n\t\t\n\t    \t\t\t\n\t\t','\n').replace('&#034;','"')
        soup = BeautifulSoup(page.text,'html5lib')
        body = soup.body
        text = body.text.replace('\n\t\t\n\t\t',',').replace('\n\t\t\n\t    \t\t\t\n\t\t','\n').replace('\n\t\t\n\t    \t\t\t\n\t\t','').replace('\n\t\n\n','')
        #.replace('\n\n\t\t\n\t    \t\t\t\n\t\t','')
        text = re.sub(r'^$\n', '', text, flags=re.MULTILINE)
        #print(text)
        with open(downloaded_file_name,'w') as downloaded_file:
          downloaded_file.write(text)
        
      print('########### Completed downloading for year '+year_str+' ################')

def main():
  read_and_download_files()
  
if __name__=="__main__":
  main()
