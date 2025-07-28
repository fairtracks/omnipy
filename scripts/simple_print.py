import omnipy as om

om.runtime.config.data.ui.terminal.width = 140
model = om.Model[list[list[str | int]]]([
    [123, 234, 345, 456, 567],
    ['abc', 'bce', 'cde', 'def', 'efg'],
])
data = om.Dataset[om.Model[list[list[str | int]]]](
    abcd=model,
    bcde=model,
    cdef=model,
    defg=model,
    efgh=model,
)

data.peek(style='random-t16-dark-high', bg=True)
data.peek(style='random-t16-dark-low', bg=True)
data.peek(style='random-t16-light-high', bg=True)
data.peek(style='random-t16-light-low', bg=True)
data.peek(style='random-t16-dark', bg=True)
data.peek(style='random-t16-light', bg=True)
data.peek(style='random-t16', bg=True)
data.peek(style='random-dark-high', bg=True)
data.peek(style='random-dark-low', bg=True)
data.peek(style='random-light-high', bg=True)
data.peek(style='random-light-low', bg=True)
data.peek(style='random-dark', bg=True)
data.peek(style='random-light', bg=True)
data.peek(style='random', bg=True)

data.list(style='random-t16-dark-high', bg=True)
data.list(style='random-t16-dark-low', bg=True)
data.list(style='random-t16-light-high', bg=True)
data.list(style='random-t16-light-low', bg=True)
data.list(style='random-t16-dark', bg=True)
data.list(style='random-t16-light', bg=True)
data.list(style='random-t16', bg=True)
data.list(style='random-dark-high', bg=True)
data.list(style='random-dark-low', bg=True)
data.list(style='random-light-high', bg=True)
data.list(style='random-light-low', bg=True)
data.list(style='random-dark', bg=True)
data.list(style='random-light', bg=True)
data.list(style='random', bg=True)
