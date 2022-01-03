from typing import Union
import logging

from nio import AsyncClient, MatrixRoom, RoomMessageFile, RoomEncryptedFile

from matrix_printer_bot.config import Config
from matrix_printer_bot.storage import Storage

logger = logging.getLogger(__name__)

class UploadedFile:
    def __init__(
        self,
        client: AsyncClient,
        store: Storage,
        config: Config,
        filename: str,
        room: MatrixRoom,
        event: Union[RoomMessageFile, RoomEncryptedFile],
    ):
        """A file uploaded by a user."""
        self.client = client
        self.store = store
        self.config = config
        self.filename = filename
        self.room = room
        self.event = event

    async def process(self) -> None:
        if not self.filename.endswith(".pdf"):
            logger.debug("Not responding to non-pdf file %s", self.filename)
            return