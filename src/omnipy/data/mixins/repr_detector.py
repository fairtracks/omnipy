from abc import ABCMeta, abstractmethod
import readline
from typing import cast

from IPython import get_ipython

from omnipy.api.enums import DataReprState
from omnipy.api.exceptions import ShouldNotOccurException
from omnipy.api.protocols.private.data import IsDataClassBase
from omnipy.data.data_class_creator import DataClassBase
from omnipy.util.contexts import hold_and_reset_prev_attrib_value
from omnipy.util.helpers import is_unreserved_identifier


class ReprDetectorMixin(metaclass=ABCMeta):
    def __repr__(self) -> str:
        match cast(IsDataClassBase, self).repr_state:
            case DataReprState.UNKNOWN:
                with hold_and_reset_prev_attrib_value(self, 'repr_state'):
                    if cast(
                            IsDataClassBase, self
                    ).config.interactive_mode and self._repr_is_from_self_enter_in_console():
                        self.repr_state = DataReprState.REPR_FROM_CONSOLE
                    else:
                        self.repr_state = DataReprState.REPR_NOT_FROM_CONSOLE
                    return repr(self)
            case DataReprState.REPR_FROM_CONSOLE:
                return self._fancy_repr()
            case DataReprState.REPR_NOT_FROM_CONSOLE:
                return super().__repr__()
            case _:
                raise ShouldNotOccurException()

    def _repr_is_from_self_enter_in_console(self) -> bool:
        last_command = self._get_last_interactive_console_command()
        if last_command and is_unreserved_identifier(last_command):
            console_globals = self._get_globals_from_console_frame()
            if last_command in console_globals and isinstance(console_globals[last_command],
                                                              DataClassBase):
                return True
        return False

    @classmethod
    def _get_last_interactive_console_command(cls) -> str | None:
        command = readline.get_history_item(readline.get_current_history_length())
        if not command:
            ipython = get_ipython()
            if ipython is not None:
                command = ipython.history_manager.input_hist_raw[-1]
        return command

    @classmethod
    def _get_globals_from_console_frame(cls) -> dict[str, object]:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            return ipython.user_ns
        else:
            import inspect
            frame = inspect.currentframe()
            while frame is not None:
                if frame.f_code.co_name == '<module>':
                    return frame.f_globals
                frame = frame.f_back
        return {}

    @abstractmethod
    def _fancy_repr(self) -> str:
        ...

    def view(self) -> None:
        print(self._fancy_repr())
