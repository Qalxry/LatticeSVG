# Rich Text & Markup

LatticeSVG supports HTML subset and Markdown syntax for rich text in `TextNode`.

## HTML Markup

Set `markup="html"` to enable HTML parsing:

```python
from latticesvg import TextNode

text = TextNode(
    "This is <b>bold</b>, <i>italic</i>, <b><i>bold-italic</i></b> text.",
    style={"font-size": "14px"},
    markup="html",
)
```

<figure markdown="span">
  ![HTML rich text](../assets/images/examples/rich_text_html.svg){ loading=lazy }
  <figcaption>HTML markup rich text rendering</figcaption>
</figure>

### Supported HTML Tags

| Tag | Effect | Example |
|---|---|---|
| `<b>`, `<strong>` | Bold | `<b>bold</b>` |
| `<i>`, `<em>` | Italic | `<i>italic</i>` |
| `<u>` | Underline | `<u>underline</u>` |
| `<s>`, `<del>` | Strikethrough | `<s>deleted</s>` |
| `<sub>` | Subscript | `H<sub>2</sub>O` |
| `<sup>` | Superscript | `E=mc<sup>2</sup>` |
| `<br>`, `<br/>` | Line break | `Line 1<br>Line 2` |
| `<span>` | Inline style | `<span style="color:red">red</span>` |
| `<math>` | Inline math | `<math>E=mc^2</math>` |
| `<code>` | Code style | `<code>print()</code>` |

### Inline Styles

The `<span>` tag supports a `style` attribute for inline styling:

```python
TextNode(
    'Normal <span style="color: #e74c3c; font-size: 18px">red large</span> normal',
    markup="html",
)
```

Supported inline style properties: `color`, `background-color`, `font-size`, `font-family`, `font-weight`, `font-style`, `text-decoration`.

## Markdown Markup

Set `markup="markdown"` to enable Markdown syntax:

```python
text = TextNode(
    "This is **bold**, *italic*, ***bold-italic*** text.",
    style={"font-size": "14px"},
    markup="markdown",
)
```

<figure markdown="span">
  ![Markdown rich text](../assets/images/examples/rich_text_markdown.svg){ loading=lazy }
  <figcaption>Markdown markup rich text rendering</figcaption>
</figure>

### Supported Markdown Syntax

| Syntax | Effect |
|---|---|
| `**text**` | Bold |
| `*text*` | Italic |
| `***text***` | Bold-italic |
| `` `code` `` | Code style |
| `~~text~~` | Strikethrough |
| `$LaTeX$` | Inline math |

## Inline Math

### HTML Mode

Use the `<math>` tag to embed LaTeX formulas:

```python
TextNode(
    "The equation <math>E = mc^2</math> was proposed by Einstein in 1905.",
    markup="html",
    style={"font-size": "14px", "line-height": "1.8"},
)
```

### Markdown Mode

Use `$...$` syntax:

```python
TextNode(
    "The equation $E = mc^2$ was proposed by Einstein in 1905.",
    markup="markdown",
    style={"font-size": "14px", "line-height": "1.8"},
)
```

## TextSpan Data Structure

The markup parser converts text into a list of `TextSpan` objects:

```python
from latticesvg.markup import parse_markup, parse_html, parse_markdown

spans = parse_markup("**bold** normal", "markdown")
# → [TextSpan(text="bold", font_weight="bold"),
#    TextSpan(text=" normal")]
```

## Combined Example

```python
from latticesvg import GridContainer, TextNode, Renderer, templates

page = GridContainer(style={**templates.REPORT_PAGE, "gap": "16px"})
page.add(TextNode("Rich Text Demo", style=templates.TITLE))

page.add(TextNode(
    "LatticeSVG's markup system supports **various styles** and *math formulas*. "
    "For example, Euler's identity $e^{i\\pi} + 1 = 0$ connects five important constants.\n\n"
    "You can also use ~~strikethrough~~ and `code` styles.",
    markup="markdown",
    style={**templates.PARAGRAPH, "line-height": "2.0"},
))

Renderer().render(page, "rich_text.svg")
```

<figure markdown="span">
  ![Rich text combined](../assets/images/examples/rich_text_markdown.svg){ loading=lazy }
  <figcaption>Rich text with math formulas</figcaption>
</figure>
