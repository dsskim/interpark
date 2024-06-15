from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

from collections import defaultdict
import re
import time
from datetime import datetime, date, timedelta
import time
import easyocr
from loguru import logger
from random import choice

from config import private_data

def get_weekday(year, month, day):
    day = date(year, month, day)
    return day.isoweekday()

def get_target_time(hour, minute):
    current_time = datetime.now()
    fixed_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return fixed_time

def get_interpark_server_time(driver):
    server_time_str = driver.execute_script("return new Date().toUTCString();")
    server_time = datetime.strptime(server_time_str, "%a, %d %b %Y %H:%M:%S %Z")

    return server_time

def get_wait_second(driver, target_hour, target_minute):
    target_time = get_target_time(target_hour, target_minute)
    interpark_time = get_interpark_server_time(driver) + timedelta(hours=9)
    time_difference = target_time - interpark_time

    print("현재시간: ", datetime.now())
    print("Interpark 웹사이트의 서버 시간:", interpark_time)
    time_difference_seconds = int(time_difference.total_seconds())
    print("대기 시간 (초):", time_difference_seconds)

    return time_difference_seconds

def calculate_time_difference(current_time, interpark_time):
    time_difference = current_time - interpark_time
    return time_difference

def get_valid_keys(valid_dict, order):
    return [key for key in order if key in valid_dict]

def find_consecutive_seats(data, N):
    # 좌석을 행과 열로 그룹화
    seats_by_row = defaultdict(list)
    for item in data:
        elem, seat = item
        row, col, seat_num = seat
        seats_by_row[(row, col)].append((int(seat_num), elem, seat))

    # 붙어 있는 좌석 조합 찾기
    consecutive_seats = []
    for key, seats in seats_by_row.items():
        seats.sort()
        temp = []
        for i in range(len(seats)):
            if i > 0 and seats[i][0] == seats[i - 1][0] + 1:
                temp.append(seats[i])
            else:
                if len(temp) >= N - 1:
                    temp.insert(0, seats[i - len(temp) - 1])
                    consecutive_seats.append((key, temp[:N]))
                temp = []
        if len(temp) >= N - 1:
            temp.insert(0, seats[i - len(temp)])
            for idx in range(len(temp)-N):
                consecutive_seats.append((key, temp[idx:idx+N]))

    # 최종 결과 반환
    result = []
    for key, seats in consecutive_seats:
        result.append([seat[1:] for seat in seats])
    
    return result

def captcha():
    # 부정예매방지 문자 이미지 요소 선택
    capchaPng = driver.find_element(By.XPATH, '//*[@id="imgCaptcha"]')

    # 부정예매방지문자 입력
    while capchaPng:
        result = reader.readtext(capchaPng.screenshot_as_png, detail=0)
        capchaValue = result[0].replace(' ', '').replace('5', 'S').replace('0', 'O').replace('$', 'S').replace(',', '')\
            .replace(':', '').replace('.', '').replace('+', 'T').replace("'", '').replace('`', '')\
            .replace('1', 'L').replace('e', 'Q').replace('3', 'S').replace('€', 'C').replace('{', '').replace('-', '')
            
        # 입력
        driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]/div[1]/div[3]').click()
        chapchaText = driver.find_element(By.XPATH,'//*[@id="txtCaptcha"]')
        chapchaText.send_keys(capchaValue)
            
        #입력완료 버튼 클릭
        driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]/div[1]/div[4]/a[2]').click()

        # 입력이 잘 됐는지 확인하기
        display = driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]').is_displayed()
        
        # 입력 문자가 틀렸을 때 새로고침하여 다시입력
        if display:
            driver.find_element(By.XPATH,'//*[@id="divRecaptcha"]/div[1]/div[1]/a[1]').click()
        # 입력 문자가 맞으면 select 함수 실행
        else:
            break

