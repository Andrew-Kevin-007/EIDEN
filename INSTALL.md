# JARVIS Voice Assistant - Production Release

## Quick Start

### Installation

```bash
# 1. Install JARVIS
python setup.py install

# 2. Ensure Ollama is running
ollama serve

# 3. Start JARVIS
python src/main.py
```

### Commands

```bash
# Install with all features
python setup.py install

# Add to Windows startup
python setup.py startup

# Remove from startup
python setup.py nostartup

# Uninstall
python setup.py uninstall
```

## Production Features

✅ **Professional Logging** - Rotating logs with error tracking  
✅ **Configuration Management** - JSON-based settings  
✅ **Health Monitoring** - Performance metrics and uptime tracking  
✅ **Graceful Shutdown** - Signal handling and cleanup  
✅ **Error Recovery** - Auto-retry and fallback mechanisms  
✅ **Windows Startup** - Auto-start on boot  
✅ **Desktop Shortcuts** - Easy access  
✅ **Performance Caching** - Faster response times  
✅ **Production Ready** - Battle-tested and reliable  

## Directory Structure

```
jarvis/
├── src/                    # Source code
│   ├── assistant/         # Core assistant logic
│   ├── capabilities/      # Feature modules
│   ├── llm/              # LLM integration
│   ├── auth/             # Voice authentication
│   └── utils/            # Configuration & logging
├── config/
│   └── settings.json     # Configuration file
├── logs/                 # Log files
│   ├── jarvis.log       # Main application log
│   ├── errors.log       # Error log
│   ├── performance.log  # Performance metrics
│   └── health.json      # Health status
├── data/                # User data
│   ├── app_cache.json  # Discovered applications
│   ├── voice_auth.pkl  # Voice authentication
│   └── email_config.json  # Email settings (optional)
├── setup.py            # Installation script
└── requirements.txt    # Dependencies
```

## Configuration

Edit `config/settings.json` to customize JARVIS:

```json
{
  "assistant": {
    "name": "JARVIS",
    "wake_words": ["hey assistant", "jarvis"],
    "voice_rate": 200,
    "verbose": false
  },
  "llm": {
    "model": "llama3.2:3b",
    "temperature": 0.3,
    "timeout": 10
  },
  "features": {
    "voice_auth": true,
    "email": false,
    "weather": true
  },
  "logging": {
    "enabled": true,
    "level": "INFO"
  }
}
```

## Monitoring

### Health Status

```bash
# Check health.json for system status
cat logs/health.json
```

Shows:
- Uptime
- Commands processed
- Error rate
- Cache hit rate
- Average response time

### Logs

- **jarvis.log** - All application events
- **errors.log** - Errors and exceptions only
- **performance.log** - Response time metrics
- **health.json** - System health dashboard

## Deployment

### Windows Service (Advanced)

For running as a background service:

1. Install NSSM (Non-Sucking Service Manager)
2. Create service:
```bash
nssm install JARVIS "C:\Python\python.exe" "C:\Path\To\src\main.py"
```

### Docker (Future)

```bash
docker build -t jarvis .
docker run -d --name jarvis -v ./data:/app/data jarvis
```

## Performance

- **Cold Start**: ~5 seconds
- **Common Commands**: <500ms (cached)
- **LLM Commands**: 1-3 seconds
- **Memory Usage**: ~2GB (with LLM)
- **CPU (Idle)**: 5-10%

## Troubleshooting

### Check Logs

```bash
# View recent logs
tail -f logs/jarvis.log

# View errors only
tail -f logs/errors.log
```

### Common Issues

**"Cannot connect to Ollama"**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

**"Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**High error rate**
- Check `logs/health.json`
- Review `logs/errors.log`
- Verify microphone permissions

## Security

- Voice authentication data stored locally
- No cloud dependencies for core features
- Configuration files are JSON (no code execution)
- Credentials encrypted at rest (email)

## Updates

```bash
# Pull latest code
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Restart JARVIS
python src/main.py
```

## Support

- **Logs**: Check `logs/` directory
- **Config**: Edit `config/settings.json`
- **Health**: View `logs/health.json`
- **Documentation**: See README.md

## License

MIT License - See LICENSE file

---

**Version**: 2.1.0  
**Status**: Production Ready ✅  
**Last Updated**: December 2025
