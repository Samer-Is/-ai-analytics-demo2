FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    pandas \
    matplotlib \
    seaborn \
    numpy \
    scipy \
    scikit-learn \
    statsmodels

# Create output directory
RUN mkdir -p /app/output

# Set matplotlib backend to non-interactive
ENV MPLBACKEND=Agg

# Copy data and output directories will be mounted at runtime
COPY . .

# Default command
CMD ["python"]
