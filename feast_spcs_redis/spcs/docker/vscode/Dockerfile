FROM lscr.io/linuxserver/code-server:latest

RUN apt-get update && \
    apt-get install -y python3.10 make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev git python3-openssl mysql-server \
    libmysqlclient-dev python3-pip

RUN pip install 'feast[snowflake,redis]'

RUN ln -s /usr/bin/python3 /usr/bin/python