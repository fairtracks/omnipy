from typing import Annotated, Tuple, Type, Union

import pytest

from compute.helpers.mocks import (CommandMockJob,
                                   CommandMockJobTemplate,
                                   mock_cmd_func,
                                   MockJobBaseSubclass,
                                   MockJobConfig,
                                   MockJobSubclass,
                                   MockJobTemplateSubclass,
                                   MockLocalRunner,
                                   PublicPropertyErrorsMockJob,
                                   PublicPropertyErrorsMockJobTemplate)
from omnipy.compute.job import Job, JobBase, JobCreator, JobTemplate

from .helpers.functions import assert_updated_wrapper


def test_init_abstract():
    with pytest.raises(TypeError):
        JobBase()

    with pytest.raises(TypeError):
        JobTemplate()

    with pytest.raises(TypeError):
        Job()


def mock_job_classes() -> Tuple[Type[JobBase], Type[JobTemplate], Type[Job]]:
    return MockJobBaseSubclass, MockJobTemplateSubclass, MockJobSubclass


def test_init_mock():
    JobBase, JobTemplate, Job = mock_job_classes()  # noqa

    job_tmpl = JobTemplate()
    assert isinstance(job_tmpl, JobTemplate)

    job = job_tmpl.apply()
    assert isinstance(job, Job)


def test_fail_only_jobtemplate_init_mock():
    JobBase, JobTemplate, Job = mock_job_classes()  # noqa

    with pytest.raises(RuntimeError):
        JobBase()  # noqa

    with pytest.raises(RuntimeError):
        Job()


def test_job_creator_singular_mock(
        teardown_reset_job_creator: Annotated[None, pytest.fixture]) -> None:
    JobBase, JobTemplate, Job = mock_job_classes()  # noqa

    assert isinstance(JobBase.job_creator, JobCreator)

    with pytest.raises(AttributeError):
        JobBase.job_creator = JobCreator()

    with pytest.raises(AttributeError):
        JobTemplate.job_creator = JobCreator()

    with pytest.raises(AttributeError):
        Job.job_creator = JobCreator()

    job_creator = JobBase.job_creator
    assert JobTemplate.job_creator is job_creator
    assert Job.job_creator is job_creator

    job_tmpl = JobTemplate()
    assert job_tmpl.__class__.job_creator is job_creator

    job = job_tmpl.apply()
    assert job.__class__.job_creator is job_creator

    job_tmpl_new = JobTemplate()
    assert job_tmpl_new.__class__.job_creator is job_creator


def test_engine_mock(teardown_reset_job_creator: Annotated[None, pytest.fixture]):
    mock_local_runner = MockLocalRunner()
    JobBase, JobTemplate, Job = mock_job_classes()  # noqa

    assert JobTemplate.engine is None

    job_tmpl = JobTemplate()
    assert job_tmpl.engine is None
    assert job_tmpl.__class__.job_creator.engine is None

    JobTemplate.job_creator.set_engine(mock_local_runner)

    assert JobTemplate.job_creator.engine is mock_local_runner
    assert JobBase.job_creator.engine is mock_local_runner
    assert Job.job_creator.engine is mock_local_runner

    assert job_tmpl.engine is mock_local_runner
    assert job_tmpl.__class__.job_creator.engine is mock_local_runner

    job_tmpl_new = JobTemplate()
    assert job_tmpl_new is not job_tmpl
    assert job_tmpl_new.engine is mock_local_runner
    assert job_tmpl_new.__class__.job_creator.engine is mock_local_runner

    assert JobTemplate.engine is mock_local_runner

    assert not hasattr(JobTemplate, 'set_engine')
    assert not hasattr(JobBase, 'engine')
    assert not hasattr(JobBase, 'set_engine')
    assert not hasattr(Job, 'engine')
    assert not hasattr(Job, 'set_engine')


