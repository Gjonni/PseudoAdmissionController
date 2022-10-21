import os
import re
from library.Logging import Logging

class add_attribute(dict):
    def __init__(self, dic):
        for key, val in dic.items():
            self.__dict__[key] = self[key] = val


def conv_memory_to_bytes(memory):
    Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_MEMORY_TO_BYTES -- START -- Memory with UNIT: {memory}")
    units = {"B": 1, "Ki": 1024, "Mi": 1048576, "Gi": 1073741824, "KiB": 1024, "MiB": 1048576, "GiB": 1073741824}
    try:
        number, unit = re.search("(^\d*)([a-zA-Z]{1,3}$)", memory).groups()
    except:
        if not memory:
            Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_MEMORY_TO_BYTES -- EXCEPT -- Memory NOT SET, return 0")
            return 0
        Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_MEMORY_TO_BYTES -- EXCEPT -- Memory Already in Bytes: {int(memory)}")
        return int(memory)
    Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_MEMORY_TO_BYTES -- END -- Memory in Bytes: {int(float(number)*units[unit])}")
    return int(float(number)*units[unit])


def conv_core_to_millicore(cpu):
    Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_CORE_TO_MILLICORE -- START -- CPU with UNIT: {cpu}")
    try:
        number, unit = re.search("(^\d*)([a-zA-Z]{1,3}$)", cpu).groups()
    except:
        Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_CORE_TO_MILLICORE -- EXCEPT -- CPU Already in Bytes: {int(float(cpu)*1000)}")
        return int(float(cpu)*1000)
    Logging.logger.debug(f"CLASS ValidationEnviroment - DEF CONV_CORE_TO_MILLICORE -- END -- CPU in Bytes: {int(number)}")
    return int(number)


class ValidationEnviroment:
    def __init__(self):
        self.namespaces = os.environ.get("NAMESPACES")
        self.excludeObject = os.environ.get("EXCLUDE_OBJECT_NAME")
        self.requestMemory = os.environ.get("REQUEST_MEMORY")
        self.requestCpu = os.environ.get("REQUEST_CPU")
        self.limitsMemory = os.environ.get("LIMITS_MEMORY")
        self.limitsCpu = os.environ.get("LIMITS_CPU")

    def memory_range_to_dict(self, mem_range):
        mem_range = {
            'min': mem_range.split('-')[0],
            'max': mem_range.split('-')[-1]
        }
        if len(mem_range['min']) == 0:
            mem_range['min'] = 0
        if len(mem_range['max']) == 0:
            mem_range['max'] = "100Gi"
        return mem_range

    def cpu_range_to_dict(self, cpu_range):
        cpu_range = {
            'min': cpu_range.split('-')[0],
            'max': cpu_range.split('-')[-1]
        }
        if len(cpu_range['min']) == 0:
            cpu_range['min'] = 0
        if len(cpu_range['max']) == 0:
            cpu_range['max'] = "100"
        return cpu_range

    @property
    def namespaces(self):
        return self._namespaces

    @namespaces.setter
    def namespaces(self, value):
        Logging.logger.debug(f"The check Namespaces are {value}")
        if not value:
            raise ValueError("NAMESPACES is not set.")
        self._namespaces = value.split(',')

    @property
    def excludeObject(self):
        return self._excludeObject

    @excludeObject.setter
    def excludeObject(self, value):
        Logging.logger.debug(f"The objects excluded from check are: {value}")
        if not value:
            value = ""
            raise ValueError("List Object BlackList is not set.")
        self._excludeObject = value.split(',')

    # Memory Request
    @property
    def requestMemory(self):
        return self._requestMemory

    @requestMemory.setter
    def requestMemory(self, value):
        Logging.logger.debug(f"CLASS ValidationEnviroment -- START -- Memory Request: {value}")
        if not value or '-' not in value:
            raise ValueError("The ENV: REQUEST_MEMORY is not set correctly.")

        value = self.memory_range_to_dict(value)
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to MEMORY_RANGE_TO_DICT --  Request Memory {value}")

        value['min'] = conv_memory_to_bytes(value['min'])
        value['max'] = conv_memory_to_bytes(value['max'])
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to CONV_MEMORY_TO_BYTES --  Request Memory {value}")

        self._requestMemory = add_attribute(value)

    # CPU Request
    @property
    def requestCpu(self):
        return self._requestCpu

    @requestCpu.setter
    def requestCpu(self, value):
        Logging.logger.debug(f"CLASS ValidationEnviroment -- START -- Request Memory {value}")
        if not value:
            raise ValueError("The ENV: REQUEST_CPU is not set correctly.")

        value = self.cpu_range_to_dict(value)
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to CPU_RANGE_TO_DICT --  Request CPU {value}")

        value['min'] = conv_core_to_millicore(value['min'])
        value['max'] = conv_core_to_millicore(value['max'])
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to CONV_CORE_TO_MILLICORE --  Request CPU {value}")

        self._requestCpu = add_attribute(value)

    # Memory Limits
    @property
    def limitsMemory(self):
        return self._limitsMemory

    @limitsMemory.setter
    def limitsMemory(self, value):
        Logging.logger.debug(f"CLASS ValidationEnviroment -- START -- Memory Limits: {value}")
        if not value or '-' not in value:
            raise ValueError("The ENV: LIMITS_MEMORY is not set correctly.")

        value = self.memory_range_to_dict(value)
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to MEMORY_RANGE_TO_DICT --  Memory Limits {value}")

        value['min'] = conv_memory_to_bytes(value['min'])
        value['max'] = conv_memory_to_bytes(value['max'])
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to CONV_MEMORY_TO_BYTES --  Memory Limits {value}")

        self._limitsMemory = add_attribute(value)

    # CPU Limits
    @property
    def limitsCpu(self):
        return self._limitsCpu

    @limitsCpu.setter
    def limitsCpu(self, value):
        Logging.logger.debug(f"La whitelist della Limits CPU {value}")
        if not value:
            raise ValueError("The ENV: LIMITS_CPU is not set correctly.")

        value = self.cpu_range_to_dict(value)
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to CPU_RANGE_TO_DICT -- CPU Limits {value}")

        value['min'] = conv_core_to_millicore(value['min'])
        value['max'] = conv_core_to_millicore(value['max'])
        Logging.logger.debug(f"CLASS ValidationEnviroment -- RETURN to CONV_CORE_TO_MILLICORE -- CPU Limits {value}")

        self._limitsCpu = add_attribute(value)
