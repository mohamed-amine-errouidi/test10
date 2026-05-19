import pandas as pd
import numpy as np
import io
import json
from datetime import datetime, timedelta
import random

REQUIRED_COLUMNS = ['Date', 'Produit', 'Prix', 'Quantité', 'Ville', 'Statut']

# Mapping pour accepter les variantes de noms de colonnes
COLUMN_ALIASES = {
    'Quantite': 'Quantité',
    'Quantité': 'Quantité',
    'quantite': 'Quantité',
    'quantité': 'Quantité',
    'qty': 'Quantité',
    'Qty': 'Quantité',
    'Status': 'Statut',
    'status': 'Statut',
    'statut': 'Statut',
    'Statut': 'Statut',
    'date': 'Date',
    'DATE': 'Date',
    'produit': 'Produit',
    'PRODUIT': 'Produit',
    'product': 'Produit',
    'Product': 'Produit',
    'prix': 'Prix',
    'PRIX': 'Prix',
    'price': 'Prix',
    'Price': 'Prix',
    'ville': 'Ville',
    'VILLE': 'Ville',
    'city': 'Ville',
    'City': 'Ville',
}

# Mapping pour normaliser les valeurs de Statut
STATUS_ALIASES = {
    'livré': 'Livré',
    'livre': 'Livré',
    'delivered': 'Livré',
    'livree': 'Livré',
    'refusé': 'Refusé',
    'refuse': 'Refusé',
    'refusee': 'Refusé',
    'rejected': 'Refusé',
    'retourné': 'Retourné',
    'retourne': 'Retourné',
    'returned': 'Retourné',
    'annulé': 'Annulé',
    'annule': 'Annulé',
    'cancelled': 'Annulé',
    'canceled': 'Annulé',
    'en cours': 'En cours',      # sera exclu du CA comme "non livré"
    'en_cours': 'En cours',
    'pending': 'En cours',
    'processing': 'En cours',
    'expédié': 'En cours',
    'expedie': 'En cours',
}

def process_file(file_bytes, extension):
    """Main entry point: reads file and returns full analytics dict."""
    
    # --- 1. Read file ---
    try:
        if extension == 'csv':
            df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine='python', encoding='utf-8-sig')
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Impossible de lire le fichier: {str(e)}")

    # --- 2. Normalize column names (fix accents, english names, case) ---
    df = df.rename(columns=lambda c: COLUMN_ALIASES.get(c.strip(), c.strip()))

    # --- 3. Validate columns ---
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {', '.join(missing)}. Colonnes requises: {', '.join(REQUIRED_COLUMNS)}")

    # --- 4. Clean data ---
    df = clean_data(df)

    # --- 4. Compute KPIs ---
    kpis = compute_kpis(df)

    # --- 5. Aggregations ---
    city_sales = aggregate_by_city(df)
    product_sales = aggregate_by_product(df)
    status_breakdown = aggregate_by_status(df)
    trend_data = aggregate_trend(df)
    hourly_data = aggregate_hourly(df)

    return {
        'kpis': kpis,
        'city_sales': city_sales,
        'product_sales': product_sales,
        'status_breakdown': status_breakdown,
        'trend_data': trend_data,
        'hourly_data': hourly_data,
        'total_rows': len(df)
    }

def clean_data(df):
    df = df.dropna(how='all')
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce').fillna(0)
    df['Quantité'] = pd.to_numeric(df['Quantité'], errors='coerce').fillna(0)
    df['Revenu'] = df['Prix'] * df['Quantité']
    # Normaliser les statuts : strip + lowercase pour lookup, sinon title()
    df['Statut'] = df['Statut'].str.strip().apply(
        lambda s: STATUS_ALIASES.get(s.lower(), s.strip().title()) if isinstance(s, str) else s
    )
    df['Ville'] = df['Ville'].str.strip().str.title()
    df['Produit'] = df['Produit'].str.strip()
    return df

def compute_kpis(df):
    livré = df[df['Statut'] == 'Livré']
    total_ca = round(float(livré['Revenu'].sum()), 2)
    total_commandes = int(len(df))
    commandes_livrées = int(len(livré))
    panier_moyen = round(total_ca / commandes_livrées, 2) if commandes_livrées > 0 else 0
    taux_livraison = round((commandes_livrées / total_commandes * 100), 1) if total_commandes > 0 else 0

    return {
        'chiffre_affaires': total_ca,
        'total_commandes': total_commandes,
        'panier_moyen': panier_moyen,
        'taux_livraison': taux_livraison
    }

def aggregate_by_city(df):
    livré = df[df['Statut'] == 'Livré']
    city = livré.groupby('Ville')['Revenu'].sum().sort_values(ascending=False).head(10)
    return {'labels': city.index.tolist(), 'values': [round(v, 2) for v in city.values.tolist()]}

def aggregate_by_product(df):
    livré = df[df['Statut'] == 'Livré']
    prod = livré.groupby('Produit')['Revenu'].sum().sort_values(ascending=False).head(5)
    return {'labels': prod.index.tolist(), 'values': [round(v, 2) for v in prod.values.tolist()]}

def aggregate_by_status(df):
    status = df['Statut'].value_counts()
    return {'labels': status.index.tolist(), 'values': status.values.tolist()}

def aggregate_trend(df):
    livré = df[df['Statut'] == 'Livré'].copy()
    livré['Jour'] = livré['Date'].dt.date
    trend = livré.groupby('Jour')['Revenu'].sum().sort_index()
    return {
        'labels': [str(d) for d in trend.index.tolist()],
        'values': [round(v, 2) for v in trend.values.tolist()]
    }

def aggregate_hourly(df):
    if 'Heure' in df.columns:
        hour = df.groupby('Heure')['Revenu'].sum()
        return {'labels': hour.index.tolist(), 'values': [round(v, 2) for v in hour.values.tolist()]}
    return {'labels': [], 'values': []}

def generate_sample_template():
    """Generate a sample Excel file for download."""
    villes = ['Casablanca', 'Marrakech', 'Rabat', 'Fès', 'Tanger', 'Agadir', 'Meknès', 'Oujda']
    produits = ['Robe Fleurie', 'Jean Slim', 'Sneakers Blanc', 'Sac à Main', 'Montre Classique', 'Parfum Oud', 'Veste Cuir', 'Lunettes Soleil']
    statuts = ['Livré', 'Livré', 'Livré', 'Refusé', 'Retourné', 'Annulé']

    rows = []
    base_date = datetime(2024, 1, 1)
    for i in range(200):
        date = base_date + timedelta(days=random.randint(0, 180))
        rows.append({
            'Date': date.strftime('%d/%m/%Y'),
            'Produit': random.choice(produits),
            'Prix': round(random.uniform(50, 800), 2),
            'Quantité': random.randint(1, 5),
            'Ville': random.choice(villes),
            'Statut': random.choice(statuts)
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Ventes')
    output.seek(0)
    return output
