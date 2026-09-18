"""Inline SVG icons.

One registry, one size system. Every icon uses a 24x24 viewBox and inherits
colour from `currentColor`, so callers never pass colour or size -- CSS does it.
Stroke icons get `vector-effect:non-scaling-stroke` from style.css (monks §8.4).
"""

# Icons that are drawn with strokes. Filled brand marks are listed in _FILLED.
_STROKE = {
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "arrow-left": '<path d="M19 12H5"/><path d="m12 19-7-7 7-7"/>',
    "arrow-up-right": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
}

_FILLED = {
    "github": (
        '<path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.5.5.09.68-.22.68-.48 0-.24-.01-.87-.01-1.7'
        '-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03'
        '.89 1.52 2.34 1.08 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68'
        '-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02.8-.22 1.65-.33 2.5-.33s1.7.11 2.5.33c1.91-1.29 2.75-1.02 2.75-1.02'
        '.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85 0 1.34-.01 2.42-.01 2.75'
        ' 0 .27.18.58.69.48A10 10 0 0 0 22 12c0-5.52-4.48-10-10-10z"/>'
    ),
    "linkedin": (
        '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.71h.05c.53-1 1.82-2.06 3.75-2.06'
        ' 4.01 0 4.75 2.64 4.75 6.07V21h-4v-5.5c0-1.31-.02-3-1.83-3-1.83 0-2.11 1.43-2.11 2.91V21H9z"/>'
    ),
    "x": (
        '<path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.65l-5.22-6.82-5.96 6.82H1.68l7.73-8.84L1.25 2.25h6.82'
        'l4.71 6.23zm-1.16 17.52h1.83L7.08 4.13H5.11z"/>'
    ),
}


def icon(name: str, extra_class: str = "") -> str:
    """Return one inline SVG. Raises on an unknown name so a typo fails the build."""
    filled = name in _FILLED
    body = _FILLED[name] if filled else _STROKE[name]
    classes = " ".join(filter(None, ["ico", "f" if filled else "", extra_class]))
    return f'<svg class="{classes}" viewBox="0 0 24 24" aria-hidden="true">{body}</svg>'
