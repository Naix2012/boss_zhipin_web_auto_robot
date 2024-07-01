import time
all_start_time = time.time()

#=====================单值类修改内容=====================
hot_city_list = ['全国','北京','上海','广州','深圳','杭州','天津','西安','苏州','武汉','厦门','长沙','成都','郑州','重庆','佛山','合肥','济南','青岛','南京','东莞','昆明','南昌','石家庄','宁波','福州']   #热门城市列表,不要改
city_choice = '全国'    #选择意向城市
job_n = 'python'  #选择意向职位
sal_dic = {'3k-': 402,'3k-5k': 403,'5-10k': 404, '10-20k': 405, '20-50k': 406, '50k+': 407, '不限':000} #薪资对应字典,不要改
sal = sal_dic['不限'] #选择薪资范围
low_sal = 6  #最低薪资要求,以千为单位
high_sal = 18  #最高薪资要求,以千为单位

#=====================多值类修改内容=====================

#公司名称黑名单,公司名称包含其中字符串则跳过
company_black_list_fr = ['输入排除公司名称']

#职位名称黑名单,职位名称包含其中字符串则跳过
jobname_black_list_fr = ['输入排除职务名称']

#职位详细信息黑名单,职位详细信息包含其中字符串则跳过
jobinfo_black_list_fr = ['输入排除职位详细信息关键词']

#=====================导入库=====================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import os
import random
from urllib import parse
import json
from pypinyin import lazy_pinyin
import sys
import re


#=====================主要代码=====================

def random_wait():  #随机等待时间
    #随机等待时间
    wait_time = random.randint(0, 2)
    time.sleep(wait_time)

def chrome_setup(): #设置浏览器属性
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    option = webdriver.ChromeOptions()
    option.add_experimental_option("debuggerAddress", "127.0.0.1:9527")
    
    driver = webdriver.Chrome(options=option)   #创建一个新的webdriver实例
    return driver

def get_hotcitycodes_dict(city_name):  #获取城市编码(只有热门城市)
    print('开始获取热门城市编码')
    if os.path.exists('site.json'):
        with open('site.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        zp_data = data['zpData']['hotCitySites']
        for city in zp_data:
            if city["name"] == city_name:
                city_codes = city["code"] 
                return city_codes
        print('城市非热门城市，开始全表查询')
        raise KeyError
    else:
        print('site.json文件不存在')
        raise FileNotFoundError

def get_allcitycodes_dict(city_name):
    print('开始获取全部城市编码')
    if os.path.exists('site.json'):
        with open('site.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        zp_data = data['zpData']

        city_name_pinyin = ''.join([pinyin.capitalize() for pinyin in lazy_pinyin(city_name)])
        for group in zp_data['siteGroup']:
            if city_name_pinyin[0] == group['firstChar']:
                for city in group['cityList']:
                    if city['name'] == city_name:
                        return city['code']
        print('未查询到城市编码,请更换城市')
        raise KeyError
    else:
        print('site.json文件不存在')
        raise FileNotFoundError

def xpath_wait(XPATH_in, timeout=6,type_in='located'):  #等待元素加载完成或者可点击，超时返回False
    if type_in == 'located':    #寻址等待
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, XPATH_in)))
            print('{0}页面加载完成'.format(XPATH_in))
            return True
        except TimeoutException:
            print("{0}等待超时".format(XPATH_in))
            return False
    elif type_in == "clickable":    #可点击等待
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_in)))
            print('{0}页面加载完成'.format(XPATH_in))
            return True
        except TimeoutException:
            print("{0}等待超时".format(XPATH_in))
            return False
    else:
        print('type_in参数错误,请输入located或者clickable')
        return False
        
