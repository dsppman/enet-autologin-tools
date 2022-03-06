FROM python:3-slim

WORKDIR /app

COPY main.py .
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
RUN pip install --no-cache-dir requests rsa pytesseract ddddocr -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["python3", "main.py"]
