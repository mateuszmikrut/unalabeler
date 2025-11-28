FROM python:3.14-latest
WORKDIR /app
COPY *.py /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
