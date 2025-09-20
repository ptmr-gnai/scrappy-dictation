# CLAUDE Configuration v1 - Compounding Engineering

## Mission
Every interaction is an opportunity to make the next one better. Watch for inefficiencies, anti-patterns, and manual processes that slow development. Proactively suggest improvements that compound over time.

## Compounding Engineering Principles

### 1. Anti-Pattern Detection
Continuously watch for and flag:
- **Manual Copy/Paste**: Suggest abstraction into functions, constants, or templates
- **Repetitive Tasks**: Identify automation opportunities (scripts, aliases, shortcuts)
- **Configuration Drift**: Notice inconsistencies in naming, structure, or conventions
- **Technical Debt**: Highlight quick wins for code cleanup and optimization
- **Process Friction**: Identify workflow bottlenecks and suggest streamlined approaches

### 2. Continuous Improvement
After each task completion:
- **Document Learnings**: What patterns emerged? What could be automated?
- **Update This File**: Suggest additions to improve future interactions
- **Create Shortcuts**: Propose aliases, scripts, or templates for repeated workflows
- **Refine Conventions**: Notice and suggest consistency improvements

### 3. Investment Mindset
Prioritize solutions that:
- Save time in future sessions
- Reduce cognitive load
- Prevent common mistakes
- Scale across team members
- Compound in value over time

