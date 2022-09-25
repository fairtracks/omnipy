from typing import Tuple, Type

import pytest

from compute.helpers.mocks import (CommandMockJob,
                                   CommandMockJobTemplate,
                                   MockJobConfigSubclass,
                                   MockJobSubclass,
                                   MockJobTemplateSubclass,
                                   PublicPropertyErrorsMockJob,
                                   PublicPropertyErrorsMockJobTemplate)
from unifair.compute.job import Job, JobConfig, JobCreator, JobTemplate


def test_init_abstract():
    with pytest.raises(TypeError):
        JobConfig()

    with pytest.raises(TypeError):
        JobTemplate()

    with pytest.raises(TypeError):
        Job()


def mock_job_classes() -> Tuple[Type[JobConfig], Type[JobTemplate], Type[Job]]:
    return MockJobConfigSubclass, MockJobTemplateSubclass, MockJobSubclass


def test_init_mock():
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    job_template = JobTemplate()
    assert isinstance(job_template, JobTemplate)
    assert job_template.name is None

    job_template = JobTemplate(name='name')
    assert job_template.name == 'name'

    job = job_template.apply()
    assert isinstance(job, Job)
    assert job.name == job_template.name


def test_fail_only_jobtemplate_init_mock():
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    with pytest.raises(RuntimeError):
        JobConfig()  # noqa

    with pytest.raises(RuntimeError):
        JobConfig(name='name')  # noqa

    with pytest.raises(RuntimeError):
        Job()

    with pytest.raises(RuntimeError):
        Job(name='name')

    with pytest.raises(RuntimeError):
        Job('name')  # noqa


def test_fail_init_arg_mock() -> None:
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    with pytest.raises(TypeError):
        JobConfig('name')  # noqa

    with pytest.raises(TypeError):
        JobTemplate('name')  # noqa


def test_job_creator_singular_mock(mock_engine) -> None:
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    assert isinstance(JobConfig.job_creator, JobCreator)

    with pytest.raises(AttributeError):
        JobConfig.job_creator = JobCreator()

    with pytest.raises(AttributeError):
        JobTemplate.job_creator = JobCreator()

    with pytest.raises(AttributeError):
        Job.job_creator = JobCreator()

    job_creator = JobConfig.job_creator
    assert JobTemplate.job_creator is job_creator
    assert Job.job_creator is job_creator

    job_template = JobTemplate()
    assert job_template.__class__.job_creator is job_creator

    job = job_template.apply()
    assert job.__class__.job_creator is job_creator

    job_template_new = JobTemplate()
    assert job_template_new.__class__.job_creator is job_creator


def test_engine_mock(mock_engine):
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    assert JobTemplate.engine is None

    job_template = JobTemplate()
    assert job_template.engine is None
    assert job_template.__class__.job_creator.engine is None

    job_template.set_engine(mock_engine)
    assert job_template.engine is mock_engine
    assert job_template.__class__.job_creator.engine is mock_engine

    job_config_new = JobTemplate()
    assert job_config_new is not job_template
    assert job_config_new.engine is mock_engine
    assert job_config_new.__class__.job_creator.engine is mock_engine

    assert JobTemplate.engine is mock_engine

    assert not hasattr(JobConfig, 'engine')
    assert not hasattr(JobConfig, 'set_engine')
    assert not hasattr(Job, 'set_engine')
    assert not hasattr(Job, 'engine')

    assert JobTemplate.job_creator.engine is mock_engine
    assert JobConfig.job_creator.engine is mock_engine
    assert Job.job_creator.engine is mock_engine


def test_property_name_default_mock() -> None:
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    job_template = JobTemplate()
    assert job_template.name is None

    with pytest.raises(AttributeError):
        job_template.name = 'cool_name'  # noqa


def test_property_name_change_mock() -> None:
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    job_template = JobTemplate(name='my_job')
    for job in job_template, job_template.apply():
        assert job.name == 'my_job'

        with pytest.raises(AttributeError):
            job.name = 'my_cool_job'


