---
title: Pandoc Markdown
date_edtf: "2026-06-25T06:46:00"
keywords: [pandoc, markdown, computer reference]
---

*[Pandoc.org](https://pandoc.org/MANUAL.html).*

***

## Starting Points

Markdown is intended to be easy to type and easy to read in plain text. One general rule is **always put a blank line between things**. Pandoc Markdown requires a blank line preceding any header, and it seems best practice to add vertical whitespace between almost all individual document elements. *Lists, nested lists, and list items can be grouped tightly.*

The standard tabulation for Markdown is **4 spaces**. Structures such as lists will not nest correctly without correct indentation/tabulation. This can usually be set in the editor. Syntax highlighting and linting are both helpful also, if the editor supports it.

*** 

## [Headers & Subheaders](#top)


Headings consist of one to six `#` *(hash)* signs and a line of text.

```markdown
# Level one
## Level two
### Level three
```

***Output:***

***

# Level one
## Level two
### Level three

***

***Note:** While the six header levels are available in Markdown, the format Pandoc is exporting to matters. The first three levels of headers are generally safe, but the styling and export format should be checked.*

***

## Blockquotes

Blockquotes are created with `>` *(greater than)*.

```markdown
> This is a blockquote. It can
> contain line breaks as this demonstrates.
>
> 1. Blockquotes can contain lists.
> 2. Item two.
>
> > Blockquotes can contain blockquotes.

> "Lazy" blockquotes are also allowed, in which there is no need to manually include the `>` symbol at the beginning of each line to continue the quote. This is easier to type but less visually distinct in plain text.
```

***Output:***

***

> This is a blockquote. It can
> contain be multiple lines long.
>
> 1. Blockquotes can contain lists.
> 2. Item two.
>
> > Blockquotes can contain blockquotes.


> "Lazy" blockquotes are also allowed, in which there is no need to manually include the `>` symbol at the beginning of each line to continue the quote. This is easier to type but less visually distinct in plain text.

***

***Note:** There is more possible, though the complexity of the spacing and indentation requirements becomes a headache.*

***

## Fenced Code Blocks

Code blocks are enclosed in 3 or more `` ` `` *(backtick)*.

````
```
if x > y {
  z = 0
}
```
````

***Output:***

***

```
if x > y {
    z = 0
}
```

### Enclosed Fence Code Blocks

Bracket fenced code blocks in more than three `` ` `` *(backticks)* to nest and include them in output.

`````
````
```
if x > y {
  z = 0
}
```
````
`````

***Output:***

***

````
```
if x > y {
  z = 0
}
```
````

## Pipe Tables

The easiest way to explain pipe tables is to demonstrate one:

```markdown
| Left | Center | Center | Right |
| :--- | :---: | :---: | ---: |
| row | 2 | three | four |
| longer row | 3.14159 | 0 | more text |
```

***Notes:** The header row can be omitted. The columns before or after the dashes in each column of the second row define the alignment used for that column. Tables are likely to require significant styling for the target export format.*

As typed above, pipe tables are very easy to type, but somewhat difficult to read. This can be improved as follows (adding spaces and hyphens) if needed:

```markdown
| Left       | Center  | Center | Right     |
| :--------- | :-----: | :----: | --------: |
| row        | 2       | three  | four      |
| longer row | 3.14159 | 0      | more text |
```

***Output:***

| Left       | Center  | Center | Right     |
| :--------- | :-----: | :----: | --------: |
| row        | 2       | three  | four      |
| longer row | 3.14159 | 0      | more text |

## Links

```markdown
[Link To Google](https://www.google.com)
```

***Output:***

[Link To Google](https://www.google.com)

## Images

```markdown
![Test - Artemis II](../assets/media/test_artemis_2.jpg)
```

![Test - Artemis II](../assets/media/test_artemis_2.jpg)
