#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 크롤링 라이브러리 설치
get_ipython().system(' pip install undetected-chromedriver')
get_ipython().system(' pip install webdriver_manager')

# 일본어 번역을 위한 라이브러리 설치
get_ipython().system(' pip install googletrans==4.0.0rc1')
get_ipython().system(' pip install deep_translator')

# 키워드 분석 라이브러리 설치
get_ipython().system(' pip install krwordrank')

# JAVA 설치 필요
get_ipython().system(' pip install JPype1>=0.7.0')

# 구글 트렌드 분석
get_ipython().system(' pip install pytrends')


# In[ ]:


# 패키지 통합 임포트

# 크롤링
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import json
import random

import requests

import pandas as pd
import time
from datetime import datetime

# ---------------------------------------------- #

# 일본어 번역
from deep_translator import GoogleTranslator

# ---------------------------------------------- #

# 키워드 분석
import os
import re
from ast import literal_eval
from konlpy.tag import Okt
from collections import Counter
from krwordrank.word import KRWordRank

# ---------------------------------------------- #

# 구글트렌드
from pytrends.request import TrendReq
import matplotlib.pyplot as plt


# # 0. 불러오기 필수 데이터셋 파일
# - 불러오기 이후 2번 목차부터 실행

# In[ ]:


# 데이터 전처리를 위한 크롤링 데이터셋 불러오기
df_combined = pd.read_csv('통합_무신사_데이터.csv')
final_df = pd.read_csv('통합_화해_데이터.csv')
olive_df = pd.read_csv('통합_올리브영_데이터.csv')
df_detail = pd.read_csv('통합_코스메_데이터_번역전.csv')
# df_detail = pd.read_csv('통합_코스메_데이터.csv', encoding='EUC-KR')


# In[ ]:


# 플랫폼 통합을 위한 전처리 데이터셋 불러오기
musinsa_df = pd.read_csv('musinsa_preprocessing.csv')
hwahae_df = pd.read_csv('hwahae_preprocessing.csv')
oliveyoung_df = pd.read_csv('oliveyoung_preprocessing.csv')


# In[ ]:


# 키워드 분석을 위한 리뷰 데이터 불러오기
olive_top_df = pd.read_csv('올리브영_워드클라우드_리뷰.csv') # 올리브영 리뷰 데이터
# df_scrap=pd.read_csv("review_scrapped_1.csv")     # 무신사 리뷰 데이터

# korea_all = pd.read_csv("korea_new_rank.csv")
# olive_top5 = pd.read_csv("올리브영_리뷰_분류.csv")   


# In[ ]:


# 4. 추가 데이터 수집 - 네이버 데이터랩에서 다운받은 데이터 불러오기

extra_age = pd.read_csv('기타_연령대.csv', encoding="utf-8-sig")
lip_age = pd.read_csv('립_연령대.csv', encoding="utf-8-sig")
clean_age = pd.read_csv('클렌징_연령대.csv', encoding="utf-8-sig")
mask_age = pd.read_csv('팩_연령대.csv', encoding="utf-8-sig")
skin_age = pd.read_csv('스킨_연령대.csv', encoding="utf-8-sig")
eye_age = pd.read_csv('아이_연령대.csv', encoding="utf-8-sig")
sun_age = pd.read_csv('선케어_연령대.csv', encoding="utf-8-sig")
base_age = pd.read_csv('베이스_연령대.csv', encoding="utf-8-sig")


# # 1. 한국 & 일본 플랫폼 크롤링

# ## 무신사 : df_combined

# ### 01. 크롤링

# #### 카테고리별 랭킹 페이지 접속

# In[ ]:


# 크롬 드라이버 설정
driver = webdriver.Chrome()

# 무신사 카테고리별 랭킹 페이지 접속
driver.get("https://www.musinsa.com/main/beauty/ranking?storeCode=beauty&sectionId=231&categoryCode=104003&period=WEEKLY&contentsId=")
time.sleep(3)
driver.find_element(By.XPATH, '/html/body/section/div[2]/button').click()

# 페이지 끝까지 스크롤하여 항목 300개 로드
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        break
    prev_height = new_height

# 브랜드, 가격, 제품명 수집 (최대 100개)
brand_list = driver.find_elements(By.XPATH, '//*[@id="commonLayoutContents"]/article/div/div/div[2]/div[1]/a[1]/p')
brand_list = [i.text for i in brand_list][:100]

price_list = driver.find_elements(By.XPATH, '//*[@id="commonLayoutContents"]/article/div/div/div[2]/div[1]/div/span')
price_list = [i.text for i in price_list]
filtered_price_list = [item for item in price_list if "원" in item][:100]

product_list = driver.find_elements(By.XPATH, '//*[@id="commonLayoutContents"]/article/div/div/div[2]/div/a[2]/p')
product_list = [i.text for i in product_list][:100]

# 결과 출력
print(len(brand_list), len(filtered_price_list), len(product_list))
print("브랜드 리스트:", brand_list)
print("가격 리스트:", filtered_price_list)
print("제품명 리스트:", product_list)

# 드라이버 종료
driver.quit()


# #### 주간 랭킹 페이지 접속

# In[ ]:


# 크롬 드라이버 설정
driver = webdriver.Chrome()

# 무신사 주간 랭킹 페이지 접속
driver.get("https://www.musinsa.com/main/beauty/ranking?storeCode=beauty&sectionId=231&categoryCode=104003&period=WEEKLY&contentsId=")
time.sleep(3)
driver.find_element(By.XPATH, '/html/body/section/div[2]/button').click()

# 상품 URL 수집
product_links = driver.find_elements(By.XPATH, '//*[@id="commonLayoutContents"]/article/div/div/div[2]/div/a[2]')
product_urls = [link.get_attribute('href') for link in product_links][:100]  # 100개까지 수집
len(product_urls)

# 드라이버 종료
driver.quit()


# In[ ]:


# 크롬 드라이버 설정
driver = webdriver.Chrome()

# 별점, 카테고리, 후기 수 리스트
ratings = []
category_list = []
review_count_list = []

for url in product_urls:
    driver.get(url)
    time.sleep(3)  # 페이지 로드 대기
    
    # 페이지 스크롤 다운 (별점 로딩 대비)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # 별점 추출
    try:
        rating_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="reviewPosition"]/div[2]/div[1]/div/div[1]/div/div/span'))
        )
        rating = rating_element.text
    except Exception as e:
        try:
            rating_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="reviewPosition"]/div/div[1]/div/div[1]/div/div/span'))
            )
            rating = rating_element.text
        except Exception as e:
            try:
                rating_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="reviewPosition"]/div/div[1]/div/div[1]/div/span[2]'))
                )
                rating = rating_element.text
            except Exception as e:
                print(f"별점 오류 발생: {e}")
                rating = "별점 없음"
    ratings.append(rating)
    
    # 세부 카테고리 추출 (2depth만 추출)
    try:
        category = driver.find_element(By.XPATH, '//a[@data-category-id="3depth"]').get_attribute('data-category-name')
    except:
        category = "카테고리 없음"
    category_list.append(category)
    
    # 후기 수 추출
    try:
        reviews = driver.find_element(By.XPATH, '//span[contains(@class, "cursor-pointer") and contains(text(), "후기")]').text
    except:
        reviews = "0"
    review_count_list.append(reviews)
    
    time.sleep(1)

# 결과 출력
print(len(category_list), len(review_count_list), len(ratings))
print("카테고리 리스트:", category_list)
print("후기 수 리스트:", review_count_list)
print("별점 리스트:", ratings)

# 드라이버 종료
driver.quit()



# ### 02. 빈 값 채우기

# In[ ]:


no_rating_indices = [i for i, rating in enumerate(ratings) if rating == "별점 없음"]
print("별점 없음인 항목의 인덱스:", no_rating_indices)

no_review_indices = [i for i, review_count_list in enumerate(review_count_list) if review_count_list == 0]
print("별점 없음인 항목의 인덱스:", no_review_indices)


# In[ ]:


# 별점 없음인 항목 수정
ratings[8] = "4.9"  
ratings[9] = "4.9"  
ratings[10] = "4.8"  
ratings[11] = "4.9"  
ratings[12] = "4.8"  
ratings[13] = "4.9"  
ratings[14] = "4.9"  


# 결과 확인
print("수정된 별점 리스트:", ratings)


# ### 03. 데이터프레임 생성

# In[ ]:


import pandas as pd

# 데이터프레임 생성
df_cleanser = pd.DataFrame({
    "순위": range(1, 101),  # 1~100 순위
    "카테고리": ["클렌징"] * 100,  
    "세부 카테고리": category_list,
    "브랜드": brand_list,
    "제품명": product_list,
    "평점": ratings,
    "후기 개수": review_count_list,
    "가격": filtered_price_list,
    "URL": product_urls
})

# 데이터프레임 확인
df_cleanser.head()


# In[ ]:


df_cleanser.to_csv("df_cleanser.csv", index=False, encoding="utf-8-sig")


# ### 04. 파일 통합

# In[ ]:


import pandas as pd

# 파일 목록 지정
file_list = ["musinsa_cleanser.csv", "musinsa_skincare.csv", "musinsa_suncare.csv", "musinsa_makeup.csv"]

# CSV 파일을 읽고 하나의 데이터프레임으로 합치기
df_list = [pd.read_csv(file) for file in file_list]
df_combined = pd.concat(df_list, ignore_index=True)

# 합쳐진 데이터프레임 저장 (필요한 경우)
# df_combined.to_csv("musinsa_weekly_ranking_category.csv", index=False, encoding="utf-8-sig")

df_combined.head(10)


# ## 화해 : final_df

# ### 01. Def

# In[ ]:


def find_product_id(url):
    """URL에서 상품 ID를 추출하는 함수"""
    match = re.search(r'/(goods|products)/(\d+)', url)  # `goods` 또는 `products` 뒤의 숫자 찾기
    return match.group(2) if match else None


# In[ ]:


now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
now_date = datetime.now().strftime('%Y%m%d')

print(now)
print(now_date)


# ### 02. URL

# In[ ]:


# # 스킨케어
# 스킨토너 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4156
# 로션/에멀젼 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4165
# 에센스/앰플/세럼 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4174
# 페이스오일 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4183
# 크림 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4184
# 아이케어 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4193
# 미스트 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4194
# 젤 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4199
# 스킨/토너 패드 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4498
# 밤/멀티밤 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4518

# # 클렌징
# 클렌징 폼 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4200
# 클렌징 워터 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4209
# 클렌징 젤 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4210
# 클렌징 오일 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4211
# 클렌징 로션/크림 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4212
# 클렌징 비누 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4213
# 클렌징 티슈/패드 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4214
# 립/아이 리무버 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4215
# 스크럽/필링 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4216
# 스크럽/필링 패드 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4507
# 클렌징 파우더 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4527
# 클렌징 밤 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4536

# # 마스크/팩
# 시트마스크 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4217
# 부분마스크/팩 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4226
# 워시오프 팩 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4235
# 필오프 팩 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4244
# 슬리핑팩 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4253
# 패치 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4262
# 코팩 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4263
# 부분마스크 패드 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4508

# # 선케어
# 선크림/로션 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4272
# 선스프레이 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4279
# 선케어 기타 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4286

# 선스틱 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4293
# 선쿠션/팩트 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4300

# # 베이스 메이크업
# 메이크업 베이스 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4307
# 프라이머 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4312
# BB/CC크림 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4317
# 파운데이션 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4322
# 쿠션 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4328
# 파우더/팩트 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4333
# 컨실러 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4338
# 블러셔 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4344
# 하이라이터 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4350
# 메이크업픽서 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4356
# 셰이딩 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4361
# 톤업크림 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4367

# # 아이메이크업
# 아이섀도 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4368
# 아이라이너 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4374
# 아이브로우 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4380
# 마스카라/픽서 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4386
# 속눈썹영양제 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4392

# # 립메이크업
# 립스틱 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4393
# 립틴트 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4398 
# 립글로스 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4403
# 립케어/립밤 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4408
# 컬러 립케어/립밤 https://www.hwahae.co.kr/rankings?english_name=category&theme_id=4497


# ### 03. Crawiling

# #### 00.카테고리명

# In[ ]:


categories = {
  "스킨케어": {
    "스킨토너": 4156,
    "로션/에멀젼": 4165,
    "에센스/앰플/세럼": 4174,
    "페이스오일": 4183,
    "크림": 4184,
    "아이케어": 4193,
    "미스트": 4194,
    "젤": 4199,
    "스킨/토너 패드": 4498,
    "밤/멀티밤": 4518
  },
  "클렌징": {
    "클렌징 폼": 4200,
    "클렌징 워터": 4209,
    "클렌징 젤": 4210,
    "클렌징 오일": 4211,
    "클렌징 로션/크림": 4212,
    "클렌징 비누": 4213,
    "클렌징 티슈/패드": 4214,
    "립/아이 리무버": 4215,
    "스크럽/필링": 4216,
    "스크럽/필링 패드": 4507,
    "클렌징 파우더": 4527,
    "클렌징 밤": 4536
  },
  "마스크/팩": {
    "시트마스크": 4217,
    "부분마스크/팩": 4226,
    "워시오프 팩": 4235,
    "필오프 팩": 4244,
    "슬리핑팩": 4253,
    "패치": 4262,
    "코팩": 4263,
    "부분마스크 패드": 4508
  },
  "선케어": {
    "선크림/로션": 4272,
    "선스프레이": 4279,
    "선케어 기타": 4286,
    "선스틱": 4293,
    "선쿠션/팩트": 4300
  },
  "베이스 메이크업": {
    "메이크업 베이스": 4307,
    "프라이머": 4312,
    "BB/CC크림": 4317,
    "파운데이션": 4322,
    "쿠션": 4328,
    "파우더/팩트": 4333,
    "컨실러": 4338,
    "블러셔": 4344,
    "하이라이터": 4350,
    "메이크업픽서": 4356,
    "셰이딩": 4361,
    "톤업크림": 4367
  },
  "아이메이크업": {
    "아이섀도": 4368,
    "아이라이너": 4374,
    "아이브로우": 4380,
    "마스카라/픽서": 4386,
    "속눈썹영양제": 4392
  },
  "립메이크업": {
    "립스틱": 4393,
    "립틴트": 4398,
    "립글로스": 4403,
    "립케어/립밤": 4408,
    "컬러 립케어/립밤": 4497
  }
}


# #### 01.스킨케어

# In[ ]:


