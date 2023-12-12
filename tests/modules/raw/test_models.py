import os
from textwrap import dedent

from omnipy.modules.raw.models import JoinLinesModel, SplitAndStripLinesModel, SplitLinesModel


def test_split_and_join_lines_models():
    data = '''\
        Alas, poor Yorick! I knew him, Horatio: a fellow
        of infinite jest, of most excellent fancy: he hath	 
        borne me on his back a thousand times; and now, how	 
        abhorred in my imagination it is! my gorge rises at	 
        it. Here hung those lips that I have kissed I know	 
        not how oft. Where be your gibes now? your
        gambols? your songs? your flashes of merriment,	 
        that were wont to set the table on a roar? Not one	 
        now, to mock your own grinning? quite chap-fallen.'''

    lines_unstripped = SplitLinesModel(data)
    assert lines_unstripped[0] == '        Alas, poor Yorick! I knew him, Horatio: a fellow'

    lines_stripped = SplitAndStripLinesModel(data)
    assert lines_stripped[0] == 'Alas, poor Yorick! I knew him, Horatio: a fellow'

    last_lines = lines_stripped[3:]
    assert last_lines[0:2].contents == [
        'abhorred in my imagination it is! my gorge rises at',
        'it. Here hung those lips that I have kissed I know'
    ]

    joined_lines = JoinLinesModel(last_lines[0:2])
    assert joined_lines.contents == dedent('''\
        abhorred in my imagination it is! my gorge rises at
        it. Here hung those lips that I have kissed I know''')

    assert joined_lines[:joined_lines.index(' ')].contents == 'abhorred'

    assert JoinLinesModel(SplitLinesModel(data)).contents == data
    assert JoinLinesModel(SplitAndStripLinesModel(data)).contents == \
           os.linesep.join([line.strip() for line in data.split(os.linesep)])
