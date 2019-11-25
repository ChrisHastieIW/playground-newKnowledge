
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

len(sessionsList)

with open(r'Web Scraping/TC19 Sessions Output.json', 'w') as outfile:
    json.dump(sessionsList, outfile)


#####################################################################################################################################


































# Another way to retrieve all pages is to find a way around the ajax fetch
# That is to say, the page is driven by javascript and we need to recreate this in our connection

# Visit the website in Chrome, open developer tools and navigate to "network".
# Notice that clicking on a page generates an ajax entry (look under the XHR tab if there are several )
# Select the ajax to see the preview. Navigate the subheader to "Headers"
# Collapse the "General", "Response Headers" and "Request Headers" areas to see the "Form Data"
# Hopefully this is a simple list of parameters which we can recreate as a dictionary using copy paste and formatting
# Scroll down to see the raw copy and paste for each of the three pages


rawCopyAndPaste = r'''view_name: sessions_list
view_display_id: random
view_args:
view_path: node/236
view_base_path:
view_dom_id: 4acf6c3f5f06ae9899558e5ff92ae10f
pager_element: 0
page: 1
ajax_html_ids[]: block-block-3
ajax_html_ids[]: block-menu-block-2
ajax_html_ids[]: block-delta-blocks-page-title
ajax_html_ids[]: page-title
ajax_html_ids[]: block-cck-blocks-field-hero-intro
ajax_html_ids[]: main-content
ajax_html_ids[]: block-cck-blocks-field-sections
ajax_html_ids[]: block-views-exp-sessions-list-random
ajax_html_ids[]: views-exposed-form-sessions-list-random
ajax_html_ids[]: edit-query-wrapper
ajax_html_ids[]: edit-query
ajax_html_ids[]: edit-type-wrapper
ajax_html_ids[]: edit-type-1
ajax_html_ids[]: edit-type-2
ajax_html_ids[]: edit-type-3
ajax_html_ids[]: edit-type-4
ajax_html_ids[]: edit-type-5
ajax_html_ids[]: edit-type-6
ajax_html_ids[]: edit-type-7
ajax_html_ids[]: edit-type-8
ajax_html_ids[]: edit-track-wrapper
ajax_html_ids[]: edit-track-1
ajax_html_ids[]: edit-track-2
ajax_html_ids[]: edit-track-3
ajax_html_ids[]: edit-track-4
ajax_html_ids[]: edit-track-5
ajax_html_ids[]: edit-track-6
ajax_html_ids[]: edit-track-7
ajax_html_ids[]: edit-level-wrapper
ajax_html_ids[]: edit-level
ajax_html_ids[]: edit-level-1
ajax_html_ids[]: edit-level-2
ajax_html_ids[]: edit-level-3
ajax_html_ids[]: edit-level-4
ajax_html_ids[]: edit-submit-sessions-list
ajax_html_ids[]: edit-reset
ajax_html_ids[]: block-nodeblock-554
ajax_html_ids[]: node-554
ajax_html_ids[]: session-563812
ajax_html_ids[]: session-539446
ajax_html_ids[]: session-561573
ajax_html_ids[]: session-567350
ajax_html_ids[]: session-542391
ajax_html_ids[]: session-554431
ajax_html_ids[]: session-561564
ajax_html_ids[]: session-546475
ajax_html_ids[]: session-539162
ajax_html_ids[]: session-543873
ajax_html_ids[]: session-567353
ajax_html_ids[]: session-539483
ajax_html_ids[]: session-538830
ajax_html_ids[]: session-546601
ajax_html_ids[]: session-554464
ajax_html_ids[]: session-539417
ajax_html_ids[]: session-561505
ajax_html_ids[]: session-560835
ajax_html_ids[]: session-561560
ajax_html_ids[]: session-538972
ajax_html_ids[]: session-540954
ajax_html_ids[]: session-561555
ajax_html_ids[]: session-567352
ajax_html_ids[]: session-539519
ajax_html_ids[]: session-540891
ajax_html_ids[]: session-554427
ajax_html_ids[]: session-538891
ajax_html_ids[]: session-539451
ajax_html_ids[]: session-567726
ajax_html_ids[]: session-538935
ajax_html_ids[]: session-539465
ajax_html_ids[]: session-539510
ajax_html_ids[]: session-539516
ajax_html_ids[]: session-567189
ajax_html_ids[]: session-539476
ajax_html_ids[]: session-539491
ajax_html_ids[]: session-539467
ajax_html_ids[]: session-546396
ajax_html_ids[]: session-539503
ajax_html_ids[]: session-543874
ajax_html_ids[]: session-546476
ajax_html_ids[]: session-561566
ajax_html_ids[]: session-550268
ajax_html_ids[]: session-539462
ajax_html_ids[]: session-554467
ajax_html_ids[]: session-540065
ajax_html_ids[]: session-560516
ajax_html_ids[]: session-538923
ajax_html_ids[]: session-539420
ajax_html_ids[]: session-566979
ajax_html_ids[]: block-nodeblock-173
ajax_html_ids[]: node-173
ajax_html_ids[]: block-block-1
ajax_html_ids[]: block-menu-menu-footer-menu
ajax_html_ids[]: block-block-2
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_page_state[theme]: tc_omega
ajax_page_state[theme_token]: HG35lOTWxLLJQ0fO9k9CoJRQTVOXBAGmghk3-Jp5Vm0
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.menus.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.messages.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.theme.css]: 1
ajax_page_state[css][sites/all/modules/date/date_api/date.css]: 1
ajax_page_state[css][sites/all/modules/date/date_popup/themes/datepicker.1.7.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/field/field.theme.css]: 1
ajax_page_state[css][sites/all/modules/logintoboggan/logintoboggan.css]: 1
ajax_page_state[css][modules/node/node.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/search/search.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.theme.css]: 1
ajax_page_state[css][sites/all/modules/youtube/css/youtube.css]: 1
ajax_page_state[css][sites/all/modules/views/css/views.css]: 1
ajax_page_state[css][sites/all/components/tc-components/build/css/style.min.css]: 1
ajax_page_state[css][sites/all/modules/tc_custom/tc_likes/tc_likes.css]: 1
ajax_page_state[css][sites/all/modules/ctools/css/ctools.css]: 1
ajax_page_state[css][sites/all/modules/views_ajax_overlay/css/views_ajax_overlay.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/libraries/magnific/magnific.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/css/tc-omega.styles.css]: 1
ajax_page_state[js][0]: 1
ajax_page_state[js][public://google_tag/google_tag.script.js]: 1
ajax_page_state[js][sites/all/libraries/modernizr/modernizr.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/jquery/1.10/jquery.min.js]: 1
ajax_page_state[js][misc/jquery-extend-3.4.0.js]: 1
ajax_page_state[js][misc/jquery.once.js]: 1
ajax_page_state[js][misc/drupal.js]: 1
ajax_page_state[js][sites/all/themes/omega/omega/omega/js/no-js.js]: 1
ajax_page_state[js][sites/all/libraries/easing/jquery.easing.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/ui/external/jquery.cookie.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/misc/jquery.form.min.js]: 1
ajax_page_state[js][misc/ajax.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/js/jquery_update.js]: 1
ajax_page_state[js][sites/all/modules/admin_menu/admin_devel/admin_devel.js]: 1
ajax_page_state[js][sites/all/modules/defer_image/defer_image.js]: 1
ajax_page_state[js][sites/all/modules/tc_custom/tc_likes/tc_likes.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv-printshiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/selectivizr/selectivizr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/respond/respond.min.js]: 1
ajax_page_state[js][sites/all/modules/better_exposed_filters/better_exposed_filters.js]: 1
ajax_page_state[js][//f.vimeocdn.com/js/froogaloop2.min.js]: 1
ajax_page_state[js][sites/all/modules/views/js/base.js]: 1
ajax_page_state[js][misc/progress.js]: 1
ajax_page_state[js][sites/all/modules/views/js/ajax_view.js]: 1
ajax_page_state[js][sites/all/modules/views_ajax_overlay/js/views_ajax_overlay.js]: 1
ajax_page_state[js][sites/all/modules/eloqua_api/js/tracking.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/matchmedia/matchmedia.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/magnific/jquery.magnific.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/placeholdr/placeholdr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/js/tc-omega.helpers.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/vendor.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/scripts.js]: 1
ajax_page_state[jquery_version]: 1.10'''

