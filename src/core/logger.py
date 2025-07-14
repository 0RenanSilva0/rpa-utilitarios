import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir='logs', log_level=logging.INFO):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        log_filename = datetime.now().strftime('%Y-%m-%d.log')
        log_path = os.path.join(self.log_dir, log_filename)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def get_logger(self):
        return self.logger