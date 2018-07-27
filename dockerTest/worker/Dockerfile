# Use an official Python runtime as a parent image
FROM tensorflow/tensorflow:1.9.0-py3

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt 

# Run app.py when the container launches
# CMD ["/app/redis-stable/src/redis-server", "--bind 127.0.0.1", "--port 6379"]
CMD ["python", "app.py", "60", "3", "512", "60"]

