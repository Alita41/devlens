FROM python:3.12-slim
WORKDIR /app
RUN useradd -m devlens
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY devlens ./devlens
COPY scripts ./scripts
COPY pyproject.toml README.md ./
RUN mkdir -p /app/.devlens && chown -R devlens:devlens /app
USER devlens
ENV PYTHONPATH=/app DEVLENS_LLM_PROVIDER=local
EXPOSE 8080
CMD ["uvicorn", "devlens.api:app", "--host", "0.0.0.0", "--port", "8080"]
