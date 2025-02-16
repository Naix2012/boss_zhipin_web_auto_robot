import time
all_start_time = time.time()

#=====================单值类修改内容=====================
hot_city_list = ['全国','北京','上海','广州','深圳','杭州','天津','西安','苏州','武汉','厦门','长沙','成都','郑州','重庆','佛山','合肥','济南','青岛','南京','东莞','昆明','南昌','石家庄','宁波','福州']   #热门城市列表,不要改
city_choice = '全国'    #选择意向城市,最好从上面一行的内容里复制,其他城市也可以,但如果网页内没有可能报错
job_n = 'python'  #选择意向职位
sal_dic = {'3k-': 402,'3k-5k': 403,'5-10k': 404, '10-20k': 405, '20-50k': 406, '50k+': 407, '不限':000} #薪资对应字典,不要改
sal = sal_dic['不限'] #选择薪资范围,从上面一行的内容里复制,记得下面两项也要对应改,此项范围是修改网站搜索范围,下面两项是脚本检测过滤
low_sal = 3  #最低薪资要求,以千为单位
high_sal = 18  #最高薪资要求,以千为单位

#=====================多值类修改内容=====================

#公司名称黑名单,公司名称包含其中字符串则跳过
company_black_list_fr = ['输入排除公司名称','以逗号分隔']

#职位名称黑名单,职位名称包含其中字符串则跳过
jobname_black_list_fr = ['输入排除职务名称','以逗号分隔']

#职位详细信息黑名单,职位详细信息包含其中字符串则跳过
jobinfo_black_list_fr = ['输入排除职位详细信息关键词','以逗号分隔']


#=====================导入库=====================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import queue  # 新增队列模块
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
    # 配置 Chrome 参数
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    # 配置ChromeOptions指定Chrome路径
    #chrome_options.binary_location = r".\Chrome\Application\chrome.exe"  # 替换为实际路径

    # 创建Service对象指定Chromedriver路径
    chromedriver_service = Service(executable_path=r".\chromedriver-win64\chromedriver.exe")  # 替换为实际路径

    chrome_options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(service=chromedriver_service, options=chrome_options)   #创建一个新的webdriver实例
    return driver

def get_hotcitycodes_dict(city_name):  #获取城市编码(只有热门城市)
    log_out('开始获取热门城市编码')
    if os.path.exists('site.json'):
        with open('site.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        zp_data = data['zpData']['hotCitySites']
        for city in zp_data:
            if city["name"] == city_name:
                city_codes = city["code"] 
                return city_codes
        log_out('城市非热门城市，开始全表查询')
        raise KeyError
    else:
        log_out('site.json文件不存在')
        raise FileNotFoundError

def get_allcitycodes_dict(city_name):
    log_out('开始获取全部城市编码')
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
        log_out('未查询到城市编码,请更换城市')
        raise KeyError
    else:
        log_out('site.json文件不存在')
        raise FileNotFoundError

def xpath_wait(XPATH_in,driver, timeout=6,type_in='located'):  #等待元素加载完成或者可点击，超时返回False
    if type_in == 'located':    #寻址等待
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.presence_of_element_located((By.XPATH, XPATH_in)))
            log_out('{0}页面加载完成'.format(XPATH_in))
            return True
        except TimeoutException:
            log_out("{0}等待超时".format(XPATH_in))
            return False
    elif type_in == "clickable":    #可点击等待
        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_in)))
            log_out('{0}页面加载完成'.format(XPATH_in))
            return True
        except TimeoutException:
            log_out("{0}等待超时".format(XPATH_in))
            return False
    else:
        log_out('type_in参数错误,请输入located或者clickable')
        return False

def handles_check(previous_window_count, driver):   #误点击打开新页面解决方案
    if len(driver.window_handles) > previous_window_count:
        driver.switch_to.window(driver.window_handles[-1])  # 切换到新页面
        driver.close()  # 关闭新页面
        driver.switch_to.window(driver.window_handles[0])   # 切换回原来的页面
        return True
    else:
        return False

