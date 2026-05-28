# Use an official Ubuntu image as a base
FROM ubuntu:22.04

# Set non-interactive frontend to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies, including those for compiling lingo and Python dev files
# ADDED: python3-dev for C/C++ projects that link against Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    git \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    pkg-config \
    libssl-dev && \
    # Clean up apt cache to reduce image size
    rm -rf /var/lib/apt/lists/*

# Install Lingua Franca compiler (lfc)
RUN curl -Ls https://install.lf-lang.org | bash -s cli

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Install Poetry
RUN pip3 install poetry

# Configure the environment PATH to include all newly installed binaries
ENV PATH="/root/.lf/bin:/root/.cargo/bin:/root/.local/bin:${PATH}"

# Clone the Lingo repository, build and install it using cargo, then clean up.
RUN git clone https://github.com/lf-lang/lingo.git /tmp/lingo && \
    cd /tmp/lingo && \
    cargo install --path . && \
    cd / && \
    rm -rf /tmp/lingo

# Build and install the 'machine-data-model' library from source.
RUN git clone https://github.com/esd-univr/machine-data-model.git /tmp/machine-data-model && \
    cd /tmp/machine-data-model && \
    poetry build && \
    pip3 install dist/*.whl && \
    cd / && \
    rm -rf /tmp/machine-data-model

# Clone the main project repository from the 'dev' branch, including its submodules
RUN git clone --branch dev --recurse-submodules https://github.com/esd-univr/ice-frost.git /app

# Set the working directory for subsequent commands
WORKDIR /app

# Set the default command to run when the container starts
CMD ["lingo", "run"]