from unifair.util.param_key_mapper import ParamKeyMapper


def test_map_matching_keys():
    param_key_mapper = ParamKeyMapper(dict(
        long_key='long',
        longer_key='longer',
    ))
    assert param_key_mapper.map_matching_keys(
        dict(long_key=8, longer_key=12, even_longer_key=17),
        inverse=False,
        keep_non_matching_keys=False,
    ) == dict(
        long=8, longer=12)

    assert param_key_mapper.map_matching_keys(
        dict(long_key=8, longer_key=12, even_longer_key=17),
        inverse=False,
        keep_non_matching_keys=False,
    ) == dict(
        long=8, longer=12)

    assert param_key_mapper.map_matching_keys(
        dict(long=8, longer=12, even_longer_key=17),
        inverse=True,
        keep_non_matching_keys=True,
    ) == dict(
        long_key=8, longer_key=12, even_longer_key=17)

    assert param_key_mapper.map_matching_keys(
        dict(long=8, longer=12, even_longer_key=17),
        inverse=True,
        keep_non_matching_keys=True,
    ) == dict(
        long_key=8, longer_key=12, even_longer_key=17)


def test_map_matching_keys_empty():
    param_key_mapper = ParamKeyMapper({})
    assert param_key_mapper.map_matching_keys(
        dict(abc=123),
        inverse=False,
        keep_non_matching_keys=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(abc=123),
        inverse=True,
        keep_non_matching_keys=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(abc=123),
        inverse=False,
        keep_non_matching_keys=True,
    ) == dict(abc=123)
    assert param_key_mapper.map_matching_keys(
        dict(abc=123),
        inverse=True,
        keep_non_matching_keys=True,
    ) == dict(abc=123)

    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=False,
        keep_non_matching_keys=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=True,
        keep_non_matching_keys=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=False,
        keep_non_matching_keys=True,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=True,
        keep_non_matching_keys=True,
    ) == dict()

    param_key_mapper = ParamKeyMapper({'abc': 'cba'})

    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=False,
        keep_non_matching_keys=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=True,
        keep_non_matching_keys=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=False,
        keep_non_matching_keys=True,
    ) == dict()
    assert param_key_mapper.map_matching_keys(
        dict(),
        inverse=True,
        keep_non_matching_keys=True,
    ) == dict()


def test_delete_matching_keys():
    param_key_mapper = ParamKeyMapper(dict(
        long_key='long',
        longer_key='longer',
    ))

    assert param_key_mapper.delete_matching_keys(
        dict(long_key=8, longer_key=12, even_longer_key=17),
        inverse=False,
    ) == dict(even_longer_key=17)

    assert param_key_mapper.delete_matching_keys(
        dict(long=8, longer=12, even_longer_key=17),
        inverse=True,
    ) == dict(even_longer_key=17)


def test_delete_matching_keys_empty():
    param_key_mapper = ParamKeyMapper(dict())

    assert param_key_mapper.delete_matching_keys(
        dict(abc=123),
        inverse=False,
    ) == dict(abc=123)

    assert param_key_mapper.delete_matching_keys(
        dict(abc=123),
        inverse=True,
    ) == dict(abc=123)

    assert param_key_mapper.delete_matching_keys(
        dict(),
        inverse=False,
    ) == dict()

    assert param_key_mapper.delete_matching_keys(
        dict(),
        inverse=True,
    ) == dict()

    param_key_mapper = ParamKeyMapper({'abc': 'cba'})

    assert param_key_mapper.delete_matching_keys(
        dict(),
        inverse=False,
    ) == dict()

    assert param_key_mapper.delete_matching_keys(
        dict(),
        inverse=True,
    ) == dict()


def test_map_matching_keys_delete_inverse_matches_keep_rest():
    param_key_mapper = ParamKeyMapper(dict(
        long_key='long',
        longer_key='longer',
    ))
    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(long_key=8, longer=12, even_longer_key=17),
        inverse=False,
    ) == dict(
        long=8, even_longer_key=17)
    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(long_key=8, longer=12, even_longer_key=17),
        inverse=True,
    ) == dict(
        longer_key=12, even_longer_key=17)


def test_map_matching_keys_delete_inverse_matches_keep_rest_empty():
    param_key_mapper = ParamKeyMapper(dict())
    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(abc=123),
        inverse=False,
    ) == dict(abc=123)
    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(abc=123),
        inverse=True,
    ) == dict(abc=123)

    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(),
        inverse=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(),
        inverse=True,
    ) == dict()

    param_key_mapper = ParamKeyMapper({'abc': 'cba'})

    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(),
        inverse=False,
    ) == dict()
    assert param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
        dict(),
        inverse=True,
    ) == dict()
