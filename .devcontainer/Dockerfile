FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Node.js for frontend tooling
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python dependencies
COPY backend/requirements.txt backend/requirements-dev.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements-dev.txt

# Install frontend dependencies
COPY frontend/package.json /tmp/
RUN cd /tmp && npm install --global npm@latest \
    && npm install

# Configure git (for Codespaces)
RUN git config --global --add safe.directory /workspace

# Set Python path
ENV PYTHONPATH=/workspace/backend/src:$PYTHONPATH

# Expose ports
EXPOSE 5000 8000
