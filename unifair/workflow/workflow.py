import abc


class WorkflowStep(metaclass=abc.ABCMeta):
    def __init__(self):
        self._input_data_type = self._get_input_data_type()
        self._input_data_type = self._get_output_data_type()

    @abc.abstractmethod
    def _get_input_data_type(self):
        pass

    @abc.abstractmethod
    def _get_output_data_type(self):
        pass

    @abc.abstractmethod
    def run(self, input):
        self._input_data_type.validate(input)
        output = self._run(input)
        self._input_data_type.validate(output)

    @abc.abstractmethod
    def _run(self):
        pass


class Workflow(metaclass=abc.ABCMeta):
    def __init__(self):
        self._steps = []

    def add_step(self, step):
        assert isinstance(step, WorkflowStep)
        self._steps.append(step)

    def run(self, input):
        cur_data = input
        for step in self._steps:
            cur_data = step.run(cur_data)
        return cur_data
