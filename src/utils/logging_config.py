"""
Logging configuration for JARVIS production deployment.
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import json

class JARVISLogger:
    """Production-grade logging system."""
    
    def __init__(self, log_dir="logs", config=None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Load config or use defaults
        if config:
            self.level = getattr(logging, config.get("level", "INFO"))
            self.max_bytes = config.get("max_size_mb", 10) * 1024 * 1024
            self.backup_count = config.get("backup_count", 5)
        else:
            self.level = logging.INFO
            self.max_bytes = 10 * 1024 * 1024  # 10MB
            self.backup_count = 5
        
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging handlers."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Main application log (rotating file)
        app_log = self.log_dir / "jarvis.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        app_handler.setLevel(self.level)
        app_handler.setFormatter(detailed_formatter)
        
        # Error log (separate file for errors only)
        error_log = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Console handler (simple format)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(simple_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(console_handler)
        
        # Performance log (for timing data)
        perf_log = self.log_dir / "performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log,
            maxBytes=self.max_bytes,
            backupCount=2
        )
        perf_handler.setLevel(logging.DEBUG)
        perf_handler.setFormatter(simple_formatter)
        
        perf_logger = logging.getLogger('performance')
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.DEBUG)
        perf_logger.propagate = False
    
    @staticmethod
    def get_logger(name):
        """Get a logger instance."""
        return logging.getLogger(name)
    
    @staticmethod
    def log_performance(operation, duration_ms, success=True):
        """Log performance metrics."""
        perf_logger = logging.getLogger('performance')
        perf_logger.info(f"{operation}: {duration_ms:.2f}ms - {'OK' if success else 'FAIL'}")
    
    @staticmethod
    def log_command(command, intent, response_time):
        """Log voice command for analytics."""
        logger = logging.getLogger('commands')
        logger.info(f"Command: '{command}' | Intent: {intent} | Time: {response_time:.2f}ms")

class HealthMonitor:
    """Monitor system health and log issues."""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.health_log = self.log_dir / "health.json"
        self.logger = logging.getLogger('health')
        self.stats = {
            "start_time": datetime.now().isoformat(),
            "commands_processed": 0,
            "errors": 0,
            "cache_hits": 0,
            "avg_response_time": 0,
            "last_error": None
        }
    
    def record_command(self, success=True, response_time=0):
        """Record command execution."""
        self.stats["commands_processed"] += 1
        
        if not success:
            self.stats["errors"] += 1
        
        # Update average response time
        total = self.stats["commands_processed"]
        current_avg = self.stats["avg_response_time"]
        self.stats["avg_response_time"] = (current_avg * (total - 1) + response_time) / total
    
    def record_error(self, error_msg):
        """Record error occurrence."""
        self.stats["errors"] += 1
        self.stats["last_error"] = {
            "time": datetime.now().isoformat(),
            "message": str(error_msg)
        }
        self.logger.error(f"System error: {error_msg}")
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.stats["cache_hits"] += 1
    
    def save_health_report(self):
        """Save health statistics to file."""
        try:
            self.stats["uptime_seconds"] = (
                datetime.now() - datetime.fromisoformat(self.stats["start_time"])
            ).total_seconds()
            
            with open(self.health_log, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")
    
    def get_health_status(self):
        """Get current health status."""
        uptime = (datetime.now() - datetime.fromisoformat(self.stats["start_time"])).total_seconds()
        
        error_rate = (self.stats["errors"] / max(self.stats["commands_processed"], 1)) * 100
        cache_rate = (self.stats["cache_hits"] / max(self.stats["commands_processed"], 1)) * 100
        
        status = {
            "status": "healthy" if error_rate < 5 else "degraded" if error_rate < 20 else "unhealthy",
            "uptime_hours": uptime / 3600,
            "commands_processed": self.stats["commands_processed"],
            "error_rate": f"{error_rate:.1f}%",
            "cache_hit_rate": f"{cache_rate:.1f}%",
            "avg_response_ms": f"{self.stats['avg_response_time']:.2f}"
        }
        
        return status

def setup_production_logging(config=None):
    """Setup production logging configuration."""
    logger_instance = JARVISLogger(config=config)
    logger = logger_instance.get_logger('jarvis')
    logger.info("="*60)
    logger.info("JARVIS Voice Assistant Started")
    logger.info(f"Log directory: {logger_instance.log_dir}")
    logger.info("="*60)
    return logger_instance
