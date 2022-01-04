from typing import Union
import asyncio
import logging
from urllib.parse import urlparse

from nio import AsyncClient, MatrixRoom, RoomMessageFile, RoomEncryptedFile
import nio.crypto

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

        file_size_bytes = self.event.source["content"]["info"]["size"]
        if file_size_bytes is None or file_size_bytes > 10_000_000:
            logger.info("Skipping %s because it's too large: %d", self.filename, file_size_bytes)
            return

        url = urlparse(self.event.url)
        response = await self.client.download(
            url.hostname,
            url.path[1:],  # Strip the leading '/'
            self.filename,
            allow_remote=False
        )
        logger.debug(response)

        if hasattr(self.event, "key"):
            # We got an encrypted event
            logger.debug("About to decrypt file %s", self.filename)
            decryption_keys = {
                "key": self.event.key["k"],
                "hash": self.event.hashes["sha256"],
                "iv": self.event.iv,
            }
            decrypted_content = nio.crypto.decrypt_attachment(response.body, **decryption_keys)
        else:
            decrypted_content = response.body

        PIPE = asyncio.subprocess.PIPE
        proc = await asyncio.create_subprocess_exec(
            "/usr/bin/lp", "-d", "MFC-1910W", stdin=PIPE, stdout=PIPE, stderr=PIPE
        )

        stdout, stderr = await proc.communicate(decrypted_content)
        if stderr:
            logger.error("Error printing file %s.\nStdout %s\nStderr %s", self.filename, stdout, stderr)
        else:
            logger.debug("Printed file %s. Stdout %s", self.filename, stdout)
