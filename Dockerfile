# Stage 1: Install Rust, build dependencies, and prepare the build environment
FROM python:3.12.2-slim AS builder

WORKDIR /code
RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential

# Install or upgrade pip and Poetry
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade poetry

# Disable Poetry virtualenv creation
RUN poetry config installer.max-workers 10
RUN poetry config virtualenvs.create false
#RUN poetry config installer.no-binary cryptography


# Copy the project files for dependency installation
COPY ./pyproject.toml ./poetry.lock /code/

# Install project dependencies using Poetry
RUN poetry install --no-interaction --no-ansi


# Stage 2: Runtime environment
FROM builder AS runtime
ENV PYTHONUNBUFFERED 1


ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create a dedicated user for running the application
RUN addgroup --system django && adduser --system --ingroup django djangouser

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=builder /code /app
COPY --from=builder /code/pyproject.toml /app/

# Copy the source code
COPY src /app/


# Change ownership to the dedicated user
RUN chown -R djangouser:django /app
#RUN  chown -R djangouser:django /app/static
#RUN chown -R djangouser:django /app/media
##
#RUN chmod -R 777 /app/static
#RUN chmod -R 777 /app/media


# Switch to the dedicated user
USER djangouser