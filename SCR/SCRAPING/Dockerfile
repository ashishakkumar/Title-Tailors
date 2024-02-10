FROM python:3.11-slim-buster 
 # Base image with Python 3.11 (adjust as needed)

# WORKDIR /app  
# Set working directory inside container

COPY . .
# Copy project files to the container's working directory

RUN pip install --no-cache-dir -r requirements.txt  
# Install dependencies (if any)

# Make a directory to store the data file
RUN mkdir -p /app

CMD ["python", "Extraction_file.py"]
  # Command to run the Python script
