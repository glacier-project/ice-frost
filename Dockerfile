FROM python:3.13-alpine3.22 AS venv_builder

COPY src /tmp/src
COPY frost /tmp/frost

# Install system dependencies, including those for compiling lingo and Python dev files
RUN pip install --upgrade pip && pip install virtualenv && python -m venv /venv
RUN apk add --update --no-cache --virtual .tmp-build-deps git gcc g++ libc-dev make cmake python3-dev zlib-dev curl bash openjdk17-jre

# Install Lingua Franca compiler (lfc)
RUN curl -Ls https://install.lf-lang.org | bash -s cli

# Frost dependencies
RUN /venv/bin/pip install git+https://github.com/esd-univr/machine-data-model.git
RUN /venv/bin/pip install typing-extensions

# Build the project
WORKDIR /tmp
RUN ~/.local/bin/lfc src/Main.lf

FROM python:3.13-alpine3.22

# Copy the generated source code
COPY --from=venv_builder /venv /venv
COPY --from=venv_builder /tmp/src-gen /app/src-gen

# Copy the configuration files and data models
COPY --from=venv_builder /tmp/src/ /app/src/

WORKDIR /app

ENTRYPOINT ["/venv/bin/python", "src-gen/Main/Main.py"]