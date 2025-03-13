FROM postgis/postgis:16-3.5

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    git \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

# Install pgvector from source
RUN git clone https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install \
    && cd .. \
    && rm -rf pgvector

EXPOSE 5432

CMD ["postgres"]