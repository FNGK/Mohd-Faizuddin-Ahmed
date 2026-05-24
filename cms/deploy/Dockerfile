FROM python:3.12-slim

WORKDIR /app
COPY cms/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY cms/backend /app/backend
COPY cms/admin /app/cms/admin
COPY . /app/site

WORKDIR /app/backend
ENV APP_ENV=production
ENV PYTHONPATH=/app/backend
ENV SITE_ROOT=/app/site

EXPOSE 8780
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8780"]
