## Introduction to Python type hints

### Duck typing in Python

The concept of "duck-typing" is a central concept in Python. The name comes from the 
[Duck test](https://en.wikipedia.org/wiki/Duck_test):

"If it looks like a duck, swims like a duck, and quacks like a duck, then it probably _is_ a duck"

This again is a reference to the 
["Canard Digérateur"](https://en.wikipedia.org/wiki/Digesting_Duck), or "The Digesting Duck", a 
mechanical duck built by [Jacques de Vaucanson](https://en.wikipedia.org/wiki/Jacques_de_Vaucanson) 
in 1739:

![The Digesting Duck](https://en.wikipedia.org/wiki/Duck_test#/media/File:Vaucanson_duck2.gif)

The duck was designed to look like it ate a mixture of water and grain, digested the food, and then 
excreted the remains. In reality, the duck excreted a pre-made mixture of bread crumbs and green dye 
in a process that was not connected to the ingestion process.

Similarly, in Python, the type of an object is determined dynamically - by its behavior - rather 
than by definition. This is in contrast to statically typed languages like C++ or Java, where the
type of an object is specified at compile time. In Python, the type of an object is determined at
runtime, allowing a level of dynamics not easily achieved in statically typed languages, e.g.:

```python
def add(x, y):
    return x + y

a = add(1, 2)  # type(a) == int; a == 3
b = add('foo', 'bar')  # type(b) == str; b == 'foobar'
c = add([1, 2], [3, 4])  # type(c) == list; c == [1, 2, 3, 4]
```

In the above example, the `add` function is defined to take two arguments and return their sum, 
regardless of the type of the arguments. The types output by the function are determined at runtime
based on the input types. This is an example of 
[duck-typing](https://en.wikipedia.org/wiki/Duck_typing) in Python.
