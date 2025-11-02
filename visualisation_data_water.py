import pandas as pd

# Charge le dataset
df = pd.read_csv('data/water_training_data.csv')

# Affiche les premières lignes
print(df.head())

# Statistiques
print(df.describe())

# Visualisation simple
import matplotlib.pyplot as plt
df['water_need_mm_per_day'].hist(bins=30)
plt.title('Distribution des besoins en eau')
plt.show()