def test_property_name_validation_mock() -> None:
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    job_template = JobTemplate(name=None)
    assert job_template.name is None

    with pytest.raises(ValueError):
        JobTemplate(name='')

    with pytest.raises(TypeError):
        JobTemplate(name=123)  # noqa


# def test_property_name_job() -> None:
#     job_template = JobTemplate()
#     assert job_template.name is None
#
#     job_1 = job_template.apply()
#     assert job_1.name is not None
#     assert isinstance(job_1.name, str) and len(job_1.name) > 0
#
#     job_2 = job_template.apply()
#     assert job_1.name != job_2.name


def test_equal_mock() -> None:
    JobConfig, JobTemplate, Job = mock_job_classes()  # noqa

    my_job_template = JobTemplate(name='my_job')
    my_job_template_2 = JobTemplate(name='my_job')
    for (my_job_obj, my_job_obj_2) in [(my_job_template, my_job_template_2),
                                       (my_job_template.apply(), my_job_template_2.apply())]:
        assert my_job_obj == my_job_obj_2

    other_job_template = JobTemplate(name='other_job')
    for (my_job_obj, other_job_obj) in [(my_job_template, other_job_template),
                                        (my_job_template.apply(), other_job_template.apply())]:
        assert my_job_obj != other_job_obj

    assert my_job_template != "123"  # noqa


def test_subclass_equal() -> None:
    cmd_template = CommandMockJobTemplate('erase', params=dict(what='all'))
    cmd_template_2 = CommandMockJobTemplate('erase', params=dict(what='all'))
    for (cmd_obj, cmd_obj_2) in [(cmd_template, cmd_template_2),
                                 (cmd_template.apply(), cmd_template_2.apply())]:
        assert cmd_obj == cmd_obj_2

    cmd_template_3 = CommandMockJobTemplate('restore', params=dict(what='all'))
    for (cmd_obj, cmd_obj_3) in [(cmd_template, cmd_template_3),
                                 (cmd_template.apply(), cmd_template_3.apply())]:
        assert cmd_obj != cmd_obj_3

    cmd_template_4 = CommandMockJobTemplate('erase', params=dict(what='nothing'))
    for (cmd_obj, cmd_obj_4) in [(cmd_template, cmd_template_4),
                                 (cmd_template.apply(), cmd_template_4.apply())]:
        assert cmd_obj != cmd_obj_4


def test_subclass_template():
    cmd_template = CommandMockJobTemplate('erase')
    assert isinstance(cmd_template, CommandMockJobTemplate)

    assert cmd_template.uppercase is False
    assert cmd_template.params == {}

    with pytest.raises(TypeError):
        cmd_template()  # noqa

    with pytest.raises(AttributeError):
        cmd_template.uppercase = False  # noqa

    with pytest.raises(AttributeError):
        cmd_template.params = {}  # noqa

    with pytest.raises(TypeError):
        cmd_template.params['what'] = 'none'  # noqa


def test_subclass_apply():
    cmd_template = CommandMockJobTemplate('erase', uppercase=True, params={'what': 'all'})
    assert isinstance(cmd_template, CommandMockJobTemplate)

    cmd = cmd_template.apply()
    assert isinstance(cmd, CommandMockJob)

    assert cmd.uppercase is True
    assert cmd.params == {'what': 'all'}

    with pytest.raises(AttributeError):
        cmd.uppercase = False  # noqa

    with pytest.raises(AttributeError):
        cmd.params = {}  # noqa

    with pytest.raises(TypeError):
        cmd.params['what'] = 'none'  # noqa

    assert cmd() == 'ALL HAS BEEN ERASED'


def test_subclass_apply_revise():
    cmd_template = CommandMockJobTemplate('restore', params={'what': 'nothing'})
    cmd = cmd_template.apply()
    assert isinstance(cmd, CommandMockJob)

    assert cmd() == 'nothing has been restored'

    cmd_template_revised = cmd.revise()
    assert isinstance(cmd_template_revised, CommandMockJobTemplate)

    assert cmd.uppercase is False
    assert cmd_template_revised.params == {'what': 'nothing'}

    with pytest.raises(TypeError):
        cmd_template_revised()  # noqa

    with pytest.raises(AttributeError):
        cmd_template_revised.uppercase = False  # noqa

    with pytest.raises(AttributeError):
        cmd_template_revised.params = {}  # noqa

    with pytest.raises(TypeError):
        cmd_template_revised.params['what'] = 'all'  # noqa

    cmd_revised = cmd_template_revised.apply()
    assert cmd_revised() == 'nothing has been restored'


