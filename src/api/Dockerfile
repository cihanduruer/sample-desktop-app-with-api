# Python Flask API — teaching image.
# NOTE: this runs the Flask dev server (app.run). The Docker lab in
# docs/modernization/08-docker-containerization.md walks through hardening this
# (e.g. switching to a production WSGI server like waitress/gunicorn, dropping
# debug mode, running as a non-root user).
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 5001
CMD ["python", "app.py"]