def payment():

    # 좌석선택 완료 버튼 클릭
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeat"]'))
    driver.find_element(By.XPATH,'//*[@id="NextStepImage"]').click()
    
    # # 가격선택
    # driver.switch_to.default_content()
    # driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmBookStep']"))
    # driver.find_element(By.XPATH, '//*[@id="li2"]/span[1]/label').click()
    # driver.find_element(By.XPATH,'//*[@id="NextStepImage"]').click()
    
    # # 이용약관 동의
    # driver.switch_to.default_content()
    # driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmBookCertify']"))
    # driver.find_element(By.XPATH, '//*[@id="Agree"]').click()
    # driver.find_element(By.XPATH, '//*[@id="information"]/div[2]/a[1]/img').click()
    
    # # 다음단계 재클릭
    # driver.switch_to.default_content()
    # driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmBookStep']"))
    # driver.find_element(By.XPATH,'//*[@id="NextStepImage"]').click()

    # # 예매자 확인
    # driver.switch_to.default_content()
    # driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmBookStep']"))
    # driver.find_element(By.XPATH,'//*[@id="YYMMDD"]').send_keys(birth)
    # driver.find_element(By.XPATH,'//*[@id="CustomEtc"]').send_keys(car_number)
    
    # # 결제방식 선택
    # driver.find_element(By.XPATH,'//*[@id="Payment_22003"]/td/label').click()
            
    # select2 = Select(driver.find_element(By.XPATH, '//*[@id="DiscountCard"]'))
    # select2.select_by_index(1)

    # driver.switch_to.default_content()
    # driver.switch_to.frame(driver.find_element(By.XPATH, "//*[@id='ifrmBookStep']"))
    # driver.find_element(By.XPATH,'//*[@id="NextStepImage"]').click()
    
    # # 동의 후, 결제하기
    # driver.find_element(By.XPATH,'//*[@id="checkAll"]').click()
    # driver.switch_to.default_content() 
    # driver.find_element(By.XPATH,'//*[@id="NextStepImage"]"]').click()

# 좌석 선택
def search_select_seat():
    while True:
        # 좌석선택 아이프레임으로 이동
        driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeatDetail"]'))
        seats = driver.find_elements(By.XPATH,'//*[@id="Seats"]')

        if len(seats) == 0:
            return False
        
        data = []
        for seat in seats:
            numbers = re.findall(r'\d+', seat.accessible_name)
            data.append([seat, numbers])
        
        results = find_consecutive_seats(data, N)

        if len(results) == 0:
            return False
        
        res = choice(results)

        for r in res:
            r[0].click()
            logger.info(f'{r[0].accessible_name} 선택!!')
        
        try:
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.XPATH,'//*[@id="ifrmSeat"]'))
            driver.find_element(By.XPATH,'//*[@id="NextStepImage"]').click()

            driver.switch_to.default_content()
            book_page = driver.find_element(By.XPATH, "//*[@id='ifrmBookStep']")

            return True
        except:
            continue

        return False

# 좌석 탐색
def select():
    # 세부 구역 탐색
    seat_grades = driver.find_elements(By.ID, 'GradeRow')

    ok = False

    for grade in seat_grades:
        if ok:
            break
        
        if grade.text == '':
            continue
        try:
            driver.switch_to.default_content()
            seat_frm = driver.find_element(By.XPATH, '//*[@id="ifrmSeat"]')
            driver.switch_to.frame(seat_frm)
            # 세부 구역 탐색
            grade.find_element(By.CLASS_NAME, 'select').click()
            logger.info(f'{grade.text} 구역 선택')

            time.sleep(0.2)
            areas = driver.find_elements(By.CSS_SELECTOR, '.box li')

            for a in areas:
                if ok:
                    break
                if a.text == '':
                    continue

                a.find_element(By.TAG_NAME, 'a').click()
                logger.info(f'{a.text} 세부구역 선택')

                while True:
                    try:
                        flag = search_select_seat()
                    except Exception as e:
                        logger.warning(e)
                    
                    if not flag:  # 좌석 없음 -> 다음 구역
                        driver.switch_to.default_content()
                        seat_frm = driver.find_element(By.XPATH, '//*[@id="ifrmSeat"]')
                        driver.switch_to.frame(seat_frm)
                        break
                    else:
                        logger.info("좌석 선택 완료!")
                        ok = True
                        break
            
        except Exception as e:
            logger.warning(f'세부 구역 찾을 수 없음 = {e}')
    

    if not ok:
        logger.error("좌석 없음...")
    
    return

