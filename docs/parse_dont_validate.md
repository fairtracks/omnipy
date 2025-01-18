/// html | div.blackboard
## Parse, don't validate
### Type-driven design

This alternative approach to [data wrangling](https://en.wikipedia.org/wiki/Data_wrangling) is
summed up in a slogan coined by Alexis King in 2019 in an influential blog post:
["Parse, don't validate"](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/). King
here argues for the use of "Type-driven design", also called "Type-driven development":

<ui-quote-text
:quote='"Type-driven development is a style of programming in which we write types first and use those types to guide the definition of functions."'
:citation='"Brady E. [Type-driven development with Idris.](https://livebook.manning.com/book/type-driven-development-with-idris/chapter-1/27). Simon and Schuster, 2017"'
no-text-color> </ui-quote-text>

This definition of "Type-driven development" entails that each parser is defined at the outset to
guarantee the production a particular data type (also called "data model", "data structure", or
"schema"). With an abundance of different precisely defined data types in the code base,
transformations can be defined with precise syntax as a cascade of data type conversions, e.g.:

<p class="pseudocode">list [ Any ]
⇩
list [ str ]
⇩
list [ conint ( ge = 0, le = 1000 ) ]*
</p>

_\* These data types were written using Python type hint notation, where `conint(ge=0, le=1000)` is
a [pydantic](https://pydantic-docs.helpmanual.io/) data type representing a positive integer less
than or equal to 1000._

### The data types remember

A main advantage of this approach is that once a variable is defined to follow a particular data
type, e.g. _"list of positive integers less than or equal to 1000"_, then this restriction is
preserved in the data type itself; the variable never needs to be parsed or validated again!

<ui-numbered-figure :figure-obj="{path: ['images', 'fair', 'validators-vs-parsers.png'], maxWidth: '65%'}">
</ui-numbered-figure>

### Requires static typing

The "Parse, don't validate" approach requires that the programming language is
[statically typed](https://en.wikipedia.org/wiki/Type_system#STATIC) and also that the language
supports complex data types, so that e.g. a full metadata schema can be expressed as a type. It is
no surprise that Alexis King in the above-mentioned blog post demonstrated the concepts in
[Haskell](https://www.haskell.org/), a statically typed and
[purely functional](https://en.wikipedia.org/wiki/Purely_functional_programming) programming
language.

### What about Python?

Python is one of the most popular programming languages in bioinformatics and data science in
general. Python is also one of the most famous examples of a
[duck typed](https://en.wikipedia.org/wiki/Duck_typing) language, i.e. that if something _"walks
like a duck and quacks like a duck, then it must be a duck"_. Unfortunately, in traditional Python
code, if a variable looks like a _"list of positive integers less than 1000"_, there is no way to
know this for sure without validating the full list, and even then, there are no guarantees that the
data will stay that way forever.

Fortunately, with the integration of [type hints](https://peps.python.org/pep-0484/) and
compile-time static type checkers such as [mypy](http://mypy-lang.org/) this is changing. Moveover,
with the advent of run-time type checking with libraries like
[pydantic](https://pydantic-docs.helpmanual.io/), the time is ripe to take advantage of type-driven
design also in Python.
///