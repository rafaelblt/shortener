import asyncio
import logging

from datetime import timedelta
from typing import Final

from aio_pika.abc import AbstractIncomingMessage

from shortener.consumer.user_deleted_message import parse_user_id
from shortener.use_cases.delete_shorturls_of_user import DeleteShortURLsOfUser
from shortener.use_cases.unavailable_error import UnavailableError


RETRY_DELAY: Final = timedelta(seconds=5)

logger = logging.getLogger(__name__)


class UserDeletedHandler:
    """
    Acknowledges a message only after its short URLs are deleted, and rejects
    the ones it can't process. See docs/architecture/consumer.md#handling
    """

    def __init__(
        self,
        delete_shorturls_of_user: DeleteShortURLsOfUser,
        retry_delay: timedelta = RETRY_DELAY,
    ):
        self._delete_shorturls_of_user = delete_shorturls_of_user
        self._retry_delay = retry_delay

    async def handle(self, message: AbstractIncomingMessage) -> None:
        user_id = parse_user_id(message.body)
        if user_id is None:
            logger.warning("Rejected a message that isn't a deleted user")
            await message.reject()
            return
        try:
            await self._delete_shorturls_of_user.execute(user_id)
        except UnavailableError as error:
            logger.warning("Requeued the deleted user %s", user_id, exc_info=error)
            # Without the pause, the message would come back at once, and be
            # tried as fast as it fails.
            await asyncio.sleep(self._retry_delay.total_seconds())
            await message.reject(requeue=True)
            return
        except Exception:
            # Trying again won't fix a bug. Raised, the message would stay
            # unacknowledged, and hold the queue, until the channel closes.
            logger.exception("Rejected the deleted user %s", user_id)
            await message.reject()
            return
        await message.ack()
