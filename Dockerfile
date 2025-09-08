FROM python:3.11-slim

WORKDIR /app

# SQLite is included with Python, no additional dependencies needed

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

# Generate demo database during build
RUN python create_demo_db.py

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]