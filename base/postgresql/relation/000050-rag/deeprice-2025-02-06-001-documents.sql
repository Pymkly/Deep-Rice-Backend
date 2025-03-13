CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768) -- 1536 dimensions pour OpenAI, à adapter selon ton modèle
);
-- CREATE INDEX documents_embedding_idx ON documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);


