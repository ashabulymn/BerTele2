import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.config import get_settings
from app.core.database import create_engine, create_session_factory
from app.events import EventBroker
from app.integrations.webhook.delivery import WebhookDeliveryService
from app.integrations.webhook.dispatcher import WebhookDispatcher
from app.integrations.webhook.manager import WebhookManager
from app.integrations.webhook.repository import WebhookRepository
from app.integrations.webhook.retry import WebhookRetryPolicy
from app.integrations.webhook.signer import WebhookSigner
from app.plugins.manager import PluginManager
from app.services.telegram_service import TelegramService
from app.session.manager import SessionManager
from app.session.repository import SessionRepository
from app.session.service import SessionService
from app.session.storage import SessionStorage
from app.telegram.media.service import TelegramMediaService, build_telegram_media_service


class AppContainer:
    def __init__(self) -> None:
        settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.engine: AsyncEngine = create_engine(settings)
        self.session_factory: async_sessionmaker[AsyncSession] = create_session_factory(self.engine)
        self.event_broker = EventBroker(logger=self.logger)
        self.telegram_service = TelegramService(settings=settings, logger=self.logger)
        self.telegram_media_service: TelegramMediaService = build_telegram_media_service(
            settings=settings,
            telegram_service=self.telegram_service,
            logger=self.logger,
        )
        self.webhook_retry_policy = WebhookRetryPolicy()
        self.webhook_signer = WebhookSigner()
        self.plugin_manager = PluginManager(event_broker=self.event_broker, logger=self.logger)

    def session_service(self, session: AsyncSession) -> SessionService:
        storage = SessionStorage(session)
        repository = SessionRepository(storage)
        manager = SessionManager(repository=repository, logger=self.logger)
        return SessionService(manager=manager)

    def webhook_manager(self, session: AsyncSession) -> WebhookManager:
        repository = WebhookRepository(session)
        delivery_service = WebhookDeliveryService(
            logger=self.logger,
            signer=self.webhook_signer,
            retry_policy=self.webhook_retry_policy,
        )
        dispatcher = WebhookDispatcher(repository=repository, delivery_service=delivery_service, logger=self.logger)
        manager = WebhookManager(
            broker=self.event_broker,
            repository=repository,
            dispatcher=dispatcher,
            logger=self.logger,
        )
        manager.subscribe()
        return manager

    async def start(self) -> None:
        self.logger.info("Starting application container")
        await self.telegram_service.connect()

    async def stop(self) -> None:
        self.logger.info("Stopping application container")
        await self.telegram_service.disconnect()
        await self.engine.dispose()
