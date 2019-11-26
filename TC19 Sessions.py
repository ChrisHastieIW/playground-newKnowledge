# This Python script can be used to scrape the website for Tableau Conference EU 2019
# The intention is to create a json file containing data for every session taking place

# The first section of this script explains some of the logic behind the commands we are doing
# The second part (after ##########) is the script to actually scrape the data

# If a package does not import, it may require installing.
# Open a command prompt and use pip install to install a package, for example:
# pip install requests
# pip install bs4

import requests
import urllib.request
import time
import re
from bs4 import BeautifulSoup
import json

# Establish connection
url = r'https://tc-europe19.tableau.com/learn/sessions'
response = requests.get(url)

# Retrieves html from site
soup = BeautifulSoup(response.text, 'html.parser')

# Prints the html nicely
print(soup.prettify())

# Browse the head/body contents, changing the index to browse
soup.body.contents[3]

# We find out main data is contained within contents 5
soup.body.contents[5]

# Look at the name/attributes to determine how this could potentially be automatically identified
soup.body.contents[5].name
soup.body.contents[5].attrs

# Compare this against all children, by name
for child in soup.body.children :
    print(child.name)

# Compare this against all children with the correct name, by class
for child in soup.body.children :
    if child.name != None : print('{0} : {1}'.format(child.name, child.attrs))

# It appears the data is only within the tag <div class="l-page">
soup.body.contents[5].attrs

# We could use this approach to drop down the levels to find what we need
# This is a long winded approach but gets us to the tag <div class="view-content">
soup.body.contents[5].contents[3].contents[1].contents[3].contents[1].contents[1]\
    .contents[1].contents[1].contents[1].contents[1].contents[1].contents[1].contents[3].contents[1].contents[3]

# We can skip a lot of this by using find, once we know what to look for
# Not that the search uses class_ instead of class as the latter is a Python-reserved CSS attribute
soup.find('div', class_='view-content')

# Another approach could be to use one of our target attributes and navigate back up the tree
soup.find('div', class_='speakers')
soup.find('div', class_='speakers').attrs
soup.find('div', class_='speakers').parent
soup.find('div', class_='speakers').parent.attrs
soup.find('div', class_='speakers').parent.parent
soup.find('div', class_='speakers').parent.parent.attrs
soup.find('div', class_='speakers').parent.parent.parent
soup.find('div', class_='speakers').parent.parent.parent.attrs

# This is sufficient to see that each individual TC session is held within a tag <div class="accordion__item">
# We use the find_all function to create a list of all sessions
soup.find_all('div', class_='accordion__item')

# Using a single entry, we can get an understanding of how this is built
soup.find_all('div', class_='accordion__item')[6]


# We can also list names and attributes for each tag, including class
for child in soup.find_all('div', class_='accordion__item')[6].children :
    if child.name != None :
        print('{0} : {1}'.format(child.name, child.attrs))
        print(child['class'])

# We can retrieve the header text from the h3 tag. If necessary, we could specify which h3 tag with class_=
soup.find_all('div', class_='accordion__item')[6].find('h3').text

# We can retrieve the session description text from the div tag. If necessary, we could specify which div tag with class_=
soup.find_all('div', class_='accordion__item')[6].find('div').text

soup.find_all('div', class_='accordion__item')[6].find('div').contents[3].text

# The content is divided into subsections. We review this structure first
for child in soup.find_all('div', class_='accordion__item')[6].find('div').children :
    if child.name != None :
        print('{0} : {1}'.format(child.name, child.attrs))

# Each child breaks down into grandchildren, most notably a label and value
for child in soup.find_all('div', class_='accordion__item')[6].find('div').children :
    if child.name != None :
        print('{0} : {1}'.format(child.name, child.attrs))
        for grandchild in child.children :
            if grandchild.name != None : print('{0} : {1}'.format(grandchild.name, grandchild.attrs))


# Isolate these tags. Notice that speakers concatenates badly so needs to be addressed
for child in soup.find_all('div', class_='accordion__item')[6].find('div').children :
    if child.name == 'div' :
        print('{0}{1}'.format(child.find('strong').text, child.find('span').text))

# We include some regex here when identifying the speakers, creating a list
for child in soup.find_all('div', class_='accordion__item')[6].find('div').children :
    if child.name == 'div' :
        if child['class'] == ['speakers']:
            speakersList = []
            for speaker in child.find_all('div', class_=re.compile(r'field__item'+'\s.*')) :
                speakersList.append(speaker.text)
            print('{0}{1}'.format(child.find('strong').text, speakersList))
        else :
            print('{0}{1}'.format(child.find('strong').text, child.find('span').text))

# Now we can put this all together into a single semi-structure
sessionsList = []
for session in soup.find_all('div', class_='accordion__item') :
    sessionTitle = session.find('h3').text
    sessionDescription = session.find('div').find('div').previous_sibling
    sessionData = {"Title": sessionTitle
        , "Description": sessionDescription}

    for child in session.find('div').children :
        if child.name == 'div' :
            if child['class'] == ['speakers']:
                speakersList = []
                for speaker in child.find_all('div', class_=re.compile(r'field__item'+'\s.*')) :
                    speakersList.append(speaker.text)
                sessionData[child.find('strong').text[:-1]] = speakersList
            else :
                sessionData[child.find('strong').text[:-1]] = child.find('span').text

    sessionsList.append(sessionData)

# Unfortunately this only reaches the first page!
len(sessionsList)

# The URL may always default to the first page, however there are links to other pages at the bottom.
# We identify these links first, and can spot them near the bottom of this code.
soup.body.contents[5]

# We can isolate this by finding all ul tags where the class == 'pager'
soup.find_all('ul', class_='pager')

# However this picks up some undesirables too. We can reduce that by searching directly for links
soup.find('ul', class_='pager').find_all('a')

# We build each of these links into a unique list
links = []
for pager in soup.find('ul', class_='pager').find_all('a'):
    link = pager.get('href')
    if link not in links :
        links.append(link)


#####################################################################################################################################

# Now all that remains is to loop through the whole thing
url = r'https://tc-europe19.tableau.com/learn/sessions'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

links = []
for pager in soup.find('ul', class_='pager').find_all('a'):
    link = pager.get('href')
    if link not in links :
        links.append(link)

#Include default page
defaultLink = re.search('(.*)\?.?', links[0]).group(1)
links.insert(0, defaultLink)

mainURL = url.replace(defaultLink, '')

sessionsList = []
for currentLink in links :
    responsePage = requests.get(mainURL+currentLink)
    soupPage = BeautifulSoup(responsePage.text, 'html.parser')
    for session in soupPage.find_all('div', class_='accordion__item') :
        sessionTitle = session.find('h3').text
        sessionDescription = session.find('div').find('div').previous_sibling
        sessionData = {"Title": sessionTitle.strip()
            , "Description": sessionDescription.strip()}

        for child in session.find('div').children :
            if child.name == 'div' :
                if child['class'] == ['speakers']:
                    speakersList = []
                    for speaker in child.find_all('div', class_=re.compile(r'field__item'+'\s.*')) :
                        speakersList.append(speaker.text.strip())
                    sessionData[child.find('strong').text[:-1]] = speakersList
                else :
                    sessionData[child.find('strong').text[:-1]] = child.find('span').text.strip()

        sessionsList.append(sessionData)

# View length of sessionList
len(sessionsList)

with open(r'Web Scraping/TC19 Sessions Output.json', 'w') as outfile:
    json.dump(sessionsList, outfile)


#####################################################################################################################################
