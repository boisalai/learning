# Markdown Formatting Test Guide

## Introduction

This document is a test example that demonstrates the different formatting possibilities in Markdown. It includes various syntax elements to test the conversion.

## Formatted Text

Here is text in **bold**, in *italic*, and in ***bold italic***. You can also use ~~strikethrough text~~ and `inline code`.

## Lists

### Unordered List

* First element
  * Sub-element 1
  * Sub-element 2
* Second element
* Third element
  * Another sub-element
    * Level 3 of the list

### Ordered List

1. First important point
   1. Sub-point A
   2. Sub-point B
2. Second important point
3. Third important point

## Quotes

> This is a simple quote
> 
> It can continue over multiple lines
>> And even have nested quotes

## Code

Here is an example of a Python code block:

```python
def hello_world():
    print("Hello, World!")
    for i in range(5):
        print(f"Counter: {i}")
```

## Tables

| Name     | Age | Profession    |
|----------|-----|---------------|
| John     | 30  | Developer     |
| Mary     | 25  | Designer      |
| Peter    | 35  | Project Manager|

### Aligned Table

| Left   | Center | Right |
|:-------|:------:|------:|
| A1     | B1     | C1    |
| A2     | B2     | C2    |

## Links

- [Link to Google](https://www.google.com)
- [Link with title](https://www.wikipedia.org "Wikipedia")
- <https://example.com> (automatic link)

## Images

![Markdown Logo](img/markdown.png)

## Task Lists

- [x] Completed task
- [ ] Task to do
- [ ] Other pending task
  - [x] Completed subtask
  - [ ] Ongoing subtask

## Definitions

Markdown
: A lightweight markup language

HTML
: The standard language of the Web

## Footnotes

Here is text with a footnote[^1] and another[^2].

[^1]: This is the first footnote.
[^2]: The second note can also contain multiple lines.

## Special Characters

Special characters can be escaped: \* \_ \` \# \[ \] \( \) \{ \} \> \+ \- \. \!

## Mathematical Expressions (if supported)

Inline: $E = mc^2$

Block:
$$
\frac{n!}{k!(n-k)!} = \binom{n}{k}
$$

## Conclusion

This document shows the main features of Markdown and can serve as a reference for testing conversion to other formats.
