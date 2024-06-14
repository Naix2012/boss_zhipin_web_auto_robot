# 简介
python萌新简单用selenium写了一个boss自动投递简历的python脚本，可以根据筛选条件自动投递符合需求的岗位，包括对公司名，职位名，薪资，期望地址和职位详情的筛选

# 启动前准备
## 需要安装Chrome以及ChromeDriver
ChromeDriver：https://developer.chrome.com/docs/chromedriver?hl=zh-cn
## 需要安装python以及一些库，我自己用的是python3.11.8
pip install selenium pypinyin
## 修改文件
修改chrome_open.bat里的chrome文件路径为自己的
修改auto_resume_submission_script_for_boss.py里上面的职务需求等自定义信息

# 启动流程

先打开chrome_open.bat，自己进入boss网站把账户登录一下，

然后就可以运行auto_resume_submission_script_for_boss.py了，

可能会偶尔有点小问题，还在调试中，脚本卡住或者报错就关了重新跑一下，可以把报错提到issue里

萌新的第一个完整功能的脚本，总之姑且能跑(

# 觉得好用的给萌新点个star吧，万分感谢
