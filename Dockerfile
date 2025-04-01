FROM python:3.10-slim

# Install tesseract-ocr system package
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy your code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Streamlit default port
EXPOSE 10000

# Start Streamlit when the container runs
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
