import os
from abc import ABC, abstractmethod

import pandas


class Data(ABC):
    @abstractmethod
    def validate(self):
        """

        :return: True if contents follows requirments for data type
        """
        pass


class NoData(Data):
    def validate(self):
        pass


class PandasDataFrames(Data):
    def __init__(self):
        self._dataframe_dict = {}

    def add_data_frame(self, name: str, dataframe: pandas.DataFrame):
        self._dataframe_dict[name] = dataframe

    def validate(self):
        assert len(self._dataframe_dict) > 0

        for df in self._dataframe_dict.values():
            self._validate_dataframe(df)

    def _validate_dataframe(self, dataframe):
        pass

    def __str__(self):
        text = ''
        for name, df in self._dataframe_dict.items():
            text += 'DataFrame "{}"'.format(name) + os.linesep
            text += df.to_string() + os.linesep
        return text
# class PandasDataFramesWithReferences(DataType):
#     def __init__(self):
#         self._dataframe_dict = {}
#         self._references_dict = {}
#
#     def add_data_frame(self, name: str, dataframe: pandas.DataFrame):
#         pass
#
#     def _validate_dataframe(self, dataframe):
#         pass