for category, code in categories["스킨케어"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '스킨케어'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# In[ ]:


time.sleep(60)


# #### 02.클렌징

# In[ ]:


for category, code in categories["클렌징"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '클렌징'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# In[ ]:


time.sleep(60)


# #### 03.선케어

# In[ ]:


for category, code in categories["선케어"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '선케어'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# In[ ]:


time.sleep(60)


# #### 04.베이스 메이크업

# In[ ]:


for category, code in categories["베이스 메이크업"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '베이스메이크업'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# In[ ]:


time.sleep(60)


# #### 05.아이메이크업

# In[ ]:


for category, code in categories["아이메이크업"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '아이메이크업'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# In[ ]:


time.sleep(60)


# #### 06.립케어

# In[ ]:


for category, code in categories["립메이크업"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '립메이크업'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# In[ ]:


time.sleep(60)


# #### 07.마스크팩

# In[ ]:


for category, code in categories["마스크/팩"].items():
    category = category.replace(' ', '').replace('/', '_')
    url = f"https://www.hwahae.co.kr/rankings?english_name=category&theme_id={code}"
    
    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 백그라운드 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(random.uniform(3, 5))  # 페이지 로딩 대기

    prev_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # 스크롤 내리기
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        # 새로운 높이 가져오기
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            break
        prev_height = new_height

        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # 데이터 추출
    titles = [t.text for t in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[1]')))]
    names = [n.text for n in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[1]/span[2]')))]
    ratings = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[1]')))]
    prices = [p.text for p in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[2]')))]
    reviews = [r.text for r in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a/div[3]/div[1]/div[2]/span[2]')))]
    product_urls = [link_element.get_attribute('href') for link_element in wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/div[3]/div/ul/li/a')))]
    productIdlist = [find_product_id(pu) for pu in product_urls]
    price_list = [re.search(r'(\d{1,3}(?:,\d{3})*)\s?원', p) for p in prices]
    price_cleaned = [match.group(1).replace(",", "") if match else None for match in price_list]


    # 리스트 길이 검증
    lengths = {
            "브랜드명": len(titles),
            "상품명": len(names),
            "별점": len(ratings),
            "리뷰수": len(reviews),
            "가격": len(price_cleaned) #,
            # "상품ID": len(productIdlist),
            # "URL": len(product_urls),
    }

    min_length = min(lengths.values())
    max_length = max(lengths.values())

    if min_length != max_length:
        print("⚠️ 데이터 길이 불일치 발생!")
        for key, length in lengths.items():
            print(f"{key}: {length} 개")

    # DataFrame 생성
    index_list = list(range(1, len(titles) + 1))

    df = pd.DataFrame({
    "순위": index_list,
    "브랜드명": titles,
    "상품명": names,
    # "상품ID": productIdlist,
    '별점': ratings,
    '리뷰수': reviews,
    '가격': price_cleaned,
    # 'url': product_urls,
    '업로드일': now
    })

    df['리뷰수'] = df['리뷰수'].fillna('0').apply(
        lambda x: int(str(x).replace(",", "")) if str(x).replace(",", "").isdigit() else 0
    )

    df['대분류'] = '마스크_팩'
    df['중분류'] = category

    # 파일 저장
    df.to_csv(f"hwahae_data/hwahae_{category}_ranking.csv", index=False, encoding="utf-8-sig")
    print(f"✅ 화해 {category} 데이터가 저장되었습니다.")

    driver.quit()


# ### 04.데이터 통합

# In[ ]:


df_list = []

for big_category in list(categories.keys()):
    for name in categories[big_category].keys():
        rename = name.replace(' ', '').replace('/', '_')
        file_path = f"hwahae_data/hwahae_{rename}_ranking.csv"
        df = pd.read_csv(file_path)
        df['소분류'] = ''
        df['플랫폼'] = '화해'
        df['URL'] = ''
        df = df.rename(columns = {'순위' : '중분류_순위', '브랜드명' : '브랜드', '상품명' : '제품명', '별점' : '평점', '리뷰수' : '후기 수'})
        df = df[['플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류', '소분류', '평점', '후기 수', '가격', 'URL']]
        df_list.append(df)


# In[ ]:


final_df = pd.concat(df_list, ignore_index=True)

# save_path = "hwahae_data/통합_화해_데이터.csv"

# CSV 파일 저장
# final_df.to_csv(save_path, encoding='utf-8-sig', index=False)


# ## 올리브영 : olive_df

# In[ ]:


# 브라우저 열기
driver = webdriver.Chrome()


# ### 1. 스킨케어 랭킹

# In[ ]:


# 1. 스킨케어 랭킹 페이지 로드
driver.get("https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo=10000010001&pageIdx=1&rowsPerPage=8&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%9E%AD%ED%82%B9BEST%EC%83%81%ED%92%88%EB%B8%8C%EB%9E%9C%EB%93%9C_%EC%9D%B8%EA%B8%B0%EC%83%81%ED%92%88%EB%8D%94%EB%B3%B4%EA%B8%B0")
time.sleep(3)  # 페이지 로드 대기


# In[ ]:


# 2. 페이지 스크롤
prev_height = driver.execute_script("return document.body.scrollHeight")

# 1위 - 100위
while True:
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 새로운 높이 가져오기
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        break
    prev_height = new_height


# In[ ]:


# 3-1. 랭킹 페이지 데이터 추출
titles = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/span')
products = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/p')
or_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[1]/span')
dis_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[2]/span')

print(len(titles))
print(len(products))
print(len(or_prices))
print(len(dis_prices)) # 세일 안하는 상품들 맞는지 더블 체크 필요


# In[ ]:


# 4-1. 데이터 텍스트 변환
title_list = [t.text for t in titles]
print(len(title_list))
print(title_list[:5])

product_list = [p.text for p in products]
print(len(product_list))
print(product_list[:5])

or_price_list = [op.text for op in or_prices]
print(len(or_price_list))
print(or_price_list[:5])


# In[ ]:


# 4-1. 할인가 밀림 현상 방지 및 데이터 텍스트 변환
dis_price_list = []

for w in range(1, 26):
  for l in range(1, 5):
    
    try:
      dis = driver.find_element(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/p[1]/span[2]/span')
      if dis.text:
         dis_price_list.append(dis.text)
      else:
        dis_price_list.append('') 
             
    except:
      dis_price_list.append('')
      
print(len(dis_price_list))
print(dis_price_list[:5])


# In[ ]:


# 3-2. 상품 상세 페이지 데이터 추출
wait = WebDriverWait(driver, 10)

main_classes = []
mid_classes = []
sub_classes = []
review_nums = []
review_scores = []

for w in range(1, 26):
  for l in range(1, 5):
    detail_page = driver.find_elements(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')
    
    if detail_page:
        detail_page[0].click()
    else:
      continue

    main_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="midCatNm"]'))).text
    mid_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="smlCatNm"]'))).text
    sub_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dtlCatNm"]'))).text 
    num = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/em'))).text
    score = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/b'))).text
  
    main_classes.append(main_class)
    mid_classes.append(mid_class)
    sub_classes.append(sub_class)
    review_nums.append(num)
    review_scores.append(score)

    driver.back()
    wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')))


# In[ ]:


# 4-2. 데이터 개수 확인
print(len(main_classes))
print(len(mid_classes))
print(len(sub_classes))
print(len(review_nums))
print(len(review_scores))

print(main_classes[0:5])
print(mid_classes[0:5])
print(sub_classes[0:5])
print(review_nums[0:5])
print(review_scores[0:5])


# In[ ]:


# 5. 데이터 저장
olive_skincare_dic = {"brand": title_list, "product": product_list, "or_price": or_price_list, "dis_price": dis_price_list, "main_class": main_classes, "mid_class": mid_classes, "sub_class": sub_classes, "review_num": review_nums, "review_score": review_scores}


# In[ ]:


# DF 변환
olive_skincare_df = pd.DataFrame.from_dict(olive_skincare_dic, orient='index')
olive_skincare_df = olive_skincare_df.transpose()
olive_skincare_df.head()


# In[ ]:


# 할인가 정상적으로 들어갔는지 확인
print(len(dis_prices))
print(olive_skincare_df.loc[olive_skincare_df['dis_price']=='']['product'].nunique())
olive_skincare_df.loc[olive_skincare_df['dis_price']=='']


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 생성
olive_skincare_df.reset_index(inplace=True)
olive_skincare_df.head()


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 변경 및 값 변경
olive_skincare_df.rename(columns={'index':'ranking'}, inplace=True)
olive_skincare_df['ranking'] = olive_skincare_df['ranking'].apply(lambda x : x+1)
olive_skincare_df.head()


# In[ ]:


# 원본 데이터 저장
# olive_skincare_df.to_csv("oliveyoung_skincare_ranking.csv", index=False, encoding="utf-8-sig")


# ### 2. 마스크팩 랭킹

# In[ ]:


# 1. 마스크팩 랭킹 페이지 로드
driver.get("https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo=10000010009&pageIdx=1&rowsPerPage=8&t_page=%EB%9E%AD%ED%82%B9&t_click=%ED%8C%90%EB%A7%A4%EB%9E%AD%ED%82%B9_%EB%A7%88%EC%8A%A4%ED%81%AC%ED%8C%A9")
time.sleep(3)  # 페이지 로드 대기


# In[ ]:


# 2. 페이지 스크롤
prev_height = driver.execute_script("return document.body.scrollHeight")


# In[ ]:


# 1위 - 100위
while True:
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 새로운 높이 가져오기
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        break
    prev_height = new_height


# In[ ]:


# 3-1. 랭킹 페이지 데이터 추출
titles = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/span')
products = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/p')
or_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[1]/span')
dis_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[2]/span')

print(len(titles))
print(len(products))
print(len(or_prices))
print(len(dis_prices)) # 세일 안하는 상품들 맞는지 더블 체크 필요


# In[ ]:


# 4-1. 데이터 텍스트로 변환
title_list = [t.text for t in titles]
print(title_list[0:5])

product_list = [p.text for p in products]
print(product_list[0:5])

or_price_list = [op.text for op in or_prices]
print(or_price_list[0:5])

# dis_price_list = [dis.text for dis in dis_prices]
# print(dis_price_list[0:5])


# In[ ]:


# 4-1. 할인가 밀림 현상 방지 및 데이터 텍스트 변환
dis_price_list = []

for w in range(1, 26):
  for l in range(1, 5):
    
    try:
      dis = driver.find_element(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/p[1]/span[2]/span')
      if dis.text:
         dis_price_list.append(dis.text)
      else:
        dis_price_list.append('') 
             
    except:
      dis_price_list.append('')
      
print(len(dis_price_list))
print(dis_price_list[:5])


# In[ ]:


# 3-2. 상품 상세 페이지 데이터 추출
wait = WebDriverWait(driver, 10)

main_classes = []
mid_classes = []
sub_classes = []
review_nums = []
review_scores = []

for w in range(1, 26):
  for l in range(1, 5):
    detail_page = driver.find_elements(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')
    
    if detail_page:
        detail_page[0].click()
    else:
      continue

    main_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="midCatNm"]'))).text
    mid_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="smlCatNm"]'))).text
    sub_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dtlCatNm"]'))).text 
    num = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/em'))).text
    score = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/b'))).text
  
    main_classes.append(main_class)
    mid_classes.append(mid_class)
    sub_classes.append(sub_class)
    review_nums.append(num)
    review_scores.append(score)

    driver.back()
    wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')))


# In[ ]:


# 4-2. 데이터 개수 확인
print(len(main_classes))
print(len(mid_classes))
print(len(sub_classes))
print(len(review_nums))
print(len(review_scores))

print(main_classes[0:5])
print(mid_classes[0:5])
print(sub_classes[0:5])
print(review_nums[0:5])
print(review_scores[0:5])


# In[ ]:


# 5. 데이터 저장
olive_mask_dic = {"brand": title_list, "product": product_list, "or_price": or_price_list, "dis_price": dis_price_list, "main_class": main_classes, "mid_class": mid_classes, "sub_class": sub_classes, "review_num": review_nums, "review_score": review_scores}


# In[ ]:


# DF 변환
olive_mask_df = pd.DataFrame.from_dict(olive_mask_dic, orient='index')
olive_mask_df = olive_mask_df.transpose()
olive_mask_df.head()


# In[ ]:


# 할인가 정상적으로 들어갔는지 확인
print(len(dis_prices))
print(olive_mask_df.loc[olive_mask_df['dis_price']=='']['product'].nunique())
olive_mask_df.loc[olive_mask_df['dis_price']=='']


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 생성
olive_mask_df.reset_index(inplace=True)
olive_mask_df.head()


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 변경 및 값 변경
olive_mask_df.rename(columns={'index':'ranking'}, inplace=True)
olive_mask_df['ranking'] = olive_mask_df['ranking'].apply(lambda x : x+1)
olive_mask_df.head()


# In[ ]:


# 원본 데이터 저장
# olive_mask_df.to_csv("oliveyoung_mask_ranking.csv", index=False, encoding="utf-8-sig")


# ### 3. 클렌징 랭킹

# In[ ]:


# 1. 클렌징 랭킹 페이지 로드
driver.get("https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo=10000010010&pageIdx=1&rowsPerPage=8&t_page=%EB%9E%AD%ED%82%B9&t_click=%ED%8C%90%EB%A7%A4%EB%9E%AD%ED%82%B9_%ED%81%B4%EB%A0%8C%EC%A7%95")
time.sleep(3)  # 페이지 로드 대기


# In[ ]:


# 2. 페이지 스크롤
prev_height = driver.execute_script("return document.body.scrollHeight")

# 1위 - 100위
while True:
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 새로운 높이 가져오기
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        break
    prev_height = new_height


# In[ ]:


# 3-1. 랭킹 페이지 데이터 추출
titles = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/span')
products = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/p')
or_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[1]/span')
dis_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[2]/span')

# 4-1. 데이터 개수 확인
print(len(titles))
print(len(products))
print(len(or_prices))
print(len(dis_prices)) # 세일 안하는 상품들 맞는지 더블 체크 필요


# In[ ]:


# 4-1. 데이터 텍스트로 변환
title_list = [t.text for t in titles]
print(title_list[0:5])

product_list = [p.text for p in products]
print(product_list[0:5])

or_price_list = [op.text for op in or_prices]
print(or_price_list[0:5])

# dis_price_list = [dis.text for dis in dis_prices]
# print(dis_price_list[0:5])


# In[ ]:


# 4-1. 할인가 밀림 현상 방지 및 데이터 텍스트 변환
dis_price_list = []

for w in range(1, 26):
  for l in range(1, 5):
    
    try:
      dis = driver.find_element(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/p[1]/span[2]/span')
      if dis.text:
         dis_price_list.append(dis.text)
      else:
        dis_price_list.append('') 
             
    except:
      dis_price_list.append('')
      
print(len(dis_price_list))
print(dis_price_list[:5])


# In[ ]:


# 3-2. 상품 상세 페이지 데이터 추출
wait = WebDriverWait(driver, 10)

main_classes = []
mid_classes = []
sub_classes = []
review_nums = []
review_scores = []

for w in range(1, 26):
  for l in range(1, 5):
    detail_page = driver.find_elements(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')
    
    if detail_page:
        detail_page[0].click()
    else:
      continue

    main_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="midCatNm"]'))).text
    mid_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="smlCatNm"]'))).text
    sub_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dtlCatNm"]'))).text 
    num = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/em'))).text
    score = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/b'))).text
  
    main_classes.append(main_class)
    mid_classes.append(mid_class)
    sub_classes.append(sub_class)
    review_nums.append(num)
    review_scores.append(score)

    driver.back()
    wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')))


# In[ ]:


# 4-2. 데이터 개수 확인
print(len(main_classes))
print(len(mid_classes))
print(len(sub_classes))
print(len(review_nums))
print(len(review_scores))

print(main_classes[0:5])
print(mid_classes[0:5])
print(sub_classes[0:5])
print(review_nums[0:5])
print(review_scores[0:5])


# In[ ]:


# 5. 데이터 저장
olive_clean_dic = {"brand": title_list, "product": product_list, "or_price": or_price_list, "dis_price": dis_price_list, "main_class": main_classes, "mid_class": mid_classes, "sub_class": sub_classes, "review_num": review_nums, "review_score": review_scores}


# In[ ]:


# DF 변환
olive_clean_df = pd.DataFrame.from_dict(olive_clean_dic, orient='index')
olive_clean_df = olive_clean_df.transpose()
olive_clean_df.head()


# In[ ]:


# 할인가 정상적으로 들어갔는지 확인
print(len(dis_prices))
print(olive_clean_df.loc[olive_clean_df['dis_price']=='']['product'].nunique())
olive_clean_df.loc[olive_clean_df['dis_price']=='']


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 생성
olive_clean_df.reset_index(inplace=True)
olive_clean_df.head()


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 변경 및 값 변경
olive_clean_df.rename(columns={'index':'ranking'}, inplace=True)
olive_clean_df['ranking'] = olive_clean_df['ranking'].apply(lambda x : x+1)
olive_clean_df.head()


# In[ ]:


# 원본 데이터 저장
# olive_clean_df.to_csv("oliveyoung_cleansing_ranking.csv", index=False, encoding="utf-8-sig")


# ### 4. 선케어 랭킹

# In[ ]:


# 선케어 랭킹 페이지 로드
driver.get("https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo=10000010011&pageIdx=1&rowsPerPage=8&t_page=%EB%9E%AD%ED%82%B9&t_click=%ED%8C%90%EB%A7%A4%EB%9E%AD%ED%82%B9_%EC%84%A0%EC%BC%80%EC%96%B4")
time.sleep(3)  # 페이지 로드 대기


# In[ ]:


# 2. 페이지 스크롤
prev_height = driver.execute_script("return document.body.scrollHeight")

# 1위 - 100위
while True:
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 새로운 높이 가져오기
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        break
    prev_height = new_height


# In[ ]:


# 3-1. 랭킹 페이지 데이터 추출출
titles = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/span')
products = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/p')
or_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[1]/span')
dis_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[2]/span')

print(len(titles))
print(len(products))
print(len(or_prices))
print(len(dis_prices)) # 세일 안하는 상품들 맞는지 더블 체크 필요


# In[ ]:


# 4-2. 데이터 텍스트로 변환
title_list = [t.text for t in titles]
print(title_list[0:5])

product_list = [p.text for p in products]
print(product_list[0:5])

or_price_list = [op.text for op in or_prices]
print(or_price_list[0:5])

# dis_price_list = [dis.text for dis in dis_prices]
# print(dis_price_list[0:5])


# In[ ]:


# 4-1. 할인가 밀림 현상 방지 및 데이터 텍스트 변환
dis_price_list = []

for w in range(1, 26):
  for l in range(1, 5):
    
    try:
      dis = driver.find_element(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/p[1]/span[2]/span')
      if dis.text:
         dis_price_list.append(dis.text)
      else:
        dis_price_list.append('') 
             
    except:
      dis_price_list.append('')
      
print(len(dis_price_list))
print(dis_price_list[:5])


# In[ ]:


# 3-2. 상품 상세 페이지 데이터 추출
wait = WebDriverWait(driver, 10)

main_classes = []
mid_classes = []
sub_classes = []
review_nums = []
review_scores = []

for w in range(1, 26):
  for l in range(1, 5):
    detail_page = driver.find_elements(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')
    
    if detail_page:
        detail_page[0].click()
    else:
      continue

    main_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="midCatNm"]'))).text
    mid_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="smlCatNm"]'))).text
    sub_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dtlCatNm"]'))).text 
    num = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/em'))).text
    score = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/b'))).text
  
    main_classes.append(main_class)
    mid_classes.append(mid_class)
    sub_classes.append(sub_class)
    review_nums.append(num)
    review_scores.append(score)

    driver.back()
    wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')))


# In[ ]:


# 4-2. 데이터 개수 확인
print(len(main_classes))
print(len(mid_classes))
print(len(sub_classes))
print(len(review_nums))
print(len(review_scores))

print(main_classes[0:5])
print(mid_classes[0:5])
print(sub_classes[0:5])
print(review_nums[0:5])
print(review_scores[0:5])


# In[ ]:


# 5. 데이터 저장
olive_suncare_dic = {"brand": title_list, "product": product_list, "or_price": or_price_list, "dis_price": dis_price_list, "main_class": main_classes, "mid_class": mid_classes, "sub_class": sub_classes, "review_num": review_nums, "review_score": review_scores}


# In[ ]:


# DF 변환
olive_suncare_df = pd.DataFrame.from_dict(olive_suncare_dic, orient='index')
olive_suncare_df = olive_suncare_df.transpose()
olive_suncare_df.head()


# In[ ]:


# 할인가 정상적으로 들어갔는지 확인
print(len(dis_prices))
print(olive_suncare_df.loc[olive_suncare_df['dis_price']=='']['product'].nunique())
olive_suncare_df.loc[olive_suncare_df['dis_price']=='']


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 생성
olive_suncare_df.reset_index(inplace=True)
olive_suncare_df.head()


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 변경 및 값 변경
olive_suncare_df.rename(columns={'index':'ranking'}, inplace=True)
olive_suncare_df['ranking'] = olive_suncare_df['ranking'].apply(lambda x : x+1)
olive_suncare_df.head()


# ### 5. 메이크업 랭킹

# In[ ]:


# 메이크업업 랭킹 페이지 로드
driver.get("https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo=10000010002&pageIdx=1&rowsPerPage=8&t_page=%EB%9E%AD%ED%82%B9&t_click=%ED%8C%90%EB%A7%A4%EB%9E%AD%ED%82%B9_%EB%A9%94%EC%9D%B4%ED%81%AC%EC%97%85")
time.sleep(3)  # 페이지 로드 대기


# In[ ]:


# 2. 페이지 스크롤
prev_height = driver.execute_script("return document.body.scrollHeight")

# 1위 - 100위
while True:
    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 새로운 높이 가져오기
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == prev_height:
        break
    prev_height = new_height


# In[ ]:


# 3-1. 랭킹 페이지 데이터 추출출
titles = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/span')
products = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/div/a/p')
or_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[1]/span')
dis_prices = driver.find_elements(By.XPATH, '//*[@id="Container"]/div[2]/div[2]/ul/li/div/p[1]/span[2]/span')

print(len(titles))
print(len(products))
print(len(or_prices))
print(len(dis_prices)) # 세일 안하는 상품들 맞는지 더블 체크 필요


# In[ ]:


# 4-1. 데이터 텍스트로 변환
title_list = [t.text for t in titles]
print(title_list[0:5])

product_list = [p.text for p in products]
print(product_list[0:5])

or_price_list = [op.text for op in or_prices]
print(or_price_list[0:5])

# dis_price_list = [dis.text for dis in dis_prices]
# print(dis_price_list[0:5])


# In[ ]:


# 4-1. 할인가 밀림 현상 방지 및 데이터 텍스트 변환
dis_price_list = []

for w in range(1, 26):
  for l in range(1, 5):
    
    try:
      dis = driver.find_element(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/p[1]/span[2]/span')
      if dis.text:
         dis_price_list.append(dis.text)
      else:
        dis_price_list.append('') 
             
    except:
      dis_price_list.append('')
      
print(len(dis_price_list))
print(dis_price_list[:5])


# In[ ]:


# 3-2. 상품 상세 페이지 데이터 추출
wait = WebDriverWait(driver, 10)

main_classes = []
mid_classes = []
sub_classes = []
review_nums = []
review_scores = []

for w in range(1, 26):
  for l in range(1, 5):
    detail_page = driver.find_elements(By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')
    
    if detail_page:
        detail_page[0].click()
    else:
      continue

    main_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="midCatNm"]'))).text
    mid_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="smlCatNm"]'))).text
    sub_class = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dtlCatNm"]'))).text 
    num = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/em'))).text
    score = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="repReview"]/b'))).text
  
    main_classes.append(main_class)
    mid_classes.append(mid_class)
    sub_classes.append(sub_class)
    review_nums.append(num)
    review_scores.append(score)

    driver.back()
    wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="Container"]/div[2]/div[2]/ul[{w}]/li[{l}]/div/a')))


# In[ ]:


# 4-2. 데이터 개수 확인
print(len(main_classes))
print(len(mid_classes))
print(len(sub_classes))
print(len(review_nums))
print(len(review_scores))

print(main_classes[0:5])
print(mid_classes[0:5])
print(sub_classes[0:5])
print(review_nums[0:5])
print(review_scores[0:5])


# In[ ]:


# 5. 데이터 저장
olive_makeup_dic = {"brand": title_list, "product": product_list, "or_price": or_price_list, "dis_price": dis_price_list, "main_class": main_classes, "mid_class": mid_classes, "sub_class": sub_classes, "review_num": review_nums, "review_score": review_scores}


# In[ ]:


# DF 변환
olive_makeup_df = pd.DataFrame.from_dict(olive_makeup_dic, orient='index')
olive_makeup_df = olive_makeup_df.transpose()
olive_makeup_df.head()


# In[ ]:


# 할인가 정상적으로 들어갔는지 확인
print(len(dis_prices))
print(olive_makeup_df.loc[olive_makeup_df['dis_price']=='']['product'].nunique())
olive_makeup_df.loc[olive_makeup_df['dis_price']=='']


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 생성
olive_makeup_df.reset_index(inplace=True)
olive_makeup_df.head()


# In[ ]:


# 인덱스 순으로 랭킹 컬럼 삽입 - 인덱스 컬럼 변경 및 값 변경
olive_makeup_df.rename(columns={'index':'ranking'}, inplace=True)
olive_makeup_df['ranking'] = olive_makeup_df['ranking'].apply(lambda x : x+1)
olive_makeup_df.head()


# In[ ]:


# 원본 데이터 저장
# olive_makeup_df.to_csv("oliveyoung_makeup_ranking.csv", index=False, encoding="utf-8-sig")


# In[162]:


driver.quit()


# ### 데이터셋 공통 전처리

# In[ ]:


olive_df = pd.concat([olive_skincare_df, olive_clean_df, olive_mask_df, olive_suncare_df, olive_makeup_df], axis=0, ignore_index=True)
print(olive_df.info())
olive_df.head()


# In[ ]:


# 1. 상품명 정리 - 신버전 
for i in range(len(olive_df)):
  
  name_list = olive_df['product'][i].split(']')
  max_i = len(name_list)-1
  
  if (len(name_list) == 2):
    if (name_list[0][0] == '['):
      if name_list[1] == '': # 3)의 경우
        name_result = name_list[0]
        name_result = name_result.strip('[')
        name_result = name_result.strip()
        olive_df['product'][i] = name_result
      else: # 1)의 경우 
        name_result = name_list[1]
        name_result = name_result.strip()
        olive_df['product'][i] = name_result
    
    else: # 2)의 경우
      name_result = name_list[0]
      second_list = name_result.split('[')
      name_result2 = second_list[0]
      olive_df['product'][i] = name_result2
  
  elif (len(name_list)==1): # 5)의 경우 
    name_result = name_list[0]
    olive_df['product'][i] = name_result
  
  else: # 길이가 3일 경우
    if name_list[2] == '': # 4)의 경우 
      name_result = name_list[1]
      second_list = name_result.split('[')
      name_result2 = second_list[0]
      olive_df['product'][i] = name_result2
    
    else: # 6의 경우 
      name_result = name_list[2]
      name_result = name_result.strip()
      olive_df['product'][i] = name_result

print(olive_df['product'].unique())     
  
  # 경우의 수
  # 1) [] 가 맨 앞에 있을 경우('[', '상품명') -> 리스트의 마지막 글자 사용 name_result = name_list[i][max_i] -> name_result.strip() => 상품명
  # 3) [] 안이 상품명일 경우('[상품명','') -> name_result = name_list[i][0] -> name_result.strip('[') & strip() => 상품명
  
  # 2) [] 가 맨 뒤에 있을 경우('상품명[~', '') -> 리스트의 첫 글자 사용 name_result = name_list[i][0] => 상품명[~
  
  # 4) [] 가 앞뒤로 있을 경우('[~','상품명[~','') -> name_result = name_list[i][max_1-1] => 상품명[~
  
  # 5) [] 가 아예 없는 경우 
  
  # 6) []가 두번 연속 있을 경우 


# In[ ]:


# 결측치 더블체크
print(olive_df[olive_df['product'] == ''])
print(olive_df[olive_df['product'] == ' '])


# In[ ]:


# 2. 리뷰 수 서식 지우기

for i in range(len(olive_df)):
  review = olive_df['review_num'][i]

  review_result = review.strip('(''건'')')
  review_result = review_result.replace(',', '')
  olive_df.loc[i, 'review_num'] = review_result

print(olive_df.loc[:5, 'review_num'])


# In[ ]:


# 결측값이 float 형태로 읽히는 것을 방지하기 위해 결측값 공백으로 대체
olive_df['dis_price'].fillna('', inplace=True)

olive_df.info()


# In[ ]:


# 3. 컬럼 타입 변경 : score(float), review_num(int), price(num)
# 1) price 컬럼의 쉼표 없애기

for i in range(len(olive_df)):
  or_p = olive_df['or_price'][i]
  dis_p = olive_df['dis_price'][i]
  
  or_result = or_p.replace(',', '')
  dis_result = dis_p.replace(',', '')
  
  olive_df.loc[i, 'or_price'] = or_result
  olive_df.loc[i, 'dis_price'] = dis_result

print(olive_df.loc[:5, ['or_price', 'dis_price', 'review_num']])


# In[ ]:


# 3. 컬럼 타입 변경 : score(float), review_num(int), price(num)
# 2) 컬럼 타입 변경

olive_df[['or_price', 'dis_price', 'review_num', 'review_score']] = olive_df[['or_price', 'dis_price', 'review_num', 'review_score']].apply(pd.to_numeric)

print(olive_df[['or_price', 'dis_price', 'review_num', 'review_score']].dtypes)
print(olive_df.loc[:5, ['or_price', 'dis_price', 'review_num', 'review_score']])


# In[ ]:


# 4. 플랫폼 컬럼 삽입 : df['플랫폼'] = '올리브영'
olive_df['플랫폼'] = '올리브영'
print(olive_df.info())


# In[ ]:


# 5. 컬럼명 및 순서 변경 : 플랫폼-브랜드-제품명-대분류_순위-대분류-중분류-소분류-평점-후기 수-가격
# 1) 컬럼명 변경
olive_df.columns = ['중분류_순위', '브랜드', '제품명', '정가', '할인가', '대분류', '중분류', '소분류', '후기 수', '평점', '플랫폼']
print(olive_df.columns)


# In[ ]:


olive_df = olive_df.reindex(['플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류', '소분류', '평점', '후기 수', '정가', '할인가'], axis=1)

print(olive_df.info())


# In[ ]:


# 데이터셋 저장
# olive_df.to_csv('통합_올리브영_데이터.csv', index=False)


# ## 앳코스메 : df_detail

# ### 01.코스메 한국 브랜드 제품 (리뷰수 내림차순)

# In[ ]:


from tqdm import tqdm


# In[ ]:


brand_names = []
product_names = []
category_names = []
rating_list = []
review_list = []
price_list = []
onsale_date = []
url_list = []

# 사이트 이동 (tqdm 적용)
for page_num in tqdm(range(1, 301), desc="Scraping Progress", unit="page"):
    url = f"https://www.cosme.net/categories/pickup/1039/product/?page={page_num}&sort=review"
    
    response = requests.get(url)
    time.sleep(random.uniform(5, 10))
    soup = BeautifulSoup(response.text, "html.parser")

    # 브랜드
    brands = soup.find_all("span", class_="brand")
    for span in brands:
        a_tag = span.find("a")
        if a_tag:
            brand_names.append(a_tag.text)
    
    # 아이템
    items = soup.find_all("h3", class_="item")
    for span in items:
        a_tag = span.find("a")  
        if a_tag:
            product_names.append(a_tag.text)

    # 카테고리
    categorys = soup.find_all("p", class_="category")
    for span in categorys:
        a_tag = span.find("a")  
        if a_tag:
            category_names.append(a_tag.text)

    # 평점
    rating_point_tags = soup.find_all('span', class_=lambda x: x and 'value reviewer-average' in x)
    for rating_point_tag in rating_point_tags:
        if rating_point_tag:
            rating = rating_point_tag.get_text().strip()
            rating_list.append(rating)

    # 리뷰 수
    review_tags = soup.find_all("a", class_="count")
    for review_tag in review_tags:
        review_count = review_tag.get_text().strip()
        review_list.append(review_count)

    # URL
    urls = soup.find_all("p", class_="pic")
    for url in urls:
        a_tag = url.find("a")
        if a_tag:
            url_list.append(a_tag.get("href"))

    # 가격과 발매일 정보 추출
    price_tags = soup.find_all("span", class_="price")
    release_date_tags = soup.find_all("span", class_="sell")
    
    for price_tag, release_date_tag in zip(price_tags, release_date_tags):
        price = price_tag.get_text().strip()
        release_date = release_date_tag.get_text().strip()
        price_list.append(price)
        onsale_date.append(release_date)


# In[ ]:


now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

df = pd.DataFrame({
    "브랜드" : brand_names,
    "제품명" : product_names,
    "카테고리" : category_names,
    "평점" : rating_list,
    "리뷰수" : review_list,
    "가격(円)" : price_list,
    "발매일" : onsale_date,
    'url' : url_list,
    '업로드일' : now
})
# 순위
df = df.reset_index()
df.rename(columns = {'index' : '순위'}, inplace=True)
df['순위'] = df['순위'] + 1

# 발매일에서 날짜 부분만 추출
df['발매일'] = df['발매일'].apply(lambda x: re.sub(r'発売日：', '', x))

# URL에서 상품 ID 추출
df['상품ID'] = df['url'].apply(lambda x: re.search(r'products/(\d+)', x).group(1))

# 가격 전처리 함수
def extract_price(price_text):
    # 정규표현식을 사용하여 숫자만 추출
    price_numbers = re.findall(r'(\d+,?\d*)', price_text)
    if price_numbers:
        # 쉼표가 있는 경우 처리
        final_price = price_numbers[-1].replace(',', '')
        return final_price
    return "0"  # 숫자가 없는 경우 기본값

# 가격 컬럼 전처리
df['가격(円)'] = df['가격(円)'].apply(extract_price)
print(df.shape)
df.head()


# In[ ]:


df.to_csv("cosme_korea/korea_cosme_product_3000.csv", index=False, encoding="utf-8")


# ### 02.코스메 한국 브랜드 제품 (리뷰수 내림차순) 상세

# In[ ]:


df = pd.read_csv("cosme_korea/korea_cosme_product_3000.csv")


# In[ ]:


# 제품 정보를 저장할 리스트 생성
all_product_details = []

# 각 제품에 대해 정보 수집 (tqdm 적용)
for product_id in tqdm(df['상품ID'].to_list(), desc="Product Scraping", unit="product"):
    url = f"https://www.cosme.net/products/{product_id}/"
    
    product_details = {'product_id': product_id}  
    response = requests.get(url)
    time.sleep(random.uniform(5, 10)) # 3~5 해도 될 듯
    soup = BeautifulSoup(response.text, "html.parser")

    maker = soup.find("dl", class_="maker clearfix")
    if maker:
        maker_name = maker.find("a").text.strip()
        product_details['メーカー'] = maker_name

    brand = soup.find("dl", class_="brand-name clearfix")
    if brand:
        brand_name = brand.find("a").text.strip()
        product_details['ブランド名'] = brand_name

    category = soup.find("dl", class_="item-category clearfix")
    if category:
        category_names = " > ".join([a.text.strip() for a in category.find_all("a")])
        product_details['アイテムカテゴリ'] = category_names

    bestcosme = soup.find("dl", class_="bestcosme clearfix")
    if bestcosme:
        bestcosme_awards = {}
        for idx, li in enumerate(bestcosme.find_all("li"), start=1):
            award_text = li.find("a").text.strip()
            award_url = li.find("a")["href"]
            bestcosme_awards[f"BestCosme_Award_{idx}"] = award_text
        product_details['ベストコスメ'] = bestcosme_awards

    rankingIn = soup.find("dl", class_="ranking-in clearfix")
    if rankingIn:
        product_details['ランキングIN'] = rankingIn.find("a").text.strip().replace("\u3000", " ")

    all_product_details.append(product_details)

# DataFrame 변환 및 저장
df_detail = pd.DataFrame(all_product_details)
df_detail.to_csv("cosme_korea/korea_cosme_product_3000_details.csv", index=False, encoding="utf-8")


# # 2. 데이터 전처리

# - 값 형식 통일
# - 분류(카테고리) 통합
# - 플랫폼 데이터 통합
# - 외국 브랜드 삭제

# ## 무신사뷰티 : musinsa_df

# In[7]:


# 데이터셋 복제
musinsa_df = df_combined.copy(deep=True)


# In[8]:


# 데이터셋 기본 정보 조회
print(musinsa_df.info())
print(musinsa_df.head(3))


# ### 기본 전처리

# In[9]:


# 1. 컬럼 타입 변경 : 평점(float), 후기 수(int), 가격(int)
# 1) 후기 수 & 가격 컬럼의 쉼표 없애기
# + 평점 컬럼의 '별점 없음' 을 0으로 변경

for i in range(len(musinsa_df)):
  score = musinsa_df['평점'][i]
  review = musinsa_df['후기 수'][i]
  price = musinsa_df['가격'][i]
  
  score_result = score.replace('별점 없음', '0')
  review_result = review.replace(',', '')
  price_result = price.replace(',', '')
  
  musinsa_df.loc[i, '평점'] = score_result
  musinsa_df.loc[i, '후기 수'] = review_result
  musinsa_df.loc[i, '가격'] = price_result

print(musinsa_df.loc[:10, ['평점', '후기 수', '가격']])


# In[10]:


# 1. 컬럼 타입 변경 : 평점(float), 후기 수(int), 가격(int)
# 2) 컬럼 타입 변경

musinsa_df[['평점', '후기 수', '가격']] = musinsa_df[['평점', '후기 수', '가격']].apply(pd.to_numeric)

print(musinsa_df[['평점', '후기 수', '가격']].dtypes)
print(musinsa_df.loc[:5, ['평점', '후기 수', '가격']])


# In[11]:


# 2. 컬럼 이름 변경
musinsa_df.rename(columns = {'순위':'중분류_순위', '카테고리':'대분류'}, inplace=True)
musinsa_df.columns


# In[12]:


# 3. 플랫폼 컬럼 추가 및 순서 변경 : '플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류', '소분류', '평점', '후기 수', '정가', '할인가'
musinsa_df['플랫폼'] = '무신사뷰티'

before_a = ['플랫폼']
a = ['브랜드', '제품명']
after_a = musinsa_df.drop(columns = {'플랫폼', '브랜드', '제품명'}).columns[:].to_list()

reorder = before_a + a + after_a
musinsa_df = musinsa_df[reorder]

musinsa_df.columns


# ### 대분류 및 중분류 통합

# In[13]:


# 1. 중분류1 & 중분류2 컬럼 생성
musinsa_df['중분류1'] = ''
print(musinsa_df['중분류1'].head())

musinsa_df['중분류2'] = ''
print(musinsa_df['중분류2'].head())


# In[14]:


# 기존 분류별 unique 값 확인
print(musinsa_df['대분류'].unique())
print(musinsa_df['중분류'].unique())
print(musinsa_df['소분류'].unique())


# In[15]:


# 기타 컬럼 소속 예정 값의 대분류 값 확인
cond1 = musinsa_df['중분류'] == '기획세트'
print(musinsa_df.loc[cond1, '대분류'].unique()) # 스킨케어

cond2 = musinsa_df['중분류'] == '립&아이 리무버'
print(musinsa_df.loc[cond2, '대분류'].unique()) # 클렌징 -> 기타에서 제외

cond3 = musinsa_df['중분류'] == '미스트'
print(musinsa_df.loc[cond3, '대분류'].unique()) # 스킨케어

cond4 = musinsa_df['중분류'] == '올인원'
print(musinsa_df.loc[cond4, '대분류'].unique()) # 스킨케어 

cond5 = musinsa_df['중분류'] == '스팟케어'
print(musinsa_df.loc[cond5, '대분류'].unique()) # 스킨케어 


# In[16]:


# 중분류2
# 스킨케어 - 마스크팩, 클렌징, 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림, 기타
# 베이스메이크업 - 선케어, 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 색조메이크업 - 립메이크업, 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제

skin_list = ['패드', '스킨/토너']
skin = '|'.join(skin_list)
cond_skin = musinsa_df['중분류'].str.contains(skin)

found_list = ['파운데이션', '쿠션', 'BB', 'CC']
found  = '|'.join(found_list)
cond_found = musinsa_df['소분류'].str.contains(found)

fixer_list = ['파우더', '팩트', '픽서']
fixer = '|'.join(fixer_list)
cond_fixer = musinsa_df['소분류'].str.contains(fixer)

shading_list = ['블러셔', '쉐이딩', '셰이딩', '하이라이터']
shading = '|'.join(shading_list)
cond_shading = musinsa_df['소분류'].str.contains(shading)

primer_list = ['프라이머', '베이스']
primer = '|'.join(primer_list)
cond_primer = musinsa_df['소분류'].str.contains(primer)

for i in range(len(musinsa_df)):
    if musinsa_df['대분류'][i] == '클렌징':
      musinsa_df.loc[i, '중분류2'] = '클렌징'

    elif musinsa_df['중분류'][i] == '에센스/세럼/앰플':
      musinsa_df.loc[i, '중분류2'] = '에센스/세럼/앰플'

    elif musinsa_df['중분류'][i] == '마스크팩':
      musinsa_df.loc[i, '중분류2'] = '마스크팩'
      
    elif musinsa_df['중분류'][i] == '크림':
      musinsa_df.loc[i, '중분류2'] = '크림'

    elif musinsa_df['중분류'][i] == '로션':
      musinsa_df.loc[i, '중분류2'] = '로션'

    elif musinsa_df['대분류'][i] == '썬케어':
      musinsa_df.loc[i, '중분류2'] = '선케어'

    elif musinsa_df['소분류'][i] == '컨실러':
      musinsa_df.loc[i, '중분류2'] = '컨실러'

    elif musinsa_df['중분류'][i] == '립메이크업':
      musinsa_df.loc[i, '중분류2'] = '립메이크업'
      
    elif musinsa_df['소분류'][i] == '아이라이너':
      musinsa_df.loc[i, '중분류2'] = '아이라이너'

    elif musinsa_df['소분류'][i] == '아이섀도':
      musinsa_df.loc[i, '중분류2'] = '아이섀도우'
      
    elif musinsa_df['소분류'][i] == '아이브로':
      musinsa_df.loc[i, '중분류2'] = '아이브로우'

    elif musinsa_df['소분류'][i] == '마스카라':
      musinsa_df.loc[i, '중분류2'] = '마스카라'
    
    elif cond_skin[i] == True:
      musinsa_df.loc[i, '중분류2'] = '토너/토너패드/스킨'
    
    elif cond_found[i] == True:
      musinsa_df.loc[i, '중분류2'] = '파운데이션/쿠션/BB/CC'

    elif cond_fixer[i] == True:
      musinsa_df.loc[i, '중분류2'] = '파우더/팩트/픽서'
    
    elif cond_shading[i] == True:
      musinsa_df.loc[i, '중분류2'] = '블러셔/쉐이딩/하이라이터'

    elif cond_primer[i] == True:
      musinsa_df.loc[i, '중분류2'] = '프라이머/베이스'
      
    else: # 기획세트
      musinsa_df.loc[i, '중분류2'] = '기타'


# In[17]:


print(musinsa_df['중분류2'].unique())
print(musinsa_df['중분류2'].nunique())
musinsa_df.loc[:, ['대분류', '중분류', '소분류', '중분류2']]


# In[18]:


# 중분류1 - 중분류2
# 스킨케어 - 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림
# 베이스메이크업 - 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 아이메이크업 - 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제
# 클렌징 / # 마스크팩 / # 기타 / # 선케어 / # 립메이크업

skincare_list = ['토너/토너패드/스킨', '에센스/세럼/앰플', '로션', '크림']
skincare = '|'.join(skincare_list)
cond_skincare = musinsa_df['중분류2'].str.contains(skincare)

base_list = ['파운데이션/쿠션/BB/CC', '파우더/팩트/픽서', '블러셔/쉐이딩/하이라이터', '프라이머/베이스', '컨실러']
base = '|'.join(base_list)
cond_base = musinsa_df['중분류2'].str.contains(base)

eye_list = ['아이섀도우', '아이라이너', '아이브로우', '마스카라', '속눈썹 영양제']
eye = '|'.join(eye_list)
cond_eye = musinsa_df['중분류2'].str.contains(eye)

for i in range(len(musinsa_df)):
  if cond_skincare[i] == True:
    musinsa_df.loc[i, '중분류1'] = '스킨케어'
  
  elif cond_base[i] == True:
    musinsa_df.loc[i, '중분류1'] = '베이스메이크업'

  elif cond_eye[i] == True:
    musinsa_df.loc[i, '중분류1'] = '아이메이크업'
      
  else:
    if musinsa_df['중분류2'][i] == '클렌징':
      musinsa_df.loc[i, '중분류1'] = '클렌징'

    elif musinsa_df['중분류2'][i] == '마스크팩':
      musinsa_df.loc[i, '중분류1'] = '마스크팩'
      
    elif musinsa_df['중분류2'][i] == '기타':
      musinsa_df.loc[i, '중분류1'] = '기타'
      
    elif musinsa_df['중분류2'][i] == '선케어':
      musinsa_df.loc[i, '중분류1'] = '선케어'
    
    elif musinsa_df['중분류2'][i] == '립메이크업':
      musinsa_df.loc[i, '중분류1'] = '립메이크업'


# In[19]:


print(musinsa_df['중분류1'].unique())
print(musinsa_df['중분류1'].nunique())
musinsa_df.loc[:, ['대분류', '중분류', '소분류', '중분류1', '중분류2']]


# In[20]:


# 대분류 - 중분류1
# 스킨케어 - 마스크팩, 클렌징, 기타, 스킨케어
# 베이스메이크업 - 선케어, 베이스메이크업
# 색조메이크업 - 립메이크업, 아이메이크업

skinclass_list = ['마스크팩', '클렌징', '기타', '스킨케어']
skinclass = '|'.join(skinclass_list)
cond_skinclass = musinsa_df['중분류1'].str.contains(skinclass)

baseclass_list = ['선케어', '베이스메이크업']
baseclass = '|'.join(baseclass_list)
cond_baseclass = musinsa_df['중분류1'].str.contains(baseclass)

colorclass_list = ['아이메이크업', '립메이크업']
colorclass = '|'.join(colorclass_list)
cond_colorclass = musinsa_df['중분류1'].str.contains(colorclass)

for i in range(len(musinsa_df)):
  if cond_skinclass[i] == True:
    musinsa_df.loc[i, '대분류'] = '스킨케어'
  
  elif cond_baseclass[i] == True:
    musinsa_df.loc[i, '대분류'] = '베이스메이크업'

  elif cond_colorclass[i] == True:
    musinsa_df.loc[i, '대분류'] = '색조메이크업'


# In[21]:


# 대분류 고유값 확인 
print(musinsa_df['대분류'].unique())
print(musinsa_df['대분류'].nunique())
musinsa_df.loc[:, ['대분류', '중분류', '소분류', '중분류1', '중분류2']]


# ### 립메이크업 중분류 세분화

# In[22]:


# musinsa_df
musinsa_df.head()


# In[23]:


# 중분류2 복제
musinsa_df['중분류3'] = musinsa_df['중분류2']
musinsa_df['중분류3'].head()


# In[24]:


# '중분류2 = 립메이크업 제품' 소분류 카테고리 고유값 확인
cond = musinsa_df['중분류2'] == '립메이크업'
musinsa_df.loc[cond, '소분류'].unique()


# In[25]:


# 립메이크업- 립글로스/립밤/립스틱/립라이너/립틴트 

for i in range(len(musinsa_df)):
  if musinsa_df['소분류'][i] == '립글로스':
    musinsa_df.loc[i, '중분류3'] = '립글로스'

  elif musinsa_df['소분류'][i] == '립밤':
    musinsa_df.loc[i, '중분류3'] = '립밤'
    
  elif musinsa_df['소분류'][i] == '립스틱':
    musinsa_df.loc[i, '중분류3'] = '립스틱'
    
  elif musinsa_df['소분류'][i] == '립라이너':
    musinsa_df.loc[i, '중분류3'] = '립라이너'

  elif musinsa_df['소분류'][i] == '립틴트':
    musinsa_df.loc[i, '중분류3'] = '립틴트'


# In[26]:


# 중분류3 입력값 확인
cond = musinsa_df['중분류2'] == '립메이크업'
print(musinsa_df.loc[cond, '중분류3'].unique())
print(musinsa_df.loc[cond, '중분류3'].nunique())
musinsa_df.loc[cond, ['소분류', '중분류3']].head()


# ### 데이터셋 정리

# In[27]:


# 기존 카테고리 지우기
musinsa_df.drop(columns={'중분류', '소분류'}, axis=1, inplace=True)
musinsa_df.info()


# In[28]:


# 컬럼 순서 변경 : '플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류1', '중분류2', '중분류3', '평점', '후기 수', '정가', '할인가'
a = ['중분류1', '중분류2', '중분류3']

before_a = musinsa_df.drop(columns = {'중분류1', '중분류2', '중분류3'}).columns[:5].to_list()
after_a = musinsa_df.drop(columns = {'중분류1', '중분류2', '중분류3'}).columns[5:].to_list()

reorder = before_a + a + after_a
musinsa_df = musinsa_df[reorder]

musinsa_df.columns


# In[29]:


# 최종 데이터셋 확인
print(musinsa_df.info())
musinsa_df.head()


# In[ ]:


# 최종 데이터셋 저장
# musinsa_df.to_csv('musinsa_preprocessing.csv', index=False, encoding="utf-8-sig")


# ## 화해 : hwahae_df

# In[31]:


# 데이터셋 복제
hwahae_df = final_df.copy(deep=True)


# In[32]:


# 데이터셋 기본 정보 조회
print(hwahae_df.info())
print(hwahae_df.head(3))


# ### 기본 전처리

# In[33]:


# 1. 컬럼 타입 변경 : 평점(float), 후기 수(int), 가격(int)
# 1) 후기 수 & 가격 컬럼의 쉼표 없애기
# 원본 데이터셋에 전처리 되어있음

'''
for i in range(len(hwahae_df)):
  score = hwahae_df['평점'][i]
  review = hwahae_df['후기 수'][i]
  price = hwahae_df['가격'][i]
  
  score_result = score.replace('별점 없음', '0')
  review_result = review.replace(',', '')
  price_result = price.replace(',', '')
  
  hwahae_df.loc[i, '평점'] = score_result
  hwahae_df.loc[i, '후기 수'] = review_result
  hwahae_df.loc[i, '가격'] = price_result

print(hwahae_df.loc[:10, ['평점', '후기 수', '가격']])
'''


# In[34]:


# 1. 컬럼 타입 변경 : 평점(float), 후기 수(int), 가격(int)
# 2) 컬럼 타입 변경
# 원본 데이터셋에 전처리 되어있음

'''
hwahae_df[['평점', '후기 수', '가격']] = hwahae_df[['평점', '후기 수', '가격']].apply(pd.to_numeric)

print(hwahae_df[['평점', '후기 수', '가격']].dtypes)
print(hwahae_df.loc[:5, ['평점', '후기 수', '가격']])
'''


# In[35]:


# 2. 컬럼 이름 변경
# 원본 데이터셋에 전처리 되어있음

'''
hwahae_df.rename(columns = {'순위':'중분류_순위', '카테고리':'대분류'}, inplace=True)
hwahae_df.columns
'''


# In[36]:


# 3. 플랫폼 컬럼 추가 및 순서 변경
# 원본 데이터셋에 전처리 되어있음

'''
hwahae_df['플랫폼'] = '화해'

a = hwahae_df.columns[-1:].to_list()

ex_a = hwahae_df.drop(columns = hwahae_df.columns[[-1]]).columns[:].to_list()

reorder = a + ex_a
hwahae_df = hwahae_df[reorder]

hwahae_df.columns
'''


# ### 카테고리 전처리

# In[37]:


# 1. 중분류1 & 중분류2 컬럼 생성
hwahae_df['중분류1'] = ''
print(hwahae_df['중분류1'].head())

hwahae_df['중분류2'] = ''
print(hwahae_df['중분류2'].head())


# In[38]:


# 기존 분류별 unique 값 확인
print(hwahae_df['대분류'].unique())
print(hwahae_df['중분류'].unique())
print(hwahae_df['소분류'].unique())


# In[39]:


# 기타 컬럼 소속 예정 값의 대분류 값 확인
cond1 = hwahae_df['중분류'] == '아이케어'
print(hwahae_df.loc[cond1, '대분류'].unique()) # 스킨케어

cond2 = hwahae_df['중분류'] == '미스트'
print(hwahae_df.loc[cond2, '대분류'].unique()) # 스킨케어

cond3 = hwahae_df['중분류'] == '젤'
print(hwahae_df.loc[cond3, '대분류'].unique()) # 스킨케어


# In[40]:


# 통합 필요한 세부 카테고리 확인
cond1 = hwahae_df['대분류'] == '스킨케어'
print(hwahae_df.loc[cond1, '중분류'].unique()) 

cond2 = hwahae_df['대분류'] == '베이스메이크업'
print(hwahae_df.loc[cond2, '중분류'].unique()) 

cond3 = hwahae_df['대분류'] == '아이메이크업'
print(hwahae_df.loc[cond3, '중분류'].unique()) 


# In[41]:


# 중분류2
# 스킨케어 - 마스크팩, 클렌징, 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림, 기타
# 베이스메이크업 - 선케어, 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 색조메이크업 - 립메이크업, 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제

skin_list = ['패드', '스킨', '토너']
skin = '|'.join(skin_list)
cond_skin = hwahae_df['중분류'].str.contains(skin)

found_list = ['파운데이션', '쿠션', 'BB', 'CC']
found  = '|'.join(found_list)
cond_found = hwahae_df['중분류'].str.contains(found)

fixer_list = ['파우더', '팩트', '메이크업픽서']
fixer = '|'.join(fixer_list)
cond_fixer = hwahae_df['중분류'].str.contains(fixer)

shading_list = ['블러셔', '쉐이딩', '셰이딩', '하이라이터']
shading = '|'.join(shading_list)
cond_shading = hwahae_df['중분류'].str.contains(shading)

primer_list = ['프라이머', '베이스', '톤업크림'] # 프라이머/베이스 컬럼에 (소분류)톤업크림 추가
primer = '|'.join(primer_list)
cond_primer = hwahae_df['중분류'].str.contains(primer)

for i in range(len(hwahae_df)):

    if hwahae_df['중분류'][i] == '로션_에멀젼':
      hwahae_df.loc[i, '중분류2'] = '로션'

    elif hwahae_df['중분류'][i] == '에센스_앰플_세럼':
      hwahae_df.loc[i, '중분류2'] = '에센스/세럼/앰플'
    
    elif hwahae_df['중분류'][i] == '크림':
      hwahae_df.loc[i, '중분류2'] = '크림'

    elif hwahae_df['대분류'][i] == '마스크_팩':
      hwahae_df.loc[i, '중분류2'] = '마스크팩'

    elif hwahae_df['대분류'][i] == '클렌징':
      hwahae_df.loc[i, '중분류2'] = '클렌징'

    elif hwahae_df['대분류'][i] == '선케어':
      hwahae_df.loc[i, '중분류2'] = '선케어'

    elif hwahae_df['대분류'][i] == '립메이크업':
      hwahae_df.loc[i, '중분류2'] = '립메이크업'
    
    elif hwahae_df['중분류'][i] == '컨실러':
      hwahae_df.loc[i, '중분류2'] = '컨실러'
      
    elif hwahae_df['중분류'][i] == '아이라이너':
      hwahae_df.loc[i, '중분류2'] = '아이라이너'

    elif hwahae_df['중분류'][i] == '아이섀도':
      hwahae_df.loc[i, '중분류2'] = '아이섀도우'
      
    elif hwahae_df['중분류'][i] == '아이브로우':
      hwahae_df.loc[i, '중분류2'] = '아이브로우'

    elif hwahae_df['중분류'][i] == '마스카라_픽서':
      hwahae_df.loc[i, '중분류2'] = '마스카라'
    
    elif hwahae_df['중분류'][i] == '속눈썹영양제':
      hwahae_df.loc[i, '중분류2'] = '속눈썹영양제'
          
    elif cond_skin[i] == True:
      hwahae_df.loc[i, '중분류2'] = '토너/토너패드/스킨'
    
    elif cond_found[i] == True:
      hwahae_df.loc[i, '중분류2'] = '파운데이션/쿠션/BB/CC'

    elif cond_fixer[i] == True:
      hwahae_df.loc[i, '중분류2'] = '파우더/팩트/픽서'
    
    elif cond_shading[i] == True:
      hwahae_df.loc[i, '중분류2'] = '블러셔/쉐이딩/하이라이터'

    elif cond_primer[i] == True:
      hwahae_df.loc[i, '중분류2'] = '프라이머/베이스'
      
    else: # 기획세트
      hwahae_df.loc[i, '중분류2'] = '기타'


# In[42]:


print(hwahae_df['중분류2'].unique())
print(hwahae_df['중분류2'].nunique())
hwahae_df.loc[:, ['대분류', '중분류', '소분류', '중분류2']]


# In[43]:


# 중분류1 - 중분류2
# 스킨케어 - 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림
# 베이스메이크업 - 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 아이메이크업 - 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제
# 클렌징 / # 마스크팩 / # 기타 / # 선케어 / # 립메이크업

skincare_list = ['토너/토너패드/스킨', '에센스/세럼/앰플', '로션', '크림']
skincare = '|'.join(skincare_list)
cond_skincare = hwahae_df['중분류2'].str.contains(skincare)

base_list = ['파운데이션/쿠션/BB/CC', '파우더/팩트/픽서', '블러셔/쉐이딩/하이라이터', '프라이머/베이스', '컨실러']
base = '|'.join(base_list)
cond_base = hwahae_df['중분류2'].str.contains(base)

eye_list = ['아이섀도우', '아이라이너', '아이브로우', '마스카라', '속눈썹영양제']
eye = '|'.join(eye_list)
cond_eye = hwahae_df['중분류2'].str.contains(eye)

for i in range(len(hwahae_df)):
  if cond_skincare[i] == True:
    hwahae_df.loc[i, '중분류1'] = '스킨케어'
  
  elif cond_base[i] == True:
    hwahae_df.loc[i, '중분류1'] = '베이스메이크업'

  elif cond_eye[i] == True:
    hwahae_df.loc[i, '중분류1'] = '아이메이크업'
      
  else:
    if hwahae_df['중분류2'][i] == '클렌징':
      hwahae_df.loc[i, '중분류1'] = '클렌징'

    elif hwahae_df['중분류2'][i] == '마스크팩':
      hwahae_df.loc[i, '중분류1'] = '마스크팩'
      
    elif hwahae_df['중분류2'][i] == '기타':
      hwahae_df.loc[i, '중분류1'] = '기타'
      
    elif hwahae_df['중분류2'][i] == '선케어':
      hwahae_df.loc[i, '중분류1'] = '선케어'
    
    elif hwahae_df['중분류2'][i] == '립메이크업':
      hwahae_df.loc[i, '중분류1'] = '립메이크업'


# In[44]:


print(hwahae_df['중분류1'].unique())
print(hwahae_df['중분류1'].nunique())
hwahae_df.loc[:, ['대분류', '중분류', '소분류', '중분류1', '중분류2']]


# In[45]:


# 대분류 - 중분류1
# 스킨케어 - 마스크팩, 클렌징, 기타, 스킨케어
# 베이스메이크업 - 선케어, 베이스메이크업
# 색조메이크업 - 립메이크업, 아이메이크업

skinclass_list = ['마스크팩', '클렌징', '기타', '스킨케어']
skinclass = '|'.join(skinclass_list)
cond_skinclass = hwahae_df['중분류1'].str.contains(skinclass)

baseclass_list = ['선케어', '베이스메이크업']
baseclass = '|'.join(baseclass_list)
cond_baseclass = hwahae_df['중분류1'].str.contains(baseclass)

colorclass_list = ['아이메이크업', '립메이크업']
colorclass = '|'.join(colorclass_list)
cond_colorclass = hwahae_df['중분류1'].str.contains(colorclass)

for i in range(len(hwahae_df)):
  if cond_skinclass[i] == True:
    hwahae_df.loc[i, '대분류'] = '스킨케어'
  
  elif cond_baseclass[i] == True:
    hwahae_df.loc[i, '대분류'] = '베이스메이크업'

  elif cond_colorclass[i] == True:
    hwahae_df.loc[i, '대분류'] = '색조메이크업'


# In[46]:


# 대분류 고유값 확인 
print(hwahae_df['대분류'].unique())
print(hwahae_df['대분류'].nunique())
hwahae_df.loc[:, ['대분류', '중분류', '소분류', '중분류1', '중분류2']]


# ### 립메이크업 중분류 세분화

# In[47]:


# musinsa_df
hwahae_df.head()


# In[48]:


# 중분류2 복제
hwahae_df['중분류3'] = hwahae_df['중분류2']
hwahae_df['중분류3'].head()


# In[49]:


# '중분류2 = 립메이크업 제품' 소분류 카테고리 고유값 확인
cond = hwahae_df['중분류2'] == '립메이크업'
hwahae_df.loc[cond, '중분류'].unique()


# In[50]:


# 립메이크업- 립글로스/립밤/립스틱/립라이너/립틴트 

lipbalm_list = ['립밤']
lipbalm = '|'.join(lipbalm_list)
cond_lipbalm = hwahae_df['중분류'].str.contains(lipbalm)

for i in range(len(hwahae_df)):
  if cond_lipbalm[i] == True:
   hwahae_df.loc[i, '중분류3'] = '립밤'
  
  else:
    if hwahae_df['중분류'][i] == '립글로스':
      hwahae_df.loc[i, '중분류3'] = '립글로스'
      
    elif hwahae_df['중분류'][i] == '립스틱':
      hwahae_df.loc[i, '중분류3'] = '립스틱'
      
    elif hwahae_df['중분류'][i] == '립라이너':
      hwahae_df.loc[i, '중분류3'] = '립라이너'

    elif hwahae_df['중분류'][i] == '립틴트':
      hwahae_df.loc[i, '중분류3'] = '립틴트'


# 중분류3 입력값 확인
cond = hwahae_df['중분류2'] == '립메이크업'
print(hwahae_df.loc[cond, '중분류3'].unique())
print(hwahae_df.loc[cond, '중분류3'].nunique())
hwahae_df.loc[cond, ['중분류', '중분류3']].head()


# ### 데이터셋 정리

# In[51]:


# 기존 카테고리 지우기
hwahae_df.drop(columns={'중분류', '소분류'}, axis=1, inplace=True)
hwahae_df.info()


# In[52]:


# 컬럼 순서 변경 : '플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류1', '중분류2', '중분류3', '평점', '후기 수', '정가', '할인가'
a = ['중분류1', '중분류2', '중분류3']

before_a = hwahae_df.drop(columns = {'중분류1', '중분류2', '중분류3'}).columns[:5].to_list()
after_a = hwahae_df.drop(columns = {'중분류1', '중분류2', '중분류3'}).columns[5:].to_list()

reorder = before_a + a + after_a
hwahae_df = hwahae_df[reorder]

hwahae_df.columns


# In[53]:


# 최종 데이터셋 확인
print(hwahae_df.info())
hwahae_df.head()


# In[ ]:


# 최종 데이터셋 저장
# hwahae_df.to_csv('hwahae_preprocessing.csv', index=False, encoding="utf-8-sig")


# ## 올리브영 : oliveyoung_df

# In[55]:


# 데이터셋 복제
oliveyoung_df = olive_df.copy(deep=True)


# In[56]:


# 데이터셋 기본 정보 조회
print(oliveyoung_df.info())
print(oliveyoung_df.head(3))


# ### 기본 전처리

# In[57]:


# 1. 컬럼 타입 변경 : 평점(float), 후기 수(int), 가격(int)
# 1) 후기 수 & 가격 컬럼의 쉼표 없애기
# 원본 데이터셋에 전처리 되어있음

'''
for i in range(len(oliveyoung_df)):
  score = oliveyoung_df['평점'][i]
  review = oliveyoung_df['후기 수'][i]
  price = oliveyoung_df['가격'][i]
  
  score_result = score.replace('별점 없음', '0')
  review_result = review.replace(',', '')
  price_result = price.replace(',', '')
  
  oliveyoung_df.loc[i, '평점'] = score_result
  oliveyoung_df.loc[i, '후기 수'] = review_result
  oliveyoung_df.loc[i, '가격'] = price_result

print(oliveyoung_df.loc[:10, ['평점', '후기 수', '가격']])
'''


# In[58]:


# 1. 컬럼 타입 변경 : 평점(float), 후기 수(int), 가격(int)
# 2) 컬럼 타입 변경
# 원본 데이터셋에 전처리 되어있음 

'''
oliveyoung_df[['평점', '후기 수', '가격']] = oliveyoung_df[['평점', '후기 수', '가격']].apply(pd.to_numeric)

print(oliveyoung_df[['평점', '후기 수', '가격']].dtypes)
print(oliveyoung_df.loc[:5, ['평점', '후기 수', '가격']])
'''


# In[59]:


# 2. 컬럼 이름 변경

oliveyoung_df.rename(columns = {'정가':'가격'}, inplace=True)
oliveyoung_df.columns


# In[60]:


# 3. 플랫폼 컬럼 추가 및 순서 변경
# 원본 데이터셋에 전처리 되어있음

'''
oliveyoung_df['플랫폼'] = '올리브영'

a = oliveyoung_df.columns[-1:].to_list()

ex_a = oliveyoung_df.drop(columns = oliveyoung_df.columns[[-1]]).columns[:].to_list()

reorder = a + ex_a
oliveyoung_df = oliveyoung_df[reorder]

oliveyoung_df.columns
'''


# ### 카테고리 전처리

# In[61]:


# 1. 중분류1 & 중분류2 컬럼 생성
oliveyoung_df['중분류1'] = ''
print(oliveyoung_df['중분류1'].head())

oliveyoung_df['중분류2'] = ''
print(oliveyoung_df['중분류2'].head())


# In[62]:


# 기존 분류별 unique 값 확인
print(oliveyoung_df['대분류'].unique())
print(oliveyoung_df['중분류'].unique())
print(oliveyoung_df['소분류'].unique())


# In[63]:


# 기타 컬럼 소속 예정 값의 대분류 값 확인
cond1 = oliveyoung_df['중분류'] == '미스트/오일'
print(oliveyoung_df.loc[cond1, '대분류'].unique()) # 스킨케어

cond2 = oliveyoung_df['중분류'] == '스킨케어세트'
print(oliveyoung_df.loc[cond2, '대분류'].unique()) # 스킨케어

cond2 = oliveyoung_df['중분류'] == '패드'
print(oliveyoung_df.loc[cond2, '대분류'].unique()) # 마스크팩


# In[64]:


# 패드 상품명 구체적으로 확인 : 토너 패드로 간주하고 대분류 자체를 스킨케어로 변경

cond = oliveyoung_df['중분류'] == '패드'
oliveyoung_df.loc[cond, ['대분류', '제품명']]


# In[65]:


# 올인원 중분류 카테고리 확인 
cond = oliveyoung_df['소분류'] == '올인원' 
oliveyoung_df.loc[cond, '중분류'].unique() # 로션 or 기타 -> 세분카테고리 추가 의논 필요


# In[66]:


# 통합 필요한 세부 카테고리 확인
cond1 = oliveyoung_df['대분류'] == '스킨케어'
print(oliveyoung_df.loc[cond1, '중분류'].unique())

cond2 = oliveyoung_df['중분류'] == '베이스메이크업'
print(oliveyoung_df.loc[cond2, '소분류'].unique())

cond3 = oliveyoung_df['중분류'] == '아이메이크업'
print(oliveyoung_df.loc[cond3, '소분류'].unique())

cond4 = oliveyoung_df['대분류'] == '마스크팩'
print(oliveyoung_df.loc[cond4, '중분류'].unique())


# In[67]:


# 중분류2
# 스킨케어 - 마스크팩, 클렌징, 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림, 기타
# 베이스메이크업 - 선케어, 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 색조메이크업 - 립메이크업, 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제

skin_list = ['스킨', '토너']
skin = '|'.join(skin_list)
cond_skin = oliveyoung_df['중분류'].str.contains(skin)

found_list = ['파운데이션', '쿠션', 'BB', 'CC']
found  = '|'.join(found_list)
cond_found = oliveyoung_df['소분류'].str.contains(found)

fixer_list = ['파우더', '팩트', '픽서']
fixer = '|'.join(fixer_list)
cond_fixer = oliveyoung_df['소분류'].str.contains(fixer)

shading_list = ['블러셔', '쉐이딩', '셰이딩', '하이라이터']
shading = '|'.join(shading_list)
cond_shading = oliveyoung_df['소분류'].str.contains(shading)

primer_list = ['프라이머', '베이스', '톤업크림'] # 프라이머/베이스 컬럼에 (소분류)톤업크림 추가
primer = '|'.join(primer_list)
cond_primer = oliveyoung_df['소분류'].str.contains(primer)

for i in range(len(oliveyoung_df)):

  if oliveyoung_df['중분류'][i] == '패드': # 패드를 검색 단어에 포함시키면 '(소분류)클렌징/패드'도 스킨케어에 포함될 수 있음
    oliveyoung_df.loc[i, '중분류2'] = '토너/토너패드/스킨' 
  
  elif oliveyoung_df['중분류'][i] == '로션':
    oliveyoung_df.loc[i, '중분류2'] = '로션'

  elif oliveyoung_df['중분류'][i] == '에센스/세럼/앰플':
    oliveyoung_df.loc[i, '중분류2'] = '에센스/세럼/앰플'
  
  elif oliveyoung_df['중분류'][i] == '미스트/오일':
    oliveyoung_df.loc[i, '중분류2'] = '기타'
  
  elif oliveyoung_df['중분류'][i] == '크림':
    oliveyoung_df.loc[i, '중분류2'] = '크림'

  elif oliveyoung_df['대분류'][i] == '마스크팩':
    oliveyoung_df.loc[i, '중분류2'] = '마스크팩'

  elif oliveyoung_df['대분류'][i] == '클렌징':
    oliveyoung_df.loc[i, '중분류2'] = '클렌징'

  elif oliveyoung_df['대분류'][i] == '선케어':
    oliveyoung_df.loc[i, '중분류2'] = '선케어'

  elif oliveyoung_df['중분류'][i] == '립메이크업':
    oliveyoung_df.loc[i, '중분류2'] = '립메이크업'
  
  elif oliveyoung_df['소분류'][i] == '컨실러':
    oliveyoung_df.loc[i, '중분류2'] = '컨실러'
    
  elif oliveyoung_df['소분류'][i] == '아이라이너':
    oliveyoung_df.loc[i, '중분류2'] = '아이라이너'

  elif oliveyoung_df['소분류'][i] == '아이섀도우':
    oliveyoung_df.loc[i, '중분류2'] = '아이섀도우'
    
  elif oliveyoung_df['소분류'][i] == '아이브로우':
    oliveyoung_df.loc[i, '중분류2'] = '아이브로우'

  elif oliveyoung_df['소분류'][i] == '마스카라':
    oliveyoung_df.loc[i, '중분류2'] = '마스카라'
  
  elif oliveyoung_df['소분류'][i] == '속눈썹영양제':
    oliveyoung_df.loc[i, '중분류2'] = '속눈썹영양제'
    
  elif cond_skin[i] == True:
    oliveyoung_df.loc[i, '중분류2'] = '토너/토너패드/스킨'
  
  elif cond_found[i] == True:
    oliveyoung_df.loc[i, '중분류2'] = '파운데이션/쿠션/BB/CC'

  elif cond_fixer[i] == True:
    oliveyoung_df.loc[i, '중분류2'] = '파우더/팩트/픽서'
  
  elif cond_shading[i] == True:
    oliveyoung_df.loc[i, '중분류2'] = '블러셔/쉐이딩/하이라이터'

  elif cond_primer[i] == True:
    oliveyoung_df.loc[i, '중분류2'] = '프라이머/베이스'
      
  else: # 기획세트
    oliveyoung_df.loc[i, '중분류2'] = '기타'


# In[68]:


print(oliveyoung_df['중분류2'].unique())
print(oliveyoung_df['중분류2'].nunique())
oliveyoung_df.loc[:, ['대분류', '중분류', '소분류', '중분류2']]


# In[69]:


# 중분류1 - 중분류2
# 스킨케어 - 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림
# 베이스메이크업 - 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 아이메이크업 - 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제
# 클렌징 / # 마스크팩 / # 기타 / # 선케어 / # 립메이크업

skincare_list = ['토너/토너패드/스킨', '에센스/세럼/앰플', '로션', '크림']
skincare = '|'.join(skincare_list)
cond_skincare = oliveyoung_df['중분류2'].str.contains(skincare)

base_list = ['파운데이션/쿠션/BB/CC', '파우더/팩트/픽서', '블러셔/쉐이딩/하이라이터', '프라이머/베이스', '컨실러']
base = '|'.join(base_list)
cond_base = oliveyoung_df['중분류2'].str.contains(base)

eye_list = ['아이섀도우', '아이라이너', '아이브로우', '마스카라', '속눈썹영양제']
eye = '|'.join(eye_list)
cond_eye = oliveyoung_df['중분류2'].str.contains(eye)

for i in range(len(oliveyoung_df)):
  if cond_skincare[i] == True:
    oliveyoung_df.loc[i, '중분류1'] = '스킨케어'
  
  elif cond_base[i] == True:
    oliveyoung_df.loc[i, '중분류1'] = '베이스메이크업'

  elif cond_eye[i] == True:
    oliveyoung_df.loc[i, '중분류1'] = '아이메이크업'
      
  else:
    if oliveyoung_df['중분류2'][i] == '클렌징':
      oliveyoung_df.loc[i, '중분류1'] = '클렌징'

    elif oliveyoung_df['중분류2'][i] == '마스크팩':
      oliveyoung_df.loc[i, '중분류1'] = '마스크팩'
      
    elif oliveyoung_df['중분류2'][i] == '기타':
      oliveyoung_df.loc[i, '중분류1'] = '기타'
      
    elif oliveyoung_df['중분류2'][i] == '선케어':
      oliveyoung_df.loc[i, '중분류1'] = '선케어'
    
    elif oliveyoung_df['중분류2'][i] == '립메이크업':
      oliveyoung_df.loc[i, '중분류1'] = '립메이크업'


# In[70]:


print(oliveyoung_df['중분류1'].unique())
print(oliveyoung_df['중분류1'].nunique())
oliveyoung_df.loc[:, ['대분류', '중분류', '소분류', '중분류1', '중분류2']]


# In[71]:


# 대분류 - 중분류1
# 스킨케어 - 마스크팩, 클렌징, 기타, 스킨케어
# 베이스메이크업 - 선케어, 베이스메이크업
# 색조메이크업 - 립메이크업, 아이메이크업

skinclass_list = ['마스크팩', '클렌징', '기타', '스킨케어']
skinclass = '|'.join(skinclass_list)
cond_skinclass = oliveyoung_df['중분류1'].str.contains(skinclass)

baseclass_list = ['선케어', '베이스메이크업']
baseclass = '|'.join(baseclass_list)
cond_baseclass = oliveyoung_df['중분류1'].str.contains(baseclass)

colorclass_list = ['아이메이크업', '립메이크업']
colorclass = '|'.join(colorclass_list)
cond_colorclass = oliveyoung_df['중분류1'].str.contains(colorclass)

for i in range(len(oliveyoung_df)):
  if cond_skinclass[i] == True:
    oliveyoung_df.loc[i, '대분류'] = '스킨케어'
  
  elif cond_baseclass[i] == True:
    oliveyoung_df.loc[i, '대분류'] = '베이스메이크업'

  elif cond_colorclass[i] == True:
    oliveyoung_df.loc[i, '대분류'] = '색조메이크업'


# In[72]:


# 대분류 고유값 확인 
print(oliveyoung_df['대분류'].unique())
print(oliveyoung_df['대분류'].nunique())
oliveyoung_df.loc[:, ['대분류', '중분류', '소분류', '중분류1', '중분류2']]


# In[73]:


# '(중분류)패드'의 분류값 확인
cond = oliveyoung_df['중분류'] == '패드'
oliveyoung_df.loc[cond, ['대분류', '중분류1', '중분류2']]


# ### 립메이크업 중분류 세분화

# In[74]:


# musinsa_df
oliveyoung_df.head()


# In[75]:


# 중분류2 복제
oliveyoung_df['중분류3'] = oliveyoung_df['중분류2']
oliveyoung_df['중분류3'].head()


# In[76]:


# '중분류2 = 립메이크업 제품' 소분류 카테고리 고유값 확인
cond = oliveyoung_df['중분류2'] == '립메이크업'
oliveyoung_df.loc[cond, '소분류'].unique()


# In[77]:


# 립메이크업- 립글로스/립밤/립스틱/립라이너/립틴트 

for i in range(len(oliveyoung_df)):
  if oliveyoung_df['소분류'][i] == '립글로스':
    oliveyoung_df.loc[i, '중분류3'] = '립글로스'

  elif oliveyoung_df['소분류'][i] == '립밤':
    oliveyoung_df.loc[i, '중분류3'] = '립밤'
    
  elif oliveyoung_df['소분류'][i] == '립스틱':
    oliveyoung_df.loc[i, '중분류3'] = '립스틱'
    
  elif oliveyoung_df['소분류'][i] == '립라이너':
    oliveyoung_df.loc[i, '중분류3'] = '립라이너'

  elif oliveyoung_df['소분류'][i] == '립틴트':
    oliveyoung_df.loc[i, '중분류3'] = '립틴트'


# 중분류3 입력값 확인
cond = oliveyoung_df['중분류2'] == '립메이크업'
print(oliveyoung_df.loc[cond, '중분류3'].unique())
print(oliveyoung_df.loc[cond, '중분류3'].nunique())
oliveyoung_df.loc[cond, ['소분류', '중분류3']].head()


# ### 데이터셋 정리

# In[78]:


# 기존 카테고리 지우기
oliveyoung_df.drop(columns={'중분류', '소분류'}, axis=1, inplace=True)
oliveyoung_df.info()


# In[79]:


# 컬럼 순서 변경 : '플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류1', '중분류2', '중분류3', '평점', '후기 수', '정가', '할인가'
a = ['중분류1', '중분류2', '중분류3']

before_a = oliveyoung_df.drop(columns = {'중분류1', '중분류2', '중분류3'}).columns[:5].to_list()
after_a = oliveyoung_df.drop(columns = {'중분류1', '중분류2', '중분류3'}).columns[5:].to_list()

reorder = before_a + a + after_a
oliveyoung_df = oliveyoung_df[reorder]

oliveyoung_df.columns


# In[80]:


# 최종 데이터셋 확인
print(oliveyoung_df.info())
oliveyoung_df.head()


# In[ ]:


# 최종 데이터셋 저장
# oliveyoung_df.to_csv('oliveyoung_preprocessing.csv', index=False, encoding="utf-8-sig")


# ## 한국 플랫폼 통합 : korea_all

# ### 데이터 통합

# In[121]:


# 플랫폼 데이터셋별 컬럼 정보 확인
print(musinsa_df.info()) # 12개 컬럼 - 할인가 X, URL O
print(hwahae_df.info()) # 12개 컬럼 - 할인가 X, URL O
print(oliveyoung_df.info()) # 12개 컬럼 - 할인가 O, URL X


# In[122]:


# 컬럼 맞추기
musinsa_df2 = musinsa_df.drop(columns={'URL'})
print(musinsa_df2.info())

hwahae_df2 = hwahae_df.drop(columns={'URL'})
print(hwahae_df2.info())

oliveyoung_df2 = oliveyoung_df.drop(columns={'할인가'})
print(oliveyoung_df2.info())


# In[123]:


korea_all = pd.concat([musinsa_df2, hwahae_df2, oliveyoung_df2], axis=0, ignore_index=True)
print(korea_all.info())
korea_all.head()


# In[124]:


# 통합 파일 저장
# korea_all.to_csv('korea_all_preprocessing.csv', index=False, encoding="utf-8-sig")


# In[125]:


# korea_check = pd.read_csv('korea_all_preprocessing.csv')
# korea_check.info()


# ### 통합 데이터 전처리

# In[126]:


# 1. 해외 브랜드 및 바디&헤어케어 브랜드 삭제
# 삭제할 브랜드명 리스트 
not_korean = ['에센허브', '다슈', '바이오더마', '오프라 코스메틱', '비오레', '키스미', '라로슈포제', '피지오겔', '비오템', '비오텀', '라씨엘르', '베네피트', '센카', '아크네스', '에스티로더', '유세린', '폰즈', '블리스텍스', '테', '아넷사', '스틸라', '그라펜', '무신사', '시코르', '뉴트로지나', '시슬리', '아벤느', '디올', '크리니크', '이솝', '샤넬', '바비브라운', '록시땅', '꼬달리', '프레쉬', '라로제', '폴메디슨', '올리세', '유리아쥬', '히루스카', '나스', '발레아', '큐어시스', '맥', '슈에무라', '비오투름', '에스테덤', '산수시', '노레바', '러쉬', '소티스', '이브롬', '마리꼬', '스킨레지민', '도브', '씨드비', '랑팔라투르', '달란디올리브', '바이오티크', '다이알', '쌍빠', '라부르켓', '블리스텍스', '후로후시', '딸리까', '제이숲', '에스까다코스메틱', '바이브랩', '케이트', '레브론', '존슨즈베이비', '샬롯틸버리', '토브', '샤넬', '클라랑스', '메이크업포에버', '지방시', '샹테카이', '로라메르시에', '입생로랑', '로레알', '아르마니', '메이블린', '안나수이', '투페이스드', '어반디케이']
nk = '|'.join(not_korean)

# 리스트 중 하나라도 포함되면 전체 삭제 
cond_nk = korea_all['브랜드'].str.contains(nk)
nk_idx = korea_all[cond_nk == True].index

korea_all.drop(nk_idx, inplace=True)

# 인덱스 재정렬
korea_all.reset_index(drop=True, inplace=True)
korea_all.info()


# In[127]:


# 2. 순위 재정립
korea_all['new_rank'] = korea_all.groupby(['플랫폼', '중분류1'])['중분류_순위'].rank(method='first', ascending=True).astype(int)


# In[128]:


korea_all.sort_values(['플랫폼', '대분류', '중분류1', '중분류_순위'], inplace=True)
korea_all.head()


# In[129]:


korea_all.reset_index(drop=True, inplace=True)
korea_all.head()


# In[130]:


# 3. 인덱스 정렬 및 컬럼 정리
# 인덱스 정렬
# korea_all.reset_index(drop=True, inplace=True)

# 기존 '중분류_순위' 값을 'new_rank' 값으로 바꾸기
korea_all['중분류_순위'] = korea_all['new_rank']

# 'new_rank' 지우기
korea_all.drop(columns = {'new_rank'}, axis=1, inplace=True)

print(korea_all.info())


# In[ ]:


# 원본 데이터 저장
# korea_all.to_csv('korea_new_rank.csv', index=False, encoding="utf-8-sig")


# ## 코스메 : cosme_df

# ### 일본어 번역

# In[ ]:


# 데이터 로드

cosme_df = df_detail.copy(deep=True)

# 번역할 열 리스트
columns_to_translate = ["브랜드", "제품명", "카테고리", "리뷰수"]

# 번역 함수
def translate_text(text):
    if pd.isna(text):
        return text
    return GoogleTranslator(source="ja", target="en").translate(text)

# 데이터프레임 변환
for col in columns_to_translate:
    cosme_df[col + "_EN"] = cosme_df[col].apply(translate_text)

# 저장
# cosme_df.to_csv("df_cosme_translated.csv", index=False)


# In[83]:


# 데이터셋 기본 정보 조회
print(cosme_df.info())
print(cosme_df.head(3))


# ### 기본 전처리

# In[84]:


# 전처리 필요한 컬럼 서식 확인
cosme_df[['평점','리뷰수_EN','가격']]


# In[85]:


# 전처리 필요한 컬럼 서식 확인

max_len = cosme_df['리뷰수_EN'].str.len().max()

cosme_df[cosme_df['리뷰수_EN'].str.len()==max_len]


# In[86]:


# 1. 컬럼 타입 변경 : 리뷰수_EN(int)
# 1) 리뷰수_EN 컬럼의 ' reviews', ',', '??' 삭제

for i in range(len(cosme_df)):
  review = cosme_df['리뷰수_EN'][i]

  review_result = review.replace('reviews', '')
  review_result = review_result.replace(',', '')
  review_result = review_result.replace(' ', '')
  review_result = review_result.replace('??', '')
  
  cosme_df.loc[i, '리뷰수_EN'] = review_result

print(cosme_df.loc[:10, '리뷰수_EN'])


# In[87]:


# 1. 컬럼 타입 변경 : 리뷰수_EN(int)
# 2) 컬럼 타입 변경

cosme_df['리뷰수_EN'] = cosme_df['리뷰수_EN'].apply(pd.to_numeric)

print(cosme_df['리뷰수_EN'].dtypes)
print(cosme_df.loc[:5, '리뷰수_EN'])


# In[88]:


# 2. 컬럼 이름 변경

cosme_df.columns = ['순위', '제품ID', '브랜드', '제품명', '소분류', '평점', '후기 수', '가격']
cosme_df.columns


# In[89]:


# 3. 플랫폼 컬럼 추가 및 순서 변경
# 원본 데이터셋에 전처리 되어있음

cosme_df['플랫폼'] = '코스메' 

a = cosme_df.columns[-1:].to_list()

ex_a = cosme_df.drop(columns = cosme_df.columns[[-1]]).columns[:].to_list()

reorder = a + ex_a
cosme_df = cosme_df[reorder]

cosme_df.columns


# - 삭제할 소분류 검색값: 'pouch', 'brush', 'body', 'Body', 'hair', 'Hair', 'Shampoo', 'perfume', 'Hand', 'hand', 'bath', 'Other skin care products', 'nail', 'Nail', 'Health', 'food', 'drink', 'supplement', 'Other eyeliner', 'Shaving remover', 'Other makeup products', 'Manicure', 'Appliance', 'Leg', 'Foot', 'Travel', 'Other kit', 'Puff', 'cotton', 'Medical', 'Scalp', 'others'
# - 삭제할 브랜드 : 'Mijangsen'(헤어케어브랜드), 'Stilla'(한국 브랜드 아님), 'Soon Plus'(단백질파우더 팔고 있음)

# In[90]:


# 4. 불필요한 행 삭제하기
# 1) 소분류 값 검색

word_list = ['pouch', 'brush', 'body', 'Body', 'hair', 'Hair', 'Shampoo', 'shampoo', 'perfume', 'Perfumes', 'Hand', 'hand', 'bath', 'Other skin care products', 'nail', 'Nail', 'Health', 'food', 'Food', 'drink', 'Drink', 'supplement', 'Other eyeliner', 'Shaving remover', 'Other makeup products', 'Manicure', 'Appliance', 'Leg', 'Foot', 'Travel', 'Other kit', 'Puff', 'cotton', 'Medical', 'Scalp', 'others', 'Blotting']
word = '|'.join(word_list)

word_idx = cosme_df[cosme_df['소분류'].str.contains(word)].index

cosme_df = cosme_df.drop(word_idx)
cosme_df.info() # 전체행 3000개 -> 2671개로 감소


# In[91]:


# 4. 불필요한 행 삭제하기
# 2) 불필요한 브랜드 삭제

brand_list = ['Mijangsen', 'Stilla', 'Soon Plus']
brand = '|'.join(brand_list)

brand_idx = cosme_df[cosme_df['브랜드'].str.contains(brand)].index

cosme_df = cosme_df.drop(brand_idx)
cosme_df.info() # 전체행 2673개 -> 2581개로 감소


# In[92]:


# 4. 불필요한 행 삭제하기
# 3) 인덱스 리셋

cosme_df.reset_index(drop=True, inplace=True)
cosme_df.head()


# In[93]:


# 브랜드 이름 한국과 통일
# 정샘물 -> 정샘물뷰티
# 비비아 -> 삐아
# CNP -> 차앤박
# 리더스 코스메틱 -> 리더스코스메틱

cosme_df['브랜드'].replace({
                          '정샘물':'정샘물뷰티',
                          '비비아':'삐아',
                          'CNP':'차앤박',
                          '리더스 코스메틱':'리더스코스메틱'})

cond = cosme_df['브랜드']=='차앤박'
print(cosme_df.loc[cond, '브랜드'])


# ### 대분류 및 중분류 통합

# In[94]:


# 1. 중분류1 & 중분류3 컬럼 생성
cosme_df['중분류1'] = ''
print(cosme_df['중분류1'].head())

cosme_df['중분류3'] = ''
print(cosme_df['중분류3'].head())


# In[95]:


# 기존 분류 unique 값 확인
print(cosme_df['소분류'].unique()) # -> 제품명에 포함된 이름으로 찾기


# 스킨케어 - 마스크팩, 클렌징, 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림, 기타
# 1) 마스크팩: (소)'Sheet mask pack'
# 2) 클렌징: (소)'wash', (소)'Peeling', (소)'clean', (소)'Clean', (소)'Remover'
# 
# 3) 토너/토너패드/스킨
#     - (소)'Lotion' => 이름에 'toner', 'Toner', 'pad', 'Pad','water', 'Water', 'skin', 'Skin', 'Shigeakisui'(설화수 제품명), 'mask', 'Mask' 들어가는 경우
# 
# 4) 에센스/세럼/앰플: (소)'Booster', (소)'Beauty fluid'
#     - (소)'Lotion' => 이름에 'essence', 'Essence', 'Essener', 'serum', 'Serum', 'booster' 들어가는 경우
# 
# 5) 로션: (소)'Milk'
#     - (소)'Lotion' => 이름에 'lotion', 'Lotion' 들어가는 경우 & 1)~4)에서 필터링하고 남은 나머지 상품들들
# 
# 6) 크림
#     - (소)'Face cream' => 'BB' 제외 나머지 제품
# 
# 7) 기타: (소)'mist', (소)'Oil Balm', (소)'Skincare kit', (소)'Other skin care', (소)'Eye Cream', (소)'All', (소)'Skincare kit'

# 베이스메이크업 - 선케어, 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 1) 선케어: (소)'Sunscreen'
# 
# 2) 파운데이션/쿠션/BB/CC: (소)'foundation'
#     - (소)'Face cream' => 이름에 'BB' 들어갈 경우
# 
# 3) 파우더/팩트/픽서:
#     - (소)'Cream and gel foundation'=> 이름에 'pact' 들어가는 경우 / 이외 모두 파운데이션으로 분류
#     - (소) 'Presto powder' => 이름에 'powder', 'Powder', 'finsh', 'Finish', 'pact', 'Pact' 들어가는 경우
#     - (소)'Loose'
# 
# 4) 블러셔/쉐이딩/하이라이터: (소)'blush', (소)'Cheek'
#     - (소) 'Presto powder' => 이름에 'shading' 'Shading', 'highlighter', 'Highlighter', 'blusher', 'Blusher', 'brusher', 'Brusher', 'contoure', 'Contoure' 들어가는 경우
# 
# 5) 프라이머/베이스: (소)'Makeup base'
# 
# 6) 컨실러: (소)'Concealer'

# 색조메이크업 - 립메이크업, 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제
# 1) 립메이크업
#     - 립글로스: (소)'Lip gloss'
#     - 립밤: (소)'lip balm'
#     - 립스틱: (소)'lipstick'
#     - 립라이너: (소)'Lip liner'
#     - 립틴트: 립글로스, 립스틱 중에서 이름에 'tint' 포함된 경우
# 
# 2) 아이섀도우: (소)'eyeshadow', (소)'Palettes'
# 
# 3) 아이라이너: (소)'eyeliner'
# 
# 4) 아이브로우: (소)'eyebrow', (소)'Eyebrow', (소)'Brow mascara'
# 
# 5) 마스카라: (소)'mascara', (소)'Mascara'
# 
# 6) 속눈썹 영양제: (소)'Eyelash'

# In[96]:


# 중분류3

clean_list = ['wash', 'Peeling', 'Wash', 'clean', 'Clean', 'Remover']
cleansing = '|'.join(clean_list)
cond_clean = cosme_df['소분류'].str.contains(cleansing)

toner_list = ['toner', 'Toner', 'pad', 'Pad','water', 'Water', 'skin', 'Skin', 'Shigeakisui', 'mask', 'Mask']
toner = '|'.join(toner_list)
cond_toner = cosme_df['제품명'].str.contains(toner)

serum_list = ['essence', 'Essence', 'Essener', 'serum', 'Serum', 'booster', 'Booster', 'Beauty fluid']
serum = '|'.join(serum_list)
cond_serum = cosme_df['제품명'].str.contains(serum)
cond_serum2 = cosme_df['소분류'].str.contains(serum)

extra_list = ['mist', 'Mist', 'Oil Balm', 'Skincare kit', 'Other skin care', 'Eye Cream', 'All', 'Skincare kit']
extra = '|'.join(extra_list)
cond_extra = cosme_df['소분류'].str.contains(extra)
#---------------------------------------------------------#
cond_bb = cosme_df['제품명'].str.contains('BB')

powder_list = ['powder', 'Powder', 'finsh', 'Finish', 'pact', 'Pact']
powder = '|'.join(powder_list)
cond_powder = cosme_df['제품명'].str.contains(powder)

shading_list = ['shading' 'Shading', 'highlighter', 'Highlighter', 'blusher', 'Blusher', 'brusher', 'Brusher', 'contoure', 'Contoure', 'face cube']
shading = '|'.join(shading_list)
cond_shading = cosme_df['제품명'].str.contains(shading)

blusher_list = ['blush', 'Cheek']
blusher = '|'.join(blusher_list)
cond_blusher = cosme_df['소분류'].str.contains(blusher)

cond_sun = cosme_df['소분류'].str.contains('Sunscreen')
cond_found = cosme_df['소분류'].str.contains('foundation')
cond_loose = cosme_df['소분류'].str.contains('Loose')
cond_base = cosme_df['소분류'].str.contains('Makeup base')
#---------------------------------------------------------#
cond_tint = cosme_df['제품명'].str.contains('tint')
cond_balm = cosme_df['소분류'].str.contains('lip balm')
cond_liner = cosme_df['소분류'].str.contains('Lip liner')
#---------------------------------------------------------#
shadow_list = ['eyeshadow', 'Palettes']
shadow = '|'.join(shadow_list)
cond_shadow = cosme_df['소분류'].str.contains(shadow)

brow_list = ['eyebrow', 'Eyebrow', 'Brow mascara']
brow= '|'.join(brow_list)
cond_brow = cosme_df['소분류'].str.contains(brow)

masc_list = ['mascara', 'Mascara']
masc= '|'.join(masc_list)
cond_masc = cosme_df['소분류'].str.contains(masc)

line_list = ['eyeliner', 'Eyeliner']
eyeline = '|'.join(line_list)
cond_eyeline = cosme_df['소분류'].str.contains(eyeline)

lash_list = ['eyelash', 'Eyelash']
eyelash = '|'.join(lash_list)
cond_eyelash = cosme_df['소분류'].str.contains(eyelash)
#---------------------------------------------------------#

for i in range(0, len(cosme_df)):
  if cosme_df['소분류'][i] == 'Lotion':
    if cond_toner[i] == True :
      cosme_df.loc[i, '중분류3'] = '토너/토너패드/스킨'
    elif cond_serum[i] == True:
      cosme_df.loc[i, '중분류3'] = '에센스/세럼/앰플'
    else:
      cosme_df.loc[i, '중분류3'] = '로션'
  
  elif cosme_df['소분류'][i] == 'Face cream':
    if cond_bb[i] == True:
      cosme_df.loc[i, '중분류3'] = '파운데이션/쿠션/BB/CC'
    else:
      cosme_df.loc[i, '중분류3'] = '크림'

  elif cosme_df['소분류'][i] == 'Cream and gel foundation':
    if cond_powder[i] == True:
      cosme_df.loc[i, '중분류3'] = '파우더/팩트/픽서'
    else:
      cosme_df.loc[i, '중분류3'] = '파운데이션/쿠션/BB/CC'
  
  elif cosme_df['소분류'][i] == 'Presto powder':
    if cond_shading[i] == True:
      cosme_df.loc[i, '중분류3'] = '블러셔/쉐이딩/하이라이터'
    else:
      cosme_df.loc[i, '중분류3'] = '파우더/팩트/픽서'      
  
  elif (cosme_df['소분류'][i]=='Lip gloss') | (cosme_df['소분류'][i]=='lipstick') :
    if cond_tint[i] == True:
      cosme_df.loc[i, '중분류3'] = '립틴트'
    elif cosme_df['소분류'][i] == 'Lip gloss':
      cosme_df.loc[i, '중분류3'] = '립글로스'      
    else:
      cosme_df.loc[i, '중분류3'] = '립스틱'
      
  else:

    if cond_clean[i] == True:
      cosme_df.loc[i, '중분류3'] = '클렌징'
    
    elif cosme_df['소분류'][i] == 'Sheet mask pack':
      cosme_df.loc[i, '중분류3'] = '마스크팩'

    elif cond_serum2[i] == True:
      cosme_df.loc[i, '중분류3'] = '에센스/세럼/앰플'
    
    elif cosme_df['소분류'][i] == 'Milk':
      cosme_df.loc[i, '중분류3'] = '로션'
  
    elif cond_extra[i] == True:
      cosme_df.loc[i, '중분류3'] = '기타'
#---------------------------------------------------------#
    elif cond_sun[i] == True:
      cosme_df.loc[i, '중분류3'] = '선케어'
#---------------------------------------------------------#    
    elif cond_found[i] == True:
      cosme_df.loc[i, '중분류3'] = '파운데이션/쿠션/BB/CC'

    elif cond_blusher[i] == True:
      cosme_df.loc[i, '중분류3'] = '블러셔/쉐이딩/하이라이터'
    
    elif cond_loose[i] == True:
      cosme_df.loc[i, '중분류3'] = '파우더/팩트/픽서'
    
    elif cond_base[i] == True:
      cosme_df.loc[i, '중분류3'] = '프라이머/베이스'
    
    elif cosme_df['소분류'][i] == 'Concealer':
      cosme_df.loc[i, '중분류3'] = '컨실러'
#---------------------------------------------------------#    
    elif cond_balm[i] == True:
      cosme_df.loc[i, '중분류3'] = '립밤'
      
    elif cond_liner[i] == True:
      cosme_df.loc[i, '중분류3'] = '립라이너'    
#---------------------------------------------------------#   
    elif cond_shadow[i] == True:
      cosme_df.loc[i, '중분류3'] = '아이섀도우'
      
    elif cond_eyeline[i] == True:
      cosme_df.loc[i, '중분류3'] = '아이라이너'  

    elif cond_brow[i] == True:
      cosme_df.loc[i, '중분류3'] = '아이브로우'  
    
    elif cond_masc[i] == True:
      cosme_df.loc[i, '중분류3'] = '마스카라'

    elif cond_eyelash[i] == True:
      cosme_df.loc[i, '중분류3'] = '속눈썹영양제'
    
    else:
      cosme_df.loc[i, '중분류3'] = '분류없음'


# In[97]:


# 고유값 수 확인 
print(cosme_df['중분류3'].unique())
print(cosme_df['중분류3'].nunique())
cosme_df.loc[:10, ['소분류', '중분류3']]


# In[98]:


# 중분류2 생성
cosme_df['중분류2'] = cosme_df['중분류3'].copy()
cosme_df['중분류2'].head(10)


# In[99]:


# 중분류2 수정
# 중분류3('립틴트', '립라이너', '립글로스', '립밤', '립스틱스틱') => 중분류2(립메이크업) 으로 일괄 변경 

lip_list = ['립틴트', '립라이너', '립글로스', '립밤', '립스틱']
lips = '|'.join(lip_list)
cond_lips = cosme_df['중분류3'].str.contains(lips)

for i in range(len(cosme_df)):
  if cond_lips[i] == True:
    cosme_df.loc[i, '중분류2'] = '립메이크업'


# In[100]:


print(cosme_df['중분류2'].unique())
print(cosme_df['중분류2'].nunique())
cosme_df.loc[:, ['소분류', '중분류2', '중분류3']]


# In[101]:


# 중분류1 - 중분류2
# 스킨케어 - 토너/토너패드/스킨, 에센스/세럼/앰플, 로션, 크림
# 베이스메이크업 - 파운데이션/쿠션/BB/CC, 파우더/팩트/픽서, 블러셔/쉐이딩/하이라이터, 프라이머/베이스, 컨실러
# 아이메이크업 - 아이섀도우, 아이라이너, 아이브로우, 마스카라, 속눈썹 영양제
# 클렌징 / # 마스크팩 / # 기타 / # 선케어 / # 립메이크업

skincare_list = ['토너/토너패드/스킨', '에센스/세럼/앰플', '로션', '크림']
skincare = '|'.join(skincare_list)
cond_skincare = cosme_df['중분류2'].str.contains(skincare)

base_list = ['파운데이션/쿠션/BB/CC', '파우더/팩트/픽서', '블러셔/쉐이딩/하이라이터', '프라이머/베이스', '컨실러']
base = '|'.join(base_list)
cond_base = cosme_df['중분류2'].str.contains(base)

eye_list = ['아이섀도우', '아이라이너', '아이브로우', '마스카라', '속눈썹영양제']
eye = '|'.join(eye_list)
cond_eye = cosme_df['중분류2'].str.contains(eye)

for i in range(len(cosme_df)):
  if cond_skincare[i] == True:
    cosme_df.loc[i, '중분류1'] = '스킨케어'
  
  elif cond_base[i] == True:
    cosme_df.loc[i, '중분류1'] = '베이스메이크업'

  elif cond_eye[i] == True:
    cosme_df.loc[i, '중분류1'] = '아이메이크업'
      
  else:
    if cosme_df['중분류2'][i] == '클렌징':
      cosme_df.loc[i, '중분류1'] = '클렌징'

    elif cosme_df['중분류2'][i] == '마스크팩':
      cosme_df.loc[i, '중분류1'] = '마스크팩'
      
    elif cosme_df['중분류2'][i] == '기타':
      cosme_df.loc[i, '중분류1'] = '기타'
      
    elif cosme_df['중분류2'][i] == '선케어':
      cosme_df.loc[i, '중분류1'] = '선케어'
    
    elif cosme_df['중분류2'][i] == '립메이크업':
      cosme_df.loc[i, '중분류1'] = '립메이크업'


# In[102]:


print(cosme_df['중분류1'].unique())
print(cosme_df['중분류1'].nunique())
cosme_df.loc[:, ['소분류', '중분류1', '중분류2', '중분류3']]


# In[103]:


# 대분류 - 중분류1
# 스킨케어 - 마스크팩, 클렌징, 기타, 스킨케어
# 베이스메이크업 - 선케어, 베이스메이크업
# 색조메이크업 - 립메이크업, 아이메이크업

skinclass_list = ['마스크팩', '클렌징', '기타', '스킨케어']
skinclass = '|'.join(skinclass_list)
cond_skinclass = cosme_df['중분류1'].str.contains(skinclass)

baseclass_list = ['선케어', '베이스메이크업']
baseclass = '|'.join(baseclass_list)
cond_baseclass = cosme_df['중분류1'].str.contains(baseclass)

colorclass_list = ['아이메이크업', '립메이크업']
colorclass = '|'.join(colorclass_list)
cond_colorclass = cosme_df['중분류1'].str.contains(colorclass)

for i in range(len(cosme_df)):
  if cond_skinclass[i] == True:
    cosme_df.loc[i, '대분류'] = '스킨케어'
  
  elif cond_baseclass[i] == True:
    cosme_df.loc[i, '대분류'] = '베이스메이크업'

  elif cond_colorclass[i] == True:
    cosme_df.loc[i, '대분류'] = '색조메이크업'


# In[104]:


# 대분류 고유값 확인 
print(cosme_df['대분류'].unique())
print(cosme_df['대분류'].nunique())
cosme_df.loc[:, ['대분류', '소분류', '중분류1', '중분류2', '중분류3']]


# ### 데이터셋 정리

# In[105]:


# 기존 카테고리 지우기
cosme_df.drop(columns={'제품ID', '소분류'}, axis=1, inplace=True)
cosme_df.info()


# In[106]:


# 컬럼 순서 변경 : '플랫폼', '브랜드', '제품명', '중분류_순위', '대분류', '중분류1', '중분류2', '중분류3', '평점', '후기 수', '정가', '할인가'
a = ['순위', '대분류', '중분류1', '중분류2', '중분류3']

before_a = cosme_df.drop(columns = {'순위', '대분류', '중분류1', '중분류2', '중분류3'}).columns[:3].to_list()
after_a = cosme_df.drop(columns = {'순위', '대분류', '중분류1', '중분류2', '중분류3'}).columns[3:].to_list()

reorder = before_a + a + after_a
cosme_df = cosme_df[reorder]

cosme_df.columns


# In[107]:


# 순위 재정립 : 인덱스 + 1

for i in range(0, len(cosme_df)):
  cosme_df['순위'][i] = i+1


# In[108]:


# 최종 데이터셋 확인
print(cosme_df.info())
cosme_df.head()


# In[ ]:


# 최종 데이터셋 저장
# cosme_df.to_csv('cosme_preprocessing.csv', index=False, encoding="utf-8-sig")


# # 3. 리뷰 데이터 크롤링 및 키워드 분석

# ## 무신사 리뷰 수집 및 키워드 분석

# ### 1) 무신사 리뷰 데이터 수집 : df_scrap

# In[ ]:


# 웹 드라이버 실행
driver = webdriver.Chrome()

# 무신사 리뷰 페이지 URL
url = "https://www.musinsa.com/review/goods/1897996"
driver.get(url)

# 1️⃣ **스크롤을 최상단으로 이동**
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(2)

# 2️⃣ **스크롤 내리면서 리뷰 즉시 수집**
reviews = []
scroll_pause_time = 0.1  # 페이지 로딩 대기 시간
current_height = 0
max_scroll_attempts = 300  # 최대 스크롤 횟수 (보완용)


for i in range(max_scroll_attempts):

    print(f"🔽 스크롤 {i+1} 번째 실행 중...")

    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")

    # 3️⃣ **"더보기" 버튼 클릭**
    more_buttons = driver.find_elements(By.CLASS_NAME, "TruncateContent__MoreButton-sc-5tx4vi-3")
    for button in more_buttons:
        try:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(0.1)  # 클릭 후 대기
        except:
            pass

    # 4️⃣ **현재 보이는 리뷰 수집**
    try:
        review_elements = driver.find_elements(By.CLASS_NAME, "TruncateContent__ContentContainer-sc-5tx4vi-1")
        for review in review_elements:
            try:
                text = review.text.strip()
                if text and text not in reviews:
                    reviews.append(text)
            except StaleElementReferenceException:
                print("⚠ StaleElementReferenceException 발생 - 요소가 갱신됨, 다시 시도")
                continue  # 다음 루프로 이동하여 다시 시도
    except Exception as e:
        print(f"❌ 리뷰 수집 중 오류 발생: {e}")

    print(f"✅ 현재까지 수집된 리뷰 개수: {len(reviews)}")

    # 더 이상 스크롤이 늘어나지 않으면 종료
    if new_height == current_height:
        break
    current_height = new_height

# 5️⃣ **스크롤 완료 후 마지막으로 "더보기" 버튼 클릭**
print("🔄 마지막 '더보기' 버튼 클릭 중...")
more_buttons = driver.find_elements(By.CLASS_NAME, "TruncateContent__MoreButton-sc-5tx4vi-3")
for button in more_buttons:
    try:
        driver.execute_script("arguments[0].click();", button)
        time.sleep(0.1)
    except:
        pass

# 6️⃣ **데이터 저장**
df_scrap = pd.DataFrame(reviews, columns=["Review"])
df_scrap.head(20)


# In[ ]:


# 리뷰 데이터 저장
# df_scrap.to_csv("review_scrapped_2.csv", index=False, encoding="utf-8-sig")


# ### 2) 형태소 분석

# In[ ]:


okt = Okt()
print(okt.morphs("한글 자연어 처리를 테스트합니다."))


# In[ ]:


# 1. 형태소 분석기 초기화
okt = Okt()

# 2. 변환할 단어 매핑
word_mapping = {
    "좋아요": "좋음", "좋은": "좋음",
    "좋습니다": "좋음","좋네요":"좋음","힐":"메디힐",
    "좋고": "좋음","좋아서":"좋음",
    "발":"발색", "오브":"오브제",
    "발림":"발림성","성도":"발림성",
    "마음":"마음에 들다","자연":"자연스러움","쿨":"쿨톤",
    "자연스럽고":"자연스러움","자연스러운":"자연스러움","광":"광택","밍":"네이밍",
    "색도":"색","색깔":"색","습":"보습",
    "색상":"색","맘":"마음에 들다","편해요":"편하다", "편하게":"편하다",
    "부담":"부담스럽지 않은","가성":"가성비","데카":"마데카소사이드","쟁여두":"쟁여두고 싶은",
    "적당히":"적당한","자연스러워서": "자연스러움","형":"제형",
    "적당하고":"적당한","쟁":"쟁여두고 싶은", "정력":"세정력","럼":"세럼","글":"글로스","팁":"브러쉬팁",
    "옷": "옷에 묻음", "잘나고" : "거품이 잘 나고", "자극":"저자극","토리":"토리든", "산성":"약산성", "끈":"끈적임","사은":"사은품" 
}

# 3. 제거할 단어 리스트
remove_words = {"거", "구매", "또","유","때", "제", "입니다", "후기", "달", "것","보기","과과","중","다른","같습니다","개","더","비",
                "개","있습니다","좀", "생각","있어서","수","조금","일리","데","이","안","일단","정말","아주","사서","제일","쓰기","과",
                 "있어요","진짜","하나","있는","원래","다음","처음", "티", "저", "벌써", "상품","구입","일","좋음","좋아요","좋고","좋아서",
                 "좋습니다", "좋네요", "좋은", "배송","같아요", "가격","성도","매번","한번","원","번","이번","요","좋","같아서","보고"
                 ,"같네요","매우","듯","로스", "제품","사","후","늘","품","편",
                 "년","걸","용","있는데","든","약","앞","감","날","은","전","위","마","장","사용"}  # 집합(set)으로 사용하면 탐색 속도 빠름

# 4. 단어 추출 및 변환
word_list = []
for review in df_scrap["Review"].dropna():
    for word, tag in okt.pos(review):
        if tag in ["Noun", "Adjective"]:  # 명사와 형용사만 추출
            if word in remove_words:  # 제거할 단어 필터링
                continue
            word = word_mapping.get(word, word)  # 단어 변환 (매핑 적용)
            word_list.append(word)

# 5. 단어 빈도수 계산
word_counts = Counter(word_list)
sorted_word_counts = word_counts.most_common()

# 6. 데이터프레임 변환
word_df = pd.DataFrame(sorted_word_counts, columns=["Word", "Frequency"])

# 7. 상위 50개 단어 출력
word_df.head(50)


# In[ ]:


# word_df.to_csv("오브제 톤업 로션 단어.csv", index=False, encoding="utf-8-sig")


# ## 올리브영 리뷰 수집 및 키워드 분석

# ### 1) 올리브영 리뷰 크롤링 제품 선택 : olive_top_class

# 1. 분류별 TOP5 상품 추출 -> new DF 생성
# 2. 상품별 리뷰 수집(크롤링) -> 페이지 수 적절히 조정해서 진행
# 3. 1 & 2 코드 통합 -> 1의 제품명이 2의 제품명에 포함되는지 여부를 기준으로 join
# 4. 리뷰 키워드 분석 진행 -> 분류 / 브랜드 / 키워드 / 키워드별 frequency - 총 5개 컬럼 생성

# In[144]:


# 올리브영 크롤링 데이터 최종 버전 불러오기
olive_top = korea_all[korea_all['플랫폼']=='올리브영'].copy(deep=True) 
olive_top.reset_index(drop=True, inplace=True) 

print(olive_top.info())
olive_top


# In[145]:


# 분류별 TOP10 상품 확인
# 1) 중분류1 고유값 확인
class_list = olive_top['중분류1'].unique()
class_list


# In[146]:


# 분류별 TOP10 상품 확인
# 2) 중분류1 단위별 top10 제품만 추출

top_list = []

for i in class_list:
  top_df = olive_top[olive_top['중분류1'] == i][:10]
  top_df.reset_index(drop=True, inplace=True)
  top_list.append(top_df)

olive_top_class = pd.concat(top_list)
print(olive_top_class['중분류1'].unique())
olive_top_class


# In[147]:


olive_top_class.head(20)


# In[148]:


# 분류별 TOP10 상품 확인
# 3) 인덱스 리셋

olive_top_class.reset_index(drop=False, inplace=True)
print(olive_top_class.info())
olive_top_class


# In[149]:


# 분류별 TOP5 상품 확인
# 3) 중분류 별 5개 제품 추출 확인을 위한 순위 재정립
# 중분류_순위 = index + 1

for i in range(0, len(olive_top_class)):
  olive_top_class['중분류_순위'][i] = olive_top_class['index'][i] + 1

olive_top_class.drop(columns = {'index'}, inplace=True)
olive_top_class = olive_top_class[olive_top_class['중분류_순위']<=5]

print(olive_top_class.info())
olive_top_class.head(10)


# ### 2) 올리브영 리뷰 크롤링 : olive_top_df

# In[ ]:


olive_top_class['제품명'].nunique()


# In[ ]:


# 브라우저 열기
driver = webdriver.Chrome()


# In[ ]:


# 1. 올리브영 페이지 로드
driver.get('https://www.oliveyoung.co.kr/store/main/main.do?oy=0&utm_source=google&utm_medium=powerlink&utm_campaign=onpro_emnet_default-main_25_0101_1231&utm_content=pc_main&utm_term=%EC%98%AC%EB%A6%AC%EB%B8%8C%EC%98%81&utm_id=141045234423&gad_source=1&gclid=CjwKCAiAn9a9BhBtEiwAbKg6foao24DhngYKkXfLJpmZNukZUpPCVhDLI-MupWtyrJ2qBM3UXS7AWhoCcmIQAvD_BwE')
time.sleep(3)  # 페이지 로드 대기


# In[ ]:


# 경고창이 있을 때 처리하는 함수
def handle_alert(driver):
    try:
        # 경고창이 나타날 때까지 기다림
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = Alert(driver)
        alert.accept()  # 'OK' 버튼 클릭
        print("경고창 처리 완료")
    except:
        print("경고창 없음")


# In[ ]:


# 리뷰 페이지 크롤링 함수

def oliveyoung_reviews(driver, idx, search_p):
  wait = WebDriverWait(driver, 3)

  data = []
  count = 0
  current_page = 0
  try:
    # 리뷰 페이지로 이동 (처음 한 번만)
    review_page = driver.find_element(By.XPATH, '//*[@id="reviewInfo"]/a')
    review_page.click()
    time.sleep(2)

    while count < 20:
    # -- 시작페이지 기준: count=0, current_page=0 으로 시작
    # -- 단락1 10페이지 기준: count=9, current_page=9 로 시작
    # -- 단락2 11페이지 기준: count=10, current_page=1 로 시작
    # -- 단락2 20페이지 기준: count=19, current_page=10 으로 시작

        # 리뷰 페이지 이동 및 추출
        contents = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="gdasList"]/li/div[2]/div[3]')))
        
        for content in contents:
          data.append(content.text)
        
        # 반복 횟수 확인
        count += 1 
        # -- 시작페이지 기준: count=1, current_page=0
        # -- 단락1 10페이지 기준: count=10, current_page=9
        # -- 단락2 11페이지 기준: count=11, current_page=1
        # -- 단락2 20페이지 기준: count=20, current_page=10
        
        if (count<10 and current_page<9) or (count>10 and current_page<10):
          # 다음 페이지로 넘어가기 
          next_page_no = current_page + 1
          try:
            next_page = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="gdasContentsArea"]/div/div[8]/a[{next_page_no}]')))
            
            next_page.click()  
            time.sleep(3)
            current_page += 1
            # -- 시작페이지 기준: count=1, current_page=1
            # -- 단락2 11페이지 기준: count=11, current_page=2
            
          except TimeoutException: 
            print(f"TimeoutException: {idx}: {search_p}의 {next_page_no} 페이지를 찾을 수 없음")
            break
        
        else: # 다음 단락으로 넘어가기
          
          try:
            next_context = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="gdasContentsArea"]/div/div[8]/a[10]')))
            
            if count==10 and current_page==9 : # current_page=9(단락1의 10페이지일 경우)
              current_page = current_page-8
              # -- 단락1 10페이지 기준: count=10, current_page=1
              
            elif count>=10 and current_page==10 : # count >= 10 & current_page >= 10 일 경우
              current_page = current_page-9
              # -- 단락2 20페이지 기준: count=20, current_page=1
            
            next_context.click()
            time.sleep(3)
          
          except TimeoutException: 
            print(f"TimeoutException: {idx}: {search_p}의 {next_page_no} 페이지를 찾을 수 없음")
            break
        
  except Exception as e:
      print(f"{idx}: {search_p} 리뷰 수집 중 오류 발생 - {e}")

  print(f'총 {len(data)}개의 리뷰를 수집')
  print(f'총 {count}번의 반복을 수행')
  
  return data


# In[ ]:


# 최종 반복문
# 올리브영 자동 검색 반복문
wait = WebDriverWait(driver, 10)
search_list = olive_top_class['제품명'].unique()
olive_top_dic = {'제품명': [], '리뷰': []}

for idx, search_p in enumerate(search_list):
  # 검색창 클릭
  search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="query"]')))
  search_box.clear()
  time.sleep(1)

  # 검색어 입력 및 검색
  search_box.send_keys(search_p)
  search_box.send_keys(Keys.RETURN)
  
  # 경고창 처리
  handle_alert(driver)  

  # 새로운 페이지 링크 가져오기
  detail_pages = driver.find_elements(By.XPATH, '//*[@id="w_cate_prd_list"]/li/div/a')
  if not detail_pages:
    print(f"{idx}: {search_p} 상품을 찾을 수 없음")
    time.sleep(1)
    continue  # 다음 검색어로 넘어가기  
  
  # 현재 탭 저장
  current_window = driver.current_window_handle
  
  # 새로운 탭에서 상품 페이지 열기
  detail_page = detail_pages[0].get_attribute('href')
  old_tabs = driver.window_handles
  driver.execute_script(f"window.open('{detail_page}');")

  # 새로운 탭으로 전환
  wait.until(lambda driver: len(driver.window_handles) > len(old_tabs))
  
  new_window = [window for window in driver.window_handles if window != current_window][0]
  driver.switch_to.window(new_window)
  
  print(f"{idx} 새 탭으로 전환 완료!")
  
  # 리뷰 데이터 저장
  top_reviews = oliveyoung_reviews(driver, idx, search_p) # 리뷰 수집 함수
  
  olive_top_dic['제품명'].append(search_p)
  olive_top_dic['리뷰'].append(top_reviews)

  print(f"{idx} 상품 페이지에 접근 완료, {len(top_reviews)}개 수집 완료!")
  
  # 작업 끝난 후 원래 탭으로 돌아오기
  driver.close()
  driver.switch_to.window(current_window)
  time.sleep(3)

print(olive_top_dic)
print(len(olive_top_dic['제품명']))


# In[ ]:


driver.quit()


# In[ ]:


# DF 변환
olive_top_df = pd.DataFrame.from_dict(olive_top_dic, orient='index')
olive_top_df = olive_top_df.transpose()
olive_top_df.head()


# In[ ]:


# 데이터셋 원본 저장
# olive_top_df.to_csv('올리브영_워드클라우드_리뷰.csv', index=False, encoding="utf-8-sig")


# ### 3) 올리브영 리뷰 데이터셋 전처리 : olive_top5

# In[193]:


# top_class 플랫폼, 중분류1, 이름 컬럼과 조인
# 1) top_cuts 형성
olive_cuts = olive_top_class[['플랫폼', '중분류1', '제품명']].copy(deep=True)
print(olive_cuts.info())
olive_cuts.head()


# In[194]:


# top_class 플랫폼, 중분류1, 이름 컬럼과 조인
# 1) top_cuts 형성
olive_top5 = pd.merge(olive_cuts, olive_top_df, how='inner', on='제품명')
print(olive_top5.info())
olive_top5.head()


# In[195]:


olive_top5['리뷰'][0]


# In[196]:


# 전처리 데이터 저장
# olive_top5.to_csv("올리브영_리뷰_분류.csv", index=False, encoding="utf-8-sig")


# ### 4) 문자열 정리

# In[197]:


olive_top5['리뷰'] = olive_top5['리뷰'].str.replace(r'\n', ' ')
olive_top5['리뷰'][0]


# In[198]:


# 1. 문자열 리뷰를 리스트로 변환

def str_to_list(x):
  try:
    if type(x) == str:
      return literal_eval(x)
    elif type(x) == list:
      return x
  except:
    return None

olive_top5['리뷰'] = olive_top5['리뷰'].apply(lambda x: str_to_list(x))

olive_top5['리뷰'][0]


# In[199]:


# 2. 리스트 내 문자열 전처리 : 특수문자 제거
for i in range(len(olive_top5)):
  text = olive_top5['리뷰'][i]
  
  for j in range(len(text)):
    line = text[j]
    line = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', line).strip()
    olive_top5['리뷰'][i][j] = line

olive_top5['리뷰'][0][0]


# In[200]:


# 3. 변환값 저장할 컬럼 생성 
olive_top5['reply_text'] = ''
olive_top5['sentences_tag'] = ''

olive_top5.info()


# In[201]:


# 4. 문자열 형태소 변환값 저장 
okt = Okt()

for i in range(len(olive_top5)):
  text = olive_top5['리뷰'][i]
  
  reply_text = []
  for line in text:
    reply_text.append(line[:-1])
  
  olive_top5['reply_text'][i] = reply_text
    
  sentences_tag = []
  for stn in reply_text:
    morph = okt.pos(stn, stem=True)
    sentences_tag.append(morph)
  
  olive_top5['sentences_tag'][i] = sentences_tag
     
olive_top5.info()


# In[202]:


# 5-1. 형태소 저장 컬럼 생성 
olive_top5['bucket_list'] = ''
olive_top5.info()


# In[203]:


# 1. 형태소 분석기 초기화
okt = Okt()

# 정력 -> 세정력

'''# 2. 변환할 단어 매핑
word_mapping = {
    "좋아요": "좋음", "좋은": "좋음",
    "좋습니다": "좋음","좋네요":"좋음",
    "좋고": "좋음","좋아서":"좋음",
    "발":"발색", "오브":"오브제",
    "발림":"발림성","성도":"발림성",
    "마음":"마음에 들다","자연":"자연스러움",
    "자연스럽고":"자연스러움","자연스러운":"자연스러움",
    "색도":"색","색깔":"색",
    "색상":"색","맘":"마음에 들다",
    "부담":"부담스럽지 않은","가성":"가성비",
    "적당히":"적당한","자연스러워서": "자연스러움",
    "적당하고":"적당한","쟁":"쟁여두고 싶은",
    "옷": "옷에 묻음"}'''
    
# 3. 제거할 단어 리스트
remove_words = {"거", "구매", "유","때", "제", "입니다", "후기", "달", "것","보기","과과","중","다른"
                "같습니다","개","더","비", "입니당", "있습니다", "있고", "있어서", "있는", "있지만",
                "개", "좀", "생각","있어서","수","조금","일리","데","이","안","일단","정말","아주","사서","제일","쓰기","과",
                 "있어요","진짜","하나","있는","원래","다음","처음", "티", "저", "벌써", "상품","구입","일","좋음","좋아요","좋고","좋아서",
                 "좋습니다", "좋네요", "좋은", "배송","같아요", "가격","성도","매번","한번","원","번","이번","요","좋","같아서","보고"
                 ,"같네요","매우","듯",
                 '가', '나', '다', '라', '마', '바', '사', '아', '자', '차', '카', '타', '파', '하',
                 '에', '이', '오', '우', 
                 '사용', '제품', '상품', '에스트', '이다', '있다', '있고', '같다', '없다', '없고', '화장', '하다', '하고'
                 }


# In[204]:


# 5-2. 문장별 명사 및 형용사 단어만 남기기 
for i in range(len(olive_top5)):
  sentences_tag = olive_top5['sentences_tag'][i]
  
  bucket_list = []
  
  for one_stn in sentences_tag:
    for word, tag in one_stn:
      if tag in ['Noun', 'Adjective']:
        if word in remove_words:
          continue
        # word = word_mapping.get(word, word)
        bucket_list.append(word)
        
  olive_top5['bucket_list'][i] = bucket_list
        
print(olive_top5['bucket_list'][0])
print(olive_top5.info())


# ### 5) 형태소 변환 후 전처리 : olive_top5_df(olive_top5의 복사본)

# In[205]:


# 원본 복제
olive_top5_df = olive_top5.copy(deep=True)


# In[206]:


# 6. 필요없는 컬럼 지우기
olive_top5_df.drop(['제품명', '리뷰', 'reply_text', 'sentences_tag'], axis=1, inplace=True)
olive_top5_df.info()


# In[207]:


olive_top5_df[-5:]


# In[208]:


# 병합 전 길이
print(len(olive_top5['bucket_list'][27]))
print(len(olive_top5['bucket_list'][28]))
print(len(olive_top5['bucket_list'][29]))
print(len(olive_top5['bucket_list'][30]))
print(len(olive_top5['bucket_list'][31]))


# In[209]:


# 중분류1 단위로 bucket_list 합치기
olive_class_list = olive_top5_df['중분류1'].unique()

for j in range(len(olive_class_list)):
  bucket = olive_top5_df[olive_top5_df['중분류1']==olive_class_list[j]].index
  min_b = min(bucket)
  
  for b in bucket:
    if b > min_b:
      min_bucket = olive_top5_df['bucket_list'][min_b]      
      min_bucket += olive_top5_df['bucket_list'][b]
  
print(len(min_bucket))


# In[210]:


# 병합 후 길이
print(len(olive_top5_df['bucket_list'][27]))
print(len(olive_top5_df['bucket_list'][28]))
print(len(olive_top5_df['bucket_list'][29]))
print(len(olive_top5_df['bucket_list'][30]))
print(len(olive_top5_df['bucket_list'][31]))


# In[211]:


# 중분류1 단위로 한 행씩만 남기기
olive_class_list = olive_top5_df['중분류1'].unique()

for j in range(len(olive_class_list)):
  bucket = olive_top5_df[olive_top5_df['중분류1']==olive_class_list[j]].index
  min_b = min(bucket)
  max_b = max(bucket)
  
  olive_top5_df.drop(labels=range(min_b+1,max_b+1), axis=0, inplace=True)

olive_top5_df.info()


# In[212]:


olive_top5_df.reset_index(drop=True, inplace=True)
olive_top5_df


# ### 6) 단어 빈도수 계산

# In[213]:


# 5. 단어 빈도수 계산
# 스킨케어

counts = Counter(olive_top5_df['bucket_list'][0])
test_counts = counts.most_common()
ret_0 = dict((x, y) for x,y in test_counts)

ret_0_df = pd.DataFrame.from_dict(ret_0, orient='index')
ret_0_df.reset_index(inplace=True)

ret_0_df.columns = ['Word', 'Frequency']
ret_0_df['플랫폼'], ret_0_df['중분류1'] = ['올리브영', '스킨케어']

ret_0_df = ret_0_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_0_df.head()


# In[214]:


# 5. 단어 빈도수 계산
# 베이스메이크업

counts = Counter(olive_top5_df['bucket_list'][1])
test_counts = counts.most_common()
ret_1 = dict((x, y) for x,y in test_counts)

ret_1_df = pd.DataFrame.from_dict(ret_1, orient='index')
ret_1_df.reset_index(inplace=True)

ret_1_df.columns = ['Word', 'Frequency']
ret_1_df['플랫폼'], ret_1_df['중분류1'] = ['올리브영', '베이스메이크업']

ret_1_df = ret_1_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_1_df.head()


# In[215]:


# 5. 단어 빈도수 계산
# 클렌징 

counts = Counter(olive_top5_df['bucket_list'][2])
test_counts = counts.most_common()
ret_2 = dict((x, y) for x,y in test_counts)

ret_2_df = pd.DataFrame.from_dict(ret_2, orient='index')
ret_2_df.reset_index(inplace=True)

ret_2_df.columns = ['Word', 'Frequency']
ret_2_df['플랫폼'], ret_2_df['중분류1'] = ['올리브영', '클렌징']

ret_2_df = ret_2_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_2_df.head()


# In[216]:


# 5. 단어 빈도수 계산
# 마스크팩  

counts = Counter(olive_top5_df['bucket_list'][3])
test_counts = counts.most_common()
ret_3 = dict((x, y) for x,y in test_counts)

ret_3_df = pd.DataFrame.from_dict(ret_3, orient='index')
ret_3_df.reset_index(inplace=True)

ret_3_df.columns = ['Word', 'Frequency']
ret_3_df['플랫폼'], ret_3_df['중분류1'] = ['올리브영', '마스크팩']

ret_3_df = ret_3_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_3_df.head()


# In[217]:


# 5. 단어 빈도수 계산
# 선케어

counts = Counter(olive_top5_df['bucket_list'][4])
test_counts = counts.most_common()
ret_4 = dict((x, y) for x,y in test_counts)

ret_4_df = pd.DataFrame.from_dict(ret_4, orient='index')
ret_4_df.reset_index(inplace=True)

ret_4_df.columns = ['Word', 'Frequency']
ret_4_df['플랫폼'], ret_4_df['중분류1'] = ['올리브영', '선케어']

ret_4_df = ret_4_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_4_df.head()


# In[218]:


# 5. 단어 빈도수 계산
# 립메이크업

counts = Counter(olive_top5_df['bucket_list'][5])
test_counts = counts.most_common()
ret_5 = dict((x, y) for x,y in test_counts)

ret_5_df = pd.DataFrame.from_dict(ret_5, orient='index')
ret_5_df.reset_index(inplace=True)

ret_5_df.columns = ['Word', 'Frequency']
ret_5_df['플랫폼'], ret_5_df['중분류1'] = ['올리브영', '립메이크업']

ret_5_df = ret_5_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_5_df.head()


# In[219]:


# 5. 단어 빈도수 계산
# 립메이크업

counts = Counter(olive_top5_df['bucket_list'][6])
test_counts = counts.most_common()
ret_6 = dict((x, y) for x,y in test_counts)

ret_6_df = pd.DataFrame.from_dict(ret_6, orient='index')
ret_6_df.reset_index(inplace=True)

ret_6_df.columns = ['Word', 'Frequency']
ret_6_df['플랫폼'], ret_6_df['중분류1'] = ['올리브영', '아이메이크업']

ret_6_df = ret_6_df.reindex(['플랫폼', '중분류1', 'Word', 'Frequency'], axis=1)

ret_6_df.head()


# In[220]:


# 6. 빈도수 데이터셋 통합
concat_list = [ret_0_df, ret_1_df, ret_2_df, ret_3_df, ret_4_df, ret_5_df, ret_6_df]
olive_ret_df = pd.concat(concat_list, ignore_index=True)

print(olive_ret_df['중분류1'].unique())
print(olive_ret_df.info())
print(olive_ret_df.head())


# In[221]:


# 데이터셋 저장
# olive_ret_df.to_csv('올리브영_워드클라우드.csv', index=False, encoding="utf-8-sig")


# # 4. 추가 데이터 수집

# ## Google Trend : 일본 & 한국 화장품 검색어 트렌드

# ### 1) 일본, 한국 화장품 검색어 트렌드

# In[ ]:


# TrendReq 객체 생성
pytrends = TrendReq(hl='ko-KR', tz=540)  

# 분석할 키워드 목록
kw_kr_list = ["화장품", "스킨케어", "메이크업"]
kw_jp_list = ["化粧品", "スキンケア", "メイクアップ"]

# 한국(KR) 데이터 수집
pytrends.build_payload(kw_kr_list, cat=0, timeframe='today 12-m', geo='KR', gprop='')
kr_data = pytrends.interest_over_time()

# 일본(JP) 데이터 수집
pytrends.build_payload(kw_jp_list, cat=0, timeframe='today 12-m', geo='JP', gprop='')
jp_data = pytrends.interest_over_time()

# 데이터 시각화
plt.figure(figsize=(12, 6))
for kw in kw_kr_list:
    plt.plot(kr_data.index, kr_data[kw], label=f"{kw} (KR)", linestyle='solid')

for kw in kw_jp_list:
    plt.plot(jp_data.index, jp_data[kw], label=f"{kw} (JP)", linestyle='dashed')

plt.legend()
plt.title("화장품 관련 검색 트렌드 (한국 vs 일본)")
plt.xlabel("날짜")
plt.ylabel("검색 관심도")
plt.xticks(rotation=45)
plt.grid()
plt.show()


# ### 2) 한국 화장품 특정 키워드

# In[ ]:


# TrendReq 객체 생성
pytrends = TrendReq(hl='ko-KR', tz=540)  # 한국어 설정, 시간대는 일본/한국 공통 (UTC+9)

# 분석할 키워드 목록
kw_kr_list = ['마이크로바이옴', '셀룰러', '클린 뷰티']

# 한국(KR) 데이터 수집
pytrends.build_payload(kw_kr_list, cat=0, timeframe='today 12-m', geo='KR', gprop='')
kr_data = pytrends.interest_over_time()

# 데이터 시각화
plt.figure(figsize=(12, 6))
for kw in kw_kr_list:
    plt.plot(kr_data.index, kr_data[kw], label=f"{kw} (KR)", linestyle='solid')

plt.legend()
plt.title("화장품 관련 검색 트렌드 (한국)")
plt.xlabel("날짜")
plt.ylabel("검색 관심도")
plt.xticks(rotation=45)
plt.grid()
plt.show()


# ### 3) 한국 뷰티, 메이크업 구글 트렌드

# In[ ]:


pytrends = TrendReq(hl="ko", tz=540)  # 한국어(ko) & 한국 시간대(UTC+9)

kw_list = ["뷰티", "메이크업"]  # 검색어 리스트

# 트렌드 데이터 요청 (5년간)
pytrends.build_payload(kw_list, cat=0, timeframe="today 5-y", geo="KR", gprop="")

# 데이터 가져오기
df = pytrends.interest_over_time()
print(df.head())  # 데이터 확인


# In[ ]:


df.drop(columns=["isPartial"], inplace=True) 
df.plot(figsize=(12,6), title="Google Trends 검색량 변화")
plt.xlabel("년도")
plt.ylabel("트렌드 점수")
plt.show()


# ## 네이버 데이터랩 - 연령별 브랜드 검색량

# In[225]:


# 전체 데이터 통합을 위한 리스트 저장 함수
all_age = []
all_len = []

def all_age_list(age_df):
    all_age.append(age_df)
    all_len.append(f'{age_df.shape}')

    return all_age, all_len


# ### 1) 기타 브랜드 : extra_age_df

# In[226]:


# 원본 데이터 확인
extra_age.info()


# In[227]:


# DF 구조 바꾸기
extra_melt = pd.melt(extra_age,id_vars=['날짜', '연령대'], value_vars=['그라운드플랜', '셀인샷', '에스네이처', '쏘내추럴'])

# DF 컬럼명 수정
extra_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(extra_melt.info())
extra_melt.head()


# In[228]:


# 브랜드별 평균 관심도 확인 
extra_avg = extra_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
extra_avg = extra_avg.reset_index()

print(extra_avg.info())
extra_avg.head()


# In[229]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
extra_avg['날짜'] = '총합'
extra_avg = extra_avg[['날짜', '연령대', '브랜드', '관심도']]

extra_avg.info()


# In[230]:


# melt & avg df 병합
extra_age_df = pd.concat([extra_avg, extra_melt])
extra_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
extra_age_df['대분류'] = '스킨케어'
extra_age_df['중분류1'] = '기타'

extra_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(extra_age_df)


# In[ ]:


# 원본 데이터 저장
# extra_age_df.to_csv('기타_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 2) 클렌징 브랜드 : clean_age_df

# In[232]:


# 원본 데이터 확인
clean_age.info()


# In[233]:


# DF 구조 바꾸기
clean_melt = pd.melt(clean_age,id_vars=['날짜', '연령대'], value_vars=['메이크프렘', '에스네이처', '일리윤', '일소', '휩드'])

# DF 컬럼명 수정
clean_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(clean_melt.info())
clean_melt.head()


# In[234]:


# 브랜드별 평균 관심도 확인 
clean_avg = clean_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
clean_avg = clean_avg.reset_index()

print(clean_avg.info())
clean_avg.head()


# In[235]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
clean_avg['날짜'] = '총합'
clean_avg = clean_avg[['날짜', '연령대', '브랜드', '관심도']]

clean_avg.info()


# In[236]:


# melt & avg df 병합
clean_age_df = pd.concat([clean_avg, clean_melt])
clean_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
clean_age_df['대분류'] = '스킨케어'
clean_age_df['중분류1'] = '클렌징'

clean_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(clean_age_df)


# In[ ]:


# 원본 데이터 저장
# clean_age_df.to_csv('클렌징_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 3) 마스크 브랜드 : mask_age_df

# In[238]:


# 원본 데이터 확인
mask_age.info()


# In[239]:


# DF 구조 바꾸기
mask_melt = pd.melt(mask_age,id_vars=['날짜', '연령대'], value_vars=['트리마이'])

# DF 컬럼명 수정
mask_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(mask_melt.info())
mask_melt.head()


# In[240]:


# 브랜드별 평균 관심도 확인 
mask_avg = mask_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
mask_avg = mask_avg.reset_index()

print(mask_avg.info())
mask_avg.head()


# In[241]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
mask_avg['날짜'] = '총합'
mask_avg = mask_avg[['날짜', '연령대', '브랜드', '관심도']]

mask_avg.info()


# In[242]:


# melt & avg df 병합
mask_age_df = pd.concat([mask_avg, mask_melt])
mask_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
mask_age_df['대분류'] = '스킨케어'
mask_age_df['중분류1'] = '마스크팩'

mask_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(mask_age_df)


# In[ ]:


# 원본 데이터 저장
# mask_age_df.to_csv('마스크팩_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 4) 스킨케어 브랜드 : skin_age_df

# In[244]:


# 원본 데이터 확인
skin_age.info()


# In[245]:


# DF 구조 바꾸기
skin_melt = pd.melt(skin_age,id_vars=['날짜', '연령대'], value_vars=['에스네이처', '일리윤', '퓨리피아'])

# DF 컬럼명 수정
skin_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(skin_melt.info())
skin_melt.head()


# In[246]:


# 브랜드별 평균 관심도 확인 
skin_avg = skin_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
skin_avg = skin_avg.reset_index()

print(skin_avg.info())
skin_avg.head()


# In[247]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
skin_avg['날짜'] = '총합'
skin_avg = skin_avg[['날짜', '연령대', '브랜드', '관심도']]

skin_avg.info()


# In[248]:


# melt & avg df 병합
skin_age_df = pd.concat([skin_avg, skin_melt])
skin_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
skin_age_df['대분류'] = '스킨케어'
skin_age_df['중분류1'] = '스킨케어'

skin_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(skin_age_df)


# In[ ]:


# 원본 데이터 저장
# skin_age_df.to_csv('스킨_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 5) 아이메이크업 브랜드 : eye_age_df

# In[250]:


# 원본 데이터 확인
eye_age.info()


# In[251]:


# DF 구조 바꾸기
eye_melt = pd.melt(eye_age,id_vars=['날짜', '연령대'], value_vars=['투크'])

# DF 컬럼명 수정
eye_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(eye_melt.info())
eye_melt.head()


# In[252]:


# 브랜드별 평균 관심도 확인 
eye_avg = eye_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
eye_avg = eye_avg.reset_index()

print(eye_avg.info())
eye_avg.head()


# In[253]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
eye_avg['날짜'] = '총합'
eye_avg = eye_avg[['날짜', '연령대', '브랜드', '관심도']]

eye_avg.info()


# In[254]:


# melt & avg df 병합
eye_age_df = pd.concat([eye_avg, eye_melt])
eye_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
eye_age_df['대분류'] = '색조메이크업'
eye_age_df['중분류1'] = '아이메이크업'

eye_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(eye_age_df)


# In[ ]:


# 원본 데이터 저장
# eye_age_df.to_csv('아이메이크업_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 6) 립메이크업 브랜드 : lip_age_df

# In[256]:


# 원본 데이터 확인
lip_age.info()


# In[257]:


# DF 구조 바꾸기
lip_melt = pd.melt(lip_age,id_vars=['날짜', '연령대'], value_vars=['글피오', '오드타입', '오브제'])

# DF 컬럼명 수정
lip_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(lip_melt.info())
lip_melt.head()


# In[258]:


# 브랜드별 평균 관심도 확인 
lip_avg = lip_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
lip_avg = lip_avg.reset_index()

print(lip_avg.info())
lip_avg.head()


# In[259]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
lip_avg['날짜'] = '총합'
lip_avg = lip_avg[['날짜', '연령대', '브랜드', '관심도']]

lip_avg.info()


# In[260]:


# melt & avg df 병합
lip_age_df = pd.concat([lip_avg, lip_melt])
lip_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
lip_age_df['대분류'] = '색조메이크업'
lip_age_df['중분류1'] = '립메이크업'

lip_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(lip_age_df)


# In[ ]:


# 원본 데이터 저장
# lip_age_df.to_csv('립_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 7) 선케어 브랜드 : sun_age_df

# In[262]:


# 원본 데이터 확인
sun_age.info()


# In[263]:


# DF 구조 바꾸기
sun_melt = pd.melt(sun_age,id_vars=['날짜', '연령대'], value_vars=['닥터아토', '바론시에', '셀퓨전씨', '에스네이처'])

# DF 컬럼명 수정
sun_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(sun_melt.info())
sun_melt.head()


# In[264]:


# 브랜드별 평균 관심도 확인 
sun_avg = sun_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
sun_avg = sun_avg.reset_index()

print(sun_avg.info())
sun_avg.head()


# In[265]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
sun_avg['날짜'] = '총합'
sun_avg = sun_avg[['날짜', '연령대', '브랜드', '관심도']]

sun_avg.info()


# In[266]:


# melt & avg df 병합
sun_age_df = pd.concat([sun_avg, sun_melt])
sun_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
sun_age_df['대분류'] = '베이스메이크업'
sun_age_df['중분류1'] = '선케어'

sun_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(sun_age_df)


# In[ ]:


# 원본 데이터 저장
# sun_age_df.to_csv('선케어_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 8) 베이스메이크업 브랜드 : base_age_df

# In[268]:


# 원본 데이터 확인
base_age.info()


# In[269]:


# DF 구조 바꾸기
base_melt = pd.melt(base_age,id_vars=['날짜', '연령대'], value_vars=['셀퓨전씨', '오브제', '에스네이처', '정샘물뷰티', '지베르니'])

# DF 컬럼명 수정
base_melt.rename(columns = {'variable':'브랜드', 'value':'관심도'}, inplace=True)

print(base_melt.info())
base_melt.head()


# In[270]:


# 브랜드별 평균 관심도 확인 
base_avg = base_melt.groupby(['연령대', '브랜드'])['관심도'].mean()
base_avg = base_avg.reset_index()

print(base_avg.info())
base_avg.head()


# In[271]:


# avg df에 날짜 컬럼 삽입 및 순서 변경
# 날짜 = '총합' 추가 -> 연령별 각 브랜드의 관심도 평균 확인 가능
base_avg['날짜'] = '총합'
base_avg = base_avg[['날짜', '연령대', '브랜드', '관심도']]

base_avg.info()


# In[272]:


# melt & avg df 병합
base_age_df = pd.concat([base_avg, base_melt])
base_age_df.info()

# 분류 필터를 위한 분류 컬럼 생성
base_age_df['대분류'] = '베이스메이크업'
base_age_df['중분류1'] = '베이스메이크업'

base_age_df.head()

# 통합시 한번에 저장하기 위한 함수
all_age_list(base_age_df)


# In[ ]:


# 원본 데이터 저장
# base_age_df.to_csv('베이스메이크업_연령별선호도.csv', index=False, encoding="utf-8-sig")


# ### 9) 연령별 검색량 데이터 통합 : all_age_df

# In[274]:


all_age_df = pd.concat(all_age, axis=0, ignore_index=True)

print(all_age_df)
all_age_df


# In[275]:


# 통합 더블체크 (1)
print(all_age_df['대분류'].nunique())
print(all_age_df['대분류'].unique())
print(all_age_df['중분류1'].nunique())
print(all_age_df['중분류1'].unique())


# In[276]:


# 통합 더블체크 (2)
print(extra_age_df.shape)
print(lip_age_df.shape)
print(clean_age_df.shape)
print(mask_age_df.shape)
print(skin_age_df.shape)
print(eye_age_df.shape)
print(sun_age_df.shape)
print(base_age_df.shape)

all_len


# In[ ]:


# 통합 데이터 저장
# all_age_df.to_csv('통합_연령별선호도.csv', index=False, encoding="utf-8-sig")

