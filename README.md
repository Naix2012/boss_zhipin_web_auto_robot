# 简介
简单用selenium写了一个boss自动投递简历的python脚本，可以根据筛选条件自动投递符合需求的岗位，包括对公司名，职位名，薪资，期望地址和职位详情的筛选
目前仅支持win64位系统,其他的系统可能需要自行更改运行脚本代码

# 启动前准备

## 需要安装最新版Chrome
chrome:https://www.google.cn/chrome/?standalone=1&platform=win49

理论上只要电脑里装了最新版的chrome就可以直接运行start_all.bat
需要的东西会自动安装,但是网络差的话可能会有点慢
要自行安装的话再看后面

## 需要安装ChromeDriver(如果不是最新版的话需要自行下载对应版本的ChromeDriver.exe到目录chromedriver-win64下)
ChromeDriver：https://googlechromelabs.github.io/chrome-for-testing/

ChromeDriver下载对应版本,解压后将ChromeDriver.exe放在目录chromedriver-win64下
启动脚本有自动安装的代码,但是考虑到网络问题最好还是自己下载一下

## 安装python
启动脚本会自动安装嵌入版的python3.11.9到目录python下,但是自动下载的流程里pip模块下载的很慢
建议自己安装一个python3.11,然后从安装目录,一般是C:\Users\用户名\AppData\Local\Programs\Python\Python311里把所有文件复制到项目的python文件夹里
其他版本的我没试过,不知道会不会有bug

# 启动流程
运行start_all.bat即可,脚本会自动安装依赖,然后自动启动脚本
你将有60秒时间扫码登录boss直聘账号,然后脚本会自动投递符合筛选条件的简历
如果弹出验证界面就再手点一下
运行的时候点的不是太快的话应该不会出问题,每个步骤的随机等待时间可以在auto_resume_submission_script_for_boss.py里代码的random_wait()里修改,45行,目前是0-2s

# 修改筛选条件
职位薪资之类的在auto_resume_submission_script_for_boss.py里修改筛选条件即可
主要是最上面的city_choice,job_n,sal,low_sal,high_sal以及后面的三个黑名单,具体可以看#后面的代码注释
后面可能会试试看做成方便改的ui

可能会偶尔有点小问题，还在调试中，脚本卡住或者报错就关了重新跑一下，可以把报错提到issue里

总之姑且能跑(


