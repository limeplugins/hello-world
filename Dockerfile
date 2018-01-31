FROM docker.lundalogik.com/lundalogik/crm/python-base:latest

CMD sh

WORKDIR /lime
COPY . /lime

RUN pip3 install --no-cache-dir -r requirements_dev.txt

# Set timezone to Sweden.
ENV TZ=Europe/Stockholm
RUN apk --no-cache add tzdata \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

RUN limeplug install .