print(rawCopyAndPaste)

rawCopyAndPaste.split('\n')[0].split(':')

payload = {}
for line in rawCopyAndPaste.split('\n') :
    payload[line.split(':')[0]] = line.split(':')[1][1:] # Remove starting space

response = requests.post(r'https://tc-europe19.tableau.com/views/ajax', data={'page':1})

response.json()



# Establish connection to retrieve headers
url = r'https://tc-europe19.tableau.com/learn/sessions'
response = requests.get(url)
requests.Session().headers

# We need to establish the right headers. We copy and paste these from Chrome developer tools and convert to a list
requestHeadersFromSite = ''':authority: tc-europe19.tableau.com
:method: POST
:path: /views/ajax
:scheme: https
accept: application/json, text/javascript, */*; q=0.01
accept-encoding: gzip, deflate, br
accept-language: en,en-US;q=0.9
content-length: 8702
content-type: application/x-www-form-urlencoded; charset=UTF-8
cookie: newGACookie=GA1.2.1561492569.1491902675; _hp2_id.1263170756=%7B%22userId%22%3A%223750194190685493%22%2C%22pageviewId%22%3A%222627580710270186%22%2C%22sessionId%22%3A%220280963038905903%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%223.0%22%7D; _ga=GA1.2.573922456.1491902675; podid=082871a7a79f9651db8fd0ef01fd7bca; coveo_visitorId=409d6346-19ff-4f15-a932-6cf697cd626d; _fbp=fb.1.1549357382664.166273231; Hm_lvt_953802b9e5c30659e0b8368ebfe2ea1b=1549971724,1549972356,1549976300,1550161222; ELOQUA=GUID=40CE5849C35643239CEC0AF9A1A9BB70; intellimizeEUID=2482e6d6a7.1557912444; _gcl_au=1.1.1659088109.1557912445; seerid=125480.85998518302; has_js=1; seerses=e; seerses=e; ly_segs=%7B%22digital_all_existing_leads%22%3A%22digital_all_existing_leads%22%2C%22digital_priming_exclusion_partner%22%3A%22digital_priming_exclusion_partner%22%2C%22prospects_not_primed_90_days%22%3A%22prospects_not_primed_90_days%22%2C%22enterprise_users_%22%3A%22enterprise_users_%22%2C%22ly_moderately_engaged_visitor%22%3A%22ly_moderately_engaged_visitor%22%2C%22active_smb_desktop_trialers%22%3A%22active_smb_desktop_trialers%22%2C%22tc_past_attendees%22%3A%22tc_past_attendees%22%2C%22tc19_core_customers%22%3A%22tc19_core_customers%22%2C%22ip_company_size_under_50%22%3A%22ip_company_size_under_50%22%2C%22high_slice_scores%22%3A%22high_slice_scores%22%2C%22persona_business_user%22%3A%22persona_business_user%22%2C%22persona_analyst%22%3A%22persona_analyst%22%2C%22tc18_target_audience_customers%22%3A%22tc18_target_audience_customers%22%2C%22nondesktop_customers%22%3A%22nondesktop_customers%22%2C%22customers%22%3A%22customers%22%2C%22ly_frequent_user%22%3A%22ly_frequent_user%22%2C%22smt_power%22%3A%22smt_power%22%2C%22all%22%3A%22all%22%7D; _gid=GA1.2.259337272.1565346476; PathforaPageView=5; _dc_gtm_UA-625217-6=1
origin: https://tc-europe19.tableau.com
referer: https://tc-europe19.tableau.com/learn/sessions
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36
x-requested-with: XMLHttpRequest'''

