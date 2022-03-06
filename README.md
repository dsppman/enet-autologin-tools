# Enet Autologin Tool [![License](http://img.shields.io/badge/license-mit-blue.svg?style=flat-square)](https://github.com/dsppman/enet-autologin-tools/blob/master/LICENSE)

一个简易的广东天翼校园宽带自动登录工具，可部署到docker配合openwrt食用～


### Required

- Python3
- pip (pip3)
- Tesseract

> 关于tesseract在windows怎么安装，可以参考这篇文章 [🔗链接直达](https://blog.csdn.net/u010454030/article/details/80515501)

## Installation
```shell
$ git clone https://github.com/dsppman/enet-autologin-tools.git
$ pip install requests rsa pytesseract
```

## How to run
```
options:
  -u, --username TEXT 校园网登录账号
  -p, --password TEXT 校园网登录密码
  -i, --intervals INT 检测是否登录间隔 默认10
  --userip TEXT 校园网的wlanuserip 默认自动获取
  --acip TEXT 校园网的wlanacip 默认自动获取
  --log-level TEXT 输出日志等级
  --log-output TEXT 日志保存路径
```

### Basic
```shell
$ cd enet-autologin-tools
$ python main.py -u [账号] -p [密码]
```

### Set Interval Time
```shell
$ cd enet-autologin-tools
$ python main.py -u [账号] -p [密码] -i 10
```

### Save Log
```shell
$ cd enet-autologin-tools
$ python main.py -u [账号] -p [密码] -log-output=$(pwd)/1.log
```

### Running on Docker
```shell
$ cd enet-autologin-tools
$ docker build -t cnet-docker .
$ docker run -d cnet-docker -u [账号] -p [密码]
```

## About
如果觉得能帮到你的话就给个Star🌟吧～