## Tech Stack
- **Core Language**: Python 3.9+
- **Speech Recognition**: Chrome Web Speech API (Google's engine)
- **WebSocket Communication**: websockets 15.x
- **System Integration**: pynput (global hotkeys), pyperclip (clipboard)
- **HTTP Server**: Built-in Python http.server
- **Browser**: Google Chrome (persistent background tab)
- **Platform**: macOS (accessibility APIs)

## Project Structure
```
scrappy-dictation/                    # Zero-manual-step dictation system
├── websocket_dictation_fixed.py     # 🚀 MAIN: Complete working system
├── speech-persistent.html           # WebSocket-controlled Chrome tab
├── websocket_server.py              # WebSocket communication infrastructure
├── clipboard_bridge_v*.py           # Evolution: Simple clipboard approaches
├── speech-auto.html                 # Auto-start speech recognition page
├── concept.md                       # Initial brainstorming and approaches
├── *-bridge-plan.md                 # Implementation strategy documents
├── websocket-solution-proposal.md   # Technical architecture specification
└── CLAUDE.md                        # This configuration file
```

## Essential Commands
```bash
# Core Dictation System
python3 websocket_dictation_fixed.py  # 🚀 Start complete dictation system
# Usage: Right Cmd → continuous listening → Right Cmd → paste

# Dependencies
pip3 install websockets pynput pyperclip  # Install required packages

# System Setup (one-time)
# macOS: System Preferences → Security & Privacy → Privacy → Input Monitoring
# Add Terminal to allowed apps for global hotkey monitoring

# Development & Testing
python3 websocket_server.py           # Test WebSocket server standalone
open speech-persistent.html           # Manual browser testing
git log --oneline -5                  # Review recent development progress

# Legacy Approaches (for reference)
python3 clipboard_bridge_v3.py        # Simple clipboard-based approach
python3 dictation-server.py           # Original Terminal-only version
```

## Code Style & Conventions
- **Python Files**: `snake_case` for modules, `PascalCase` for classes
- **HTML Files**: `kebab-case` with descriptive purpose (e.g., `speech-persistent.html`)
- **Function Naming**: Descriptive verbs (`handle_transcript`, `start_dictation`)
- **Async/Await**: Consistent async patterns with proper thread-safe communication
- **Error Handling**: Comprehensive try/catch with user-friendly error messages
- **WebSocket Protocol**: Structured JSON messages with `type` and `timestamp` fields
- **Documentation**: Inline docstrings for complex async coordination

## Efficiency Patterns to Promote
1. **Template Creation**: When creating similar files, generate templates
2. **Configuration as Code**: Store common setups in version-controlled configs
3. **Snippet Libraries**: Build reusable code snippets for common patterns
4. **Documentation Integration**: Keep docs close to code, update simultaneously
5. **Testing Automation**: Write tests that prevent future regressions

## Anti-Patterns to Flag & Fix
1. **Magic Numbers**: Replace with named constants
2. **Duplicate Code**: Extract into shared utilities
3. **Manual File Creation**: Create generators for common file types
4. **Inconsistent Naming**: Establish and enforce naming conventions
5. **Missing Documentation**: Add inline docs for complex logic
6. **Hard-coded Values**: Move to configuration files
7. **Copy-Paste Debugging**: Create proper debugging workflows

## Repository Workflow
- Branch naming: `feature/description` or `fix/description`
- Commit format: `type: description` (e.g., `feat: add user authentication`)
- PR requirements: Tests pass, linting clean, description includes context
- Code review: Focus on maintainability and future developer experience

## Key Patterns Discovered This Session

### 1. **Iterative Complexity Management**
- **Pattern**: Start with simplest possible solution, then add complexity only when needed
- **Example**: clipboard_bridge.py → clipboard_bridge_v2.py → websocket_dictation_fixed.py
- **Learning**: Each iteration solved specific limitations without over-engineering

### 2. **Thread-Safe Async Communication**
- **Challenge**: Global hotkeys run in different thread than WebSocket event loop
- **Solution**: `asyncio.run_coroutine_threadsafe()` for cross-thread async coordination
- **Anti-Pattern**: Using `asyncio.create_task()` from sync thread (causes "no event loop" errors)

### 3. **WebSocket Protocol Design**
- **Effective Pattern**: Structured JSON messages with `type`, `timestamp`, and specific data fields
- **Key Insight**: Browser-to-server communication works better than server-to-browser control
- **Learning**: WebSocket serves as command channel, not data pipeline (clipboard handles data)

### 4. **Hardware Constraint Workarounds**
- **Constraint**: 2015 MBP insufficient for local AI models
- **Creative Solution**: Leverage Chrome's cloud-connected speech recognition APIs
- **Architecture**: Local coordination + cloud processing = optimal resource utilization

### 5. **User Experience Iteration**
- **V1**: Manual clicking required → Poor UX
- **V2**: Auto-start but auto-stop between pauses → Interrupts natural speech
- **V3**: User-controlled start/stop with text accumulation → Perfect workflow
- **Learning**: UX details matter more than technical sophistication

## Continuous Learning Protocol
At the end of each session, consider:

1. **What was repeated?** → Can we automate it?
2. **What was confusing?** → Can we document it?
3. **What was slow?** → Can we optimize it?
4. **What was error-prone?** → Can we prevent it?
5. **What patterns emerged?** → Can we template them?

## Session Improvement Tracking

## Recent Improvements
- **2025-09-20**: Built complete zero-manual-step dictation system from concept to production
  - **Evolution**: clipboard_bridge.py → websocket_dictation_fixed.py (solved all manual interaction issues)
  - **Breakthrough**: WebSocket-controlled persistent Chrome tab eliminates UI interaction
  - **Key Innovation**: Continuous speech accumulation until user explicitly stops
  - **Technical Win**: Thread-safe async/sync coordination for global hotkeys + WebSocket communication
  - **Result**: Right Cmd → continuous listening → Right Cmd → complete text paste (no interruptions)

- **2025-09-20**: Solved websockets 15.x compatibility issues through iterative debugging
  - **Pattern**: Modern library versions often change handler signatures - always check version compatibility
  - **Solution**: Used proper async function signatures instead of lambda wrappers

- **2025-09-20**: Achieved Google-quality speech recognition on 2015 MBP hardware limitation
  - **Constraint**: 2015 MBP can't run local Whisper models
  - **Breakthrough**: Chrome Web Speech API provides high-quality recognition via cloud processing
  - **Architecture**: Local WebSocket server + persistent browser tab = best of both worlds

## Next Optimization Targets
- [ ] **Auto-startup script**: Create launch daemon for system startup integration
- [ ] **Voice commands**: Extend beyond dictation to include system control ("new line", "delete last word")
- [ ] **Multi-language support**: Dynamic language switching via voice commands or hotkeys
- [ ] **Text formatting**: Voice-controlled punctuation and formatting ("all caps", "new paragraph")
- [ ] **Custom vocabulary**: Personal name/term recognition and auto-correction
- [ ] **Usage analytics**: Track dictation sessions and accuracy improvements over time
- [ ] **Port binding optimization**: Smart port selection to avoid conflicts with other services

## Do Not
- Manually repeat tasks that could be scripted
- Copy-paste code without considering abstraction
- Accept inefficient workflows as "just how we do things"
- Skip documentation for complex or non-obvious solutions
- Ignore opportunities to reduce future cognitive load

## Remember
Every inefficiency spotted is an investment opportunity. Every manual process is automation waiting to happen. Every repeated pattern is a template in disguise. Make each session count for all future sessions.

---

*This file should evolve with each session. Update it when you discover new patterns, inefficiencies, or optimization opportunities.*