# Dockerfile
FROM python:3.11-slim

# set workdir
WORKDIR /usr/src/app

# copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# copy and make startup script executable
RUN chmod +x ./wait_for_db_and_run.sh

# expose port and run (startup script waits for DB)
EXPOSE 8000
CMD ["./wait_for_db_and_run.sh"]
