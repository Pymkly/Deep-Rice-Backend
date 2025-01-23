# from ragsystem.rice.retrieve.document_search import calculate_cosine_similarity, find_best_match_keyword_search, \
#     print_formatted_response
#
# db_records = [
#     "Dans un système RAG, l'étape de récupération des informations (Retrieve) est essentielle pour fournir au modèle de génération (Generate) les données les plus pertinentes. Cette étape implique souvent l'utilisation d'algorithmes sophistiqués, tels que la recherche dense avec des embeddings, pour identifier les documents qui répondent au mieux à la requête de l'utilisateur. Une récupération efficace garantit que le modèle génératif produit des réponses précises et cohérentes, même pour des questions complexes.",
#     "La mise en œuvre d'un système RAG repose sur des outils avancés comme les moteurs de recherche vectoriels (FAISS, Pinecone) et des modèles d'encodage du langage naturel (BERT, Sentence Transformers). Ces technologies permettent de transformer des documents en vecteurs dans un espace sémantique, facilitant ainsi la recherche rapide et pertinente. L'intégration harmonieuse entre la recherche d'informations et la génération de texte constitue le cœur de cette approche.",
#     "Les systèmes RAG trouvent des applications dans divers domaines tels que la santé, la finance, et l'éducation. Par exemple, dans le domaine médical, un système RAG peut récupérer des articles scientifiques pertinents pour répondre à des questions de diagnostic. De même, dans l'éducation, il peut fournir des explications adaptées aux questions des étudiants en s'appuyant sur des ressources pédagogiques disponibles. Leur capacité à intégrer rapidement des informations externes les rend particulièrement précieux pour des scénarios nécessitant une précision élevée.",
#     "L'intelligence émotionnelle (IE) désigne la capacité à reconnaître, comprendre et gérer ses propres émotions tout en percevant et influençant celles des autres. Contrairement à l'intelligence cognitive, l'IE joue un rôle clé dans la communication interpersonnelle, la résolution des conflits et le leadership. Elle est particulièrement valorisée dans les environnements de travail modernes où la collaboration est essentielle.",
#     "Les études montrent que les individus ayant une intelligence émotionnelle élevée sont plus susceptibles de réussir dans leur carrière. Ils savent gérer le stress, s'adapter aux changements et maintenir des relations harmonieuses avec leurs collègues. En outre, les leaders dotés d'une forte IE inspirent confiance et loyauté, ce qui contribue à renforcer la cohésion des équipes et à améliorer la productivité globale."
#     ]
#
# query = "define a rag store"
# print(len(db_records))
# for record in db_records:
#     print(calculate_cosine_similarity(query, record))
#     print("eps")
#
# print("fin")
#
# best_keyword_score, best_matching_record = find_best_match_keyword_search(query, db_records)
# print(f"Best Keyword Score: {best_keyword_score}")
# # print(f"Best Matching Record: {best_matching_record}")
# print_formatted_response(best_matching_record)