FROM python:3.8.3-alpine

RUN mkdir -p /home/onepost

RUN addgroup -S onepost && adduser -S onepost -G onepost

# create the appropriate directories
ENV HOME=/home/onepost
ENV APP_HOME=/home/onepost/onepost_backend
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles

WORKDIR $APP_HOME

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.prod.sh .
RUN chmod +x  $APP_HOME/entrypoint.prod.sh
RUN mkdir $APP_HOME/log
RUN mkdir $APP_HOME/log/nginx
RUN touch $APP_HOME/log/gunicorn.error.log
RUN touch $APP_HOME/log/gunicorn.access.log
RUN touch $APP_HOME/log/nginx/access.log
RUN touch $APP_HOME/log/nginx/error.log

COPY . $APP_HOME

RUN chown -R onepost:onepost $APP_HOME

USER onepost

ENTRYPOINT ["/home/onepost/onepost_backend/entrypoint.prod.sh"]
