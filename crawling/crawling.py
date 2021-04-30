import os
import time
import socket
import datetime

from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, \
    ElementNotInteractableException
from PIL import Image


def scroll_down():
    scroll_count = 0

    print("ㅡ 스크롤 다운 시작 ㅡ")

    last_height = driver.execute_script("return document.body.scrollHeight")

    after_click = False

    while True:
        print(f"ㅡ 스크롤 횟수 : {scroll_count} ㅡ")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_count += 1
        print("last_height : " + str(last_height))
        time.sleep(1)

        new_height = driver.execute_script("return document.body.scrollHeight")
        print("new_height : " + str(new_height))

        if last_height == new_height:
            if after_click is True:
                print("ㅡ 스크롤 다운 종료 1ㅡ")
                break

            if after_click is False:
                #if driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').is_displayed():
                if driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div[1]/div[4]').is_displayed():
                    driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div[1]/div[4]').click()
                    #driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').click()
                    after_click = True
                elif NoSuchElementException:
                    print("ㅡ NoSuchElemnetException ㅡ")
                    print("ㅡ 스크롤 다운 종료 2ㅡ")
                    break

        last_height = new_height


def click_and_retrieve(index, img, img_list_length):
    global crawled_count
    try:
        img.click()
        driver.implicitly_wait(3)
        # //*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div[1]/div[1]/div/div[2]/a/img[@src="http"]
        #src_img = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div[1]/div[1]/div/div[2]/a/img')
        src_img = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div/div[2]/a/img')
        src = src_img.get_attribute('src')

        if src.split('.')[-1] == "png":
            urlretrieve(src, path + date + '/' + query + '/' + str(crawled_count + 1) + ".png")
            print(f"{index + 1} / {img_list_length} 번째 사진 저장 (png)")
        else:
            urlretrieve(src, path + date + '/' + query + '/' + str(crawled_count + 1) + ".jpg")
            print(f"{index + 1} / {img_list_length} 번째 사진 저장 (jpg)")
        crawled_count += 1

    except HTTPError:
        print("ㅡ HTTPError & 패스 ㅡ")
        pass


def crawling():
    global crawled_count

    print("ㅡ 크롤링 시작 ㅡ")

    url = f"https://www.google.com/search?as_st=y&tbm=isch&h1=ko&as_q={query}&as_epq=&as_op=&as_eq=&cr=&as_sitesearch=&safe=images&tbs=itp:photo"
    driver.get(url)
    driver.maximize_window()
    scroll_down()

    img_list = driver.find_elements_by_css_selector(".rg_i.Q4LuWd")

    os.makedirs(path + date + '/' + query)
    print(f"ㅡ {path}{date}/{query} 생성 ㅡ")

    for index, img in enumerate(img_list):
        try:
            click_and_retrieve(index, img, len(img_list))

        except ElementClickInterceptedException:
            print("ㅡ ElementClickInterceptedException ㅡ")
            driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            print("ㅡ 100만큼 스크롤 다운 및 3초 슬립 ㅡ")
            time.sleep(3)
            click_and_retrieve(index, img, len(img_list))

        except NoSuchElementException:
            print("ㅡ NoSuchElementException ㅡ")
            driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            print("ㅡ 100만큼 스크롤 다운 및 3초 슬립 ㅡ")
            time.sleep(3)
            click_and_retrieve(index, img, len(img_list))

        except ConnectionResetError:
            print("ㅡ ConnectionResetError & 패스 ㅡ")
            pass

        except URLError:
            print("ㅡ URLError & 패스 ㅡ")
            pass

        except socket.timeout:
            print("ㅡ socket.timeout & 패스 ㅡ")
            pass

        except socket.gaierror:
            print("ㅡ socket.gaierror & 패스 ㅡ")
            pass

        except ElementNotInteractableException:
            print("ㅡ ElementNotInteractableException ㅡ")
            break

    try:
        print("ㅡ 크롤링 종료 (성공률 : %.2f%%) ㅡ" % (crawled_count / len(img_list) * 100.0))

    except ZeroDivisionError:
        print("ㅡ img_list가 비어있음 ㅡ")

    driver.quit()


def filtering():
    print("ㅡ 필터링 시작 ㅡ")
    filtered_count = 0
    dir_name = path + date + '/' + query
    for index, file_name in enumerate(os.listdir(dir_name)):
        try:
            file_path = os.path.join(dir_name, file_name)
            img = Image.open(file_path)

            if img.width < 351 and img.height < 351:
                img.close()
                os.remove(file_path)
                print(f"{index} 번째 사진 삭제")
                filtered_count += 1

        except OSError:
            os.remove(file_path)
            filtered_count += 1

    print(f"ㅡ 필터링 종료 (총 갯수 : {crawled_count - filtered_count}) ㅡ")


def checking():
    for dir_name in os.listdir(path):
        file_list = os.listdir(path + dir_name)
        if query in file_list:
            print(f"ㅡ 중복된 검색어 ({dir_name}) ㅡ")
            return True


if __name__ == '__main__':
    socket.setdefaulttimeout(30)

    path = "C:/development/crawling/"
    date = datetime.datetime.now().strftime('%Y.%m.%d')

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome("C:/development/crawling/chrome-driver/chromedriver.exe", options=options)
    #driver = webdriver.Chrome("C:/development/crawling/chrome-driver/chromedriver.exe")

    crawled_count = 0

    query = input("입력 : ")

    crawling()
    # filtering()

