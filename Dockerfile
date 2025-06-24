FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY btc_data_tracking.py .

CMD ["python", "-u", "btc_data_tracking.py"]