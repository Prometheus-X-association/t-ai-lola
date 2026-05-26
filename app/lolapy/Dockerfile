FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive
ENV NXF_VER=25.10.5
ENV PYTHON_VERSION=3.12

# 1. Install prerequisites needed to add repositories
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    wget \
    sed=4.9-2ubuntu0.24.04.1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Add all necessary repositories (Docker, Kubernetes, Python PPA)
RUN install -m 0755 -d /etc/apt/keyrings \
    # Docker repository
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    # Kubernetes repository
    && curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg \
    && chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg \
    && echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list \
    # Python PPA
    && add-apt-repository ppa:deadsnakes/ppa -y

# 3. Install all remaining packages in a single apt-get operation to reduce layers
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin \
        openjdk-17-jre-headless \
        slurm-client \
        munge \
        kubectl \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        python${PYTHON_VERSION}-venv \
        build-essential \
        libffi-dev \
        libssl-dev \
        libyajl-dev \
        git \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and necessary directories for Slurm
RUN useradd -m -s /bin/bash lolauser \
    && mkdir -p /etc/slurm /var/run/munge /etc/munge \
    && chown munge:munge /var/run/munge /etc/munge

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash \
    && mv nextflow /usr/local/bin/ \
    && chmod +x /usr/local/bin/nextflow

WORKDIR /app

# Ensure lolauser owns the working directory
RUN chown lolauser:lolauser /app

# Switch to non-root user for pip installs and execution
USER lolauser

# Activate the virtual environment
ENV PYTHONPATH=/app

# Copy requirements separately to leverage Docker layer caching
COPY --chown=lolauser:lolauser requirements.txt requirements.txt

# Create venv and install dependencies as non-root to avoid permission issues
# Using --no-cache-dir to reduce image size
RUN python${PYTHON_VERSION} -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir wheel "setuptools>=78.1.1" \
    && /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=lolauser:lolauser . .
