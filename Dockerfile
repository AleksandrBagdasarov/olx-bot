# Use Python 3 with Alpine
FROM python:3-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run scraper.py when the container launches
CMD ["python3", "scraper.py"]