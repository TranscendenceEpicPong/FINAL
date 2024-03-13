FROM python:3.12.1

RUN pip install pipenv
RUN apt-get update -y && apt-get install -y --no-install-recommends gcc

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --deploy --system

RUN 
RUN mkdir /app
WORKDIR /app

COPY . .

EXPOSE 8000


COPY ./entrypoint.sh /tmp/entrypoint.sh
RUN chmod +x /tmp/entrypoint.sh
ENTRYPOINT [ "sh" , "/tmp/entrypoint.sh"]