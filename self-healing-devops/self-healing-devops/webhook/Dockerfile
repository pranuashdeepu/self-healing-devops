FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir flask ansible-core docker

# Install Ansible community.docker collection (for docker_container module)
RUN ansible-galaxy collection install community.docker

# Create app directory
WORKDIR /app

# Copy app and default Ansible content
COPY app.py /app/app.py
COPY ../ansible /ansible

EXPOSE 5001
CMD ["python", "/app/app.py"]