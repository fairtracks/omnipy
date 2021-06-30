import os
from abc import ABC, abstractmethod

import pandas as pd


class Data(ABC):
    @abstractmethod
    def validate(self):
        """
        Should raise an exception if data contents does not follow the requirements for the data class
        """
        pass

    def read_from_file(self, in_path):
        self._read(in_path)

    @abstractmethod
    def _read(self, in_path):
        pass

    def write_to_file(self, out_path):
        self._write(out_path)

    @abstractmethod
    def _write(self, out_path):
        pass


class NoData(Data):
    def validate(self):
        pass

    def _read(self, in_path):
        pass

    def _write(self, out_path):
        pass


class PandasDataFrames(Data):
    def __init__(self):
        self._dataframe_dict = {}

    def all_dataframe_names(self):
        return list(self._dataframe_dict.keys())

    def add_dataframe(self, name: str, dataframe: pd.DataFrame):
        self._dataframe_dict[name] = dataframe

    def get_dataframe(self, name: str):
        return self._dataframe_dict[name]

    def validate(self):
        assert len(self._dataframe_dict) > 0

        for df in self._dataframe_dict.values():
            self._validate_dataframe(df)

    def _validate_dataframe(self, dataframe):
        pass

    def _read(self, in_path):
        for csv_filename in os.listdir(in_path):
            assert csv_filename.endswith('.csv')
            self._dataframe_dict[csv_filename[:-4]] = pd.read_csv(os.path.join(in_path, csv_filename))

    def _write(self, out_path):
        os.makedirs(out_path)
        for name, df in self._dataframe_dict.items():
            df.to_csv(os.path.join(out_path, name + '.csv'))

    def __str__(self):
        text = ''
        for name, df in self._dataframe_dict.items():
            text += 'DataFrame "{}"'.format(name) + os.linesep
            text += df.to_string() + os.linesep
        return text