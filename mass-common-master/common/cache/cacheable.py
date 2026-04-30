import shutil
from pathlib import Path

from common import logging
from common.serialization import Serializable

from .args import parser

CACHE_DIRECTORY = "~/.cache/mass"

log = logging.getLogger(__name__)
args, _ = parser.parse_known_args()


def clear():
    path = Path(CACHE_DIRECTORY).expanduser()
    shutil.rmtree(path, ignore_errors=True)
    log.info(f'Cleared cache folder ({path})')


if args.cache_clear:
    clear()


class Cacheable(Serializable):
    def cache_params(self):
        """Generator used to determine cached data parametrization.

        Example:
        ```
        def cache_params(self)
            yield self.uuid
            yield self.unique_name
        ```

        Above example will result file name:
        ```
        "ClassName_UUID_UniqueName.json"
        ```
        """
        name = type(self).__name__
        raise NotImplementedError(f'Cache parameters not specified for {name}')

    def cache_is_usable(self, *params) -> bool:
        """Tests is cache file can be loaded. Has priority over loading cache via `cache_params`.

        Args:
            params: list of parameters

        Returns:
            True if file can be used as cache, False otherwise
        """
        return False

    @property
    def cache_path(self) -> Path:
        """Based on cache parameters it constructs cache file path.

        Returns:
            Path for storing cache
        """
        path = Path(CACHE_DIRECTORY).expanduser()

        name = type(self).__name__
        params = (str(x) for x in self.cache_params())
        return path / f'{name}_{"_".join(params)}.json'

    @property
    def cache_path_usable(self) -> Path:
        """Finds usable cache file."""
        path = Path(CACHE_DIRECTORY).expanduser()
        name = type(self).__name__
        for file in path.glob(f'{name}_*.json'):
            params = str(file.stem).split('_')
            if self.cache_is_usable(*params):
                return file

        return None

    def cache_save(self):
        """Saves class data to cache file"""
        if args.cache_disable:
            return
        path = self.cache_path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.to_file(path)
        log.info(f'Saved cache to {path.name}')

    def cache_load(self) -> bool:
        """Loads class data from cache file

        Returns:
            True if cache was loaded successfully,
            False otherwise
        """
        if args.cache_disable:
            return False
        path = self.cache_path_usable or self.cache_path
        loaded = not args.cache_disable and path is not None and path.exists()
        if loaded:
            self.deserialize_from_file(path)
            log.info(f'Loaded cache from {path.name}')
        return loaded
