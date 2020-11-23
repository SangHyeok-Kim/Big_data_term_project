from bs4 import BeautifulSoup
from urllib import request,response
import requests
from selenium import webdriver
import pandas as pd
import time
import datetime
from selenium.webdriver.chrome.options import Options

condition_day = ['1', '2', '3', '4', '5']
condition_time = '080000'

while(1):

    now_day = time.strftime('%w', time.localtime(time.time()))
    now_time = (time.strftime('%H%M%S', time.localtime(time.time())))

    if now_day in condition_day:
        if now_time == condition_time:    
    
        YMD = time.strftime('%Y-%m-%d', time.localtime(time.time()))

        driver_path = "/home/ubuntu/chromedriver"
        url = "https://kr.investing.com/portfolio/?portfolioID=Y2c1YG4%2FYj5iNjw1YjI0Pg%3D%3D"
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')



        driver = webdriver.Chrome(driver_path, chrome_options=chrome_options)
        driver.get(url)
        time.sleep(0.3)

        username = 'slsnsi@naver.com'
        password = 'bigdata1212'


        ### 로그인 -> 내 포트폴리오 -> 가격이 가장 많이 오른 순서대로 나열 ###
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="loginFormUser_email"]').send_keys(username)
        driver.find_element_by_xpath('//*[@id="loginForm_password"]').send_keys(password)
        driver.find_element_by_xpath('//*[@id="signup"]/a').click()
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="navMenu"]/ul/li[10]/a').click()
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="portfolioData_16702538"]/div/table/thead/tr/th[16]').click()
        driver.find_element_by_xpath('//*[@id="portfolioData_16702538"]/div/table/thead/tr/th[16]').click()
        time.sleep(2)

        for i in range(4):
            driver.find_element_by_xpath('//*[@id="paginationShowMoreText"]').click()
            time.sleep(3)


        print('최신 포트폴리오 뉴스를 파싱중입니다...')
        pp_news_title = []
        pp_news_title_time = []
        pp_news_href = []
        for i in range(1, 20+1):  #최신 20개 기사추출
            title_xpath = driver.find_element_by_xpath('//*[@id="fullColumn"]/div[7]/div[8]/div[1]/div/article[{}]/div[1]/a'.format(i))
            try:
                title_xpath_time = driver.find_element_by_xpath('//*[@id="fullColumn"]/div[7]/div[8]/div[1]/div/article[{}]/div[1]/div/span[2]'.format(i))
            except:
                title_xpath_time = driver.find_element_by_xpath('//*[@id="fullColumn"]/div[7]/div[8]/div[1]/div/article[{}]/div[1]/span/span[2]'.format(i))

            title_text = title_xpath.text
            title_time = title_xpath_time.text
            title_time = title_time.replace(' ', '').replace('-', '')
            title_href = title_xpath.get_attribute('href')

            pp_news_title.append(title_text)
            pp_news_title_time.append(title_time)
            pp_news_href.append(title_href)

        mail_pp_news = '{} ({})\n{}\n\n'.format(pp_news_title[0], pp_news_title_time[0], pp_news_href[0])
        for i in range(1, 20):
        mail_pp_news += '{} ({})\n{}\n\n'.format(pp_news_title[i], pp_news_title_time[i], pp_news_href[i])


        ###포트폴리오 속 주식들의 이름(NAME), 페이지링크(HREF), 고유 pair-id값(PAIRID) 수집###
        pp_stocks = driver.find_elements_by_xpath('//*[@id]/td[3]/span[1]/a')
        NAME = []
        HREF = []
        PAIRID = []

        NAME = []; CLOSE = []; PE95 = []; CHG = []; CHG_RATIO = []; OPEN = []; JJ_L_H = []

        for i in range(len(pp_stocks)):
            href = pp_stocks[i].get_attribute('href')
            pairid = pp_stocks[i].get_attribute('data-pairid')
            HREF.append(href)
            PAIRID.append(pairid)


        for i in range(len(pp_stocks)):
            name = driver.find_element_by_xpath('//*[@id="sort_{}"]/td[4]/a'.format(PAIRID[i]))
            n = name.get_attribute('text')
            NAME.append(n)

        #print(HREF)
        #print(PAIRID)
        #print(NAME)

        def get_text_append(k, j):
            k = k.get_text().strip()
            j.append(k)

        ### 수집한 href를 따라 들어가서, 고유 pair-id값을 통해 원하는 정보들 수집 ###

        for i in range(len(pp_stocks)):
            request_url = requests.get(HREF[i], headers = headers)
            soup = BeautifulSoup(request_url.content, 'html.parser')
            print('{}의 정보를 파싱중입니다...'.format(NAME[i]))

        #오픈
            opening_price = soup.select_one('div:nth-child(4) > span.float_lang_base_2.bold')
            get_text_append(opening_price, OPEN)

        #종가
            closing_price = soup.select_one('div:nth-child(1) > span.float_lang_base_2.bold')
            get_text_append(closing_price, CLOSE)

        #per*eps*0.95
            try:
                per = soup.select_one('div:nth-child(11) > span.float_lang_base_2.bold')
                eps = soup.select_one('div:nth-child(6) > span.float_lang_base_2.bold')
                per = per.get_text().strip(); eps = eps.get_text().strip()
                p_e_95 = round(float(per) * float(eps) * 0.95, 2)
                PE95.append(p_e_95)
            except:
                PE95.append('N/A')

        #변동
            try:
                fluctuation = soup.select_one('span.arial_20.redFont.pid-{}-pc'.format(PAIRID[i]))
                get_text_append(fluctuation, CHG)
            except:
                fluctuation = soup.select_one('span.arial_20.greenFont.pid-{}-pc'.format(PAIRID[i]))
                get_text_append(fluctuation, CHG)

        #변동(%)
            try:
                fluctuation_ratio = soup.select_one('span.arial_20.redFont.pid-{}-pcp.parentheses'.format(PAIRID[i]))
                get_text_append(fluctuation_ratio, CHG_RATIO)
            except:
                fluctuation_ratio = soup.select_one('span.arial_20.greenFont.pid-{}-pcp.parentheses'.format(PAIRID[i]))
                get_text_append(fluctuation_ratio, CHG_RATIO)
                
        #장중 변동(최저가 - 최고가)
            L_to_H = soup.select_one('div:nth-child(2) > span.float_lang_base_2.bold')
            get_text_append(L_to_H, JJ_L_H)






        ### pandas 데이터프레임 만들기 ###
        df = pd.DataFrame({"NAME" : NAME, \
                            "OPEN" : OPEN, \
                            "CLOSE" : CLOSE, \
                            "P*E*(.95)" : PE95, \
                            "Chg." : CHG, \
                            "Chg. %" : CHG_RATIO, \
                            "Low - High" : JJ_L_H})                   
        print(df)



        ### 만든 데이터프레임 csv파일로 저장하고, 크롬창 닫기 ###
        df.to_csv('/home/ubuntu/Investing.csv', mode = 'w', encoding = 'cp949')
        driver.close()




        ### 원/달러, 나스닥100 지수 파싱 ###
        print('원/달러 파싱중입니다...')
        USD_KRW_url = 'https://kr.investing.com/currencies/usd-krw'
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        request_url = requests.get(USD_KRW_url, headers = headers)
        soup = BeautifulSoup(request_url.content, 'html.parser')

        exch_won = soup.select_one('#last_last')

        exch_won_bd = soup.select_one('div.inlineblock > div.top.bold.inlineblock > span.arial_20.redFont.pid-650-pc')
        if exch_won_bd == None:
            exch_won_bd = soup.select_one('div.inlineblock > div.top.bold.inlineblock > span.arial_20.greenFont.pid-650-pc')

        exch_won_bd_rate = soup.select_one('div.top.bold.inlineblock > span.arial_20.redFont.pid-650-pcp.parentheses')
        if exch_won_bd_rate == None:
            exch_won_bd_rate = soup.select_one('div.top.bold.inlineblock > span.arial_20.greenFont.pid-650-pcp.parentheses')

        exch_won = exch_won.get_text().strip()
        exch_won_bd = exch_won_bd.get_text().strip()
        exch_won_bd_rate = exch_won_bd_rate.get_text().strip()

        mail_exchange = "<원/달러 환율>\n{}원\n{} ({})".format(exch_won, exch_won_bd, exch_won_bd_rate)

        print('나스닥100 파싱중입니다...')
        NDX_url = 'https://kr.investing.com/indices/nq-100'
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        request_url = requests.get(NDX_url, headers = headers)
        soup = BeautifulSoup(request_url.content, 'html.parser')

        NDX = soup.select_one('#last_last')

        NDX_bd = soup.select_one('div.inlineblock > div.top.bold.inlineblock > span.arial_20.redFont.pid-20-pc')
        if NDX_bd == None:
            NDX_bd = soup.select_one('div.inlineblock > div.top.bold.inlineblock > span.arial_20.greenFont.pid-20-pc')

        NDX_bd_rate = soup.select_one('div.top.bold.inlineblock > span.arial_20.redFont.pid-20-pcp.parentheses')
        if NDX_bd_rate == None:
            NDX_bd_rate = soup.select_one('div.top.bold.inlineblock > span.arial_20.greenFont.pid-20-pcp.parentheses')

        NDX = NDX.get_text().strip()
        NDX_bd = NDX_bd.get_text().strip()
        NDX_bd_rate = NDX_bd_rate.get_text().strip()

        mail_NDX = '<나스닥100>\n{}\n{} ({})'.format(NDX, NDX_bd, NDX_bd_rate)



        print('메일 전송중입니다...')
        ### 만들어진 csv파일을 메일로 전송하기 ###
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders


        ### 메일 세션생성 & 로그인 ###
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login('slsnsi1212@gmail.com', 'ijesmhehsdnopohk')


        ### 제목 & 본문 작성 ###
        msg = MIMEMultipart()
        msg['Subject'] = '오늘의 포트폴리오 리포트'
        msg.attach(MIMEText(mail_exchange+'\n\n'+mail_NDX+'\n\n\n\n'+mail_pp_news, 'plain'))


        ### 파일 첨부 ###
        attachment = open('/home/ubuntu/Investing.csv', 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= " + '{}.csv'.format(YMD))
        msg.attach(part)


        ### 메일 전송 ###
        s.sendmail("slsnsi1212@gmail.com", "slsnsi1212@gmail.com", msg.as_string())
        s.quit()
