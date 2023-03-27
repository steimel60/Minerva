FROM python:alpine3.16
WORKDIR /app
COPY config.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/db db/
COPY src/api api/
COPY tests/populate_tables.sql .

# below is for debug purposes only, remove for prod
RUN apk update && apk upgrade
RUN apk add --no-cache sqlite
###################################################

CMD ["gunicorn", "--bind", "0.0.0.0:3005", "api:factory(\"config.toml\")"]
EXPOSE 3005

