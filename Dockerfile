FROM python:3.6
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app
CMD [ "python", "./run.py"]
