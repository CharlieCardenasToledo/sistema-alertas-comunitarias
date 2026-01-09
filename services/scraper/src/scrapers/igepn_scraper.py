"""
Scraper para Instituto Geofísico del Ecuador (IGEPN) - Sismos
URL: https://www.igepn.edu.ec/servicios/noticias
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()

class IGEPNScraper:
    """Scraper para eventos sísmicos del Instituto Geofísico"""
    
    def __init__(self, source_config: Dict):
        self.source_id = source_config['source_id']
        self.base_url = source_config['base_url']
        self.parser_config = source_config.get('parser_config', {})
        self.domain = source_config.get('domain', 'igepn.edu.ec')
        
    def scrape(self) -> Optional[Dict]:
        """Ejecuta el scraping y retorna evento crudo"""
        try:
            logger.info("scraping_started", source="IGEPN", url=self.base_url)
            
            # Hacer request con headers apropiados
            response = requests.get(
                self.base_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                },
                timeout=30
            )
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información usando selectores configurables
            title_selector = self.parser_config.get('title_selector', 'h1')
            date_selector = self.parser_config.get('date_selector', '.date, .fecha')
            content_selector = self.parser_config.get('content_selector', '.content, .contenido, p')
            
            title_elem = soup.select_one(title_selector)
            date_elem = soup.select_one(date_selector)
            content_elem = soup.select_one(content_selector)
            
            if not title_elem:
                logger.warning("no_title_found", url=self.base_url)
                # Intentar con selector alternativo
                title_elem = soup.find('h1') or soup.find('h2')
            
            if not title_elem:
                logger.error("no_content_found", url=self.base_url)
                return None
            
            # Construir payload crudo
            raw_payload = {
                'title': title_elem.get_text(strip=True) if title_elem else 'Sin título',
                'date': date_elem.get_text(strip=True) if date_elem else None,
                'content': content_elem.get_text(strip=True) if content_elem else None,
                'url': self.base_url,
                'domain': self.domain,
                'html_snippet': str(title_elem)[:500] if title_elem else '',
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            # Generar hash único basado en contenido
            content_for_hash = f"{raw_payload['title']}_{raw_payload['date']}_{raw_payload['url']}"
            raw_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
            
            event = {
                'source_id': self.source_id,
                'fetched_at': datetime.utcnow().isoformat(),
                'raw_payload': raw_payload,
                'raw_hash': raw_hash
            }
            
            logger.info("scraping_completed", 
                       source="IGEPN", 
                       hash=raw_hash[:8],
                       title=raw_payload['title'][:50])
            return event
            
        except requests.RequestException as e:
            logger.error("scraping_request_failed", 
                        source="IGEPN", 
                        error=str(e),
                        error_type=type(e).__name__)
            return None
        except Exception as e:
            logger.error("scraping_failed", 
                        source="IGEPN", 
                        error=str(e),
                        error_type=type(e).__name__)
            return None
