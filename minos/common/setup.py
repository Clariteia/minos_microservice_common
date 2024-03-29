from __future__ import (
    annotations,
)

import logging
import warnings
from pathlib import (
    Path,
)
from typing import (
    Optional,
    Type,
    TypeVar,
    Union,
)

from dependency_injector.wiring import (
    Provide,
    inject,
)

from .configuration import (
    MinosConfig,
)
from .exceptions import (
    NotProvidedException,
)

logger = logging.getLogger(__name__)


class MinosSetup:
    """Minos setup base class."""

    def __init__(self, *args, already_setup: bool = False, **kwargs):
        self._already_setup = already_setup

    @property
    def already_setup(self) -> bool:
        """Already Setup getter.

        :return: A boolean value.
        """
        return self._already_setup

    @property
    def already_destroyed(self) -> bool:
        """Already Destroy getter.

        :return: A boolean value.
        """
        return not self._already_setup

    @classmethod
    def from_config(cls: Type[S], config: Optional[Union[MinosConfig, Path]] = None, **kwargs) -> S:
        """Build a new instance from config.

        :param config: Config instance. If `None` is provided, default config is chosen.
        :param kwargs: Additional named arguments.
        :return: A instance of the called class.
        """
        if config is None:
            config = cls._get_config()
        elif isinstance(config, Path):
            config = MinosConfig(config)

        logger.info(f"Building a {cls.__name__!r} instance from config...")
        return cls._from_config(config=config, **kwargs)

    @staticmethod
    @inject
    def _get_config(config: MinosConfig = Provide["config"]) -> MinosConfig:
        if isinstance(config, Provide):
            raise NotProvidedException("The config object must be provided.")
        return config

    @classmethod
    def _from_config(cls: Type[S], config: MinosConfig, **kwargs) -> S:
        return cls(**kwargs)

    async def __aenter__(self: S) -> S:
        await self.setup()
        return self

    async def setup(self) -> None:
        """Setup miscellaneous repository things.

        :return: This method does not return anything.
        """
        if not self._already_setup:
            logger.info(f"Setting up a {type(self).__name__!r} instance...")
            await self._setup()
            self._already_setup = True

    async def _setup(self) -> None:
        return

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        await self.destroy()

    async def destroy(self) -> None:
        """Destroy miscellaneous repository things.

        :return: This method does not return anything.
        """
        if self._already_setup:
            logger.info(f"Destroying a {type(self).__name__!r} instance...")
            await self._destroy()
            self._already_setup = False

    async def _destroy(self) -> None:
        """Destroy miscellaneous repository things."""

    def __del__(self):
        if not self.already_destroyed:
            warnings.warn(
                f"A not destroyed {type(self).__name__!r} instance is trying to be deleted...", ResourceWarning
            )


S = TypeVar("S", bound=MinosSetup)
