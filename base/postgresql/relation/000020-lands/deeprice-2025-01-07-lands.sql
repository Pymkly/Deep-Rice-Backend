CREATE TABLE lands (
    id SERIAL PRIMARY KEY, -- Unique identifier for the land
    user_id INT NOT NULL, -- ID of the owner (foreign key)
    title VARCHAR(150) NOT NULL, -- Title of the land
    global_location GEOMETRY(Point, 4326) NOT NULL, -- Global location (latitude, longitude)
    boundary GEOMETRY(Polygon, 4326) NOT NULL, -- Polygon defining the land surface
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation timestamp
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- Relationship with users
);
CREATE INDEX idx_lands_global_location ON lands USING GIST (global_location);
CREATE INDEX idx_lands_boundary ON lands USING GIST (boundary);

CREATE TABLE parcels (
    id SERIAL PRIMARY KEY, -- Unique identifier for the parcel
    land_id INT NOT NULL, -- Reference to the land it belongs to
    title VARCHAR(150) NOT NULL, -- Title of the parcel
    boundary GEOMETRY(Polygon, 4326) NOT NULL, -- Polygon defining the parcel boundary
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation timestamp
    FOREIGN KEY (land_id) REFERENCES lands(id) ON DELETE CASCADE -- Relationship with 000020-lands
);
CREATE INDEX idx_parcels_boundary ON parcels USING GIST (boundary);
