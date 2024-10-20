FROM python:latest

WORKDIR /app 

COPY requirements.txt .

RUN pip install -r requirements.txt 
RUN python3 -m spacy download en_core_web_sm

COPY extract.py .
COPY transform.py .
COPY load.py .
COPY pipeline.py .

CMD ["python", "pipeline.py"]