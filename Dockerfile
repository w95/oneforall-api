FROM python:3.10-alpine

# Install system dependencies
RUN apk update && apk --no-cache add \
    git \
    build-base \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    openssl-dev \
    wget \
    unzip \
    make

# Set working directory
WORKDIR /app

# Download and extract OneForAll latest release
RUN wget -O oneforall.zip https://gitee.com/shmilylty/OneForAll/repository/archive/master.zip && \
    unzip oneforall.zip && \
    mv OneForAll-master OneForAll && \
    rm oneforall.zip

# Clone and build massdns
RUN git clone https://github.com/blechschmidt/massdns
WORKDIR /app/massdns
RUN make

# Copy massdns binary to OneForAll thirdparty directory
RUN mv /app/massdns/bin/massdns /app/OneForAll/thirdparty/massdns/massdns_linux_$(uname -m)

# Create results directory
RUN mkdir -p /app/OneForAll/results

# Copy FastAPI application files
COPY main.py /app/
COPY requirements.txt /app/

# Install Python dependencies for FastAPI
WORKDIR /app
RUN pip3.10 install --no-cache-dir -r requirements.txt

# Install OneForAll dependencies
WORKDIR /app/OneForAll
RUN pip3.10 install --no-cache-dir -r requirements.txt

# Switch back to app directory
WORKDIR /app

# Expose the port
EXPOSE 9403

# Run the FastAPI application
CMD ["python3.10", "main.py"]
