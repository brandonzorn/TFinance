FROM python:3.12.4-slim

RUN apt update

COPY ./requirements /requirements
RUN pip install -r requirements/prod.txt
RUN rm -rf requirements

COPY ./tfinance /tfinance/
WORKDIR /tfinance

CMD ["python", "main.py"]