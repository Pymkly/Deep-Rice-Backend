import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
start_time = time.time()
model = SentenceTransformer('all-mpnet-base-v2')
loadtime = time.time() - start_time
db_records = [
    "Dans un système RAG, l'étape de récupération des informations (Retrieve) est essentielle pour fournir au modèle de génération (Generate) les données les plus pertinentes. Cette étape implique souvent l'utilisation d'algorithmes sophistiqués, tels que la recherche dense avec des embeddings, pour identifier les documents qui répondent au mieux à la requête de l'utilisateur. Une récupération efficace garantit que le modèle génératif produit des réponses précises et cohérentes, même pour des questions complexes.",
    "La mise en œuvre d'un système RAG repose sur des outils avancés comme les moteurs de recherche vectoriels (FAISS, Pinecone) et des modèles d'encodage du langage naturel (BERT, Sentence Transformers). Ces technologies permettent de transformer des documents en vecteurs dans un espace sémantique, facilitant ainsi la recherche rapide et pertinente. L'intégration harmonieuse entre la recherche d'informations et la génération de texte constitue le cœur de cette approche.",
    "Les systèmes RAG trouvent des applications dans divers domaines tels que la santé, la finance, et l'éducation. Par exemple, dans le domaine médical, un système RAG peut récupérer des articles scientifiques pertinents pour répondre à des questions de diagnostic. De même, dans l'éducation, il peut fournir des explications adaptées aux questions des étudiants en s'appuyant sur des ressources pédagogiques disponibles. Leur capacité à intégrer rapidement des informations externes les rend particulièrement précieux pour des scénarios nécessitant une précision élevée.",
    "L'intelligence émotionnelle (IE) désigne la capacité à reconnaître, comprendre et gérer ses propres émotions tout en percevant et influençant celles des autres. Contrairement à l'intelligence cognitive, l'IE joue un rôle clé dans la communication interpersonnelle, la résolution des conflits et le leadership. Elle est particulièrement valorisée dans les environnements de travail modernes où la collaboration est essentielle.",
    "Les études montrent que les individus ayant une intelligence émotionnelle élevée sont plus susceptibles de réussir dans leur carrière. Ils savent gérer le stress, s'adapter aux changements et maintenir des relations harmonieuses avec leurs collègues. En outre, les leaders dotés d'une forte IE inspirent confiance et loyauté, ce qui contribue à renforcer la cohésion des équipes et à améliorer la productivité globale."
    ]
query = "define a rag store"
embeddings = model.encode(db_records)
question = model.encode([query])
print(embeddings.shape)

for _embedding in embeddings:
    similarity = cosine_similarity([question[0]], [_embedding])
    print(similarity)
# similarity = cosine_similarity([embeddings[0]], [embeddings[1]])
# # print(similarity)

end_time = time.time()
execution_time = end_time - start_time
print(f"Temps d'exécution : {execution_time:.5f} secondes")
print(f"Temps de chargement du model : {loadtime:.5f} secondes")