def test_subclass_refine_empty():
    cmd_tmpl = CommandMockJobTemplate('restore', params={'what': 'nothing'})

    cmd_tmpl_refined = cmd_tmpl.refine()
    assert isinstance(cmd_tmpl_refined, CommandMockJobTemplate)
    assert cmd_tmpl_refined is not cmd_tmpl
    assert cmd_tmpl_refined == cmd_tmpl


def test_subclass_refine_scalar() -> None:
    # Job template with name and mapping property 'params' as dict
    all_erased_tmpl = CommandMockJobTemplate(
        'erase',
        name='all_erased',
        params={
            'what': 'all',
            'where': 'everywhere',
        },
    )
    all_erased = all_erased_tmpl.apply()
    assert all_erased() == 'all has been erased, everywhere'

    # Refine job template with scalar property 'uppercase' as bool (update=True, default).
    # Other properties are unchanged
    shout_tmpl = all_erased_tmpl.refine(uppercase=True)
    assert shout_tmpl != all_erased_tmpl
    for shout_obj in shout_tmpl, shout_tmpl.apply():
        assert shout_obj.name == 'all_erased'
        assert shout_obj.uppercase is True
        assert shout_obj.params == dict(what='all', where='everywhere')

    shout = shout_tmpl.apply()
    assert shout != all_erased
    assert shout() == 'ALL HAS BEEN ERASED, EVERYWHERE'

    # Refine job template with name and scalar property 'uppercase' as bool (update=False).
    # Other properties are reset to default.
    silent_tmpl = shout_tmpl.refine(uppercase=False, update=False)  # noqa
    assert silent_tmpl != shout_tmpl
    for silent_obj in silent_tmpl, silent_tmpl.apply():
        assert silent_obj.name is None
        assert silent_obj.uppercase is False
        assert silent_obj.params == {}

    silent = silent_tmpl.refine(name='silent').apply()
    assert silent != shout
    assert silent.name is 'silent'
    assert silent() == 'I know nothing'


def test_subclass_refine_mapping() -> None:
    # Job template with name and scalar property 'uppercase' as bool
    cmd_tmpl = CommandMockJobTemplate('restore', name='restore', uppercase=True)
    assert cmd_tmpl.name == 'restore'
    assert cmd_tmpl.uppercase is True
    assert cmd_tmpl.params == {}
    cmd = cmd_tmpl.apply()
    assert cmd() == 'I KNOW NOTHING'

    # Refine job template with mapping property 'params' as dict (update=True, default).
    # Other properties are unchanged. 'params' was previously empty and is now filled
    nicer_tmpl = cmd_tmpl.refine(params=dict(what='something', where='somewhere'))
    assert nicer_tmpl != cmd_tmpl
    for nicer_obj in nicer_tmpl, nicer_tmpl.apply():
        assert nicer_obj.name == 'restore'
        assert nicer_obj.uppercase is True
        assert nicer_obj.params == dict(what='something', where='somewhere')

    nicer = nicer_tmpl.apply()
    assert nicer != cmd
    assert nicer() == 'SOMETHING HAS BEEN RESTORED, SOMEWHERE'

    # Refine job template with mapping property 'params' as list of tuples (update=True).
    # Other properties are unchanged, as well as other entries in 'params'
    secret_tmpl = nicer_tmpl.refine(params=[('where', 'but it is a secret')])  # noqa
    assert secret_tmpl != nicer_tmpl
    for secret_obj in secret_tmpl, secret_tmpl.apply():
        assert secret_obj.name == 'restore'
        assert secret_obj.uppercase is True
        assert secret_obj.params == dict(what='something', where='but it is a secret')

    secret = secret_tmpl.apply()
    assert secret != nicer
    assert secret() == 'SOMETHING HAS BEEN RESTORED, BUT IT IS A SECRET'

    # Refine job template with 'params' as dict (update=False).
    # Other properties are reset to default. Previous 'params' mapping property is fully replaced
    nothing_tmpl = secret_tmpl.refine(params=dict(what='nothing'), update=False)
    assert nothing_tmpl != secret_tmpl
    for nothing_obj in nothing_tmpl, nothing_tmpl.apply():
        assert nothing_obj.name is None
        assert nothing_obj.uppercase is False
        assert nothing_obj.params == dict(what='nothing')

    nothing = nothing_tmpl.refine(name='nothing').apply()
    assert nothing != secret
    assert nothing.name is 'nothing'
    assert nothing() == 'nothing has been restored'


