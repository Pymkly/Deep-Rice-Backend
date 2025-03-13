CREATE TABLE drone_report (
    id SERIAL PRIMARY KEY,         -- Identifiant unique de la mission
    report_date DATE NOT NULL,    -- Date de la mission
    description TEXT,              -- Description de la mission (optionnel)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Horodatage de création
);
CREATE TABLE drone_images (
    id SERIAL PRIMARY KEY,             -- Identifiant unique de l'image
    report_id INT NOT NULL,            -- Référence à la table mère (drone_report)
    photo_url TEXT NOT NULL,           -- Lien vers la photo
    predicted_class INT NOT NULL,      -- Classe prédite (indice)
    location GEOMETRY(Point, 4326) NOT NULL, -- Coordonnées GPS sous forme de Point
    parcel_id INT NOT NULL,            -- Référence à la parcelle (parcelle associée à l'image)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Horodatage de création

    -- Clé étrangère vers la table mère
    FOREIGN KEY (report_id) REFERENCES drone_report (id) ON DELETE CASCADE,

    -- Clé étrangère vers les parcelles
    FOREIGN KEY (parcel_id) REFERENCES parcels (id) ON DELETE CASCADE
);
CREATE INDEX idx_drone_images_location ON drone_images USING GIST (location);
CREATE INDEX idx_drone_images_report_id ON drone_images (report_id);
CREATE INDEX idx_drone_images_parcel_id ON drone_images (parcel_id);


ALTER TABLE drone_images
ADD COLUMN probability NUMERIC(5, 2) NOT NULL DEFAULT 0.0;
