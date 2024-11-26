FROM python:3.10.14
EXPOSE 8501
CMD mkdir -p /app
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN apt-get update
RUN apt-get -y install xvfb
RUN apt-get -y install xclip
RUN Xvfb :99 -screen 0 1280x720x16 &
RUN export DISPLAY=:99
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]