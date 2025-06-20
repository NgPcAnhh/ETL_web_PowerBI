FROM apache/airflow:3.0.0-python3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Go
ENV GO_VERSION=1.21.5
ENV GOROOT=/usr/local/go
ENV GOPATH=/opt/airflow/go
ENV PATH=$GOROOT/bin:$GOPATH/bin:$PATH

RUN wget https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz && \
    chmod -R 755 /usr/local/go

# Create Go workspace
RUN mkdir -p $GOPATH && \
    chown -R airflow:root $GOPATH

# Make Go available globally
RUN ln -sf /usr/local/go/bin/go /usr/bin/go && \
    ln -sf /usr/local/go/bin/gofmt /usr/bin/gofmt && \
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/bash.bashrc

USER airflow

# Install Python dependencies
COPY requirements2.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# USER airflow

# Verify installations
RUN go version && python --version