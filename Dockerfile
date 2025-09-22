FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    freetds-bin \
    tdsodbc \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configure FreeTDS for SQL Server connectivity
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so\n\
CPTimeout = \n\
CPReuse = \n\
FileUsage = 1" >> /etc/odbcinst.ini

# Configure FreeTDS TDS version and settings
RUN echo "[global]\n\
tds version = 7.1\n\
text size = 64512\n\
client charset = UTF-8" >> /etc/freetds/freetds.conf

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]