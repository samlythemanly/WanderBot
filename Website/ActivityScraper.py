from bs4 import BeautifulSoup
import requests
from math import ceil
import datetime as dt
import re
import mysql.connector
import sys
sys.path.append("..")
from private_info import DB_HOST, DB_USER, DB_PASSWORD, DB_CATALOG

''' 
    Activity Scraper.

Scrape all the top posts from the site and update DBs accordingly.
In order to avoid DOSing the site, we export a pickle object at the end of
  a successful scrape to be reused next time. (development only.)

Scraper will format the data as a list of character objects.
  activityList = [
      {
        id: int
        name: str
        postCount: int
      },
      ...
  ]
'''

# Consts
START_INDEX = 0
MAX_RESULTS_PER_PAGE = 50

def main():
  print(f"\nRUN AT: {dt.datetime.now()}\n**************************************\nStarting up!")
  
  activityList = []
  # Request the first page
  result = requests.get(createURL(MAX_RESULTS_PER_PAGE,0))
  print("Calculating metadata")
  #Figure out how many pages there are 
  total_pages = ceil(int(getTotalMembers(result.content)) / MAX_RESULTS_PER_PAGE)
  # Don't forget to scrape the first page
  print("Scraping page 0")
  scrapePage(result.content, activityList)
  for page in range(1,total_pages+1): # Everyone knows arrays start at 1.
    print(f"Scraping page {page}")
    url = createURL(MAX_RESULTS_PER_PAGE, page)
    result = requests.get(url)
    scrapePage(result.content, activityList)
  print(f"Finished scraping. Sanity Check: {len(activityList)} total scraped data")
  updateDatabase(activityList)
  return

def getTotalMembers(data):
  print("Getting total memebers...", end='')
  soup = BeautifulSoup(data, 'html.parser')
  # Figure out how many members there are using the pagination_pagetxt class
  paginatorField = soup.find('span', {'class':'pagination_pagetxt'})
  if paginatorField:
    hrefField = paginatorField.find('a')['href']
    totalMembers = hrefField.split(',')[1] # super fucking hacky I know...
    print(f"done. {totalMembers} total members")
  else:
    totalMembers = MAX_RESULTS_PER_PAGE # maximum results displayed in one page. Reaching this block means there's no pagination
    print(f"done. All members fit in a page, so...50?")
  return totalMembers

def scrapePage(data, activityList):
  soup = BeautifulSoup(data, 'html.parser')
  table = soup.find('table', border=0)
  raw_rows = table.findAll('tr')
  for row in raw_rows:
    nameField = row.find('td', {"class": "row4 name"})
    postCountField = row.find('td', {"class": "row4 posts"})
    if nameField and postCountField:
      characterData = {}
      characterData["id"] = int(re.findall(r"\d{1,}$",nameField.find('a')['href'])[0])
      characterData["name"] = str(nameField.string)
      characterData["postCount"] = int(postCountField.string)
      activityList.append(characterData)

def updateDatabase(activityList):
  mydb = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    passwd=DB_PASSWORD,
    database=DB_CATALOG
  )

  flag = 1 
  mycursor = mydb.cursor(dictionary=True)
  mycursor.execute("SELECT * FROM Characters")
  # Grab all currently known characters from the database
  characters = mycursor.fetchall()

  #check post count
  flagged_chars = []
  updated_chars = []
  for activity in activityList:
    char_found = False
    #print(f"Working on {activity['name']}")
    for character in characters:
      if character['ID'] == activity['id']:
        char_found = True
        if character["total_posts"] < activity['postCount']: # we want to update this character
        #ActivityHistory update
          sql = "INSERT INTO ActivityHistory (characterID, old_post_count, new_post_count) VALUES (%s, %s, %s)"
          val = (character["ID"], character["total_posts"], activity['postCount'])
          mycursor.execute(sql, val)
          mydb.commit()
          #print(mycursor.rowcount, f"record(s) affected for {activity['name']} in ActivityHistory table")

          #character montly post increment
          newPosts = character["posts_this_month"] + (activity['postCount'] - character["total_posts"])
          sql = "UPDATE Characters SET total_posts = %s, posts_this_month = %s WHERE ID = %s"
          val = (activity['postCount'], newPosts, character["ID"])
          mycursor.execute(sql, val)
          mydb.commit()
          #print(mycursor.rowcount, f"record(s) affected for {activity['name']} in Characters table")
          updated_chars.append((activity['id'], activity['name'], activity['postCount'], activity['postCount']))
          flag = 0

      else:
        continue
    if not char_found:
      # This is a new character, we want to insert it
      # print(f"Flagging {activity['name']} to be inserted.")
      flagged_chars.append((activity['id'], activity['name'], activity['postCount'], activity['postCount']))
  if len(flagged_chars) >= 1:
    sql = "INSERT INTO Characters (id, name, total_posts, posts_this_month) VALUES (%s, %s, %s, %s)"
    mycursor.executemany(sql, flagged_chars)
    mydb.commit()
    print(mycursor.rowcount, " new characters were inserted.")
  if flag:
    print(f'\n*No post counts updated or characters inserted*')
  else:
    print(f"\n**** {len(updated_chars)} Characters updated: ")
    for c in updated_chars:
      print(f"{c[0]} - '{c[1]}' now has {c[2]} posts.")
    print(f"**** {len(flagged_chars)} new characters added: ")
    for c in flagged_chars:
      print(f"{c[0]} - '{c[1]}'")

def createURL(maxResultsPerPage, pageNumber):
  ind = pageNumber * maxResultsPerPage
  return f"https://wanderingwithwerewolves.jcink.net/index.php?&act=Members&photoonly=&name=&name_box=all&max_results={MAX_RESULTS_PER_PAGE}&filter=ALL&sort_order=desc&sort_key=posts&st={ind}"

if __name__ == '__main__':
  main()