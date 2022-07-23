FROM python:3.8

WORKDIR /techtrends

COPY techtrends/ ./

RUN pip3 install -r requirements.txt && python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]
