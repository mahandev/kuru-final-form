FROM python:3.10-bookworm
# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set the application directory
ENV APP_HOME /back-end
WORKDIR $APP_HOME

# Copy the application code into the container
COPY . ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
