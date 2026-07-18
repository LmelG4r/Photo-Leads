import asyncio
from src.scraper_maps import scrape_google_maps
from src.extraction_web import extract_instagram_from_website
from src.filters_ig import get_instagram_followers, is_target_lead
from src.exporter import export_leads_to_csv

async def build_pipeline(query: str, max_results: int = 10):
    print(f"Fase 1: Extracción en Google Maps para '{query}'")
    raw_leads = await scrape_google_maps(query, max_results=max_results)
    print(f"-> {len(raw_leads)} negocios extraídos.\n")
    
    qualified_leads = []
    
    print("Fase 2 y 3: Enriquecimiento Web y Validación Social")
    for idx, lead in enumerate(raw_leads, 1):
        print(f"Procesando [{idx}/{len(raw_leads)}]: {lead.get('name', 'Desconocido')}")
        
        ig_url = extract_instagram_from_website(lead.get('website'))
        if not ig_url:
            print("  [X] Descartado: Sin perfil de Instagram localizable.")
            continue
            
        followers = get_instagram_followers(ig_url)
        if followers is None:
            print(f"  [X] Descartado: Imposible resolver métricas para {ig_url}.")
            continue
            
        is_target = is_target_lead(followers)
        print(f"  [>] IG: {ig_url} | Seguidores: {followers} | Objetivo: {is_target}")
        
        if is_target:
            # Inyección de métricas al diccionario del lead
            lead['instagram'] = ig_url
            lead['followers'] = followers
            qualified_leads.append(lead)
            
    print(f"\nFase 4: Exportación. Leads cualificados totales: {len(qualified_leads)}")
    
    if qualified_leads:
        filepath = export_leads_to_csv(qualified_leads)
        print(f"-> Archivo generado: {filepath}")
    else:
        print("-> Fin del proceso. Ningún lead cumplió los criterios de cualificación.")

if __name__ == "__main__":
    # Configuración de entrada
    search_query = "restaurantes en Ciudad Nicolás Romero"
    limit_results = 10
    
    # Ejecución del event loop
    asyncio.run(build_pipeline(search_query, limit_results))