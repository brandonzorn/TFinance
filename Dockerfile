FROM python:3.13.2-slim

COPY ./requirements /requirements
RUN pip install -r requirements/prod.txt
RUN rm -rf requirements

COPY ./tfinance /tfinance/
WORKDIR /tfinance

CMD ["python", "main.py"]