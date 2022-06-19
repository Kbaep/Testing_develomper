FROM python:3.8-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

# Устанавливаем зависимости для Postgre
RUN apk update & apk add gcc python3-dev musl-dev libffi-dev
# Устанавливаем библиотеки
COPY requirements.txt /usr/src/app/
RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install -r requirements.txt

COPY . /usr/src/app/

ENTRYPOINT ["/bin/sh", "-c" , "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]