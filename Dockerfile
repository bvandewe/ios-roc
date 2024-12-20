FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ENV PYTHONPATH=/app/src

COPY poetry.lock pyproject.toml /app/
RUN pip install poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENV api_log_level="DEBUG"
ENV LOG_LEVEL="DEBUG"
ENV CONSUMER_GROUP="ios-roc"
ENV CLOUD_EVENT_SINK="http://event-player/events/pub"
ENV CLOUD_EVENT_SOURCE="http://ios-roc.dev.mysite.com"
ENV CLOUD_EVENT_TYPE_PREFIX="com.mysite.ios-roc"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
