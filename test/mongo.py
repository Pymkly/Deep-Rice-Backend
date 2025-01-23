from api.database.conn import get_mongo_db

db = get_mongo_db()
collection = db["my_collection"]

# Insérer un document
collection.insert_one({"title": "Document PDF", "content": "Texte extrait du PDF"})

# Rechercher des documents
for doc in collection.find():
    print(doc)