def test_subclass_refine_reset_mapping() -> None:
    cmd_tmpl = CommandMockJobTemplate('erase')
    cmd = cmd_tmpl.apply()
    assert cmd() == 'I know nothing'

    nothing_tmpl = cmd_tmpl.refine(uppercase=True, params=dict(what='nothing'))
    nothing = nothing_tmpl.apply()
    assert nothing() == 'NOTHING HAS BEEN ERASED'

    # Resetting mapping property 'params' does not work with update=True
    reset_params_tmpl = nothing_tmpl.refine(params={})
    assert reset_params_tmpl == nothing_tmpl
    assert reset_params_tmpl.uppercase is True
    assert reset_params_tmpl.params == dict(what='nothing')

    # Reset only mapping property 'params' with update=False.
    # Other properties needs to be explicitly added to not be reset
    for val in ({}, [], None):
        reset_params_tmpl = nothing_tmpl.refine(
            uppercase=nothing_tmpl.uppercase,
            params=val,
            update=False,
        )
        assert reset_params_tmpl != cmd_tmpl
        for reset_params_obj in reset_params_tmpl, reset_params_tmpl.apply():
            assert reset_params_tmpl.uppercase is True
            assert reset_params_obj.params == {}

    # One-liner to reset job to default values
    reset = nothing.revise().refine(update=False).apply()

    assert reset == cmd
    assert reset() == 'I know nothing'
    assert reset.uppercase is False
    assert reset.params == {}


def test_revise_refine_mappings_are_copied() -> None:
    all_tmpl = CommandMockJobTemplate('erase', params={'what': 'all'})
    all_refined_tmpl = all_tmpl.refine(params=dict(where='everywhere'),)

    assert len(all_tmpl.params) == 1
    assert len(all_refined_tmpl.params) == 2

    all_job = all_tmpl.apply()
    all_revised_tmpl = all_job.revise()
    all_revised_refined_tmpl = all_revised_tmpl.refine(params=dict(where='sadly'),)

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


# def test_job_template_as_decorator() -> None:
#     @JobTemplate
#     def plus_one(number: int) -> int:
#         return number + 1
#
#     assert isinstance(plus_one, JobTemplate)
#
#     plus_one = plus_one.apply()
#     assert isinstance(plus_one, Job)
#
#     assert plus_one(3) == 4
#
#
# def test_job_template_as_decorator_with_keyword_arguments() -> None:
#     @JobTemplate(
#         name='plus_one',
#         param_key_map=dict(number_a='number'),
#         fixed_params=dict(number_b=1),
#         result_key='plus_one',
#     )
#     def plus_func(number_a: int, number_b: int) -> int:
#         return number_a + number_b
#
#     plus_one_template = plus_func
#
#     assert isinstance(plus_one_template, JobTemplate)
#
#     plus_one = plus_one_template.apply()
#     assert isinstance(plus_one, Job)
#
#     assert plus_one(3) == {'plus_one': 4}
#
#
# def test_error_job_template_decorator_with_func_argument() -> None:
#
#     with pytest.raises(TypeError):
#
#         def myfunc(a: Callable) -> Callable:
#             return a
#
#         @JobTemplate(myfunc)
#         def plus_one(number: int) -> int:
#             return number + 1
#
#         assert isinstance(plus_one, JobTemplate)
