# Proper Solution Plan: Native Dictation App

## Overview
A native macOS menu bar application with global hotkeys, accessibility-based text insertion, and integrated speech recognition. Professional-grade solution that feels like a built-in macOS feature.

## Architecture
```
[Native Menu Bar App] → [Global Hotkey System] → [Speech Recognition] → [Accessibility Text Insertion] → [Any App at Cursor]
```

## Core Design Principles
1. **Native macOS integration**: Feels like built-in dictation
2. **Accessibility-first**: Uses proper text insertion APIs
3. **Context awareness**: Adapts behavior based on active app and UI element
4. **Privacy focused**: Local processing when possible
5. **Professional UX**: Menu bar app with proper state management

## Implementation Plan

### Phase 1: Native App Foundation
1. **Swift/Objective-C menu bar app**
   - NSStatusItem for menu bar presence
   - Global hotkey registration (Carbon or modern APIs)
   - Background service architecture
   - Proper macOS app lifecycle management

2. **Alternative: Python with native bindings**
   - PyObjC for macOS integration
   - Faster prototyping than Swift
   - Can package as .app bundle later

### Phase 2: Speech Recognition Engine
1. **Multi-engine approach**
   - **Primary**: NSSpeechRecognizer (offline, privacy-focused)
   - **Fallback**: Web Speech API via embedded WebView
   - **Optional**: Whisper.cpp (if performance allows)
   - Engine selection based on availability and user preference

2. **Speech processing pipeline**
   - Voice activity detection
   - Noise filtering and normalization
   - Confidence scoring and error handling
   - Real-time interim results display

### Phase 3: Accessibility Text Insertion
1. **AXUIElement-based insertion**
   - Query active app's accessibility tree
   - Find focused text field/cursor position
   - Insert text at exact cursor location
   - Handle various text field types (NSTextField, web inputs, etc.)

2. **Fallback mechanisms**
   - Keystroke simulation for non-accessible apps
   - Clipboard bridge for compatibility
   - App-specific integrations (Terminal, Xcode, etc.)

### Phase 4: Advanced Features
1. **Context awareness**
   - App-specific behavior (code vs prose vs terminal)
   - Text field type detection (password, search, code)
   - Smart formatting (camelCase in code, proper punctuation in prose)

2. **User experience enhancements**
   - Inline editing of dictated text
   - Undo/redo for dictation actions
   - Custom vocabulary and corrections
   - Multi-language support

## Technical Implementation

### Native App Structure (Swift)
```swift
import Cocoa
import Speech

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var statusBarItem: NSStatusItem!
    var speechRecognizer: SFSpeechRecognizer!
    var hotKeyCenter: HotKeyCenter!

    func applicationDidFinishLaunching(_ notification: Notification) {
        setupMenuBar()
        setupSpeechRecognition()
        setupGlobalHotkeys()
        setupAccessibilityPermissions()
    }
}

class DictationManager {
    func startDictation() {
        // Get focused element
        let focusedElement = AXUIElementCopyAttributeValue(
            systemWideElement,
            kAXFocusedUIElementAttribute,
            &focusedElement
        )

        // Start speech recognition
        startSpeechRecognition { [weak self] text in
            self?.insertTextAtCursor(text, in: focusedElement)
        }
    }

    func insertTextAtCursor(_ text: String, in element: AXUIElement) {
        // Use accessibility APIs to insert text
        AXUIElementSetAttributeValue(element, kAXValueAttribute, text as CFString)
    }
}
```

### Python Alternative (PyObjC)
```python
import objc
from Foundation import *
from AppKit import *
from ApplicationServices import *

class DictationApp(NSObject):
    def init(self):
        self = objc.super(DictationApp, self).init()
        self.status_item = None
        self.speech_recognizer = None
        return self

    def setupMenuBar(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSSquareStatusItemLength
        )
        self.status_item.setTitle_("🎤")

    def setupGlobalHotkey(self):
        # Register Cmd+Shift+Space
        pass

    def startDictation(self):
        # Get focused accessibility element
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        pid = app.processIdentifier()
        app_ref = AXUIElementCreateApplication(pid)

        focused_element = self.getFocusedElement(app_ref)

        # Start speech recognition and insert at cursor
        self.recognizeSpeech(lambda text: self.insertText(text, focused_element))
```

