import abc


class DataType(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def validate(self):
        """

        :return: True if contents follows requirments for data type
        """
        pass