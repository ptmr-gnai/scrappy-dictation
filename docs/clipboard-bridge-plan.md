# Clipboard Bridge Solution Plan

## Overview
Quick & dirty solution using clipboard as intermediary between speech recognition and text insertion. Global hotkey triggers dictation, result goes to clipboard, then auto-pastes into active app.

## Architecture
```
[Global Hotkey] → [Start Speech Recognition] → [Text to Clipboard] → [Auto Paste] → [Any App]
```

## Implementation Plan

### Phase 1: Core Components
1. **Background daemon** (Python script)
   - Listens for global hotkey (e.g., Cmd+Shift+Space)
   - Manages speech recognition lifecycle
   - Handles clipboard operations
   - Simulates paste command

2. **Speech recognition trigger**
   - Programmatically open Chrome with speech page
   - OR embed lightweight speech recognition
   - Capture transcribed text

3. **Clipboard & paste automation**
   - Write text to macOS clipboard
   - Send Cmd+V to active application
   - Handle timing/delays appropriately

### Phase 2: User Experience
1. **Status indicators**
   - Menu bar icon showing listening state
   - Audio feedback (beep on start/stop)
   - Visual feedback in menu bar

2. **Configuration**
   - Customizable hotkey
   - Speech recognition timeout settings
   - Enable/disable auto-paste

### Phase 3: Edge Cases
1. **App compatibility**
   - Handle apps that don't accept clipboard paste
   - Special handling for Terminal (avoid command execution)
   - Detect password fields and skip

2. **Error handling**
   - Network failures (Chrome speech needs internet)
   - Speech recognition timeouts
   - Clipboard access issues

## Technical Implementation

### Dependencies
```bash
pip install pynput pyobjc keyboard
```

### Core Architecture
```python
# Global hotkey listener
from pynput import keyboard
import subprocess
import time
import pyperclip

class ClipboardDictation:
    def __init__(self):
        self.is_listening = False
        self.hotkey = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.KeyCode.from_char(' ')}

    def on_hotkey_press(self):
        if not self.is_listening:
            self.start_dictation()
        else:
            self.stop_dictation()

    def start_dictation(self):
        # Method 1: Launch Chrome with speech page
        # Method 2: Use local speech recognition
        pass

    def on_text_received(self, text):
        # Put text in clipboard
        pyperclip.copy(text)
        # Simulate Cmd+V
        self.paste_to_active_app()

    def paste_to_active_app(self):
        # Get active app info
        # Send Cmd+V keystroke
        pass
```

### Speech Recognition Options

#### Option A: Chrome Automation
```python
def start_chrome_dictation(self):
    # Open Chrome with our speech page
    subprocess.run(['open', '-a', 'Google Chrome', 'speech-test.html'])
    # Wait for user to start speaking
    # Monitor clipboard for changes
```

#### Option B: Embedded Browser
```python
# Use PyQt5/Tkinter WebView
# Embed Chrome engine with speech recognition
# More complex but cleaner UX
```

#### Option C: Native macOS Speech
```python
# Use NSSpeechRecognizer via pyobjc
# Requires more complex Objective-C bridging
# But works offline
```

### Clipboard Monitoring
```python
import time
import pyperclip

def monitor_clipboard_changes():
    last_clipboard = ""
    while self.is_listening:
        current = pyperclip.paste()
        if current != last_clipboard and self.is_speech_text(current):
            self.on_text_received(current)
            last_clipboard = current
        time.sleep(0.1)
```

### Auto-paste Implementation
```python
from pynput.keyboard import Key, Controller

def paste_to_active_app(self):
    keyboard = Controller()

    # Get active app (to handle special cases)
    active_app = self.get_active_app()

    if active_app == "Terminal" and self.should_avoid_execution():
        # Don't auto-paste commands in terminal
        return

    # Simulate Cmd+V
    keyboard.press(Key.cmd)
    keyboard.press(KeyCode.from_char('v'))
    keyboard.release(KeyCode.from_char('v'))
    keyboard.release(Key.cmd)
```

## User Workflow
1. User presses **Cmd+Shift+Space** in any app
2. Menu bar icon changes to "listening" state
3. User speaks their text
4. System captures speech, puts in clipboard
5. System auto-pastes into current app at cursor position
6. Menu bar icon returns to ready state

## Pros
- **Quick to implement**: Leverages existing clipboard/paste mechanisms
- **Universal compatibility**: Works with any app that accepts paste
- **No app-specific code**: Uses standard macOS paste behavior
- **Familiar UX**: Uses clipboard like normal copy/paste

## Cons
- **Overwrites clipboard**: Loses current clipboard contents
- **Timing sensitive**: Need delays between clipboard write and paste
- **Chrome dependency**: Relies on browser for speech recognition
- **No inline editing**: Can't modify dictated text before paste

## Risk Mitigation
1. **Clipboard backup**: Save current clipboard before dictation, restore after
2. **Confirmation mode**: Show preview before auto-paste (optional)
3. **App blacklist**: Skip auto-paste for Terminal, password fields, etc.
4. **Timeout handling**: Auto-stop listening after 30 seconds

## Quick Prototype Steps
1. Create Python script with global hotkey listener
2. Test clipboard write/read functionality
3. Implement auto-paste with keystroke simulation
4. Connect to existing Chrome speech recognition
5. Add menu bar status indicator
6. Test with various apps (Terminal, VS Code, browsers, etc.)

## Estimated Timeline
- **Day 1**: Basic hotkey + clipboard + paste working
- **Day 2**: Chrome integration + error handling
- **Day 3**: Menu bar UI + configuration
- **Day 4**: Testing + edge case handling

This approach gets us 80% functionality with 20% effort - perfect for a scrappy solution!