# Mock Hardware Input Dialog Implementation

## Overview

This implementation replaces terminal-based `input()` prompts in mock hardware with on-screen popup dialogs. This allows the application to run in autorun mode on the Raspberry Pi without requiring terminal access.

## Problem Solved

Previously, when using mock hardware (MockRFIDReader and MockQRScanner), the application would prompt for input via Python's `input()` function in the terminal. This had several issues:

1. **Autorun incompatibility**: When the app runs automatically on boot (via systemd service), there's no terminal available
2. **User experience**: Users had to switch between the touchscreen UI and a separate terminal window
3. **Accessibility**: Touch-only users couldn't provide input

## Solution

The mock hardware classes now show on-screen input dialogs using the existing UI components:

- `InputBox`: Text input field
- `OnScreenKeyboard`: Touch-friendly keyboard
- `InputDialogScreen`: Modal dialog that combines both

### How It Works

1. **Manager Setup**: The mock hardware classes receive references to `ui_manager` and `screen_manager` via the `set_managers()` method
2. **Dialog Display**: When `scan()` or `read()` is called, the mock hardware pushes an `InputDialogScreen` onto the screen stack
3. **Event Loop**: The mock hardware runs its own event loop to handle the dialog interaction
4. **Callback**: When the user clicks OK or Cancel, the callback is triggered and the result is returned
5. **Fallback**: If managers aren't set, the mock hardware falls back to terminal `input()` for backward compatibility

## Files Changed

### New Files
- `src/screens/input_dialog.py`: Modal input dialog screen with keyboard

### Modified Files
- `src/hardware/mock_qr.py`: Added dialog support to QR scanner
- `src/hardware/mock_rfid.py`: Added dialog support to RFID reader
- `src/main.py`: Sets up managers on mock hardware instances
- `src/screens/__init__.py`: Exports InputDialogScreen
- `src/ui/input_box.py`: Fixed TEXT_COLOR import

## Usage

### For Developers

No changes needed to existing code! The mock hardware automatically uses on-screen dialogs when managers are set:

```python
# In any screen
qr_code = self.ui.qr.scan()  # Shows on-screen dialog
card_id = self.ui.rfid.read()  # Shows on-screen dialog
```

### For Testing Without Display

The mock hardware automatically falls back to terminal input if managers aren't set:

```python
# Direct usage without UI
qr = MockQRScanner()
code = qr.scan()  # Uses terminal input() as fallback
```

### Manual Visual Testing

Run the visual test script to verify the dialogs work correctly:

```bash
cd /home/runner/work/Sinine-kapp/Sinine-kapp
python3 manual_visual_test.py
```

## Technical Details

### InputDialogScreen

The dialog screen provides:
- Semi-transparent overlay over the previous screen
- Title text (e.g., "Scan QR Code", "Scan ID Card")
- Input box with placeholder text
- On-screen keyboard
- OK and Cancel buttons
- Callback mechanism to return the result

### Mock Hardware Event Loop

When showing a dialog, the mock hardware:
1. Pushes the dialog onto the screen stack
2. Runs a nested event loop that:
   - Handles pygame events
   - Updates the screen manager
   - Updates character animations
   - Renders all screens in the stack
   - Renders the character mascot
3. Waits for the callback to be triggered
4. Returns the user's input (or None if cancelled)

### Backward Compatibility

The implementation maintains backward compatibility:
- If `set_managers()` is not called, terminal input is used
- Existing tests that don't set managers continue to work
- The mock hardware can be used standalone for testing

## Benefits

1. **Autorun Support**: App can run on boot without terminal
2. **Better UX**: All interaction happens on the touchscreen
3. **Consistency**: Input uses the same UI components as the rest of the app
4. **Accessibility**: Touch-only users can provide mock input
5. **Testing**: Easier to test the full flow on development machines

## Testing

### Automated Tests
```bash
python3 /tmp/test_mock_integration.py
```

Verifies:
- Mock hardware instances can be created
- UI manager properly sets managers on mock hardware
- Fallback to terminal input works
- InputDialogScreen can be instantiated
- Callback mechanism works

### Manual Tests

1. Run the app
2. Click "Borrow Items"
3. Verify on-screen dialog appears (not terminal prompt)
4. Enter card ID using on-screen keyboard
5. Verify authentication works
6. Click "Scan Item"
7. Verify on-screen dialog appears
8. Enter QR code using on-screen keyboard
9. Verify item is added to basket

## Future Enhancements

Potential improvements:
- Add number-only keyboard layout for numeric inputs
- Add barcode scanner simulation visuals
- Add sound effects when dialogs appear
- Cache dialog instances for better performance
