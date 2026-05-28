FROM python:3.13-alpine3.22 AS venv_builder

# Install system dependencies, including those for compiling lingo and Python dev files
RUN pip install --upgrade pip && pip install virtualenv && python -m venv /venv
RUN apk add --update --no-cache --virtual .tmp-build-deps git gcc g++ libc-dev make cmake python3-dev zlib-dev curl bash openjdk17-jre

# Install Lingua Franca compiler (lfc)
RUN curl -Ls https://install.lf-lang.org | bash -s cli

# ICE Frost dependencies
COPY requirements.txt /tmp/requirements.txt
RUN /venv/bin/pip install -r /tmp/requirements.txt

# Build the project
WORKDIR /tmp
COPY src /tmp/src
COPY frost /tmp/frost
RUN ~/.local/bin/lfc src/Main.lf

FROM python:3.13-alpine3.22

# Copy the generated source code
COPY --from=venv_builder /venv /venv
COPY --from=venv_builder /tmp/src-gen /app/src-gen

# Copy the configuration files and data models
COPY resources /app/resources

WORKDIR /app

ENTRYPOINT ["/venv/bin/python", "src-gen/Main/Main.py"]