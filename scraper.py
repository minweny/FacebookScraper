"""
This is a Python program to scrap Facebook data.
You need to change base_url,account,password if you want to run the program successfully.
This program takes about 30 minutes to scrape 1000 posts. Don't worry if it's a little slow.
The output file is csv, stored in the same folder as this script.
Have fun!!!!!!!!
"""


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,pickle,csv
from pathlib import Path
import ast
import datetime

# debug mode: doesn't store any data. only output the data of the first page
debug=False

# scrape only recent months data or all the history data
onlyRecentData=False

# mobile version of someone's home page(must be mobile version!!!)
base_url='https://mbasic.facebook.com/momlifekeepingitreal/'

# type your facebook account and password here!!!!!!!!!!!!!!!!!!!
# only needed when you use the scrapper for the first time
account=''
password=''

# disable firefox notification
profile=webdriver.FirefoxProfile()
profile.set_preference("dom.webnotifications.enabled", False)
# open firefox
browser=webdriver.Firefox(firefox_profile=profile)
browser.get(base_url)

# login
print('----------------------------log in started----------------------------')
cookies_location=Path("./cookies.pkl")
if cookies_location.exists():
    print('cookies found !!!')
    with open("cookies.pkl", "rb") as infile:
        cookies = pickle.load(infile)
        for cookie in cookies:
            browser.add_cookie(cookie)
else:
    print('cookies not found... login for you!!!')
    # automate log in
    browser.get('https://www.facebook.com/')
    a = browser.find_element_by_id('email')
    a.send_keys(account)
    print("Email Id entered...")
    b = browser.find_element_by_id('pass')
    b.send_keys(password)
    print("Password entered...")
    c = browser.find_element_by_id('loginbutton')
    c.click()
    # store cookies
    with open("cookies.pkl", "wb") as outfile:
        pickle.dump(browser.get_cookies(), outfile)
print('----------------------------log in ended----------------------------')

