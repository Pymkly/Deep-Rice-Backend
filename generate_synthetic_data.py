"""
GÉNÉRATEUR DE DONNÉES SYNTHÉTIQUES POUR LA GESTION DE L'EAU
Dataset réaliste basé sur les conditions climatiques de Madagascar
et les besoins en eau du riz à différents stades de croissance.

Usage:
    python generate_synthetic_data.py
    
Sortie:
    - data/water_training_data.csv (dataset complet)
    - data/water_training_split/ (train/val/test splits)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import random

# Configuration
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = "data"
DATASET_SIZE = 1000  # Nombre d'échantillons

# ============================================================================
# PARAMÈTRES RÉALISTES POUR MADAGASCAR
# ============================================================================

# Climat Madagascar (Hautes Terres - Antananarivo région)
TEMP_RANGE = (18, 32)  # °C
HUMIDITY_RANGE = (60, 95)  # %
RAINFALL_RANGE = (0, 80)  # mm/jour (saison des pluies Nov-Mars)
ET0_RANGE = (3, 7)  # mm/jour (évapotranspiration de référence)
WIND_SPEED_RANGE = (5, 25)  # km/h

# Stades de croissance du riz et coefficients culturaux (Kc)
GROWTH_STAGES = {
    'germination': {'kc': 0.7, 'duration_days': 15, 'water_need_base': 35},
    'vegetative': {'kc': 1.1, 'duration_days': 35, 'water_need_base': 55},
    'reproductive': {'kc': 1.3, 'duration_days': 35, 'water_need_base': 65},
    'maturation': {'kc': 0.9, 'duration_days': 25, 'water_need_base': 40}
}

# Types de sol et rétention d'eau
SOIL_TYPES = {
    'clay': {'retention': 0.85, 'infiltration': 0.3},      # Argileux (bon pour riz inondé)
    'loamy': {'retention': 0.70, 'infiltration': 0.5},     # Limoneux (idéal)
    'sandy': {'retention': 0.45, 'infiltration': 0.8},     # Sableux (drainage rapide)
    'peat': {'retention': 0.90, 'infiltration': 0.2}       # Tourbeux (très rétentif)
}

# Méthodes d'irrigation
IRRIGATION_METHODS = {
    'flooded': {'efficiency': 0.60, 'water_multiplier': 1.4},  # Traditionnel inondé
    'sri': {'efficiency': 0.85, 'water_multiplier': 0.7},      # System of Rice Intensification
    'awd': {'efficiency': 0.75, 'water_multiplier': 0.9}       # Alternate Wetting Drying
}

# ============================================================================
# FONCTIONS DE GÉNÉRATION
# ============================================================================

def generate_weather_conditions(season='rainy'):
    """Génère des conditions météo réalistes selon la saison"""
    
    if season == 'rainy':  # Nov-Mars (saison de culture principale)
        temp = np.random.normal(26, 3)
        humidity = np.random.normal(80, 8)
        rainfall = np.random.gamma(2, 5)  # Distribution gamma pour pluies
        et0 = np.random.normal(4.5, 1)
    else:  # Saison sèche
        temp = np.random.normal(22, 4)
        humidity = np.random.normal(65, 10)
        rainfall = np.random.exponential(2)
        et0 = np.random.normal(5.5, 1.2)
    
    # Contraintes réalistes
    temp = np.clip(temp, *TEMP_RANGE)
    humidity = np.clip(humidity, *HUMIDITY_RANGE)
    rainfall = np.clip(rainfall, *RAINFALL_RANGE)
    et0 = np.clip(et0, *ET0_RANGE)
    wind_speed = np.random.uniform(*WIND_SPEED_RANGE)
    
    return {
        'temperature_celsius': round(temp, 1),
        'humidity_percent': round(humidity, 1),
        'rainfall_mm': round(rainfall, 1),
        'evapotranspiration_mm': round(et0, 1),
        'wind_speed_kmh': round(wind_speed, 1)
    }

def calculate_water_need(weather, soil_type, growth_stage, irrigation_method, soil_moisture):
    """
    Calcule les besoins réels en eau (en mm/jour) selon la formule agronomique
    
    Formule simplifiée:
    ETc = ET0 × Kc (Évapotranspiration de la culture)
    Besoins = ETc - Pluie efficace + Percolation + Ajustements
    """
    
    # Récupération des paramètres
    stage_params = GROWTH_STAGES[growth_stage]
    soil_params = SOIL_TYPES[soil_type]
    irrig_params = IRRIGATION_METHODS[irrigation_method]
    
    # 1. ETc = ET0 × Kc
    etc = weather['evapotranspiration_mm'] * stage_params['kc']
    
    # 2. Pluie efficace (pas toute la pluie est absorbée)
    effective_rainfall = weather['rainfall_mm'] * 0.8
    
    # 3. Percolation (perte par infiltration profonde)
    percolation = 5 * soil_params['infiltration']  # mm/jour
    
    # 4. Ajustement selon l'humidité du sol actuelle
    if soil_moisture < 50:  # Sol sec
        moisture_stress_factor = 1.3
    elif soil_moisture > 80:  # Sol saturé
        moisture_stress_factor = 0.7
    else:  # Optimal
        moisture_stress_factor = 1.0
    
    # 5. Ajustement température (stress thermique)
    if weather['temperature_celsius'] > 30:
        temp_stress = 1.2
    elif weather['temperature_celsius'] < 20:
        temp_stress = 0.9
    else:
        temp_stress = 1.0
    
    # 6. Calcul du besoin net
    base_need = stage_params['water_need_base']
    net_need = (
        base_need +
        etc - 
        effective_rainfall + 
        percolation
    ) * moisture_stress_factor * temp_stress
    
    # 7. Ajustement selon méthode d'irrigation
    gross_need = net_need * irrig_params['water_multiplier'] / irrig_params['efficiency']
    
    # 8. Contraintes réalistes (entre 0 et 100 mm/jour)
    water_need = np.clip(gross_need, 0, 100)
    
    return round(water_need, 2)

def generate_dataset(size=1000):
    """Génère le dataset complet"""
    
    print(f"🌾 Génération de {size} échantillons...")
    
    data = []
    
    for i in range(size):
        # Saison (80% saison des pluies car c'est la période de culture)
        season = 'rainy' if random.random() < 0.8 else 'dry'
        
        # Conditions météo
        weather = generate_weather_conditions(season)
        
        # Paramètres du champ (tirés aléatoirement)
        soil_type = random.choice(list(SOIL_TYPES.keys()))
        growth_stage = random.choice(list(GROWTH_STAGES.keys()))
        irrigation_method = random.choice(list(IRRIGATION_METHODS.keys()))
        
        # Humidité du sol actuelle (distribution normale autour de 65%)
        soil_moisture = np.clip(np.random.normal(65, 15), 20, 95)
        
        # Calcul des besoins en eau (TARGET)
        water_need = calculate_water_need(
            weather, 
            soil_type, 
            growth_stage, 
            irrigation_method,
            soil_moisture
        )
        
        # Création de l'échantillon
        sample = {
            # Features météo
            'temperature_celsius': weather['temperature_celsius'],
            'humidity_percent': weather['humidity_percent'],
            'rainfall_mm': weather['rainfall_mm'],
            'evapotranspiration_mm': weather['evapotranspiration_mm'],
            'wind_speed_kmh': weather['wind_speed_kmh'],
            
            # Features sol et culture
            'soil_moisture_percent': round(soil_moisture, 1),
            'soil_type': soil_type,
            'growth_stage': growth_stage,
            'irrigation_method': irrigation_method,
            
            # Features encodées (pour ML)
            'soil_type_encoded': list(SOIL_TYPES.keys()).index(soil_type),
            'growth_stage_encoded': list(GROWTH_STAGES.keys()).index(growth_stage),
            'irrigation_method_encoded': list(IRRIGATION_METHODS.keys()).index(irrigation_method),
            
            # TARGET
            'water_need_mm_per_day': water_need,
            
            # Métadonnées
            'season': season,
            'sample_id': f'sample_{i:04d}'
        }
        
        data.append(sample)
        
        # Progression
        if (i + 1) % 100 == 0:
            print(f"   ✓ {i + 1}/{size} échantillons générés")
    
    df = pd.DataFrame(data)
    print(f"✅ Dataset généré : {df.shape[0]} lignes × {df.shape[1]} colonnes")
    
    return df

def save_dataset(df, output_dir=OUTPUT_DIR):
    """Sauvegarde le dataset et crée les splits train/val/test"""
    
    # Créer les dossiers
    os.makedirs(output_dir, exist_ok=True)
    split_dir = os.path.join(output_dir, "water_training_split")
    os.makedirs(split_dir, exist_ok=True)
    
    # 1. Sauvegarder le dataset complet
    full_path = os.path.join(output_dir, "water_training_data.csv")
    df.to_csv(full_path, index=False)
    print(f"📊 Dataset complet sauvegardé : {full_path}")
    
    # 2. Créer les splits (70% train, 15% val, 15% test)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    train_size = int(0.70 * len(df_shuffled))
    val_size = int(0.15 * len(df_shuffled))
    
    train_df = df_shuffled[:train_size]
    val_df = df_shuffled[train_size:train_size + val_size]
    test_df = df_shuffled[train_size + val_size:]
    
    # Sauvegarder les splits
    train_df.to_csv(os.path.join(split_dir, "train.csv"), index=False)
    val_df.to_csv(os.path.join(split_dir, "val.csv"), index=False)
    test_df.to_csv(os.path.join(split_dir, "test.csv"), index=False)
    
    print(f"📁 Splits sauvegardés dans : {split_dir}/")
    print(f"   - Train: {len(train_df)} échantillons (70%)")
    print(f"   - Val:   {len(val_df)} échantillons (15%)")
    print(f"   - Test:  {len(test_df)} échantillons (15%)")
    
    return train_df, val_df, test_df

def display_statistics(df):
    """Affiche des statistiques sur le dataset"""
    
    print("\n" + "="*60)
    print("📈 STATISTIQUES DU DATASET")
    print("="*60)
    
    print("\n🌡️  Variables météorologiques:")
    print(df[['temperature_celsius', 'humidity_percent', 'rainfall_mm', 
              'evapotranspiration_mm']].describe().round(2))
    
    print("\n💧 Besoins en eau (TARGET):")
    print(df['water_need_mm_per_day'].describe().round(2))
    
    print("\n🌾 Distribution par stade de croissance:")
    print(df['growth_stage'].value_counts())
    
    print("\n🏞️  Distribution par type de sol:")
    print(df['soil_type'].value_counts())
    
    print("\n💦 Distribution par méthode d'irrigation:")
    print(df['irrigation_method'].value_counts())
    
    print("\n🌧️  Distribution par saison:")
    print(df['season'].value_counts())
    
    print("\n✅ Dataset prêt pour l'entraînement !")
    print("="*60 + "\n")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌾 GÉNÉRATEUR DE DONNÉES SYNTHÉTIQUES - GESTION EAU RIZ")
    print("="*60 + "\n")
    
    # Génération
    df = generate_dataset(size=DATASET_SIZE)
    
    # Statistiques
    display_statistics(df)
    
    # Sauvegarde
    train_df, val_df, test_df = save_dataset(df)
    
    print("\n🎉 TERMINÉ ! Tu peux maintenant utiliser ces données pour entraîner ton modèle.")
    print(f"📂 Fichiers créés dans le dossier '{OUTPUT_DIR}/'")
    print("\n💡 Prochaine étape : Lance le notebook d'entraînement !")