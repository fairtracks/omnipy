from abc import ABC, abstractmethod
from datetime import datetime
import os

from unifair.core.data import NoData


class WorkflowStep(ABC):
    @staticmethod
    @abstractmethod
    def _get_name():
        pass

    @abstractmethod
    def _get_input_data_cls(self):
        pass

    @abstractmethod
    def _get_output_data_cls(self):
        pass

    def run(self, invocation_dir, in_data_dirname):
        input_data_cls = self._get_input_data_cls()
        output_data_cls = self._get_output_data_cls()

        if in_data_dirname:
            in_path = os.path.join(invocation_dir, in_data_dirname)
            input_data = input_data_cls.read_from_dir(in_path)
        else:
            input_data = NoData()

        out_data_dirname = self._get_name()
        out_path = os.path.join(invocation_dir, out_data_dirname)
        self._validate_data_object(input_data, input_data_cls, input_data=True)
        output_data = self._run(input_data)
        self._validate_data_object(output_data, output_data_cls, input_data=False)
        output_data.write_to_dir(out_path)

        return out_data_dirname

    @staticmethod
    def _validate_data_object(data_obj, data_cls, input_data):
        assert isinstance(data_obj, data_cls), \
            '{} data object is not a subclass of {}, as required.'.format(
                'Input' if input_data else 'Output', data_cls
        )
        data_obj.validate()

    @abstractmethod
    def _run(self, input_data):
        pass


class Workflow:
    def __init__(self):
        self._steps = []

    def add_step(self, step):
        assert isinstance(step, WorkflowStep)
        self._steps.append(step)

    def run(self, data_path):
        invocation_dir = os.path.join(data_path, datetime.now().strftime('%d_%m_%Y_%H_%M_%S'))
        os.makedirs(invocation_dir)
        cur_data_dirname = ''

        for step in self._steps:
            cur_data_dirname = step.run(invocation_dir, cur_data_dirname)
        return invocation_dir
