from abc import ABC, abstractmethod


class WorkflowStep(ABC):
    @abstractmethod
    def _get_input_data_cls(self):
        pass

    @abstractmethod
    def _get_output_data_cls(self):
        pass

    def run(self, input_data):
        self._validate_data_object(input_data, self._get_input_data_cls(), input_data=True)
        output_data = self._run(input_data)
        self._validate_data_object(output_data, self._get_output_data_cls(), input_data=False)
        return output_data

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

    def run(self, input_data):
        cur_data = input_data
        for step in self._steps:
            cur_data = step.run(cur_data)
        return cur_data
