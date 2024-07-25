FROM python:3.9

RUN pip install jupyter

EXPOSE 8000

ENTRYPOINT ["jupyter","notebook", "--ip=0.0.0.0", "--port=8000", "--no-browser"]