def test_config_mock(teardown_reset_job_creator: Annotated[None, pytest.fixture]):
    mock_job_config = MockJobConfig()
    JobBase, JobTemplate, Job = mock_job_classes()  # noqa

    assert JobTemplate.config is None

    job_tmpl = JobTemplate()
    assert job_tmpl.config is None
    assert job_tmpl.__class__.job_creator.config is None

    JobTemplate.job_creator.set_config(mock_job_config)

    assert JobTemplate.job_creator.config is mock_job_config
    assert JobBase.job_creator.config is mock_job_config
    assert Job.job_creator.config is mock_job_config

    assert job_tmpl.config is mock_job_config
    assert job_tmpl.apply().config is mock_job_config
    assert job_tmpl.__class__.job_creator.config is mock_job_config

    job_tmpl_new = JobTemplate()
    assert job_tmpl_new is not job_tmpl
    assert job_tmpl_new.config is mock_job_config
    assert job_tmpl_new.apply().config is mock_job_config
    assert job_tmpl_new.__class__.job_creator.config is mock_job_config

    assert JobBase.config is mock_job_config
    assert JobTemplate.config is mock_job_config
    assert Job.config is mock_job_config

    assert not hasattr(JobTemplate, 'set_config')
    assert not hasattr(JobBase, 'set_config')
    assert not hasattr(Job, 'set_config')


def test_equal_mock() -> None:
    JobBase, JobTemplate, Job = mock_job_classes()  # noqa

    my_job_tmpl = JobTemplate()
    my_job_tmpl_2 = JobTemplate()

    for (my_job_obj, my_job_obj_2) in [(my_job_tmpl, my_job_tmpl_2),
                                       (my_job_tmpl.apply(), my_job_tmpl_2.apply())]:
        assert my_job_obj == my_job_obj_2

    assert my_job_tmpl != "123"  # noqa


def test_subclass_equal() -> None:

    cmd_tmpl = CommandMockJobTemplate('erase', params=dict(what='all'))(mock_cmd_func)
    cmd_tmpl_2 = CommandMockJobTemplate('erase', params=dict(what='all'))(mock_cmd_func)

    for (cmd_obj, cmd_obj_2) in [(cmd_tmpl, cmd_tmpl_2), (cmd_tmpl.apply(), cmd_tmpl_2.apply())]:
        assert cmd_obj == cmd_obj_2

    cmd_tmpl_3 = CommandMockJobTemplate('restore', params=dict(what='all'))(mock_cmd_func)

    for (cmd_obj, cmd_obj_3) in [(cmd_tmpl, cmd_tmpl_3), (cmd_tmpl.apply(), cmd_tmpl_3.apply())]:
        assert cmd_obj != cmd_obj_3

    cmd_tmpl_4 = CommandMockJobTemplate('erase', params=dict(what='nothing'))(mock_cmd_func)

    for (cmd_obj, cmd_obj_4) in [(cmd_tmpl, cmd_tmpl_4), (cmd_tmpl.apply(), cmd_tmpl_4.apply())]:
        assert cmd_obj != cmd_obj_4


def _assert_immutable_command_mock_job_properties(
        cmd_obj: Union[CommandMockJobTemplate, CommandMockJob]) -> None:

    with pytest.raises(AttributeError):
        cmd_obj.uppercase = False  # noqa

    with pytest.raises(AttributeError):
        cmd_obj.params = {}  # noqa

    with pytest.raises(TypeError):
        cmd_obj.params['what'] = 'none'  # noqa

    with pytest.raises(TypeError):
        del cmd_obj.params['what']  # noqa


def test_subclass_tmpl():
    cmd_tmpl = CommandMockJobTemplate('erase')(mock_cmd_func)
    assert isinstance(cmd_tmpl, CommandMockJobTemplate)

    assert cmd_tmpl.uppercase is False
    assert cmd_tmpl.params == {}

    with pytest.raises(TypeError):
        cmd_tmpl()  # noqa

    _assert_immutable_command_mock_job_properties(cmd_tmpl)


