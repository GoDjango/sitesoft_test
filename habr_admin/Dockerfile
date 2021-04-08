FROM python:3.7-buster

RUN apt -y update && \
    apt -y install postgresql-client

RUN mkdir -pv /opt/habr_admin
WORKDIR /opt/habr_admin
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
