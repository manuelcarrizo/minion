FROM python:3-slim

RUN mkdir /code
WORKDIR /code
ADD requirements.txt manage.py /code/
RUN pip install -r requirements.txt

COPY src /code/src

RUN apt-get update && apt-get install -y git && apt-get clean
RUN python manage.py makemigrations && python manage.py migrate

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