def test_subclass_apply():
    cmd_tmpl = CommandMockJobTemplate(
        'erase', uppercase=True, params={'what': 'all'})(mock_cmd_func,)
    assert isinstance(cmd_tmpl, CommandMockJobTemplate)
    assert cmd_tmpl.engine_decorator_applied is False

    cmd = cmd_tmpl.apply()
    assert isinstance(cmd, CommandMockJob)
    assert cmd_tmpl.engine_decorator_applied is True
    assert_updated_wrapper(cmd, cmd_tmpl)

    assert cmd.uppercase is True
    assert cmd.params == {'what': 'all'}

    _assert_immutable_command_mock_job_properties(cmd)

    assert cmd() == 'ALL HAS BEEN ERASED'


def test_subclass_apply_revise():
    cmd_tmpl = CommandMockJobTemplate('restore', params={'what': 'nothing'})(mock_cmd_func)
    cmd = cmd_tmpl.apply()
    assert_updated_wrapper(cmd, cmd_tmpl)
    assert isinstance(cmd, CommandMockJob)

    assert cmd() == 'nothing has been restored'

    cmd_tmpl_revised = cmd.revise()
    assert_updated_wrapper(cmd_tmpl_revised, cmd)
    assert isinstance(cmd_tmpl_revised, CommandMockJobTemplate)

    assert cmd.uppercase is False
    assert cmd_tmpl_revised.params == {'what': 'nothing'}

    with pytest.raises(TypeError):
        cmd_tmpl_revised()  # noqa

    _assert_immutable_command_mock_job_properties(cmd_tmpl_revised)

    cmd_revised = cmd_tmpl_revised.apply()
    assert_updated_wrapper(cmd_revised, cmd_tmpl_revised)
    assert cmd_revised() == 'nothing has been restored'


def test_subclass_refine_empty():
    cmd_tmpl = CommandMockJobTemplate('restore', params={'what': 'nothing'})(mock_cmd_func)

    cmd_tmpl_refined = cmd_tmpl.refine()
    assert_updated_wrapper(cmd_tmpl_refined, cmd_tmpl)
    assert isinstance(cmd_tmpl_refined, CommandMockJobTemplate)
    assert cmd_tmpl_refined is not cmd_tmpl
    assert cmd_tmpl_refined == cmd_tmpl


def test_subclass_refine_scalar() -> None:
    # Job template with id and mapping property 'params' as dict
    all_erased_tmpl = CommandMockJobTemplate(
        'erase', id='all_erased', params={
            'what': 'all', 'where': 'everywhere'
        })(mock_cmd_func,)
    all_erased = all_erased_tmpl.apply()
    assert_updated_wrapper(all_erased, all_erased_tmpl)
    assert all_erased() == 'all has been erased, everywhere'

    # Refine job template with scalar property 'uppercase' as bool (update=True, default).
    # Other properties are unchanged
    shout_tmpl = all_erased_tmpl.refine(uppercase=True)
    assert_updated_wrapper(shout_tmpl, all_erased_tmpl)
    assert shout_tmpl != all_erased_tmpl
    for shout_obj in shout_tmpl, shout_tmpl.apply():
        assert_updated_wrapper(shout_obj, shout_tmpl)
        assert shout_obj.id == 'all_erased'
        assert shout_obj.uppercase is True
        assert shout_obj.params == dict(what='all', where='everywhere')

    shout = shout_tmpl.apply()
    assert_updated_wrapper(shout, shout_tmpl)
    assert shout != all_erased
    assert shout() == 'ALL HAS BEEN ERASED, EVERYWHERE'

    # Refine job template with id and scalar property 'uppercase' as bool (update=False).
    # Other properties are reset to default.
    silent_tmpl = shout_tmpl.refine(uppercase=False, update=False)  # noqa
    assert_updated_wrapper(silent_tmpl, shout_tmpl)
    assert silent_tmpl != shout_tmpl
    for silent_obj in silent_tmpl, silent_tmpl.apply():
        assert_updated_wrapper(silent_obj, silent_tmpl)
        assert silent_obj.id is ''
        assert silent_obj.uppercase is False
        assert silent_obj.params == {}

    silent = silent_tmpl.refine(id='silent').apply()
    assert_updated_wrapper(silent, silent_tmpl)
    assert silent != shout
    assert silent.id is 'silent'
    assert silent() == 'I know nothing'


