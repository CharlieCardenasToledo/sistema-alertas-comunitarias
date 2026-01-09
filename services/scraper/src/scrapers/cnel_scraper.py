"""
Scraper para CNEL - Corporacion Nacional de Electricidad
Extrae informacion sobre cortes programados de energia
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import structlog

logger = structlog.get_logger()

class CnelScraper:
    """Scraper para cortes programados de CNEL"""
    
    def __init__(self, source_url):
        self.source_url = source_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape(self):
        """
        Scrape de cortes programados
        """
        try:
            logger.info("cnel_scraping_started", url=self.source_url)
            
            response = requests.get(self.source_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []
            
            # Buscar avisos de cortes
            # La estructura puede variar, buscar multiples patrones
            outage_sections = soup.find_all(['div', 'article', 'tr'], 
                                           class_=['corte', 'suspension', 'aviso', 'programacion'])
            
            if not outage_sections:
                # Buscar en tablas
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows[:5]:  # Maximo 5 cortes
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            event = {
                                'title': f"Corte programado - {cells[0].get_text(strip=True)}",
                                'content': ' | '.join([cell.get_text(strip=True) for cell in cells]),
                                'url': self.source_url,
                                'date': None,
                                'scraped_at': datetime.utcnow().isoformat()
                            }
                            events.append(event)
            else:
                # Procesar cada aviso de corte
                for section in outage_sections[:5]:
                    title_tag = section.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                    title = title_tag.get_text(strip=True) if title_tag else 'Corte programado de energia'
                    
                    content = section.get_text(strip=True)
                    
                    # Buscar fecha y hora
                    date_tag = section.find(['time', 'span'], class_=['date', 'fecha', 'hora'])
                    date = date_tag.get_text(strip=True) if date_tag else None
                    
                    event = {
                        'title': title,
                        'content': content[:500],
                        'url': self.source_url,
                        'date': date,
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    events.append(event)
            
            # Si no se encontraron eventos estructurados, buscar en el contenido general
            if not events:
                content = soup.get_text()
                keywords = ['corte', 'suspension', 'mantenimiento', 'energia', 'electrica']
                if any(keyword in content.lower() for keyword in keywords):
                    event = {
                        'title': 'Aviso de corte de energia detectado',
                        'content': content[:500],
                        'url': self.source_url,
                        'date': None,
                        'scraped_at': datetime.utcnow().isoformat()
                    }
                    events.append(event)
            
            logger.info("cnel_scraping_completed", events_found=len(events))
            return events
            
        except requests.RequestException as e:
            logger.error("cnel_scraping_failed", error=str(e))
            return []
        except Exception as e:
            logger.error("cnel_unexpected_error", error=str(e))
            return []
