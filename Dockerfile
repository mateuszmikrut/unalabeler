FROM python:3.14.0-slim
WORKDIR /app
COPY *.py /app/
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