def xpath_wait_longer(XPATH_in, timeout=6,type_in='located'): #循环等待元素加载完成
    start_time = time.time()
    loop_count = 0
    if XPATH_in != '//a[@class="default-btn cancel-btn"]':
        while True:
            loop_count += 1
            print(f"循环等待第{loop_count}次")
            if xpath_wait(XPATH_in, timeout,type_in=type_in):
                end_time = time.time()
                elapsed_time = (end_time - start_time) * 1000  # 计算运行时间（毫秒）
                print(f"循环等待完成，共循环{loop_count}次，{XPATH_in}代码运行了{elapsed_time:.2f}毫秒")
                break
            else:
                continue
    else:
        while True:
            loop_count += 1
            print(f"循环等待第{loop_count}次")
            if loop_count < 3:
                if xpath_wait(XPATH_in, timeout,type_in=type_in):
                    end_time = time.time()
                    elapsed_time = (end_time - start_time) * 1000  # 计算运行时间（毫秒）
                    print(f"循环等待完成，共循环{loop_count}次，{XPATH_in}代码运行了{elapsed_time:.2f}毫秒")
                    break
                else:
                    continue
            else:
                if xpath_wait('//a[@class="default-btn sure-btn"]', timeout,type_in='clickable'):
                    if driver.find_element(By.XPATH, '//div[@class="chat-block-header"]/h3').text == '无法进行沟通':
                        print('投递已达上限，程序结束')
                        sys.exit()
                    window_count = len(driver.window_handles)
                    click = driver.find_element(By.XPATH, '//a[@class="default-btn sure-btn"]')
                    click.click
                    try_self_cont = 0
                    try_click_cont = 0
                    while True:
                        if handles_check(window_count):
                            print('已关闭个人中心窗口')
                            break
                        else:
                            print('等待个人中心窗口出现')
                            if xpath_wait('//a[@class="default-btn sure-btn"]',type_in='clickable'):
                                try_click_cont += 1
                                print('按钮可点击,尝试点击,尝试第',try_click_cont,'次')
                                scroll_to_element(driver, '//a[@class="default-btn sure-btn"]')
                                click = driver.find_element(By.XPATH, '//a[@class="default-btn sure-btn"]')
                                click.click
                                continue
                            else:
                                try_self_cont += 1
                                print('等待个人中心窗口出现失败，尝试次数：',try_self_cont)
                                continue
                    end_time = time.time()
                    elapsed_time = (end_time - start_time) * 1000  # 计算运行时间（毫秒）
                    print(f"错误投递关闭完成，{XPATH_in}代码运行了{elapsed_time:.2f}毫秒")
                    break
                else:
                    print('点击事件可能出错，请手动重置')
                    loop_count =1
                    continue




def company_black_list(company_name,company_black_list_fr=company_black_list_fr):   #公司黑名单
    for i in company_black_list_fr: #判断公司是否在黑名单中
        if i in company_name:
            print('公司在黑名单中')
            return True
    return False

def jobinfo_black_list(job_info,jobinfo_black_list_fr=jobinfo_black_list_fr):   #职位内容黑名单
    job_info_lower = job_info.lower()
    for i in jobinfo_black_list_fr: 
        if i in job_info_lower:
            print('职位内容不符')
            return True
    return False

def jobname_black_list(job_name,jobname_black_list_fr=jobname_black_list_fr):   #职位黑名单
    job_name_lower = job_name.lower()
    for i in jobname_black_list_fr: 
        if i in job_name_lower:
            print('职位名不符')
            return True
    return False

def scroll_to_element(driver, xpath):   #将指定元素滚动到窗口中心区域
    xpath_wait_longer(xpath)
    element = driver.find_element(By.XPATH, xpath)    # 获取指定元素的坐标
    x = element.location['x']
    y = element.location['y']
    centerX = driver.execute_script("return window.innerWidth / 2;")    # 计算浏览器窗口中心位置的坐标
    centerY = driver.execute_script("return window.innerHeight / 2;")
    deltaX = x - centerX    # 计算需要滚动的距离
    deltaY = y - centerY
    print('{6}元素位置为:({0}, {1}),浏览器窗口中心坐标为({2},{3}),滚动距离为:({4}, {5})'.format(x, y, centerX, centerY, deltaX, deltaY,xpath))
    driver.execute_script(f"window.scrollBy({deltaX}, {deltaY});")    # 滚动页面
    xpath_wait_longer(xpath)

def handles_check(previous_window_count):   #误点击打开新页面解决方案
    if len(driver.window_handles) > previous_window_count:
        driver.switch_to.window(driver.window_handles[-1])  # 切换到新页面
        driver.close()  # 关闭新页面
        driver.switch_to.window(driver.window_handles[0])   # 切换回原来的页面
        return True
    else:
        return False
    
