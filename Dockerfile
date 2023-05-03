FROM python:3.8-slim-buster

RUN pip install fastapi
RUN pip install "uvicorn[standard]"

COPY ./src /src

CMD [ "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port",  "8000"]