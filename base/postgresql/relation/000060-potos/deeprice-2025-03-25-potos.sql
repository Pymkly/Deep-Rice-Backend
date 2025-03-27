CREATE TABLE potos (
    id SERIAL PRIMARY KEY,            -- Identifiant unique du "Poto"
    parcel_id INT,                    -- Référence à la parcelle concernée (optionnel mais recommandé)
    title VARCHAR(150) NOT NULL,      -- Nom du "Poto" (ex : Poto_1, Poto_2, etc.)
    global_location GEOMETRY(Point, 4326) NOT NULL, -- Localisation GPS (latitude, longitude)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Date de création
    FOREIGN KEY (parcel_id) REFERENCES parcels(id) ON DELETE CASCADE -- Lien avec les parcelles
);

CREATE INDEX idx_potos_global_location ON potos USING GIST (global_location);
alter table potos add foreign key (parcel_id) references parcels(id);

alter table potos add ref varchar(50);