def extract_salary_range(salary_str):
    pattern = r'(\d+)-(\d+)K'
    match = re.search(pattern, salary_str)
    if match:
        lower_bound = int(match.group(1))
        upper_bound = int(match.group(2))
        return lower_bound, upper_bound
    else:
        return None


if city_choice in hot_city_list:
    city = get_hotcitycodes_dict(city_choice)
else:
    city = get_allcitycodes_dict(city_choice)
query = parse.quote(job_n)

driver = chrome_setup()
if sal == 000:
    driver.get(f'https://www.zhipin.com/web/geek/job?query={query}&city={city}')
else:
    driver.get(f'https://www.zhipin.com/web/geek/job?query={query}&city={city}&salary={sal}')
print('开始获取职位信息')
xpath_wait_longer('//div[@class="search-job-result"]')

list = driver.find_elements(By.XPATH, '//div[@class="info-public"]')    #获取职位


count_num = 0
count_company = 0
page_count = 1

while count_num < 101:  #每天投递上限100个
    for i in range(1,31):  #遍历点击职位列表
        count_company += 1
        temp_count = 0
        while temp_count<3:
            try:
                if xpath_wait(f'//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a'):
                    print('已找到//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a')
                    break
                else:
                    temp_count += 1
                    print('无法获取职位信息，尝试重新获取,temp_count={0}'.format(temp_count))
                    continue
            except:
                temp_count += 1
                print('无法获取职位信息，尝试重新获取,temp_count={0}'.format(temp_count))
                continue
        if temp_count >= 3:
            print('职位{0}无法获取,跳过'.format(f'//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a'))
            continue
        company_name = driver.find_element(By.XPATH, f'//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a').text   #读取公司名
        print('第{0}个公司是{1}'.format(count_company, company_name))
        if count_company%30 == 0 or (count_company+1)%30 == 0 or (count_company+2)%30 == 0:  #最后三个经常识别不出，先跳过
            continue
        if company_black_list(company_name):    #判断公司是否在黑名单中
            print('公司{0}在黑名单中,跳过'.format(company_name))
            random_wait()
            continue
        else:    
            job_name = driver.find_element(By.XPATH, f'//li[@ka="search_list_{count_company}"]/div[1]/a/div/span[1]')
            print('job_name={0}'.format(job_name.text))

            if jobname_black_list(job_name.text):    #判断职位是否在黑名单中
                print('职位{0}在黑名单中,跳过'.format(job_name.text))
                random_wait()
                continue

            job_sal = driver.find_element(By.XPATH, f'//li[@ka="search_list_{count_company}"]/div[1]/a/div[2]/span').text
            print('job_sal={0}'.format(job_sal))
            result = extract_salary_range(job_sal)
            if result:
                lower_bound, upper_bound = result
                print('薪资范围是{0}到{1}'.format(lower_bound, upper_bound))
            else:
                print('无法识别数字格式的薪资范围,跳过')
                continue
            if upper_bound > high_sal or lower_bound < low_sal:
                print('薪资范围不在指定范围内,跳过')
                random_wait()
                continue

            try_count = 0
            while True: #由于模拟鼠标的不稳定性，读取职务详细信息将进行多次尝试
                if try_count > 3:
                    print('尝试次数过3,退出info查找,跳过此职务')
                    break
                try_count += 1
                print('职位info查询尝试次数{0}'.format(try_count))
                scroll_to_element(driver, f'//li[@ka="search_list_{count_company}"]')
                ActionChains(driver).move_to_element(job_name).perform()
                if xpath_wait('//div[@class="job-detail-card"]',3):
                    break  # 如果成功找到元素,跳出循环
                else:
                    continue
            if try_count > 3:
                continue

            job_detail = driver.find_element(By.XPATH, '//div[@class="job-detail-card"]')   #读取职位详细信息
            job_info = job_detail.find_element(By.XPATH, './/div[@class="job-detail-body"]').text

            mouse_out = driver.find_element(By.XPATH, '//ul[@class="tag-list"]')    #把鼠标移出到标签栏避免详细信息的元素重叠
            print("job_info={0}".format(job_info))
            ActionChains(driver).move_to_element(mouse_out).perform()
            previous_window_count = len(driver.window_handles)  # 记录点击前的窗口句柄数量，防止误点击打开新窗口

            if jobinfo_black_list(job_info):
                print('职位{0}的详细信息在黑名单中,跳过'.format(job_name.text))
                random_wait()
                continue 
            else:
                error = 0
                while True: #可点击元素在模拟鼠标悬停时会变化，由于模拟鼠标的不稳定性将进行多次尝试
                    if error > 5:
                        print('超过5次按钮错误,此次投递不计算,跳过')
                        break
                    try:
                        scroll_to_element(driver, f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/div")
                        print('count_company={0}'.format(count_company))
                        job_list = driver.find_element(By.XPATH, f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/a") #定位到hr
                        print('butten_text={0}'.format(job_list.text))
                        #random_wait()
                        xpath_wait(f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/a", timeout=3,type_in='clickable')
                        job_list.click()    #点击立即沟通

                        if handles_check(previous_window_count):
                            print('已关闭误开窗口')
                            continue
                        xpath_wait_longer('//a[@class="default-btn cancel-btn"]')
                        break
                    except Exception as e:
                        print('click_error_one={0}'.format(e))
                        error += 1
                        if handles_check(previous_window_count):
                            print('已关闭误开窗口')
                        try:
                            job_l2 = driver.find_element(By.XPATH, f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/div")
                            print('butten_text={0}'.format(job_list.text))
                            #random_wait()
                            xpath_wait(f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/div", timeout=3,type_in='clickable')
                            job_l2.click()

                            if handles_check(previous_window_count):
                                print('已关闭误开窗口')

                            xpath_wait_longer('//a[@class="default-btn cancel-btn"]')
                            break
                        except Exception as e:
                            print('click_error_two={0}'.format(e))
                            error += 1
                            continue
                if error > 5:
                    continue
                else:
                    count_num += 1
                    print('已投递{0}个职位'.format(count_num))

                    #关闭弹窗
                    guanbitanchuang = driver.find_element(By.XPATH, '//a[@class="default-btn cancel-btn"]')
                    guanbitanchuang.click()
    
                xpath_wait_longer('//div[@class="info-public"]')
    if page_count < 10 :
        while True: #翻页功能实现，有时不稳定
            try:
                if xpath_wait('//i[@class="ui-icon-arrow-right"]', timeout=10,type_in='clickable'):
                    scroll_to_element(driver, '//i[@class="ui-icon-arrow-right"]')
                    next_page = driver.find_element(By.XPATH, '//i[@class="ui-icon-arrow-right"]')    #点击下一页
                    next_page.click()
                    test_count = 0
                    while True:
                        if xpath_wait(f'//a[@ka="search_list_company_{count_company+1}_custompage"]',40):
                            page_count += 1
                            print('翻到第{0}页'.format(page_count))
                            break
                        else:
                            test_count += 1
                            scroll_to_element(driver, '//i[@class="ui-icon-arrow-right"]')
                            next_page = driver.find_element(By.XPATH, '//i[@class="ui-icon-arrow-right"]')
                            print('翻第{0}页失败，正在尝试第{1}次，次数过多可手动重新运行'.format(page_count+1,test_count))
                            next_page.click()
                    break
                else:
                    scroll_to_element(driver, '//i[@class="ui-icon-arrow-right"]')
                    continue
            except Exception as e:
                print('next_page_error={0}'.format(e))
                driver.execute_script("window.scrollTo(document.body.scrollWidth, 0);")
                continue
    else:
        driver.get(f'https://www.zhipin.com/web/geek/job?query={query}&city={city}&salary={sal}')
        print('从第一页开始获取职位信息')
        xpath_wait_longer('//div[@class="search-job-result"]')

        list = driver.find_elements(By.XPATH, '//div[@class="info-public"]') 
        count_company = 0
        page_count = 1


all_end_time = time.time()
all_elapsed_time = (all_end_time - all_start_time) * 1000  # 计算运行时间（毫秒）

print(f"100岗位投递完成,全部代码运行了{all_elapsed_time:.2f}毫秒")