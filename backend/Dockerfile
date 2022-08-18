FROM python:3.8-slim
# ARM64 (apple m1) bug mitigation
RUN apt-get update && apt-get -y install g++ libpq-dev gcc unixodbc unixodbc-dev

WORKDIR /app
COPY ./ ./

RUN pip3 install --upgrade pip --no-cache-dir
RUN pip3 install --upgrade setuptools --no-cache-dir
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]