if not debug:
    # prepare a csv
    csvName = input('choose a name for your output csv:')+datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    csvFile = open(csvName + '.csv', 'w', newline='', encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    # build the csv headers
    csvWriter.writerow(
        ['Post ID', 'Time', 'Text', 'Comments', 'Shares', 'All', 'Love', 'Thankful', 'Wow', 'Like', 'Angry', 'Yay', 'Haha', 'Sad',
         'Post Link'])

# store the scraping data for all of the pages
articleIDListSum = []
articleTimeListSum=[]
articleTextListSum = []
articleLinkListSum = []
totalEmotionsListSum=[]
# emotionSet=set()

# get this info from last running result
emotionList=['All', 'Love', 'Thankful', 'Wow', 'Like', 'Angry', 'Yay', 'Haha', 'Sad']

page=1

def loadPage(page_url):
    global page
    print('------------------------------------------page:', page)
    page += 1

    browser.get(page_url)

    # get all articles
    articles = browser.find_elements_by_xpath("//div[@id='structured_composer_async_container']/div/div/div/div[@role='article']")
    print(len(articles), 'articles in this page')

    # store the basic info about articles
    articleIDList = []
    articleTextList = []
    articleLinkList = []
    totalEmotionsList=[]
    articleTimeList=[]
    commentList=[]
    shareList=[]


    for i in range(len(articles)):
        postDicStr=articles[i].get_attribute('data-ft')
        postDic=ast.literal_eval(postDicStr)
        print('post id is:',postDic["mf_story_key"])
        articleIDList.append(postDic["mf_story_key"])

        # store date
        curdate=articles[i].find_elements_by_xpath("./div/div/abbr")
        if len(curdate)==0:
            articleTimeList.append('time not showing')
        else:
            articleTimeList.append(curdate[0].text)
        # print(curdate)

        ps = articles[i].find_elements_by_xpath("./div/div/span/p")
        strTemp=''
        for p in ps:
            p.text.replace("\n"," ")
            strTemp+=(p.text+' ')
        articleTextList.append(strTemp)

        bottomColumn=articles[i].find_elements_by_xpath("./div")[1].find_elements_by_xpath("./div")[1]

        commentNum = 0
        try:
            comment=bottomColumn.find_elements_by_xpath("./a")[0].text
            comment:str
            if comment.index('Comment')!=0:
                commentNum=comment[0:comment.index('Comment')-1]
        except:
            print('not being able to extract comment element')
        commentList.append(commentNum)
        print('comment', commentNum)

        shareNum = 0
        try:
            share=bottomColumn.find_elements_by_xpath("./a")[1].text
            share:str
            if share.index('Share')!=0:
                shareNum=share[0:share.index('Share')-1]
        except:
            print('not being able to extract share element')
        shareList.append(shareNum)
        print('share', shareNum)

        emojiElements=articles[i].find_elements_by_xpath("./div/div/span/a")
        if len(emojiElements)!=0:
            emojiLinkHref = emojiElements[0].get_attribute('href')
            # we use emoji link for the article link. They are basically the same.
            articleLinkList.append(emojiLinkHref)
        else:
            articleLinkList.append('')

    print('articleIDList length',len(articleIDList))
    print('articleTextList length',len(articleTextList))
    print('-------------begin processing')

    # process the stored data in each post
    for i in range(len(articleLinkList)):
        # print text
        print(articleTextList[i])

        currentEmotionDic={}
        if articleLinkList[i]!='':
            try:
                browser.get(articleLinkList[i])
                print('artile link:',articleLinkList[i])
                style1=browser.find_elements_by_xpath("//div[@role='article']/div/div/div/div/div/a")
                style2=browser.find_elements_by_xpath("//div[@id='m_story_permalink_view']/div/div/div/a")
                style3 = browser.find_elements_by_xpath("//div[@role='main']/div/div/div/div/div/div/div/div/a")
                if len(style1)!=0:
                    style1[0].click()
                elif len(style2)!=0:
                    style2[0].click()
                else:
                    style3[0].click()
                innerPageEmotionEles=browser.find_elements_by_xpath("//a[@role='button']")
                for innerPageEmotionEle in innerPageEmotionEles:
                    if 'All' in innerPageEmotionEle.text:
                        # emotionSet.add("All")
                        text=innerPageEmotionEle.text
                        text:str
                        subText=text[text.index(' ')+1:]
                        currentEmotionDic['All']=subText
                    else:
                        altStr=innerPageEmotionEle.find_element_by_xpath('./img').get_attribute('alt')
                        # emotionSet.add(altStr)
                        num=innerPageEmotionEle.find_element_by_xpath('./span').text
                        currentEmotionDic[altStr]=num
            except Exception as exc:
                print('exception!!! program dies in this post\n',exc)
                # raise
        totalEmotionsList.append(currentEmotionDic)

        # print emoji dic
        print(currentEmotionDic)



    articleIDListSum.extend(articleIDList)
    articleTimeListSum.extend(articleTimeList)
    articleTextListSum.extend(articleTextList)
    articleLinkListSum.extend(articleLinkList)
    totalEmotionsListSum.extend(totalEmotionsList)


    if not debug:
        # write this page's data to csv
        for i in range(len(articleIDList)):
            rowList=[]
            rowList.append(articleIDList[i])
            rowList.append(articleTimeList[i])
            rowList.append(articleTextList[i])

            # append comments and shares
            rowList.append(commentList[i])
            rowList.append(shareList[i])

            # append emoji
            for emo in emotionList:
                if emo in totalEmotionsList[i]:
                    rowList.append(totalEmotionsList[i][emo])
                else:
                    rowList.append(0)

            rowList.append(articleLinkList[i])
            print(rowList)
            print('------')
            csvWriter.writerow(rowList)

    # redirect to the same page
    browser.get(page_url)
    # go to next page
    morePages=browser.find_elements_by_link_text('Show more')
    if not debug and len(morePages)!=0:
        nextPage = morePages[0].get_attribute('href')
        loadPage(nextPage)



if onlyRecentData:
    loadPage(base_url)
else:
    # year data + recent data
    loadPage(base_url)

    # get year list elements
    browser.get(base_url)

    yearsEle=browser.find_elements_by_xpath("//div[@id='structured_composer_async_container']/div[@class='j']")
    print('yearsEle\n',yearsEle)

    links = []
    yearsIdx = []

    # create year list links
    for i in range(len(yearsEle)):
        if i == 0 or i == len(yearsEle) - 1:
            continue
        yearElement = yearsEle[i].find_element_by_tag_name('a')
        links.append(yearElement.get_attribute('href'))
        yearsIdx.append(yearElement.text)
        print(yearElement.text, yearElement.get_attribute('href'))
    # loop through different years
    # now we only need 2 years data
    cnt=0
    for i in range(len(links)):
        if cnt>1:
            break
        cnt+=1
        print('--------------------------  ', yearsIdx[i], '  --------------------------')
        loadPage(links[i])



if not debug:
    # close csv
    csvFile.close()

print('---------------------finally')
print('total posts found',len(articleIDListSum))
