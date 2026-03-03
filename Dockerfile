FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Enable bytecode compilation, to improve startup time
ENV UV_COMPILE_BYTECODE=1

# Copy dependency definition to leverage Docker cache layer
COPY pyproject.toml uv.lock ./

# Install dependencies (including dev and extras) Without installing project
RUN uv sync --all-extras --no-install-project

# Copy project files
COPY . .

# Install the project itself and verify
RUN uv sync --all-extras

# Set the default command to run tests
CMD ["uv", "run", "pytest"]