requestHeadersFromSite.split('\n')




'''
Page 0

view_name: sessions_list
view_display_id: random
view_args:
view_path: node/236
view_base_path:
view_dom_id: 4acf6c3f5f06ae9899558e5ff92ae10f
pager_element: 0
ajax_html_ids[]: block-block-3
ajax_html_ids[]: block-menu-block-2
ajax_html_ids[]: block-delta-blocks-page-title
ajax_html_ids[]: page-title
ajax_html_ids[]: block-cck-blocks-field-hero-intro
ajax_html_ids[]: main-content
ajax_html_ids[]: block-cck-blocks-field-sections
ajax_html_ids[]: block-views-exp-sessions-list-random
ajax_html_ids[]: views-exposed-form-sessions-list-random
ajax_html_ids[]: edit-query-wrapper
ajax_html_ids[]: edit-query
ajax_html_ids[]: edit-type-wrapper
ajax_html_ids[]: edit-type-1
ajax_html_ids[]: edit-type-2
ajax_html_ids[]: edit-type-3
ajax_html_ids[]: edit-type-4
ajax_html_ids[]: edit-type-5
ajax_html_ids[]: edit-type-6
ajax_html_ids[]: edit-type-7
ajax_html_ids[]: edit-type-8
ajax_html_ids[]: edit-track-wrapper
ajax_html_ids[]: edit-track-1
ajax_html_ids[]: edit-track-2
ajax_html_ids[]: edit-track-3
ajax_html_ids[]: edit-track-4
ajax_html_ids[]: edit-track-5
ajax_html_ids[]: edit-track-6
ajax_html_ids[]: edit-track-7
ajax_html_ids[]: edit-level-wrapper
ajax_html_ids[]: edit-level
ajax_html_ids[]: edit-level-1
ajax_html_ids[]: edit-level-2
ajax_html_ids[]: edit-level-3
ajax_html_ids[]: edit-level-4
ajax_html_ids[]: edit-submit-sessions-list
ajax_html_ids[]: edit-reset
ajax_html_ids[]: block-nodeblock-554
ajax_html_ids[]: node-554
ajax_html_ids[]: session-539483
ajax_html_ids[]: session-539510
ajax_html_ids[]: session-539462
ajax_html_ids[]: session-539440
ajax_html_ids[]: session-554472
ajax_html_ids[]: session-540473
ajax_html_ids[]: session-539519
ajax_html_ids[]: session-567351
ajax_html_ids[]: session-539415
ajax_html_ids[]: session-539489
ajax_html_ids[]: session-554469
ajax_html_ids[]: session-539503
ajax_html_ids[]: session-539506
ajax_html_ids[]: session-538972
ajax_html_ids[]: session-567726
ajax_html_ids[]: session-563957
ajax_html_ids[]: session-539427
ajax_html_ids[]: session-538923
ajax_html_ids[]: session-546273
ajax_html_ids[]: session-539473
ajax_html_ids[]: session-539420
ajax_html_ids[]: session-554464
ajax_html_ids[]: session-554470
ajax_html_ids[]: session-539479
ajax_html_ids[]: session-561555
ajax_html_ids[]: session-538822
ajax_html_ids[]: session-561557
ajax_html_ids[]: session-538978
ajax_html_ids[]: session-554463
ajax_html_ids[]: block-nodeblock-173
ajax_html_ids[]: node-173
ajax_html_ids[]: block-block-1
ajax_html_ids[]: block-menu-menu-footer-menu
ajax_html_ids[]: block-block-2
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_page_state[theme]: tc_omega
ajax_page_state[theme_token]: ospgnzzGIaNCjfHfUkJ1pweInUJJuaO7-2f3uJ2d8gs
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.menus.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.messages.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.theme.css]: 1
ajax_page_state[css][sites/all/modules/date/date_api/date.css]: 1
ajax_page_state[css][sites/all/modules/date/date_popup/themes/datepicker.1.7.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/field/field.theme.css]: 1
ajax_page_state[css][sites/all/modules/logintoboggan/logintoboggan.css]: 1
ajax_page_state[css][modules/node/node.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/search/search.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.theme.css]: 1
ajax_page_state[css][sites/all/modules/youtube/css/youtube.css]: 1
ajax_page_state[css][sites/all/modules/views/css/views.css]: 1
ajax_page_state[css][sites/all/components/tc-components/build/css/style.min.css]: 1
ajax_page_state[css][sites/all/modules/tc_custom/tc_likes/tc_likes.css]: 1
ajax_page_state[css][sites/all/modules/ctools/css/ctools.css]: 1
ajax_page_state[css][sites/all/modules/views_ajax_overlay/css/views_ajax_overlay.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/libraries/magnific/magnific.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/css/tc-omega.styles.css]: 1
ajax_page_state[js][0]: 1
ajax_page_state[js][public://google_tag/google_tag.script.js]: 1
ajax_page_state[js][sites/all/libraries/modernizr/modernizr.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/jquery/1.10/jquery.min.js]: 1
ajax_page_state[js][misc/jquery-extend-3.4.0.js]: 1
ajax_page_state[js][misc/jquery.once.js]: 1
ajax_page_state[js][misc/drupal.js]: 1
ajax_page_state[js][sites/all/themes/omega/omega/omega/js/no-js.js]: 1
ajax_page_state[js][sites/all/libraries/easing/jquery.easing.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/ui/external/jquery.cookie.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/misc/jquery.form.min.js]: 1
ajax_page_state[js][misc/ajax.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/js/jquery_update.js]: 1
ajax_page_state[js][sites/all/modules/admin_menu/admin_devel/admin_devel.js]: 1
ajax_page_state[js][sites/all/modules/defer_image/defer_image.js]: 1
ajax_page_state[js][sites/all/modules/tc_custom/tc_likes/tc_likes.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv-printshiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/selectivizr/selectivizr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/respond/respond.min.js]: 1
ajax_page_state[js][sites/all/modules/better_exposed_filters/better_exposed_filters.js]: 1
ajax_page_state[js][//f.vimeocdn.com/js/froogaloop2.min.js]: 1
ajax_page_state[js][sites/all/modules/views/js/base.js]: 1
ajax_page_state[js][misc/progress.js]: 1
ajax_page_state[js][sites/all/modules/views/js/ajax_view.js]: 1
ajax_page_state[js][sites/all/modules/views_ajax_overlay/js/views_ajax_overlay.js]: 1
ajax_page_state[js][sites/all/modules/eloqua_api/js/tracking.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/matchmedia/matchmedia.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/magnific/jquery.magnific.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/placeholdr/placeholdr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/js/tc-omega.helpers.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/vendor.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/scripts.js]: 1
ajax_page_state[jquery_version]: 1.10
'''

