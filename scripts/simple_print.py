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

data.peek(style='random-dark-high-t16', bg=True)
data.peek(style='random-dark-low-t16', bg=True)
data.peek(style='random-light-high-t16', bg=True)
data.peek(style='random-light-low-t16', bg=True)
data.peek(style='random-dark-t16', bg=True)
data.peek(style='random-light-t16', bg=True)
data.peek(style='random-t16', bg=True)
data.peek(style='random-dark-high', bg=True)
data.peek(style='random-dark-low', bg=True)
data.peek(style='random-light-high', bg=True)
data.peek(style='random-light-low', bg=True)
data.peek(style='random-dark', bg=True)
data.peek(style='random-light', bg=True)
data.peek(style='random', bg=True)

data.list(style='random-dark-high-t16', bg=True)
data.list(style='random-dark-low-t16', bg=True)
data.list(style='random-light-high-t16', bg=True)
data.list(style='random-light-low-t16', bg=True)
data.list(style='random-dark-t16', bg=True)
data.list(style='random-light-t16', bg=True)
data.list(style='random-t16', bg=True)
data.list(style='random-dark-high', bg=True)
data.list(style='random-dark-low', bg=True)
data.list(style='random-light-high', bg=True)
data.list(style='random-light-low', bg=True)
data.list(style='random-dark', bg=True)
data.list(style='random-light', bg=True)
data.list(style='random', bg=True)