if __name__ == "__main__":
    id = private_data['username']
    pw = private_data['password']

    # # Real
    code = 24007162

    open_hour = 20
    open_minute = 00

    target_year = 2024
    target_month = 7
    target_day = 6
    N = 2

    ref_weekday = get_weekday(target_year, target_month, 1) % 7 # 일요일은 7 -> 0

    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)

    # 부정예매방지문자 OCR 생성
    reader = easyocr.Reader(['en'])

    # 브라우저 사이즈
    driver.set_window_size(1500, 800)

    # 웹페이지가 로드될 때까지 1초를 대기
    driver.implicitly_wait(time_to_wait=1)  

    driver.get(url='https://tickets.interpark.com/')

    driver.find_element(By.LINK_TEXT,'로그인').click()
    userId = driver.find_element(By.XPATH, '//*[@id="userId"]')
    userId.send_keys(id)
    userPwd = driver.find_element(By.XPATH, '//*[@id="userPwd"]')
    userPwd.send_keys(pw)
    userPwd.send_keys(Keys.ENTER)

    driver.get(url=f'https://tickets.interpark.com/goods/{code}')
        # 새로운 탭으로 이동
    print('--------------------')
    driver.switch_to.window(driver.window_handles[-1])
    # 팝업 있으면 제거
    try:
        driver.find_element(By.XPATH,'//*[@id="popup-prdGuide"]/div/div[3]/button').click()
    except Exception:
        logger.info('팝업 없음')

    while True:
        wait_time = get_wait_second(driver, open_hour, open_minute)
        print(f"남은 시간(초): {wait_time}")
        if wait_time < 2:
            break
        time.sleep(0.5)

    # 예매하기 버튼 클릭 & 새로운 탭으로 이동
    while True:
        try:
            logger.info("예매하기 클릭 시도")
            month = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[2]')
            current_month = int(month.text.split()[-1])

            # next month
            if current_month < target_month:
                elem = driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[1]/li[3]')
                # 요소의 "class" 속성 값을 가져옵니다.
                class_attribute = elem.get_attribute("class")

                # "disabled" 클래스가 포함되어 있는지 확인합니다.
                if "disabled" in class_attribute:
                    logger.warning(f'버튼이 비활성화 되어있어 다음달로 넘어갈 수 없음. 재시도...')
                    continue
                elem.click()
            
            # 날짜 클릭
            if target_day != 1:
                idx = ref_weekday + target_day
            
            driver.find_element(By.XPATH, f'//*[@id="productSide"]/div/div[1]/div[1]/div[2]/div/div/div/div/ul[3]/li[{idx}]').click()

            # 예매하기 선택
            driver.find_element(By.XPATH, '//*[@id="productSide"]/div/div[2]/a[1]/span').click()
            
        except Exception:
            logger.info("예매하기 클릭 실패 XXXXXX")
            continue
        else:
            logger.info("예매하기 클릭 성공 OOOO")
            break

    while True:    
        if len(driver.window_handles) == 1:
            logger.info("창 안뜸 XXXXXX")
        else:
            logger.info("창 뜸 OOOOOOOOO")
            break

    driver.switch_to.window(driver.window_handles[-1])

    # 아이프레임으로 이동
    while True:
        try:
            logger.info("ifrmSeat 찾기!!!")
            element = driver.find_element(By.XPATH, '//*[@id="ifrmSeat"]')
        except Exception:
            logger.info("ifrmSeat 찾기 실패 XXXXXXX")
            continue
        else:
            print("ifrmSeat 찾기 성공 OOOOOOO")
            break

    driver.switch_to.frame(element)
    
    try:
        captcha()
    except Exception as e:
        logger.warning(f"캡챠 없음? - {e}")

    # 팝업 닫기
    try:
        driver.find_element(By.XPATH, '//*[@id="divBookNotice"]/div/div/span').click()
    except:
        logger.info("팝업 없음")
    
    select()