def test_subclass_refine_mapping() -> None:
    # Job template with id and scalar property 'uppercase' as bool
    cmd_tmpl = CommandMockJobTemplate('restore', id='restore', uppercase=True)(mock_cmd_func)
    assert cmd_tmpl.id == 'restore'
    assert cmd_tmpl.uppercase is True
    assert cmd_tmpl.params == {}
    cmd = cmd_tmpl.apply()
    assert_updated_wrapper(cmd, cmd_tmpl)
    assert cmd() == 'I KNOW NOTHING'

    # Refine job template with mapping property 'params' as dict (update=True, default).
    # Other properties are unchanged. 'params' was previously empty and is now filled
    nicer_tmpl = cmd_tmpl.refine(params=dict(what='something', where='somewhere'))
    assert_updated_wrapper(nicer_tmpl, cmd_tmpl)
    assert nicer_tmpl != cmd_tmpl
    for nicer_obj in nicer_tmpl, nicer_tmpl.apply():
        assert nicer_obj.id == 'restore'
        assert nicer_obj.uppercase is True
        assert nicer_obj.params == dict(what='something', where='somewhere')

    nicer = nicer_tmpl.apply()
    assert_updated_wrapper(nicer, nicer_tmpl)
    assert nicer != cmd
    assert nicer() == 'SOMETHING HAS BEEN RESTORED, SOMEWHERE'

    # Refine job template with mapping property 'params' as list of tuples (update=True).
    # Other properties are unchanged, as well as other entries in 'params'
    secret_tmpl = nicer_tmpl.refine(params=[('where', 'but it is a secret')])  # noqa
    assert_updated_wrapper(secret_tmpl, nicer_tmpl)
    assert secret_tmpl != nicer_tmpl
    for secret_obj in secret_tmpl, secret_tmpl.apply():
        assert_updated_wrapper(secret_obj, secret_tmpl)
        assert secret_obj.id == 'restore'
        assert secret_obj.uppercase is True
        assert secret_obj.params == dict(what='something', where='but it is a secret')

    secret = secret_tmpl.apply()
    assert_updated_wrapper(secret, secret_tmpl)
    assert secret != nicer
    assert secret() == 'SOMETHING HAS BEEN RESTORED, BUT IT IS A SECRET'

    # Refine job template with 'params' as dict (update=False).
    # Other properties are reset to default. Previous 'params' mapping property is fully replaced
    nothing_tmpl = secret_tmpl.refine(params=dict(what='nothing'), update=False)
    assert_updated_wrapper(nothing_tmpl, secret_tmpl)
    assert nothing_tmpl != secret_tmpl
    for nothing_obj in nothing_tmpl, nothing_tmpl.apply():
        assert_updated_wrapper(nothing_obj, nothing_tmpl)
        assert nothing_obj.id is ''
        assert nothing_obj.uppercase is False
        assert nothing_obj.params == dict(what='nothing')

    nothing = nothing_tmpl.refine(id='nothing').apply()
    assert_updated_wrapper(nothing, nothing_tmpl)
    assert nothing != secret
    assert nothing.id is 'nothing'
    assert nothing() == 'nothing has been restored'