### Accessibility Text Insertion
```swift
func insertTextAtCursor(_ text: String, in element: AXUIElement) {
    // Method 1: Direct value setting (best)
    if AXUIElementIsAttributeSettable(element, kAXValueAttribute) {
        AXUIElementSetAttributeValue(element, kAXValueAttribute, text as CFString)
        return
    }

    // Method 2: Selection manipulation
    var selectionRange: CFTypeRef?
    AXUIElementCopyAttributeValue(element, kAXSelectedTextRangeAttribute, &selectionRange)

    // Insert text at selection
    AXUIElementSetAttributeValue(element, kAXSelectedTextAttribute, text as CFString)

    // Method 3: Keystroke simulation fallback
    if above methods fail {
        simulateKeystrokes(text)
    }
}
```

### Speech Recognition Integration
```swift
class SpeechManager: NSObject, SFSpeechRecognizerDelegate {
    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var audioEngine = AVAudioEngine()

    func startRecording() throws {
        // Configure audio session
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

        // Create recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            throw SpeechError.recognitionRequestFailed
        }

        recognitionRequest.shouldReportPartialResults = true

        // Start recognition task
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                let text = result.bestTranscription.formattedString
                if result.isFinal {
                    self.onFinalTranscription(text)
                } else {
                    self.onPartialTranscription(text)
                }
            }
        }

        // Configure audio input
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()
    }
}
```

## User Experience Design

### Menu Bar Interface
```
🎤 (Idle)
🔴 (Listening)
⏸️ (Processing)
✅ (Success)
❌ (Error)
```

### Settings Panel
- **Hotkey configuration**: Customizable global shortcut
- **Speech engine selection**: Local vs online options
- **App-specific settings**: Different behavior per app
- **Privacy controls**: Data handling preferences
- **Accessibility permissions**: Setup wizard

### Workflow States
1. **Idle**: Menu bar shows microphone icon
2. **Activated**: User presses hotkey, icon turns red
3. **Listening**: Audio visualization, interim results in overlay
4. **Processing**: Brief processing state for final recognition
5. **Inserted**: Text appears at cursor, success indicator
6. **Error**: Clear error state with retry option

## Advanced Features

### Context-Aware Formatting
```swift
func formatTextForContext(_ text: String, app: String, element: AXUIElement) -> String {
    switch app {
    case "Xcode", "Visual Studio Code":
        return formatForCode(text)
    case "Terminal":
        return formatForTerminal(text)
    case "Mail", "Messages":
        return formatForProse(text)
    default:
        return smartFormat(text, basedOn: element)
    }
}
```

### Custom Vocabulary
- User-defined abbreviations and expansions
- Technical term recognition for developers
- Project-specific vocabulary loading
- Learning from user corrections

### Privacy & Security
- All speech processing local by default
- Optional cloud processing with explicit consent
- No data logging or telemetry
- Accessibility permission management

## Pros
- **Native experience**: Feels like built-in macOS feature
- **Precise text insertion**: Uses proper accessibility APIs
- **Context awareness**: Adapts to different apps and scenarios
- **Privacy focused**: Local processing, no external dependencies
- **Professional quality**: Proper error handling, state management
- **Extensible**: Can add features like custom vocabulary, corrections

## Cons
- **Development complexity**: Requires native macOS development
- **Accessibility permissions**: Users must grant system access
- **Speech engine limitations**: NSSpeechRecognizer quality varies
- **Maintenance overhead**: Need to handle macOS updates, app compatibility
- **Testing complexity**: Many edge cases across different apps

## Development Approach

### MVP (Week 1-2)
1. Basic menu bar app with global hotkey
2. Simple speech recognition (Web Speech API fallback)
3. Basic text insertion via accessibility APIs
4. Core workflow: hotkey → listen → insert

### V1 (Week 3-4)
1. Native NSSpeechRecognizer integration
2. Improved accessibility text insertion
3. App-specific handling for common cases
4. Settings panel and configuration

### V2 (Month 2)
1. Context-aware formatting
2. Custom vocabulary support
3. Inline editing capabilities
4. Advanced error handling and recovery

## Risk Assessment
- **Accessibility API changes**: Apple may modify APIs
- **App compatibility**: Some apps may not support text insertion
- **Permission model**: Users may be hesitant to grant accessibility access
- **Performance**: Speech recognition CPU usage on older hardware

## Success Metrics
- **Accuracy**: >95% speech recognition accuracy
- **Latency**: <2 seconds from speech end to text insertion
- **Compatibility**: Works with 90% of common macOS apps
- **User adoption**: Natural integration into daily workflow

This represents a production-quality solution that could rival Apple's built-in dictation while providing the flexibility and universal app support you need.