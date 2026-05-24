# UI Architecture Notes

The touchscreen UI should avoid putting reusable drawing/event logic directly into `touchscreen.py`.

## Current Direction

- `touchscreen.py` owns screen-specific layouts and the pygame process loop.
- `components.py` owns reusable UI primitives and helpers.
- `styles.py` owns colors and fonts.

## Reusable UI Layer

New or refactored screens should prefer:

- `BaseScreen` for common `fonts`, `buttons`, `fill()`, `draw_buttons()`, and `handle_input()`.
- `Button` for clickable actions.
- `render_centered()` and `render_at()` for text rendering.
- `wrap_text()` for message text.
- `draw_count_list()` for repeated product/count lists.
- `draw_debug_name()` via `BaseScreen.draw_debug_name()` instead of manually drawing class names.

## Screen Pattern

```python
class ExampleScreen(BaseScreen):
    def __init__(self, payload, fonts):
        super().__init__(fonts)
        self.items = payload if isinstance(payload, dict) else {}
        self.buttons.append(Button(412, 650, 200, 60, "Jätka", fonts.body, Colors.GREEN, True))

    def draw(self, screen):
        self.fill(screen)
        render_centered(screen, self.fonts.header, "Title", (512, 50))
        draw_count_list(screen, self.fonts, self.items, empty_text="Nothing to show")
        self.draw_buttons(screen)
        self.draw_debug_name(screen)
```

## Next Cleanup Targets

- Move screen classes out of `touchscreen.py` into a `sinine_kapp/ui/screens/` package.
- Split `DEFAULT_SCREEN` into separate main menu, card wait, and account options screens.
- Split `MESSAGE` into passive status, confirmation prompt, and wait prompt variants.
- Move barcode keyboard buffering out of the pygame loop into a small input helper.
