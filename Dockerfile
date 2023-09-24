FROM python:3.8

WORKDIR /app

ADD techtrends .

RUN pip install --no-cache-dir -r requirements.txt && python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]
