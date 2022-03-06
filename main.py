import argparse
import logging
import signal
import sys
import time
from io import BytesIO
from urllib.parse import urlparse, parse_qsl

import pytesseract
import requests
import rsa
# import ddddocr
from PIL import Image


class CampusNet:
    Req = requests.Session()

    def __init__(self, username: str, password: str):
        self.wlan_user_ip = None
        self.wlan_ac_ip = None
        self.username = username
        self.password = password
        self.timeout = 2

    def needLogin(self):
        r = requests.get(url="http://www.baidu.com/", allow_redirects=False, timeout=self.timeout)
        times = r.elapsed.total_seconds()
        logging.info('network connection times=%s s' % times)
        need_login = 'location' in r.headers and 'enet.10000.gd.cn' in r.headers['location']
        if need_login and self.wlan_ac_ip is None and self.wlan_user_ip is None:
            enet_url = r.headers['location']
            enet_query = dict(parse_qsl(urlparse(enet_url).query))
            if 'wlanacip' in enet_query and 'wlanuserip' in enet_query:
                self.setWlanACIP(enet_query['wlanacip'])
                self.setWlanUserIP(enet_query['wlanuserip'])
                logging.info("wlan_user_ip=%s, wlan_user_ip=%s" % (enet_query['wlanacip'], enet_query['wlanuserip']))
            else:
                raise "Fail to get enet ip. Please set them manually. "
        return need_login

    def _encryptByRSA(self, message: str):
        e = "10001"
        n = "b2867727e19e1163cc084ea57b9fa8406a910c6703413fa7df96c1acdca7b983a262e005af35f9485d92cd4c622eca4a14d6fd818adca5cae73d9d228b4ef05d732b41fb85f80af578a150ebd9a2eb5ececb853372ca4731ca1c8686892987409be3247f9b26cae8e787d8c135fc0652ec0678a5eda0c3d95cc1741517c0c9c3"
        pubkey = rsa.PublicKey(e=int(e, 16), n=int(n, 16))
        result = rsa.encrypt(message.encode(), pubkey).hex()
        logging.info("RSA encrypt result=%s" % result)
        return result

    def getCodeImage(self):
        code_image_url = "http://enet.10000.gd.cn:10001/common/image_code.jsp?time=%d" % time.time() * 1000
        code_image = self.Req.get(url=code_image_url).content
        logging.info("code image byte length={}".format(len(code_image)))
        return code_image

    def setCodeByTesseract(self):
        image_obj = Image.open(BytesIO(self.getCodeImage()))
        result = pytesseract.image_to_string(image_obj).strip()
        logging.info("tesseract result={}".format(result))
        self.setCode(result)
        return result

    # def setCodeByDdddocr(self):
    #     ocr = ddddocr.DdddOcr()
    #     result = ocr.classification(self.getCodeImage())
    #     logging.info("ddddocr result=%s" % result)
    #     self.setCode(result)
    #     return result

    def login(self):
        login_url = "http://enet.10000.gd.cn:10001/ajax/login"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        data = '{"userName":"%s","password":"%s","rand":"%s"}' % (self.username, self.password, self.code)
        payload = {
            "loginKey": self._encryptByRSA(data),
            "wlanuserip": self.wlan_user_ip,
            "wlanacip": self.wlan_ac_ip
        }

        result = self.Req.post(url=login_url, data=payload, headers=headers).json()
        logging.info("login result={}".format(result))
        return result

    def setWlanUserIP(self, wlan_user_ip: str):
        self.wlan_user_ip = wlan_user_ip
        return self

    def setWlanACIP(self, wlan_ac_ip: str):
        self.wlan_ac_ip = wlan_ac_ip
        return self

    def setCode(self, code: str):
        self.code = code
        return self

    def setTimeout(self, timeout: int):
        self.timeout = timeout
        return self


def handle_args():
    parser = argparse.ArgumentParser(description='Campus Network Control.')
    parser.add_argument('-u', '--username', type=str, required=True, help='Set the username')
    parser.add_argument('-p', '--password', type=str, required=True, help='Set the password')
    parser.add_argument('-i', '--intervals', type=int, help='Set the network test intervals (s)', default=10)
    # parser.add_argument('-o', '--ocr', type=str, help='Set the ocr engine to use (tesseract, ddddocr)', default='tesseract')
    parser.add_argument('--userip', type=str, help='Set the wlan user ip')
    parser.add_argument('--acip', type=str, help='Set the wlan ac ip')
    parser.add_argument('--log-level', type=str, help='Set the logging level', default='info')
    parser.add_argument('--log-output', type=str, help='Set eht logging output')
    args = parser.parse_args()
    return args


def signal_exit(signum, frame):
    logging.info('CampusNetwork stopped.')
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_exit)
    signal.signal(signal.SIGTERM, signal_exit)
    try:
        args = handle_args()
        logging.basicConfig(
            filename=args.log_output,
            level=logging.getLevelName(args.log_level.upper()),
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")

        cnet = CampusNet(args.username, args.password)
        while True:
            if cnet.needLogin():
                # 获取验证码，如果没够四位则重新获取
                while True:
                    # code = None
                    code = cnet.setCodeByTesseract()
                    # if args.engine == 'tesseract':
                    #     code = cnet.setCodeByTesseract()
                    # elif args.engine == 'ddddocr':
                    #     code = cnet.setCodeByDdddocr()
                    # else:
                    #     raise 'Failed to set ocr engine.'
                    if len(code) != 4:
                        logging.info("The result doesn't seem to be right so that need to get it again")
                        continue
                    result = cnet.login()
                    if 'resultCode' in result:
                        ret_code = int(result['resultCode'])
                        if ret_code == 0:
                            logging.info('登录成功')
                            break
                        elif ret_code == 11063000:
                            continue
                    raise "login failed."
            time.sleep(args.intervals)

    except Exception as e:
        logging.error(e)
        sys.exit(2)
