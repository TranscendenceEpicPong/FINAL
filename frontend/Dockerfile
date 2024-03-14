FROM node:20.8.1 as builder

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN npm install
RUN npx webpack build

RUN mkdir /app/dist/assets
COPY ./src/assets/ /app/dist/assets/


FROM nginx:1.25
COPY --from=builder /app/dist/ /usr/share/nginx/html

RUN mkdir -p /etc/nginx/ssl
RUN openssl req -x509 -nodes \
        -out /etc/nginx/ssl/42trans.crt \
        -keyout /etc/nginx/ssl/42trans.key \
        -subj "/C=CH/ST=Vaud/L=Lausanne/O=42/OU=42/CN=*.42lausanne.ch/emailAddress=transcendence@42.fr"

COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/self-signed.conf /etc/nginx/snippets/self-signed.conf
COPY ./nginx/ssl-params.conf /etc/nginx/snippets/ssl-params.conf