def test_subclass_refine_reset_mapping() -> None:
    cmd_tmpl = CommandMockJobTemplate('erase')(mock_cmd_func)
    cmd = cmd_tmpl.apply()
    assert_updated_wrapper(cmd, cmd_tmpl)
    assert cmd() == 'I know nothing'

    nothing_tmpl = cmd_tmpl.refine(uppercase=True, params=dict(what='nothing'))
    assert_updated_wrapper(nothing_tmpl, cmd_tmpl)
    nothing = nothing_tmpl.apply()
    assert_updated_wrapper(nothing, nothing_tmpl)
    assert nothing() == 'NOTHING HAS BEEN ERASED'

    # Resetting mapping property 'params' does not work with update=True
    reset_params_tmpl = nothing_tmpl.refine(params={})
    assert_updated_wrapper(reset_params_tmpl, nothing_tmpl)
    assert reset_params_tmpl == nothing_tmpl
    assert reset_params_tmpl.uppercase is True
    assert reset_params_tmpl.params == dict(what='nothing')

    # Reset mapping property 'params' with update=False.
    # Other properties needs to be explicitly added to not be reset
    for val in ({}, [], None):
        reset_params_tmpl = nothing_tmpl.refine(
            uppercase=nothing_tmpl.uppercase,
            params=val,
            update=False,
        )
        assert_updated_wrapper(reset_params_tmpl, nothing_tmpl)
        assert reset_params_tmpl != cmd_tmpl
        for reset_params_obj in reset_params_tmpl, reset_params_tmpl.apply():
            assert_updated_wrapper(reset_params_obj, reset_params_tmpl)
            assert reset_params_tmpl.uppercase is True
            assert reset_params_obj.params == {}

    # One-liner to reset job to default values
    reset = nothing.revise().refine(update=False).apply()
    assert_updated_wrapper(reset, nothing)

    assert reset == cmd
    assert reset() == 'I know nothing'
    assert reset.uppercase is False
    assert reset.params == {}


def test_revise_refine_mappings_are_copied() -> None:
    all_tmpl = CommandMockJobTemplate('erase', params={'what': 'all'})(mock_cmd_func)
    all_refined_tmpl = all_tmpl.refine(params=dict(where='everywhere'),)
    assert_updated_wrapper(all_refined_tmpl, all_tmpl)

    assert len(all_tmpl.params) == 1
    assert len(all_refined_tmpl.params) == 2

    all_job = all_tmpl.apply()
    assert_updated_wrapper(all_job, all_tmpl)
    all_revised_tmpl = all_job.revise()
    assert_updated_wrapper(all_revised_tmpl, all_job)
    all_revised_refined_tmpl = all_revised_tmpl.refine(params=dict(where='sadly'),)
    assert_updated_wrapper(all_revised_refined_tmpl, all_revised_tmpl)

    assert len(all_tmpl.params) == 1
    assert len(all_job.params) == 1
    assert all_job.params is not all_tmpl.params

    assert len(all_revised_tmpl.params) == 1
    assert all_revised_tmpl.params is not all_job.params

    assert len(all_revised_refined_tmpl.params) == 2


def test_subclass_apply_public_property_errors():
    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=None)
    job = job_tmpl.apply()
    assert isinstance(job, PublicPropertyErrorsMockJob)

    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=0)
    with pytest.raises(AttributeError):  # No attribute job_tmpl.verbose
        job_tmpl.apply()

    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=1)
    with pytest.raises(AttributeError):  # job_tmpl.cost is object attribute
        job_tmpl.apply()

    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=2)
    with pytest.raises(TypeError):  # job_tmpl.strength is class attribute
        job_tmpl.apply()

    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=3)
    with pytest.raises(TypeError):  # job_tmpl.power is method
        job_tmpl.apply()

    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=4)
    with pytest.raises(TypeError):  # job_tmpl.speed property is writable
        job_tmpl.apply()

    job_tmpl = PublicPropertyErrorsMockJobTemplate(property_index=5)
    with pytest.raises(TypeError):  # job_tmpl.params property value is mutable
        job_tmpl.apply()
