FROM continuumio/miniconda3
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY ./ /app
WORKDIR "/app"
CMD gunicorn --bind 0.0.0.0:$PORT wsgi