# Use official Python 3.12.2 runtime as a base image
FROM python:3.12.2

# Set environment variables to improve performance and debugging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files into the container
COPY . .

# Expose the application port
EXPOSE 8000

# Entrypoint script to allow multiple commands
ENTRYPOINT [ "sh", "-c" ]
CMD ["python manage.py migrate && \
      python manage.py create_groups && \
      python manage.py create_superuser && \
      python manage.py runserver 0.0.0.0:8000"]


      