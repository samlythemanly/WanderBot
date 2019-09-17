from bs4 import BeautifulSoup
import requests
from math import ceil
import pickle
import re
import mysql.connector

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
  print("Starting up!")
  try:
    with open("activityList.p", "rb") as cache_in:
      activityList = pickle.load(cache_in)
  except FileNotFoundError:
    activityList = []
    print("Could not find cached data, scraping again")
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
    with open("activityList.p","wb") as cache_out:
      pickle.dump( activityList, cache_out )
  updateDatabase(activityList)
  #print(activityList)
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
    host="",
    user="",
    passwd="", 
    database=""
  )

  flag = 1
  mycursor = mydb.cursor()
  mycursor.execute("SELECT * FROM Characters")
  characters = mycursor.fetchall()
  newCharactersCount = len(activityList) - len(characters)

  #insert new characters
  if newCharactersCount > 0 :
    val = []
    newCharacters = activityList[-newCharactersCount:]
    for character in newCharacters:
      val.append((character['id'], character['name'], character['postCount'], character['postCount']))

    sql = "INSERT INTO Characters (id, name, total_posts, posts_this_month) VALUES (%s, %s, %s, %s)"
    mycursor.executemany(sql, val)
    mydb.commit()
    print(mycursor.rowcount, val, " was inserted.")
    flag = 0

  #check post count
  for character in characters:
    for activity in activityList:
      if character[0] == activity['id'] and character[3] < activity['postCount']:
        #update database
        #character[]
        #0 id
        #1 name
        #2 DiscordID
        #3 total_posts
        #4 posts_this_month

        #ActivityHistory update
        sql = "INSERT INTO ActivityHistory (characterID, old_post_count, new_post_count) VALUES (%s, %s, %s)"
        val = (character[0], character[3], activity['postCount'])
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record(s) affected")

        #character post increment
        newPosts = character[4] + (character[3] - activity['postCount'])
        sql = "UPDATE Characters SET total_posts = %s, posts_this_month = %s WHERE id = %s"
        val = (activity['postCount'], newPosts, character[0])

        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record(s) affected")
        flag = 0

      else:
        continue
  if flag:
    print(f'No post counts updated or characters inserted')

def createURL(maxResultsPerPage, pageNumber):
  ind = pageNumber * maxResultsPerPage
  return f"https://wanderingwithwerewolves.jcink.net/index.php?&act=Members&photoonly=&name=&name_box=all&max_results={MAX_RESULTS_PER_PAGE}&filter=ALL&sort_order=desc&sort_key=posts&st={ind}"

if __name__ == '__main__':
  main()