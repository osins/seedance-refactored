# Volces API Client

A Python client library for interacting with the Volces API v3.

## Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Set up environment variables in `.env` file:
   ```
   VOLCES_API_KEY=your_api_key_here
   # Optional: Override the default API base host (without version)
   VOLCES_BASE_HOST=https://api.volces.com
   ```

   The API client prioritizes the base host in the following order:
   1. `VOLCES_BASE_HOST` - Environment variable for custom base host (without version)
   2. Default host - `https://api.volces.com` if the environment variable is not set
   
   Note: The API version (/v3) is fixed in the client code and appended to the base host.

## Usage

Import and use the API functions from the `src.seedance.v3` module.

## Development Standards

This project follows the Python coding standards outlined in [docs/python_coding_standards.md](./docs/python_coding_standards.md). Please refer to this document when contributing to the project.