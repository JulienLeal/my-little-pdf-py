# Templating System Integration Demo

This document demonstrates the integration of the templating system with custom block components.

## Regular Markdown

This is regular markdown content that gets processed normally.

- Lists work fine
- **Bold text** and *italic text*
- `Code snippets` are preserved

## Custom Components with Templates

### Tip Box Component

:::tip_box color="blue"
This is a helpful tip that gets rendered using the Jinja2 template system!
The template provides nice styling and structure.
:::

### Magic Secret Component

:::magic_secret reveal_text="Click to reveal!"
This is a secret message that only true wizards can see! 🧙‍♂️✨
:::

### Attention Box Component

:::attention_box type="warning" urgency="high"
**Important Notice:** This system integrates markdown processing with custom templating for rich component rendering.
:::

## Fallback for Unknown Components

:::unknown_component custom_attr="test" flag
This component doesn't have a template, so it falls back to a simple div with data attributes.
:::

## Nested Content

:::tip_box color="green"
This tip box contains:

- **Nested markdown** formatting
- Lists and other elements
- Even `code snippets`

All processed correctly within the template!
:::

## Multiple Components

:::tip_box color="purple"
First tip box with purple styling.
:::

:::attention_box type="info"
An informational attention box right after the tip.
:::

## The End

This demonstrates the seamless integration of the templating system with markdown processing! 