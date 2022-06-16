from abc import ABC, abstractmethod
import json
import os

import pandas as pd


class Data(ABC):
    @abstractmethod
    def validate(self):
        """
        Should raise an exception if data contents does not follow the requirements for the data
        class
        """

    @abstractmethod
    def read_from_dir(self, in_path):
        pass

    @abstractmethod
    def write_to_dir(self, out_path):
        pass


class NoData(Data):
    def validate(self):
        pass

    def read_from_dir(self, in_path):
        pass

    def write_to_dir(self, out_path):
        pass


class ObjectCollection(Data):
    OBJECT_TYPE = ''
    FILE_SUFFIX = ''

    def __init__(self):
        self._object_dict = {}
        super().__init__()

    def all_object_names(self):
        return list(self._object_dict.keys())

    def __setitem__(self, name: str, obj):
        self._object_dict[name] = obj

    def __getitem__(self, name: str):
        return self._object_dict[name]

    def validate(self):
        assert len(self._object_dict) > 0

        for obj in self._object_dict.values():
            self._validate_object(obj)

    @classmethod
    @abstractmethod
    def _validate_object(cls, obj):
        pass

    def read_from_dir(self, in_path):
        for filename in os.listdir(in_path):
            assert filename.endswith(self.FILE_SUFFIX)
            basename = filename[:-len(self.FILE_SUFFIX)]
            self._object_dict[basename] = self._read_object_from_file(
                os.path.join(in_path, filename))

    @classmethod
    @abstractmethod
    def _read_object_from_file(cls, file_path):
        pass

    def write_to_dir(self, out_path):
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        for name, obj in self._object_dict.items():
            self._write_object_to_file(obj, os.path.join(out_path, name + self.FILE_SUFFIX))

    @classmethod
    @abstractmethod
    def _write_object_to_file(cls, obj, file_path):
        pass

    def __str__(self):
        text = ''
        for name, obj in self._object_dict.items():
            text += f'{self.OBJECT_TYPE} "{name}"' + os.linesep
            text += self._object_to_string(obj) + os.linesep
        return text

    @classmethod
    @abstractmethod
    def _object_to_string(cls, obj):
        pass


class JsonDocumentCollection(ObjectCollection):
    OBJECT_TYPE = 'JSON document'
    FILE_SUFFIX = '.json'

    @classmethod
    def _read_object_from_file(cls, file_path):
        with open(file_path, encoding='utf8') as infile:
            return json.load(infile)

    @classmethod
    def _write_object_to_file(cls, obj, file_path):
        with open(file_path, 'w', encoding='utf8') as outfile:
            json.dump(obj, outfile, indent=4)
            outfile.write(os.linesep)

    @classmethod
    def _validate_object(cls, obj):
        pass

    @classmethod
    def _object_to_string(cls, obj):
        return json.dumps(obj, indent=4)


class PandasDataFrameCollection(ObjectCollection):
    OBJECT_TYPE = 'DataFrame'
    FILE_SUFFIX = '.csv'

    @classmethod
    def _read_object_from_file(cls, file_path):
        return pd.read_csv(file_path, index_col=0)

    @classmethod
    def _write_object_to_file(cls, obj, file_path):
        obj.to_csv(file_path)

    @classmethod
    def _validate_object(cls, obj):
        pass

    @classmethod
    def _object_to_string(cls, obj):
        return obj.to_string()
