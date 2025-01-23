# from api.database.conn import get_mongo_db
# from api.metadata.metadata import set_gps_coordinates, read_gps_coordinates
# import math
# import time

# from ragsystem.rice.collect.ricepdfextractor import extract_save_mongo_all_rice_txt_pdf
from ragsystem.rice.retrieve.retrieve import relevant_info

# import os
#
# from ragsystem.rice.collect.ricepdfextractor import extract_save_mongo_all_rice_txt_pdf
# from ragsystem.rice.generative import generate_answer
# from ragsystem.rice.retrieve.document_search import search_documents

# os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
#
# db = get_mongo_db()
query = "parle moi du maladie du pyriculariose"
documents, similarities = relevant_info(query, 0.5)
for document in documents:
    print(document['content'])
print(len(documents))
mean = sum(similarities)/len(similarities)
print(f"mean = {str(mean)}")
max_sim = max(similarities)
print(f"max_sim = {str(max_sim)}")
#
# path = "./uploads/drone/vague1/1736197996_brownspot_orig_003.jpg"
# set_gps_coordinates(path, 48.858844, 2.294351)
# read_gps_coordinates(path)

# extract_save_mongo_all_rice_txt_pdf()
# start_time = time.time()
# documents = find_all()
# end_time = time.time()
# duration = end_time - start_time
# for document in documents:
#     print(document)
# print(f"Temps d'execution : {duration:.5f} secondes")

# question = "Quelles sont les maladies des plantes ?"
# documents = search_documents(question, db)
# for doc in documents:
#     print(doc)

# Exemple d'utilisation
# answer = generate_answer("Quelles sont les maladies des plantes ?", db)
# print(answer)

print("ok")