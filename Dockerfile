FROM python:3.11-slim

# Make Python faster and quieter in containers
# to make python code run fast, no cache .pyc file and also should show python logs for debugging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set working directory
WORKDIR /app

# Upgrade pip first (helps with manylinux wheels)
# to install the latest version of pip without using cache
RUN pip install --no-cache-dir --upgrade pip

# Leverage Docker layer cache: install deps first
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the app
COPY . /app

# Ensure vector store dir exists and can be mounted for persistence
# we are creating a directory named chroma_db inside the /app directory in the Docker container.
# volume means if data will be stored in that directory and if docker container restarted again the data will persist
RUN mkdir -p /app/chroma_db
VOLUME ["/app/chroma_db"]

# Streamlit port (common for streamlit apps)
EXPOSE 8501

# Start the app (to run streamlit app on all network interfaces inside the container)
CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]