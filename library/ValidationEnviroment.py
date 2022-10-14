import os
from library.Logging import Logging


class ValidationEnviroment:
    def __init__(self):
        self.namespaces = os.environ.get("NAMESPACES")
        self.excludeObject = os.environ.get("EXCLUDE_OBJECT_NAME")
        self.requestMemory = os.environ.get("REQUEST_MEMORY")
        self.requestCpu = os.environ.get("REQUEST_CPU")
        self.limitsMemory = os.environ.get("LIMITS_MEMORY")
        self.limitsCpu = os.environ.get("LIMITS_CPU")

    @property
    def namespaces(self):
        return self._namespaces

    @namespaces.setter
    def namespaces(self, value):
        Logging.logger.debug(f"I Namespaces verificati sono {value}")
        if not value:
            raise ValueError("NAMESPACES is not set.")
        self._namespaces = value.split(',')

    @property
    def excludeObject(self):
        return self._excludeObject

    @excludeObject.setter
    def excludeObject(self, value):
        Logging.logger.debug(f"Gli oggetti esclusi dalla verifica sono {value}")
        if not value:
            raise ValueError("List Object BlackList is not set.")
        self._excludeObject = value.split(',')

    @property
    def requestMemory(self):
        return self._requestMemory

    @requestMemory.setter
    def requestMemory(self, value):
        Logging.logger.debug(f"La whitelist della Request Memory {value}")
        if not value:
            raise ValueError("Limits Memory  is not set.")
        self._requestMemory = value.split(',')


    @property
    def requestCpu(self):
        return self._requestCpu

    @requestCpu.setter
    def requestCpu(self, value):
        Logging.logger.debug(f"La whitelist della Request CPU {value}")
        if not value:
            raise ValueError("Request Cpu  is not set.")
        self._requestCpu = value.split(',')


    @property
    def limitsMemory(self):
        return self._limitsMemory

    @limitsMemory.setter
    def limitsMemory(self, value):
        Logging.logger.debug(f"La whitelist della Limits Memory {value}")
        if not value:
            raise ValueError("Limits Memory  is not set.")
        self._limitsMemory = value.split(',')

    @property
    def limitsCpu(self):
        return self._limitsCpu

    @limitsCpu.setter
    def limitsCpu(self, value):
        Logging.logger.debug(f"La whitelist della Limits CPU {value}")
        if not value:
            raise ValueError("Limits Cpu  is not set.")
        self._limitsCpu = value.split(',')
