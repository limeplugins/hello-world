FROM docker.lundalogik.com/lundalogik/crm/python-base:latest

CMD sh

WORKDIR /lime
COPY . /lime

# The copying of timezone info is a hack to solve a bug in pytz regarding
# name conflict for local timezone
RUN pip3 install --no-cache-dir -r requirements_dev.txt \
    && if [ -f /usr/local/lib/python3.5/site-packages/pytzdata/zoneinfo/localtime ]; \
       then cp /usr/local/lib/python3.5/site-packages/pytzdata/zoneinfo/localtime \
               /usr/local/lib/python3.5/site-packages/pytzdata/zoneinfo/local; fi

RUN limeplug install .
