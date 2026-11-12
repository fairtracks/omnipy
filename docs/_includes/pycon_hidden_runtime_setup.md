>>> om.runtime.config.root_log.log_to_stdout = False  # markdown-exec: hide
>>> om.runtime.config.root_log.log_to_stderr = False  # markdown-exec: hide
>>> om.runtime.config.root_log.log_to_file = False  # markdown-exec: hide
>>> om.runtime.config.job.output_storage.persist_outputs = 'disabled'  # markdown-exec: hide
>>> om.runtime.config.data.model.interactive = True  # markdown-exec: hide
>>> om.runtime.config.data.ui.browser.color.style = 'omnipy-selenized-white'  # markdown-exec: hide
>>> om.runtime.config.data.ui.browser.font.size = 15  # markdown-exec: hide
>>> om.runtime.config.data.ui.browser.width = 114  # markdown-exec: hide
>>> import sys  # markdown-exec: hide
>>> from contextlib import contextmanager  # markdown-exec: hide
>>> @contextmanager  # markdown-exec: hide
... def catch_and_format_error():  # markdown-exec: hide
...     try:  # markdown-exec: hide
...         yield  # markdown-exec: hide
...     except Exception as e:  # markdown-exec: hide
...         # Extract the string name of the exception class (e.g., "ValidationError")  # markdown-exec: hide
...         error_title = type(e).__name__  # markdown-exec: hide
...         # 1. Print the Admonition header using the dynamic class name  # markdown-exec: hide
...         print(f'!!! failure "{error_title}"\n')  # markdown-exec: hide
...         # 2. Open an indented code block with python syntax coloring  # markdown-exec: hide
...         print("    ```")  # markdown-exec: hide
...         for line in str(e).splitlines():  # markdown-exec: hide
...             print(f"    {line}")  # markdown-exec: hide
...         print("    ```")  # markdown-exec: hide
>>> from textwrap import dedent  # markdown-exec: hide
>>> def exec_and_display_code(code):  # markdown-exec: hide
...     code = dedent(code)  # markdown-exec: hide
...     exec(code, globals())  # markdown-exec: hide
...     print(  # markdown-exec: hide
...         om.StrModel(code)._docs(  # markdown-exec: hide
...             max_title_height=0,  # markdown-exec: hide
...             method='full',  # markdown-exec: hide
...             width=None,  # markdown-exec: hide
...             syntax='python',  # markdown-exec: hide
...             style=om.DarkHighContrastColorStyles.CHINOISERIE_MORANDI_T16,  # markdown-exec: hide
...         )  # markdown-exec: hide
...     )  # markdown-exec: hide
