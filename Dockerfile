FROM python:3

RUN mkdir /code
WORKDIR /code
ADD requirements.txt manage.py /code/
RUN pip install -r requirements.txt

COPY src /code/src

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