def xpath_wait_longer(XPATH_in, driver, timeout=6,type_in='located'): #循环等待元素加载完成
    start_time = time.time()
    loop_count = 0
    if XPATH_in != '//a[@class="default-btn cancel-btn"]':
        while True:
            loop_count += 1
            log_out(f"循环等待第{loop_count}次")
            if xpath_wait(XPATH_in,driver, timeout,type_in=type_in):
                end_time = time.time()
                elapsed_time = (end_time - start_time) * 1000  # 计算运行时间（毫秒）
                log_out(f"循环等待完成，共循环{loop_count}次，{XPATH_in}代码运行了{elapsed_time:.2f}毫秒")
                break
            else:
                continue
    else:
        while True:
            loop_count += 1
            log_out(f"循环等待第{loop_count}次")
            if loop_count < 3:
                if xpath_wait(XPATH_in, driver, timeout,type_in=type_in):
                    end_time = time.time()
                    elapsed_time = (end_time - start_time) * 1000  # 计算运行时间（毫秒）
                    log_out(f"循环等待完成，共循环{loop_count}次，{XPATH_in}代码运行了{elapsed_time:.2f}毫秒")
                    break
                else:
                    continue
            else:
                if xpath_wait('//a[@class="default-btn sure-btn"]', driver, timeout,type_in='clickable'):
                    if driver.find_element(By.XPATH, '//div[@class="chat-block-header"]/h3').text == '无法进行沟通':
                        log_out('投递已达上限，程序结束')
                        sys.exit()
                    window_count = len(driver.window_handles)
                    click = driver.find_element(By.XPATH, '//a[@class="default-btn sure-btn"]')
                    click.click()
                    try_self_cont = 0
                    try_click_cont = 0
                    while True:
                        if handles_check(window_count, driver):
                            log_out('已关闭个人中心窗口')
                            break
                        else:
                            log_out('等待个人中心窗口出现')
                            if xpath_wait('//a[@class="default-btn sure-btn"]', driver, type_in='clickable'):
                                try_click_cont += 1
                                log_out('按钮可点击,尝试点击,尝试第',try_click_cont,'次')
                                scroll_to_element(driver, '//a[@class="default-btn sure-btn"]')
                                click = driver.find_element(By.XPATH, '//a[@class="default-btn sure-btn"]')
                                click.click()
                                continue
                            else:
                                try_self_cont += 1
                                log_out('等待个人中心窗口出现失败，尝试次数：',try_self_cont)
                                continue
                    end_time = time.time()
                    elapsed_time = (end_time - start_time) * 1000  # 计算运行时间（毫秒）
                    log_out(f"错误投递关闭完成，{XPATH_in}代码运行了{elapsed_time:.2f}毫秒")
                    break
                else:
                    log_out('点击事件可能出错，请手动重置')
                    loop_count =1
                    continue

def company_black_list(company_name,company_black_list_fr=company_black_list_fr):   #公司黑名单
    for i in company_black_list_fr: #判断公司是否在黑名单中
        if i in company_name:
            log_out('公司在黑名单中')
            return True
    return False

def jobinfo_black_list(job_info,jobinfo_black_list_fr=jobinfo_black_list_fr):   #职位内容黑名单
    job_info_lower = job_info.lower()
    for i in jobinfo_black_list_fr: 
        if i in job_info_lower:
            log_out('职位内容不符')
            return True
    return False

def jobname_black_list(job_name,jobname_black_list_fr=jobname_black_list_fr):   #职位黑名单
    job_name_lower = job_name.lower()
    for i in jobname_black_list_fr: 
        if i in job_name_lower:
            log_out('职位名不符')
            return True
    return False

def scroll_to_element(driver, xpath):   #将指定元素滚动到窗口中心区域
    xpath_wait_longer(xpath, driver, )
    element = driver.find_element(By.XPATH, xpath)    # 获取指定元素的坐标
    x = element.location['x']
    y = element.location['y']
    center_x = driver.execute_script("return window.innerWidth / 2;")    # 计算浏览器窗口中心位置的坐标
    center_y = driver.execute_script("return window.innerHeight / 2;")
    delta_x = x - center_x    # 计算需要滚动的距离
    delta_y = y - center_y
    log_out('{6}元素位置为:({0}, {1}),浏览器窗口中心坐标为({2},{3}),滚动距离为:({4}, {5})'.format(x, y, center_x, center_y, delta_x, delta_y,xpath))
    driver.execute_script(f"window.scrollBy({delta_x}, {delta_y});")    # 滚动页面
    xpath_wait_longer(xpath, driver)
    
def extract_salary_range(salary_str):
    pattern = r'(\d+)-(\d+)K'
    match = re.search(pattern, salary_str)
    if match:
        lower_bound = int(match.group(1))
        upper_bound = int(match.group(2))
        return lower_bound, upper_bound
    else:
        return None

