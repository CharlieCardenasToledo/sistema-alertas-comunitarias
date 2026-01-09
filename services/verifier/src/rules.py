"""
Reglas de verificacion para calculo de score de confianza
"""
import requests
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class VerificationRules:
    """Conjunto de reglas para verificar eventos"""
    
    # Dominios en lista blanca (fuentes oficiales)
    TRUSTED_DOMAINS = [
        'igepn.edu.ec',
        'gestionderiesgos.gob.ec',
        'inamhi.gob.ec',
        'cnel.gob.ec',
        'epmaps.gob.ec',
        'bomberos.gob.ec'
    ]
    
    def __init__(self, db_conn):
        self.db_conn = db_conn
    
    def rule_trusted_domain(self, event):
        """
        R1: Dominio en lista blanca
        Puntos: +40
        """
        evidence_url = event.get('evidence_url', '')
        
        for domain in self.TRUSTED_DOMAINS:
            if domain in evidence_url:
                logger.info("rule_passed", rule="R1_trusted_domain", points=40)
                return 40
        
        logger.info("rule_failed", rule="R1_trusted_domain", points=0)
        return 0
    
    def rule_valid_url(self, event):
        """
        R2: URL valida y accesible
        Puntos: +15
        """
        evidence_url = event.get('evidence_url', '')
        
        if not evidence_url:
            logger.info("rule_failed", rule="R2_valid_url", reason="no_url")
            return 0
        
        try:
            response = requests.head(evidence_url, timeout=5, allow_redirects=True)
            if response.status_code < 400:
                logger.info("rule_passed", rule="R2_valid_url", points=15, status=response.status_code)
                return 15
            else:
                logger.info("rule_failed", rule="R2_valid_url", status=response.status_code)
                return 0
        except Exception as e:
            logger.warning("rule_failed", rule="R2_valid_url", error=str(e))
            return 0
    
    def rule_recent_timestamp(self, event):
        """
        R3: Timestamp reciente (ultimas 24 horas)
        Puntos: +15
        """
        occurred_at_str = event.get('occurred_at')
        
        if not occurred_at_str:
            logger.info("rule_failed", rule="R3_recent_timestamp", reason="no_timestamp")
            return 0
        
        try:
            occurred_at = datetime.fromisoformat(occurred_at_str.replace('Z', '+00:00'))
            now = datetime.utcnow()
            age = now - occurred_at.replace(tzinfo=None)
            
            if age <= timedelta(hours=24):
                logger.info("rule_passed", rule="R3_recent_timestamp", points=15, age_hours=age.total_seconds()/3600)
                return 15
            else:
                logger.info("rule_failed", rule="R3_recent_timestamp", age_hours=age.total_seconds()/3600)
                return 0
        except Exception as e:
            logger.warning("rule_failed", rule="R3_recent_timestamp", error=str(e))
            return 0
    
    def rule_complete_fields(self, event):
        """
        R4: Campos completos
        Puntos: +10
        """
        required_fields = ['type', 'zone', 'severity', 'title', 'evidence_url']
        optional_fields = ['description']
        
        score = 0
        
        # Verificar campos requeridos
        all_required = all(event.get(field) for field in required_fields)
        if all_required:
            score += 7
        
        # Verificar campos opcionales
        if event.get('description'):
            score += 3
        
        logger.info("rule_evaluated", rule="R4_complete_fields", points=score)
        return score
    
    def rule_cross_validation(self, event):
        """
        R5: Corroboracion cruzada (mismo evento de multiples fuentes)
        Puntos: +20
        """
        dedup_hash = event.get('dedup_hash')
        
        if not dedup_hash:
            return 0
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT source_id) as source_count
                FROM events
                WHERE dedup_hash = %s
            """, (dedup_hash,))
            
            result = cursor.fetchone()
            cursor.close()
            
            source_count = result[0] if result else 0
            
            if source_count >= 2:
                logger.info("rule_passed", rule="R5_cross_validation", points=20, sources=source_count)
                return 20
            else:
                logger.info("rule_failed", rule="R5_cross_validation", sources=source_count)
                return 0
                
        except Exception as e:
            logger.error("rule_error", rule="R5_cross_validation", error=str(e))
            return 0
    
    def calculate_score(self, event):
        """
        Calcular score total aplicando todas las reglas
        """
        score = 0
        
        score += self.rule_trusted_domain(event)
        score += self.rule_valid_url(event)
        score += self.rule_recent_timestamp(event)
        score += self.rule_complete_fields(event)
        score += self.rule_cross_validation(event)
        
        logger.info("score_calculated", total_score=score)
        return score
    
    def determine_status(self, score):
        """
        Determinar estado segun score
        - CONFIRMADO: score >= 70
        - EN_VERIFICACION: 40 <= score < 70
        - NO_VERIFICADO: score < 40
        """
        if score >= 70:
            return 'CONFIRMADO'
        elif score >= 40:
            return 'EN_VERIFICACION'
        else:
            return 'NO_VERIFICADO'
