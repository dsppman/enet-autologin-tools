FROM python:3-slim

WORKDIR /app

COPY ["main.py", "requirements.txt", "./"]
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requestments.txt \
    && rm -rf requestments.txt

ENTRYPOINT ["python3", "main.py"]
