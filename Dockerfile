FROM python:3
COPY . /app
RUN pip3 install -r /app/requirements.txt
WORKDIR /app
CMD bokeh serve ukr_supply/
