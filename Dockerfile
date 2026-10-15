FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY hostel-web/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY hostel-web/app.py ./app.py
COPY hostel-web/templates/ ./templates/
COPY hostel-web/static/ ./static/

FROM base AS test
COPY hostel-web/tests/ ./tests/
RUN python -m unittest discover -s tests -v

FROM base AS runtime
RUN groupadd --system app && useradd --system --gid app --no-create-home app
USER app

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