def star_log_in():

    driver = chrome_setup()
    driver.get("https://www.zhipin.com")

    try:
        # 点击登录按钮
        xpath_wait('//*[@id="header"]/div[1]/div[4]/div/a', driver, type_in='clickable')
        login_btn = driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div[4]/div/a')
        login_btn.click()

        # 切换扫码登录
        xpath_wait('//*[@id="wrap"]/div/div[2]/div[2]/div[1]', driver, type_in='clickable')
        switch_tab = driver.find_element(By.XPATH, '//*[@id="wrap"]/div/div[2]/div[2]/div[1]')
        switch_tab.click()

        # 等待扫码完成
        #wait = WebDriverWait(driver, 60)
        #wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="header"]/div[1]/div[1]/a')))
        #log_out("登录成功！")

    except Exception as e:
        log_out(f"操作失败: {str(e)}")
        return
    return driver

def main_part(
        driver,
        values,
        stop_event,
        city_choice_in,
        job_n_in,
        sal_in,
        low_sal_in,
        high_sal_in,
        company_black,
        jobname_black,
        jobinfo_black
        ):

    company_black=company_black.split(',')
    jobname_black=jobname_black.split(',')
    jobinfo_black=jobinfo_black.split(',')

    if city_choice_in in hot_city_list:
        city = get_hotcitycodes_dict(city_choice_in)
    else:
        city = get_allcitycodes_dict(city_choice_in)

    query = parse.quote(job_n_in)

    if sal_in == 000:
        driver.get(f'https://www.zhipin.com/web/geek/job?query={query}&city={city}')
    else:
        driver.get(f'https://www.zhipin.com/web/geek/job?query={query}&city={city}&salary={sal_in}')
    log_out('开始获取职位信息')

    if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

    xpath_wait_longer('//div[@class="search-job-result"]', driver)

    if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

    list = driver.find_elements(By.XPATH, '//div[@class="info-public"]')    #获取职位


    count_num = 0
    count_company = 0
    page_count = 1

    while count_num < 101:  #每天投递上限100个
        for i in range(1,31):  #遍历点击职位列表
            if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止
            count_company += 1
            temp_count = 0
            while temp_count<3:
                if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止
                try:
                    if xpath_wait(f'//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a', driver):
                        log_out('已找到//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a')
                        break
                    else:
                        if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止
                        temp_count += 1
                        log_out('无法获取职位信息，尝试重新获取,temp_count={0}'.format(temp_count))
                        continue
                except:
                    if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止
                    temp_count += 1
                    log_out('无法获取职位信息，尝试重新获取,temp_count={0}'.format(temp_count))
                    continue
            if temp_count >= 3:
                log_out('职位{0}无法获取,跳过'.format(f'//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a'))
                continue
            company_name = driver.find_element(By.XPATH, f'//li[@ka="search_list_{count_company}"]/div[1]/div/div[2]/h3/a').text   #读取公司名
            log_out('第{0}个公司是{1}'.format(count_company, company_name))
            if count_company%30 == 0 or (count_company+1)%30 == 0 or (count_company+2)%30 == 0:  #最后三个经常识别不出，先跳过
                continue
            if company_black_list(company_name,company_black):    #判断公司是否在黑名单中
                log_out('公司{0}在黑名单中,跳过'.format(company_name))
                random_wait()
                continue
            else:
                job_name = driver.find_element(By.XPATH, f'//li[@ka="search_list_{count_company}"]/div[1]/a/div/span[1]')
                log_out('job_name={0}'.format(job_name.text))

                if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                if jobname_black_list(job_name.text,jobname_black):    #判断职位是否在黑名单中
                    log_out('职位{0}在黑名单中,跳过'.format(job_name.text))
                    random_wait()
                    continue

                job_sal = driver.find_element(By.XPATH, f'//li[@ka="search_list_{count_company}"]/div[1]/a/div[2]/span').text
                log_out('job_sal={0}'.format(job_sal))
                result = extract_salary_range(job_sal)
                if result:
                    lower_bound, upper_bound = result
                    log_out('薪资范围是{0}到{1}'.format(lower_bound, upper_bound))
                else:
                    log_out('无法识别数字格式的薪资范围,跳过')
                    continue
                if upper_bound < int(low_sal_in) or lower_bound > int(high_sal_in):
                    log_out('薪资范围不在指定范围内,跳过')
                    random_wait()
                    continue

                if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                try_count = 0
                while True: #由于模拟鼠标的不稳定性，读取职务详细信息将进行多次尝试

                    if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                    if try_count > 3:
                        log_out('尝试次数过3,退出info查找,跳过此职务')
                        break
                    try_count += 1
                    log_out('职位info查询尝试次数{0}'.format(try_count))
                    scroll_to_element(driver, f'//li[@ka="search_list_{count_company}"]')
                    ActionChains(driver).move_to_element(job_name).perform()
                    if xpath_wait('//div[@class="job-detail-card"]', driver,3):
                        break  # 如果成功找到元素,跳出循环
                    else:
                        continue
                if try_count > 3:
                    continue

                job_detail = driver.find_element(By.XPATH, '//div[@class="job-detail-card"]')   #读取职位详细信息
                job_info = job_detail.find_element(By.XPATH, './/div[@class="job-detail-body"]').text

                mouse_out = driver.find_element(By.XPATH, '//ul[@class="tag-list"]')    #把鼠标移出到标签栏避免详细信息的元素重叠
                log_out("job_info={0}".format(job_info))
                ActionChains(driver).move_to_element(mouse_out).perform()
                previous_window_count = len(driver.window_handles)  # 记录点击前的窗口句柄数量，防止误点击打开新窗口

                if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                if jobinfo_black_list(job_info,jobinfo_black):
                    log_out('职位{0}的详细信息在黑名单中,跳过'.format(job_name.text))
                    random_wait()
                    continue
                else:
                    error = 0
                    while True: #可点击元素在模拟鼠标悬停时会变化，由于模拟鼠标的不稳定性将进行多次尝试

                        if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                        if error > 5:
                            log_out('超过5次按钮错误,此次投递不计算,跳过')
                            break
                        try:
                            scroll_to_element(driver, f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/div")
                            log_out('count_company={0}'.format(count_company))
                            job_list = driver.find_element(By.XPATH, f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/a") #定位到hr
                            log_out('butten_text={0}'.format(job_list.text))
                            #random_wait()
                            xpath_wait(f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/a", driver, timeout=3,type_in='clickable')
                            job_list.click()    #点击立即沟通

                            if handles_check(previous_window_count, driver):
                                log_out('已关闭误开窗口')
                                continue

                            if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                            xpath_wait_longer('//a[@class="default-btn cancel-btn"]', driver)
                            break
                        except Exception as e:

                            if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                            log_out('click_error_one={0}'.format(e))
                            error += 1
                            if handles_check(previous_window_count, driver):
                                log_out('已关闭误开窗口')
                            try:
                                job_l2 = driver.find_element(By.XPATH, f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/div")
                                log_out('butten_text={0}'.format(job_list.text))
                                #random_wait()
                                xpath_wait(f"//li[@ka='search_list_{count_company}']/div[1]/a/div[2]/div", driver, timeout=3,type_in='clickable')
                                job_l2.click()

                                if handles_check(previous_window_count, driver):
                                    log_out('已关闭误开窗口')

                                xpath_wait_longer('//a[@class="default-btn cancel-btn"]', driver)
                                break
                            except Exception as e:

                                if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                                log_out('click_error_two={0}'.format(e))
                                error += 1
                                continue
                    if error > 5:
                        continue
                    else:

                        if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                        count_num += 1
                        log_out('已投递{0}个职位'.format(count_num))

                        #关闭弹窗
                        guanbitanchuang = driver.find_element(By.XPATH, '//a[@class="default-btn cancel-btn"]')
                        guanbitanchuang.click()

                    xpath_wait_longer('//div[@class="info-public"]', driver)
        if page_count < 10 :
            while True: #翻页功能实现，有时不稳定

                if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                try:
                    if xpath_wait('//i[@class="ui-icon-arrow-right"]', driver, timeout=10,type_in='clickable'):
                        scroll_to_element(driver, '//i[@class="ui-icon-arrow-right"]')
                        next_page = driver.find_element(By.XPATH, '//i[@class="ui-icon-arrow-right"]')    #点击下一页
                        next_page.click()
                        test_count = 0
                        while True:

                            if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

                            if xpath_wait(f'//a[@ka="search_list_company_{count_company+1}_custompage"]', driver,40):
                                page_count += 1
                                log_out('翻到第{0}页'.format(page_count))
                                break
                            else:
                                test_count += 1
                                scroll_to_element(driver, '//i[@class="ui-icon-arrow-right"]')
                                next_page = driver.find_element(By.XPATH, '//i[@class="ui-icon-arrow-right"]')
                                log_out('翻第{0}页失败，正在尝试第{1}次，次数过多可手动重新运行'.format(page_count+1,test_count))
                                next_page.click()
                        break
                    else:
                        scroll_to_element(driver, '//i[@class="ui-icon-arrow-right"]')
                        continue
                except Exception as e:
                    log_out('next_page_error={0}'.format(e))
                    driver.execute_script("window.scrollTo(document.body.scrollWidth, 0);")
                    continue
        else:

            if stop_event.is_set(): log_out('中止进程'); return  # 检查是否需要停止

            driver.get(f'https://www.zhipin.com/web/geek/job?query={query}&city={city}&salary={sal}')
            log_out('从第一页开始获取职位信息')
            xpath_wait_longer('//div[@class="search-job-result"]', driver)

            list = driver.find_elements(By.XPATH, '//div[@class="info-public"]')
            count_company = 0
            page_count = 1


    all_end_time = time.time()
    all_elapsed_time = (all_end_time - all_start_time) * 1000  # 计算运行时间（毫秒）

    log_out(f"100岗位投递完成,全部代码运行了{all_elapsed_time:.2f}毫秒")

# 历史记录文件路径
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'search_history.json')
data_name = {
    "city_choice": "意向城市",
    "job_n": "意向职位",
    "sal": "薪资范围",
    "low_sal": "最低薪资",
    "high_sal": "最高薪资",
    "company_black": "公司名称黑名单",
    "jobname_black": "职位名称黑名单",
    "jobinfo_black": "职位详细信息黑名单"
}

def load_history():
    """加载历史记录（自动创建文件）"""
    default_data = {
        "city_choice": "全国",
        "job_n": "python",
        "sal": "不限",
        "low_sal": "3",
        "high_sal": "18",
        "company_black": "输入排除公司名称,以逗号分割",
        "jobname_black": "输入排除职务名称,以逗号分割",
        "jobinfo_black": "输入排除职位详细信息关键词,以逗号分割"
    }
    try:
        # 如果文件不存在则创建
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            return default_data

        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_out(f"历史记录初始化失败：{str(e)}")
        return default_data


def save_history(values):
    """保存历史记录（确保文件存在）"""
    try:
        # 自动创建父目录（如果需要）
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

        data = {key: values[key] for key in data_name}
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, "配置保存成功"
    except Exception as e:
        return False, f"保存失败：{str(e)}"

def save_data(values_in):
    # 检查是否缺少必填选项
    for k, v in data_name.items():
        new_text_in = values_in[k].strip()
        if not new_text_in and k not in ("company_black", "jobname_black", "jobinfo_black"):
            sg.popup_error('缺少' + v)
            continue

    # 执行保存操作
    success, msg = save_history(values_in)  # 保存本次搜索内容

    log_out(msg)  # 记录日志

    # 失败时弹出错误提示
    if not success:
        sg.popup_error(msg)

def log_out(msg_in):
    # 生成带时间戳的日志
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg_in}\n"

    # 更新日志显示（使用更高效的print方式）
    window['-LOG-'].print(log_msg, end='')

#====================启动ui=======================
import PySimpleGUI as sg
import threading
import datetime

# 创建界面布局时加载历史记录
history = load_history()
layout = [
    [sg.Text("意向城市(可以任意输入,但网页中不存在的话会报错)")],
    [
        sg.Input(default_text=history["city_choice"], key="city_choice",size=(20, 1)),
        sg.Listbox(  # 选项列表框
            hot_city_list,
            size=(20, 5),
            key='-CITY_LIST-',
            enable_events=True,
            background_color='white',
            text_color='black'
        )
     ],
    [sg.Text("意向职位(任意输入)")],
    [sg.Input(default_text=history["job_n"], key="job_n",size=(44, 1))],
    [sg.Text("薪资范围(请在右侧下拉框选择,用于网页内筛选条件,优先度高)")],
    [
        sg.Input(default_text=history["sal"], key="sal",size=(20,1), disabled=True),
        sg.Combo(
            list(sal_dic.keys()),
            default_value='不限',  # 默认选中项
            readonly=True,        # 禁止编辑
            enable_events=True,
            key='-SALARY_COMBO-',
            size=(20,1)
        )
    ],
    [sg.Text("最低薪资(单位:k,非负整数,用于脚本内筛选条件,不满足的自动跳过)")],
    [sg.Input(default_text=history["low_sal"], key="low_sal",size=(20, 1))],
    [sg.Text("最高薪资(单位:k,非负整数,用于脚本内筛选条件,不满足的自动跳过)")],
    [sg.Input(default_text=history["high_sal"], key="high_sal",size=(20, 1))],
    [sg.Text("以下黑名单设置均填入需要屏蔽的关键词,多个词之间以逗号分割,会自动避开包含对应字符串的职位")],
    [sg.Text("公司名称黑名单")],
    [sg.Multiline(default_text=history["company_black"], key="company_black", size=(60,3), expand_x=True,expand_y=True)],
    [sg.Text("职位名称黑名单")],
    [sg.Multiline(default_text=history["jobname_black"], key="jobname_black", size=(60,3), expand_x=True,expand_y=True)],
    [sg.Text("职位详细信息黑名单")],
    [sg.Multiline(default_text=history["jobinfo_black"], key="jobinfo_black", size=(60,3), expand_x=True,expand_y=True)],
    [
        sg.Button("扫码登录", key="-SCAN-"),
        sg.Button("开始自动投递(先登录)", key="-START-", disabled=True),
        sg.Button("暂停投递(用于改设置)", key="-PAUSE-", disabled=True),
        sg.Button("强制中止(重新扫码登录)", key="-STOP-", disabled=True),
        sg.Button("记录当前选项(开始投递时也会自动保存)", key="-SAVE-"),
        sg.Exit()
    ],
    [sg.Multiline(size=(60,5), key="-LOG-", autoscroll=True,disabled=True, background_color='#F0F0F0', expand_x=True,expand_y=True)]
]
sg.theme('bluemono')
window = sg.Window("全自动简历投递", layout)


# 控制变量和通信队列
worker_thread = None
command_queue = queue.Queue()  # 用于线程间通信的队列
driver_lock = threading.Lock()  # 用于线程安全操作
stop_flag = threading.Event()

while True:
    event, values = window.read()  # 设置超时以便后台处理(timeout=1000)

    # 定义窗口关闭事件
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    # 城市列表选择事件
    elif event == '-CITY_LIST-':
        if values['-CITY_LIST-']:  # 确保有选中项
            window['city_choice'].update(values['-CITY_LIST-'][0])  # 更新输入框

    # 薪资下拉框选择事件
    elif event == '-SALARY_COMBO-':
        selected_salary = values['-SALARY_COMBO-']
        window['sal'].update(selected_salary)

    elif event == "-SCAN-":
        window["-SCAN-"].update(disabled=True)
        window["-START-"].update(disabled=False)
        window["-STOP-"].update(disabled=False)
        driver_s = star_log_in()

    elif event == "-START-":
        save_data(values)

        if worker_thread and worker_thread.is_alive():
            stop_flag.set()
            worker_thread.join()

        stop_flag.clear()

        window["-START-"].update(disabled=True)
        window["-PAUSE-"].update(disabled=False)
        worker_thread = threading.Thread(
            target=main_part,
            args=(
                driver_s,
                values,
                stop_flag,
                values['city_choice'],
                values['job_n'],
                values['sal'],
                values['low_sal'],
                values['high_sal'],
                values['company_black'],
                values['jobname_black'],
                values['jobinfo_black']
            ),
            daemon=True
        )
        worker_thread.start()

    elif event == "-PAUSE-":
        window["-START-"].update(disabled=False)
        window["-PAUSE-"].update(disabled=True)
        if worker_thread and worker_thread.is_alive():
            stop_flag.set()

    elif event == "-STOP-":
        window["-SCAN-"].update(disabled=False)
        window["-PAUSE-"].update(disabled=True)
        stop_flag.set()
        if driver_s:
            try:
                driver_s.quit()
                log_out("! 浏览器实例已被强制关闭 !")
            except Exception as e:
                log_out(f"强制关闭异常: {str(e)}")

        if worker_thread and worker_thread.is_alive():
            worker_thread.join(0.5)
            if worker_thread.is_alive():
                log_out("警告：线程未正常退出！")
            else:
                log_out("线程已终止")

    elif event == "-SAVE-":
        save_thread = threading.Thread(
            target=save_data,
            args=(values,),
            daemon=True
        )
        save_thread.start()

# 清理资源
if worker_thread and worker_thread.is_alive():
    stop_flag.set()
    worker_thread.join()

window.close()