'''
Page 1

view_name: sessions_list
view_display_id: random
view_args:
view_path: node/236
view_base_path:
view_dom_id: 4acf6c3f5f06ae9899558e5ff92ae10f
pager_element: 0
page: 1
ajax_html_ids[]: block-block-3
ajax_html_ids[]: block-menu-block-2
ajax_html_ids[]: block-delta-blocks-page-title
ajax_html_ids[]: page-title
ajax_html_ids[]: block-cck-blocks-field-hero-intro
ajax_html_ids[]: main-content
ajax_html_ids[]: block-cck-blocks-field-sections
ajax_html_ids[]: block-views-exp-sessions-list-random
ajax_html_ids[]: views-exposed-form-sessions-list-random
ajax_html_ids[]: edit-query-wrapper
ajax_html_ids[]: edit-query
ajax_html_ids[]: edit-type-wrapper
ajax_html_ids[]: edit-type-1
ajax_html_ids[]: edit-type-2
ajax_html_ids[]: edit-type-3
ajax_html_ids[]: edit-type-4
ajax_html_ids[]: edit-type-5
ajax_html_ids[]: edit-type-6
ajax_html_ids[]: edit-type-7
ajax_html_ids[]: edit-type-8
ajax_html_ids[]: edit-track-wrapper
ajax_html_ids[]: edit-track-1
ajax_html_ids[]: edit-track-2
ajax_html_ids[]: edit-track-3
ajax_html_ids[]: edit-track-4
ajax_html_ids[]: edit-track-5
ajax_html_ids[]: edit-track-6
ajax_html_ids[]: edit-track-7
ajax_html_ids[]: edit-level-wrapper
ajax_html_ids[]: edit-level
ajax_html_ids[]: edit-level-1
ajax_html_ids[]: edit-level-2
ajax_html_ids[]: edit-level-3
ajax_html_ids[]: edit-level-4
ajax_html_ids[]: edit-submit-sessions-list
ajax_html_ids[]: edit-reset
ajax_html_ids[]: block-nodeblock-554
ajax_html_ids[]: node-554
ajax_html_ids[]: session-563812
ajax_html_ids[]: session-539446
ajax_html_ids[]: session-561573
ajax_html_ids[]: session-567350
ajax_html_ids[]: session-542391
ajax_html_ids[]: session-554431
ajax_html_ids[]: session-561564
ajax_html_ids[]: session-546475
ajax_html_ids[]: session-539162
ajax_html_ids[]: session-543873
ajax_html_ids[]: session-567353
ajax_html_ids[]: session-539483
ajax_html_ids[]: session-538830
ajax_html_ids[]: session-546601
ajax_html_ids[]: session-554464
ajax_html_ids[]: session-539417
ajax_html_ids[]: session-561505
ajax_html_ids[]: session-560835
ajax_html_ids[]: session-561560
ajax_html_ids[]: session-538972
ajax_html_ids[]: session-540954
ajax_html_ids[]: session-561555
ajax_html_ids[]: session-567352
ajax_html_ids[]: session-539519
ajax_html_ids[]: session-540891
ajax_html_ids[]: session-554427
ajax_html_ids[]: session-538891
ajax_html_ids[]: session-539451
ajax_html_ids[]: session-567726
ajax_html_ids[]: session-538935
ajax_html_ids[]: session-539465
ajax_html_ids[]: session-539510
ajax_html_ids[]: session-539516
ajax_html_ids[]: session-567189
ajax_html_ids[]: session-539476
ajax_html_ids[]: session-539491
ajax_html_ids[]: session-539467
ajax_html_ids[]: session-546396
ajax_html_ids[]: session-539503
ajax_html_ids[]: session-543874
ajax_html_ids[]: session-546476
ajax_html_ids[]: session-561566
ajax_html_ids[]: session-550268
ajax_html_ids[]: session-539462
ajax_html_ids[]: session-554467
ajax_html_ids[]: session-540065
ajax_html_ids[]: session-560516
ajax_html_ids[]: session-538923
ajax_html_ids[]: session-539420
ajax_html_ids[]: session-566979
ajax_html_ids[]: block-nodeblock-173
ajax_html_ids[]: node-173
ajax_html_ids[]: block-block-1
ajax_html_ids[]: block-menu-menu-footer-menu
ajax_html_ids[]: block-block-2
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_page_state[theme]: tc_omega
ajax_page_state[theme_token]: HG35lOTWxLLJQ0fO9k9CoJRQTVOXBAGmghk3-Jp5Vm0
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.menus.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.messages.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.theme.css]: 1
ajax_page_state[css][sites/all/modules/date/date_api/date.css]: 1
ajax_page_state[css][sites/all/modules/date/date_popup/themes/datepicker.1.7.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/field/field.theme.css]: 1
ajax_page_state[css][sites/all/modules/logintoboggan/logintoboggan.css]: 1
ajax_page_state[css][modules/node/node.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/search/search.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.theme.css]: 1
ajax_page_state[css][sites/all/modules/youtube/css/youtube.css]: 1
ajax_page_state[css][sites/all/modules/views/css/views.css]: 1
ajax_page_state[css][sites/all/components/tc-components/build/css/style.min.css]: 1
ajax_page_state[css][sites/all/modules/tc_custom/tc_likes/tc_likes.css]: 1
ajax_page_state[css][sites/all/modules/ctools/css/ctools.css]: 1
ajax_page_state[css][sites/all/modules/views_ajax_overlay/css/views_ajax_overlay.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/libraries/magnific/magnific.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/css/tc-omega.styles.css]: 1
ajax_page_state[js][0]: 1
ajax_page_state[js][public://google_tag/google_tag.script.js]: 1
ajax_page_state[js][sites/all/libraries/modernizr/modernizr.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/jquery/1.10/jquery.min.js]: 1
ajax_page_state[js][misc/jquery-extend-3.4.0.js]: 1
ajax_page_state[js][misc/jquery.once.js]: 1
ajax_page_state[js][misc/drupal.js]: 1
ajax_page_state[js][sites/all/themes/omega/omega/omega/js/no-js.js]: 1
ajax_page_state[js][sites/all/libraries/easing/jquery.easing.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/ui/external/jquery.cookie.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/misc/jquery.form.min.js]: 1
ajax_page_state[js][misc/ajax.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/js/jquery_update.js]: 1
ajax_page_state[js][sites/all/modules/admin_menu/admin_devel/admin_devel.js]: 1
ajax_page_state[js][sites/all/modules/defer_image/defer_image.js]: 1
ajax_page_state[js][sites/all/modules/tc_custom/tc_likes/tc_likes.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv-printshiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/selectivizr/selectivizr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/respond/respond.min.js]: 1
ajax_page_state[js][sites/all/modules/better_exposed_filters/better_exposed_filters.js]: 1
ajax_page_state[js][//f.vimeocdn.com/js/froogaloop2.min.js]: 1
ajax_page_state[js][sites/all/modules/views/js/base.js]: 1
ajax_page_state[js][misc/progress.js]: 1
ajax_page_state[js][sites/all/modules/views/js/ajax_view.js]: 1
ajax_page_state[js][sites/all/modules/views_ajax_overlay/js/views_ajax_overlay.js]: 1
ajax_page_state[js][sites/all/modules/eloqua_api/js/tracking.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/matchmedia/matchmedia.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/magnific/jquery.magnific.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/placeholdr/placeholdr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/js/tc-omega.helpers.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/vendor.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/scripts.js]: 1
ajax_page_state[jquery_version]: 1.10
'''






