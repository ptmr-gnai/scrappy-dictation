# Scrappy Dictation

A zero-manual-step voice dictation system for macOS that combines Chrome's Web Speech API with WebSocket communication for seamless voice-to-text input.

## Features

- **Hands-free Operation**: Right Cmd key to start/stop dictation
- **Continuous Listening**: Accumulates speech until you stop, no interruptions
- **Zero Manual Steps**: Direct paste to active application
- **High-Quality Recognition**: Uses Google's Web Speech API via Chrome
- **Secure WebSocket Communication**: Token-based authentication
- **Production Ready**: Comprehensive error handling and recovery

## Quick Start

1. **Install Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Grant Permissions**
   - macOS: System Preferences → Security & Privacy → Privacy → Input Monitoring
   - Add Terminal to allowed apps for global hotkey monitoring

3. **Run the System**
   ```bash
   python3 src/server/websocket_dictation_fixed.py
   ```

4. **Use**
   - Right Cmd → Start continuous listening
   - Speak naturally (text accumulates)
   - Right Cmd → Stop and paste to active app

## Architecture

- **Main Server**: `src/server/websocket_dictation_fixed.py` - Complete dictation system
- **Client Interface**: `src/client/speech-persistent.html` - WebSocket-controlled Chrome tab
- **WebSocket Server**: `src/server/websocket_server.py` - Communication infrastructure

## Project Structure

```
scrappy-dictation/
├── src/                          # Core application code
│   ├── server/                   # Backend services
│   ├── client/                   # Frontend interface
│   └── utils/                    # Utilities and testing
├── docs/                         # Documentation and analysis
├── archive/                      # Development iterations
├── scripts/                      # Build and utility scripts
└── requirements.txt              # Python dependencies
```

## Development Process

This project showcases iterative development with comprehensive documentation:

- **docs/**: Technical analysis, security reports, architecture documentation
- **archive/**: Complete development history from simple clipboard approach to WebSocket solution

## Requirements

- **macOS**: Uses macOS accessibility APIs
- **Python 3.9+**: Modern async/await support
- **Google Chrome**: For Web Speech API access
- **Microphone**: Hardware or software audio input

## Security

The system implements production-ready security features:
- Token-based WebSocket authentication
- Restricted HTTP file serving
- Input sanitization and validation
- Rate limiting and abuse prevention

See `docs/SECURITY_ANALYSIS_REPORT.md` for detailed security analysis.

## License

MIT License - see LICENSE file for details.

---

**Note**: This system is optimized for personal use on trusted local networks. See security documentation before deploying in shared environments.