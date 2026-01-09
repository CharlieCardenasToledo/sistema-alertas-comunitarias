"""
Scraper para INAMHI - Instituto Nacional de Meteorologia e Hidrologia
Extrae alertas meteorologicas y datos de precipitacion
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import structlog

logger = structlog.get_logger()

class InamhiScraper:
    """Scraper para alertas meteorologicas de INAMHI"""
    
    def __init__(self, source_url):
        self.source_url = source_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape(self):
        """
        Scrape de alertas meteorologicas
        """
        try:
            logger.info("inamhi_scraping_started", url=self.source_url)
            
            response = requests.get(self.source_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar alertas meteorologicas
            # Nota: La estructura real del sitio puede variar
            # Este es un ejemplo de como extraer datos
            
            events = []
            
            # Buscar secciones de alertas
            alert_sections = soup.find_all(['div', 'article'], class_=['alert', 'aviso', 'noticia'])
            
            if not alert_sections:
                # Si no hay estructura especifica, buscar en el contenido general
                content = soup.get_text()
                
                # Detectar palabras clave de alertas
                keywords = ['lluvia', 'precipitacion', 'tormenta', 'alerta', 'aviso']
                if any(keyword in content.lower() for keyword in keywords):
                    # Crear evento generico
                    event = {
                        'title': 'Alerta meteorologica detectada',
                        'content': content[:500],  # Primeros 500 caracteres
                        'url': self.source_url,
                        'date': datetime.utcnow().isoformat(),
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    events.append(event)
            else:
                # Procesar cada alerta encontrada
                for section in alert_sections[:5]:  # Maximo 5 alertas
                    title_tag = section.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_tag.get_text(strip=True) if title_tag else 'Alerta meteorologica'
                    
                    content = section.get_text(strip=True)
                    
                    # Buscar fecha
                    date_tag = section.find(['time', 'span'], class_=['date', 'fecha'])
                    date = date_tag.get_text(strip=True) if date_tag else None
                    
                    event = {
                        'title': title,
                        'content': content[:500],
                        'url': self.source_url,
                        'date': date,
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    events.append(event)
            
            logger.info("inamhi_scraping_completed", events_found=len(events))
            return events
            
        except requests.RequestException as e:
            logger.error("inamhi_scraping_failed", error=str(e))
            return []
        except Exception as e:
            logger.error("inamhi_unexpected_error", error=str(e))
            return []
