# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.187.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3.8"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# Install common software
RUN apt update && apt install -y software-properties-common zip less groff

# Install AWS CLI
RUN curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
	unzip -qq awscliv2.zip && \
	./aws/install && \
	rm -rf aws*

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | \
	POETRY_HOME=/opt/poetry python - && \
	chmod -R 755 /opt/poetry

RUN pip install cleanpy

ENV PATH "/opt/poetry/bin:$PATH"

ENV VIRTUAL_ENV_DISABLE_PROMPT 1

COPY .devcontainer/.bashrc /home/vscode/.bashrc
RUN chown 1000:1000 /home/vscode/.bashrc
