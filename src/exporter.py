import pandas as pd
import os
from datetime import datetime

def export_leads_to_csv(leads: list[dict], output_dir: str = "data/processed") -> str | None:
    """Exporta la lista de leads validados a un archivo CSV."""
    if not leads:
        return None
        
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"leads_{timestamp}.csv")
    
    df = pd.DataFrame(leads)
    
    # Definición estricta de estructura tabular para el equipo de ventas
    columns_order = ['name', 'phone', 'instagram', 'followers', 'website', 'maps_url']
    
    # Retención de columnas dinámicas presentes en el DataFrame
    available_columns = [col for col in columns_order if col in df.columns]
    df = df[available_columns]
    
    df.to_csv(filepath, index=False, encoding='utf-8')
    return filepath