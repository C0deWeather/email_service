import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """
    Configures the root logger to output structured JSON logs to stdout.
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Set the default log level
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers (like the default one)
    for handler in logger.handlers:
        logger.removeHandler(handler)
        
    # Create a new handler to log to stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Define the JSON log format
    # This adds standard log fields plus any 'extra' fields we pass
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
   