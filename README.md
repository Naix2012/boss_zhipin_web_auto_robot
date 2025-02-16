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
启动脚本会自动安装python3.11.9到目录python下,但是不确定会不会有问题
建议自己安装一个python3.11,然后加入系统path
只要系统path里有python脚本就会自动用系统的创建虚拟环境

# 启动流程
运行start_all.bat即可,脚本会自动安装依赖,然后自动启动脚本
在弹出的ui里修改需要的地址,岗位信息等,改好了建议先点记录当前选项按钮,然后再点开始自动投递
暂停投递键会等脚本运行到某个节点才能停,没法立刻停止,如果你需要立刻停就点强制中止,不过需要重新扫码

可能会偶尔有点小问题，还在调试中，脚本卡住或者报错就关了重新跑一下，可以把报错提到issue里

总之姑且能跑(


