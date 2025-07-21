FROM python:3.10-slim
WORKDIR /app/app.py
COPY req.txt ./
RUN pip install --no-cache-dir -r req.txt
COPY . .
CMD ["flask", "run", "--host=0.0.0.0", "--port=5004"] 