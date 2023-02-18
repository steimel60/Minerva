FROM python:alpine3.16
WORKDIR /app
COPY config.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/sqlite sqlite/
COPY src/api api/
CMD ["gunicorn", "--bind", "0.0.0.0:3005", "api:factory(\"config.toml\")"]
EXPOSE 3005

