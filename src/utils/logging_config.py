import sys
from loguru import logger

logger.remove(0)
logger.add(
    sys.stdout,
    format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}",
    serialize=False,
)

