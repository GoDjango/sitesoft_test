FROM python:3.7-buster

RUN mkdir -pv /opt/habr_parser
WORKDIR /opt/habr_parser
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
