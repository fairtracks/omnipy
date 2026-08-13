from omnipy.compute.task import TaskTemplate


@TaskTemplate()
def uppercase(text: str) -> str:
    return text.upper()


@TaskTemplate()
def square_root(number: int) -> dict[str, float]:
    return {'neg_root': -number**0.5, 'pos_root': number**0.5}


@TaskTemplate()
def merge_key_value_into_str(key: object, val: object) -> str:
    return '{}: {}'.format(key, val)
