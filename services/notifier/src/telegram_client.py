"""
Cliente de Telegram para envio de notificaciones
"""
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import structlog

logger = structlog.get_logger()

class TelegramClient:
    """Cliente para enviar notificaciones via Telegram"""
    
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        
    async def send_notification(self, chat_id, event):
        """
        Enviar notificacion de evento a un chat
        """
        try:
            # Formatear mensaje
            message = self._format_message(event)
            
            # Enviar mensaje
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            
            logger.info("telegram_notification_sent",
                       chat_id=chat_id,
                       event_id=event.get('event_id'))
            return True
            
        except TelegramError as e:
            logger.error("telegram_send_failed",
                        chat_id=chat_id,
                        error=str(e))
            return False
        except Exception as e:
            logger.error("telegram_unexpected_error",
                        error=str(e))
            return False
    
    def _format_message(self, event):
        """
        Formatear mensaje de notificacion
        """
        type_emoji = {
            'sismo': '🌍',
            'lluvia': '🌧️',
            'corte': '⚡'
        }
        
        severity_emoji = {
            'Alta': '🔴',
            'Media': '🟡',
            'Baja': '🟢'
        }
        
        event_type = event.get('type', 'evento')
        severity = event.get('severity', 'Baja')
        zone = event.get('zone', 'Desconocida')
        title = event.get('title', 'Sin titulo')
        description = event.get('description', '')
        evidence_url = event.get('evidence_url', '')
        score = event.get('score', 0)
        
        # Construir mensaje
        message = f"{type_emoji.get(event_type, '📢')} <b>ALERTA: {event_type.upper()}</b>\n\n"
        message += f"{severity_emoji.get(severity, '⚪')} <b>Severidad:</b> {severity}\n"
        message += f"📍 <b>Zona:</b> {zone}\n"
        message += f"⭐ <b>Confianza:</b> {score}/100\n\n"
        message += f"<b>{title}</b>\n"
        
        if description:
            # Limitar descripcion a 200 caracteres
            desc_preview = description[:200] + '...' if len(description) > 200 else description
            message += f"\n{desc_preview}\n"
        
        if evidence_url:
            message += f"\n🔗 <a href='{evidence_url}'>Ver fuente oficial</a>"
        
        message += f"\n\n<i>Sistema de Alertas Comunitarias Verificadas</i>"
        
        return message
    
    async def test_connection(self):
        """
        Probar conexion con Telegram
        """
        try:
            me = await self.bot.get_me()
            logger.info("telegram_bot_connected",
                       bot_username=me.username,
                       bot_id=me.id)
            return True
        except Exception as e:
            logger.error("telegram_connection_failed", error=str(e))
            return False
