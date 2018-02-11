import sys
import pandas as pd
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
from bs4 import BeautifulSoup
 
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
 
import schedule
import time




def flights_fare():
    url ="https://www.google.com/flights/explore/#explore;f=ORD;t=r-Europe-0x46ed8886cfadda85%253A0x72ef99e6b3fcf079;li=9;lx=14;d=2018-02-03"
    driver = webdriver.PhantomJS()
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36")
    driver = webdriver.PhantomJS(desired_capabilities=dcap,service_args=['--ignore-ssl-errors=true'])
    driver.get(url)
 
 
 
	### Wait till reloading
    wait = WebDriverWait(driver, 20)

 
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,
    "span.CTPFVNB-v-c")))    

    s = BeautifulSoup(driver.page_source, "lxml")
    bp = s.findAll('div', class_='CTPFVNB-w-e')
 
    #best_price_tags = s.findAll('div', 'FTWFGDB-w-e')
	
    for index, i in enumerate(bp):
        a=bp[index].text
        a=a[1:]
        bp[index]=int(a)
    # check if scrape worked - alert if it fails and shutdown
    
    if len(bp) < 4:
        print('Failed to Load Page Data')
		
        requests.post('https://maker.ifttt.com/trigger/fare_alert/with/key/mhIKQv_WUlGFyfMpmwbwaKEk2OR5wxoD2SoGbXDvLjk',data={"value1": "script", "value2": "failed",
"value3": ""})
        sys.exit(0)
    else:
        print('This Software has successfully fetched the data')
 
    height_bp= s.findAll('div', class_='CTPFVNB-w-f' )
    for index, i in enumerate(height_bp) :
        height_bp[index]=float(i['style'].split('height: ')[1].split('px')[0])
	
	
    k=np.array(bp)/np.array(height_bp)
    cities= s.findAll('span', class_='CTPFVNB-v-c')
	
	
    for index, i in enumerate(cities):
        cities[index]=i.text.split(',')[0]
	
	
    fares=s.findAll('div', elt='graph')[0].findAll('div', class_='CTPFVNB-w-x')
    l=[]
    for i in fares:
        l.append(float(i['style'].split('height:')[1].split('px')[0]))
	
	
	
    prices=[]
    for index, i in enumerate(fares):
        a=(l[index]/height_bp[0])*bp[0]
        prices.append(a)	
    
	
    df=pd.DataFrame(prices, columns=['Price'])
	

    scaler=StandardScaler()
    scaler.fit(df[['Price']]) 
    db = DBSCAN(eps=.5, min_samples=1).fit(scaler.transform(df[['Price']]))
    number_lb=set(db.labels_)
    df1=df.reset_index()
    df1['labels']=db.labels_
    a=df1.groupby('labels')['Price'].min().sort_values(ascending=True)
    a_min=a.iloc[0]
    a_min_label=a.index[0]
	
	
    k=0
    for group_label, df3 in df1.groupby('labels'):
        if(group_label==a_min_label):
            if (len(df3) > 1):
                k=1
	
    n=0
    if (len(number_lb) > 2):
        n=1
	
    p=0
    if (a.iloc[1] > a.iloc[0] + 50):
        p=1
    
    if(p==1 and k==1 and n==1):
        city=cities[0]
        fare=a_min
        print("test-   pppp")
        
        requests.post('https://maker.ifttt.com/trigger/fare_alert/with/key/mhIKQv_WUlGFyfMpmwbwaKEk2OR5wxoD2SoGbXDvLjk', data={"value1": city, "value2": fare, "value3": ""})
    else:
        print('no alert triggered')
						
flights_fare()


 