'''
Page 2

view_name: sessions_list
view_display_id: random
view_args:
view_path: node/236
view_base_path:
view_dom_id: 4acf6c3f5f06ae9899558e5ff92ae10f
pager_element: 0
page: 2
ajax_html_ids[]: block-block-3
ajax_html_ids[]: block-menu-block-2
ajax_html_ids[]: block-delta-blocks-page-title
ajax_html_ids[]: page-title
ajax_html_ids[]: block-cck-blocks-field-hero-intro
ajax_html_ids[]: main-content
ajax_html_ids[]: block-cck-blocks-field-sections
ajax_html_ids[]: block-views-exp-sessions-list-random
ajax_html_ids[]: views-exposed-form-sessions-list-random
ajax_html_ids[]: edit-query-wrapper
ajax_html_ids[]: edit-query
ajax_html_ids[]: edit-type-wrapper
ajax_html_ids[]: edit-type-1
ajax_html_ids[]: edit-type-2
ajax_html_ids[]: edit-type-3
ajax_html_ids[]: edit-type-4
ajax_html_ids[]: edit-type-5
ajax_html_ids[]: edit-type-6
ajax_html_ids[]: edit-type-7
ajax_html_ids[]: edit-type-8
ajax_html_ids[]: edit-track-wrapper
ajax_html_ids[]: edit-track-1
ajax_html_ids[]: edit-track-2
ajax_html_ids[]: edit-track-3
ajax_html_ids[]: edit-track-4
ajax_html_ids[]: edit-track-5
ajax_html_ids[]: edit-track-6
ajax_html_ids[]: edit-track-7
ajax_html_ids[]: edit-level-wrapper
ajax_html_ids[]: edit-level
ajax_html_ids[]: edit-level-1
ajax_html_ids[]: edit-level-2
ajax_html_ids[]: edit-level-3
ajax_html_ids[]: edit-level-4
ajax_html_ids[]: edit-submit-sessions-list
ajax_html_ids[]: edit-reset
ajax_html_ids[]: block-nodeblock-554
ajax_html_ids[]: node-554
ajax_html_ids[]: session-546476
ajax_html_ids[]: session-554471
ajax_html_ids[]: session-538877
ajax_html_ids[]: session-538829
ajax_html_ids[]: session-567189
ajax_html_ids[]: session-567323
ajax_html_ids[]: session-563812
ajax_html_ids[]: session-567350
ajax_html_ids[]: session-539451
ajax_html_ids[]: session-554431
ajax_html_ids[]: session-561573
ajax_html_ids[]: session-561565
ajax_html_ids[]: session-539440
ajax_html_ids[]: session-539475
ajax_html_ids[]: session-538767
ajax_html_ids[]: session-539162
ajax_html_ids[]: session-561505
ajax_html_ids[]: session-539476
ajax_html_ids[]: session-554462
ajax_html_ids[]: session-563957
ajax_html_ids[]: session-546475
ajax_html_ids[]: session-539482
ajax_html_ids[]: session-539483
ajax_html_ids[]: session-567353
ajax_html_ids[]: session-567335
ajax_html_ids[]: session-539448
ajax_html_ids[]: session-538824
ajax_html_ids[]: session-539511
ajax_html_ids[]: session-560835
ajax_html_ids[]: session-538873
ajax_html_ids[]: session-538835
ajax_html_ids[]: session-554472
ajax_html_ids[]: session-539420
ajax_html_ids[]: session-554429
ajax_html_ids[]: session-538828
ajax_html_ids[]: session-538876
ajax_html_ids[]: session-539429
ajax_html_ids[]: session-539468
ajax_html_ids[]: session-566979
ajax_html_ids[]: session-546396
ajax_html_ids[]: session-539449
ajax_html_ids[]: session-540917
ajax_html_ids[]: session-554461
ajax_html_ids[]: session-538944
ajax_html_ids[]: session-539491
ajax_html_ids[]: session-561536
ajax_html_ids[]: session-554470
ajax_html_ids[]: session-554425
ajax_html_ids[]: session-567601
ajax_html_ids[]: session-567354
ajax_html_ids[]: block-nodeblock-173
ajax_html_ids[]: node-173
ajax_html_ids[]: block-block-1
ajax_html_ids[]: block-menu-menu-footer-menu
ajax_html_ids[]: block-block-2
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_html_ids[]:
ajax_page_state[theme]: tc_omega
ajax_page_state[theme_token]: 0gX69c5_pVXwOPwER8MDFIWm3oyWXtbe0ZSGntefmec
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.menus.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.messages.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/system/system.theme.css]: 1
ajax_page_state[css][sites/all/modules/date/date_api/date.css]: 1
ajax_page_state[css][sites/all/modules/date/date_popup/themes/datepicker.1.7.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/field/field.theme.css]: 1
ajax_page_state[css][sites/all/modules/logintoboggan/logintoboggan.css]: 1
ajax_page_state[css][modules/node/node.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/search/search.theme.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.base.css]: 1
ajax_page_state[css][sites/all/themes/omega/omega/omega/css/modules/user/user.theme.css]: 1
ajax_page_state[css][sites/all/modules/youtube/css/youtube.css]: 1
ajax_page_state[css][sites/all/modules/views/css/views.css]: 1
ajax_page_state[css][sites/all/components/tc-components/build/css/style.min.css]: 1
ajax_page_state[css][sites/all/modules/tc_custom/tc_likes/tc_likes.css]: 1
ajax_page_state[css][sites/all/modules/ctools/css/ctools.css]: 1
ajax_page_state[css][sites/all/modules/views_ajax_overlay/css/views_ajax_overlay.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/libraries/magnific/magnific.css]: 1
ajax_page_state[css][sites/all/themes/tc_omega/css/tc-omega.styles.css]: 1
ajax_page_state[js][0]: 1
ajax_page_state[js][public://google_tag/google_tag.script.js]: 1
ajax_page_state[js][sites/all/libraries/modernizr/modernizr.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/jquery/1.10/jquery.min.js]: 1
ajax_page_state[js][misc/jquery-extend-3.4.0.js]: 1
ajax_page_state[js][misc/jquery.once.js]: 1
ajax_page_state[js][misc/drupal.js]: 1
ajax_page_state[js][sites/all/themes/omega/omega/omega/js/no-js.js]: 1
ajax_page_state[js][sites/all/libraries/easing/jquery.easing.min.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/ui/external/jquery.cookie.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/replace/misc/jquery.form.min.js]: 1
ajax_page_state[js][misc/ajax.js]: 1
ajax_page_state[js][sites/all/modules/jquery_update/js/jquery_update.js]: 1
ajax_page_state[js][sites/all/modules/admin_menu/admin_devel/admin_devel.js]: 1
ajax_page_state[js][sites/all/modules/defer_image/defer_image.js]: 1
ajax_page_state[js][sites/all/modules/tc_custom/tc_likes/tc_likes.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv-printshiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/html5shiv/html5shiv.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/selectivizr/selectivizr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/respond/respond.min.js]: 1
ajax_page_state[js][sites/all/modules/better_exposed_filters/better_exposed_filters.js]: 1
ajax_page_state[js][//f.vimeocdn.com/js/froogaloop2.min.js]: 1
ajax_page_state[js][sites/all/modules/views/js/base.js]: 1
ajax_page_state[js][misc/progress.js]: 1
ajax_page_state[js][sites/all/modules/views/js/ajax_view.js]: 1
ajax_page_state[js][sites/all/modules/views_ajax_overlay/js/views_ajax_overlay.js]: 1
ajax_page_state[js][sites/all/modules/eloqua_api/js/tracking.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/matchmedia/matchmedia.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/magnific/jquery.magnific.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/libraries/placeholdr/placeholdr.min.js]: 1
ajax_page_state[js][sites/all/themes/tc_omega/js/tc-omega.helpers.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/vendor.js]: 1
ajax_page_state[js][sites/all/components/tc-components/build/js/scripts.js]: 1
ajax_page_state[jquery_version]: 1.10
'''
