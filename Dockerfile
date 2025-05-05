FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD parking .
EXPOSE 5000
ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "manage:app", "--timeout=600"]
