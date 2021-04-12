FROM python:3.8-slim-buster

# Set display port to avoid crash
ENV DISPLAY=:99

# Set Poetry environment variables
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.10

# Install the latest versions of Mozilla Firefox and Geckodriver
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update \
  && apt-get install --no-install-recommends --no-install-suggests --assume-yes \
    curl \
    bzip2 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    xvfb \
  && FIREFOX_DOWNLOAD_URL='https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64' \
  && curl -sL "$FIREFOX_DOWNLOAD_URL" | tar -xj -C /opt \
  && ln -s /opt/firefox/firefox /usr/local/bin/ \
  && BASE_URL='https://github.com/mozilla/geckodriver/releases/download' \
  && VERSION=$(curl -sL 'https://api.github.com/repos/mozilla/geckodriver/releases/latest' | grep tag_name | cut -d '"' -f 4) \
  && curl -sL "${BASE_URL}/${VERSION}/geckodriver-${VERSION}-linux64.tar.gz" | tar -xz -C /usr/local/bin \
  && apt-get purge -y \
    curl \
    bzip2 \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /tmp/* /usr/share/doc/* /var/cache/* /var/lib/apt/lists/* /var/tmp/*

# Create working directory
WORKDIR /myapp

# System dependencies
RUN pip install "poetry==$POETRY_VERSION"

# Copy Poetry requirements to cache them in Docker layer
COPY poetry.lock pyproject.toml /myapp/

# Project initialization
RUN poetry config virtualenvs.create false \
    && poetry install

# Copy files to image
COPY . .

# Expose Flask
EXPOSE 8080

ENV DB_USER "<user>"
ENV DB_PASS "<password>"
ENV DB_NAME "<db name>"
ENV SQL_HOST "<database IP>"
ENV DB_PORT "<db port>"

CMD [ "python", "./src/scraper.py" ]
