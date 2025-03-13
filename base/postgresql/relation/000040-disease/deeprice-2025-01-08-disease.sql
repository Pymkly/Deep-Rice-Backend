CREATE TABLE diseases (
    id SERIAL PRIMARY KEY,               -- Identifiant unique pour la maladie
    name VARCHAR(100) NOT NULL,          -- Nom de la maladie
    description TEXT,                    -- Description de la maladie
    instructions TEXT,                   -- Instructions à suivre en cas de détection
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP-- Date de mise à jour
);
