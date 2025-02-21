# @cosme, 화해 화장품 크롤링 
### 요약
1. @cosme 화장품 랭킹
2. @cosme 한국 브랜드 화장품 랭킹
3. 화장품 관련 구글 트렌드
4. 화해 세부 카테고리별 랭킹

### 파일 구조  
📦beauty_crawling  
 ┣ 📂cosme_category  
 ┃ ┣ 📜기타_스킨케어_cosme_ranking.csv  
 ┃ ┣ 📜눈가_입원_케어_cosme_ranking.csv  
 ┃ ┣ 📜메이크업_cosme_ranking.csv  
 ┃ ┣ 📜미용액_유액_cosme_ranking.csv  
 ┃ ┣ 📜베이스_메이크업_cosme_ranking.csv  
 ┃ ┣ 📜스킨케어 전체 순위_cosme_ranking.csv  
 ┃ ┣ 📜썬크림_cosme_ranking.csv  
 ┃ ┣ 📜클렌징_cosme_ranking.csv  
 ┃ ┣ 📜팩_페이스마스크_cosme_ranking.csv  
 ┃ ┗ 📜화장수_cosme_ranking.csv  
 ┃ ┗ 📜cosme_category_product_details.csv  
 ┣ 📂cosme_data  
 ┃ ┣ 📜2025-2-6_2025-2-12_cosme_ranking.csv  
 ┃ ┣ 📜cosme_brand.csv  
 ┃ ┗ 📜cosme_ranking_details.csv  
 ┣ 📂cosme_korea  
 ┃ ┣ 📜2024-11-13_2025-2-12_korea_cosme_ranking.csv  
 ┃ ┣ 📜korea_cosme_product_3000.csv  
 ┃ ┣ 📜korea_cosme_product_3000_details.csv  
 ┃ ┗ 📜korea_cosme_ranking_details.csv  
 ┣ 📂hwahae_data  
 ┃ ┣ 📜hwahae_BB_CC크림_ranking.csv  
 ┃ ┣ 📜hwahae_로션_에멀젼_ranking.csv  
 ┃ ┣ 📜hwahae_립_아이리무버_ranking.csv  
 ┃ ┣ 📜hwahae_립글로스_ranking.csv  
 ┃ ┣ 📜hwahae_립스틱_ranking.csv  
 ┃ ┣ 📜hwahae_립케어_립밤_ranking.csv  
 ┃ ┣ 📜hwahae_립틴트_ranking.csv  
 ┃ ┣ 📜hwahae_마스카라_픽서_ranking.csv  
 ┃ ┣ 📜hwahae_메이크업베이스_ranking.csv  
 ┃ ┣ 📜hwahae_메이크업픽서_ranking.csv  
 ┃ ┣ 📜hwahae_미스트_ranking.csv  
 ┃ ┣ 📜hwahae_밤_멀티밤_ranking.csv  
 ┃ ┣ 📜hwahae_부분마스크_팩_ranking.csv  
 ┃ ┣ 📜hwahae_부분마스크패드_ranking.csv  
 ┃ ┣ 📜hwahae_블러셔_ranking.csv  
 ┃ ┣ 📜hwahae_선스틱_ranking.csv  
 ┃ ┣ 📜hwahae_선스프레이_ranking.csv  
 ┃ ┣ 📜hwahae_선케어기타_ranking.csv  
 ┃ ┣ 📜hwahae_선쿠션_팩트_ranking.csv  
 ┃ ┣ 📜hwahae_선크림_로션_ranking.csv  
 ┃ ┣ 📜hwahae_셰이딩_ranking.csv  
 ┃ ┣ 📜hwahae_속눈썹영양제_ranking.csv  
 ┃ ┣ 📜hwahae_스크럽_필링_ranking.csv  
 ┃ ┣ 📜hwahae_스크럽_필링패드_ranking.csv  
 ┃ ┣ 📜hwahae_스킨_토너패드_ranking.csv  
 ┃ ┣ 📜hwahae_스킨토너_ranking.csv  
 ┃ ┣ 📜hwahae_슬리핑팩_ranking.csv  
 ┃ ┣ 📜hwahae_시트마스크_ranking.csv  
 ┃ ┣ 📜hwahae_아이라이너_ranking.csv  
 ┃ ┣ 📜hwahae_아이브로우_ranking.csv  
 ┃ ┣ 📜hwahae_아이섀도_ranking.csv  
 ┃ ┣ 📜hwahae_아이케어_ranking.csv  
 ┃ ┣ 📜hwahae_에센스_앰플_세럼_ranking.csv  
 ┃ ┣ 📜hwahae_워시오프팩_ranking.csv  
 ┃ ┣ 📜hwahae_젤_ranking.csv  
 ┃ ┣ 📜hwahae_컨실러_ranking.csv  
 ┃ ┣ 📜hwahae_컬러립케어_립밤_ranking.csv  
 ┃ ┣ 📜hwahae_코팩_ranking.csv  
 ┃ ┣ 📜hwahae_쿠션_ranking.csv  
 ┃ ┣ 📜hwahae_크림_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징로션_크림_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징밤_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징비누_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징오일_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징워터_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징젤_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징티슈_패드_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징파우더_ranking.csv  
 ┃ ┣ 📜hwahae_클렌징폼_ranking.csv  
 ┃ ┣ 📜hwahae_톤업크림_ranking.csv  
 ┃ ┣ 📜hwahae_파우더_팩트_ranking.csv  
 ┃ ┣ 📜hwahae_파운데이션_ranking.csv  
 ┃ ┣ 📜hwahae_패치_ranking.csv  
 ┃ ┣ 📜hwahae_페이스오일_ranking.csv  
 ┃ ┣ 📜hwahae_프라이머_ranking.csv  
 ┃ ┣ 📜hwahae_필오프팩_ranking.csv  
 ┃ ┣ 📜hwahae_하이라이터_ranking.csv  
 ┃ ┗ 📜통합_화해_데이터.csv  
 ┣ 📜cosme_all_ranking.ipynb  
 ┣ 📜cosme_koreabrand_ranking.ipynb  
 ┣ 📜google_trends.ipynb  
 ┣ 📜hawhae.ipynb  
 ┗ 📜readme.md  

