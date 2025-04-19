
# Django Project with Docker and Minio

## Overview

This project is a Django application containerized using Docker. It integrates with PostgreSQL for database management and Minio for object storage. The environment is easily reproducible with Docker Compose, ensuring a seamless development experience.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

To get started with this project, clone the repository and set up the environment.

### Clone the Repository

```bash
git clone https://github.com/moeinnajafi1998/dms_sanaap.git
cd dms_sanaap
```

### Environment Variables

Create a `.env` file in the root directory of the project with the following environment variables:

```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
MINIO_ACCESS_KEY=your_minio_access_key
MINIO_SECRET_KEY=your_minio_secret_key
```

Replace the placeholders with your actual values.

## Docker Setup

### Docker Compose Configuration

This project includes a `docker-compose.yml` file, which defines the following services:

- **db**: A PostgreSQL 14 container.
- **minio**: A Minio container for object storage.
- **django**: The Django application container.

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    networks:
      - app-network

  minio:
    image: minio/minio:latest
    environment:
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
    command: server /data
    ports:
      - "9000:9000"
    volumes:
      - minio_data:/data
    networks:
      - app-network

  django:
    build: .
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - minio
    environment:
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_HOST: db
      DB_PORT: 5432
      MINIO_ENDPOINT: minio
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  minio_data:
```

This configuration will:

- Set up a PostgreSQL container with persistent storage.
- Set up a Minio container for object storage accessible at port `9000`.
- Build and run the Django application, ensuring it depends on the database and Minio containers.

### Dockerfile

The Dockerfile for the Django application container uses Python 3.12.2, installs dependencies, and runs migrations and other necessary commands before starting the server.

```dockerfile
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
CMD ["python manage.py migrate &&       python manage.py create_groups &&       python manage.py create_superuser &&       python manage.py runserver 0.0.0.0:8000"]
```

## Running the Application

With Docker Compose, you can easily start up the services.

### Build and Start the Services

To build the containers and start the services, run the following command:

```bash
docker-compose up --build
```

This will:

- Build the Django application container.
- Start PostgreSQL and Minio containers.
- Run migrations, create groups, and create a superuser automatically.
- Expose the Django application on port `8000`.

### Accessing the Application

Once the containers are up, access the Django application at:

```
http://localhost:8000
```

For Minio, access the web interface at:

```
http://localhost:9000
```

Use the `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY` from the `.env` file to log in.

## Stopping the Services

To stop the containers, run:

```bash
docker-compose down
```

This will stop and remove all containers, networks, and volumes defined in the `docker-compose.yml` file.

## Additional Commands

You can run Django management commands inside the `django` container as follows:

```bash
docker-compose exec django python manage.py <command>
```

For example, to run a custom management command:

```bash
docker-compose exec django python manage.py custom_command
```

## Contributing

We welcome contributions to this project! Please fork the repository and submit a pull request for any improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
