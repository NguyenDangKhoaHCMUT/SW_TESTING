"""
Config Manager for Level 2 - Data-driven testing with element locators
Manages configuration for test elements and URLs
"""
import pandas as pd
import os
import csv


class ConfigManager:
    """Manages configuration for test elements and URLs"""
    
    def __init__(self, config_file):
        """
        Initialize ConfigManager with config file
        
        Args:
            config_file: Path to config CSV file
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        # Read CSV with proper quoting to handle commas in values
        # quoting=1 means QUOTE_ALL, which handles quoted fields correctly
        self.config = pd.read_csv(config_file, quoting=csv.QUOTE_ALL)
        self.urls = {}
        self.elements = {}
        self._load_config()
    
    def _load_config(self):
        """Load URLs and elements from config file"""
        # Separate URLs and elements
        url_config = self.config[self.config['section'] == 'url']
        element_config = self.config[self.config['section'] == 'element']
        
        # Load URLs
        for _, row in url_config.iterrows():
            self.urls[row['element_name']] = row['locator_value']
        
        # Load Elements
        for _, row in element_config.iterrows():
            self.elements[row['element_name']] = {
                'locator_type': row['locator_type'],
                'locator_value': row['locator_value'],
                'wait_type': row['wait_type'],
                'description': row.get('description', '')
            }
    
    def get_url(self, url_name):
        """
        Get URL by name
        
        Args:
            url_name: Name of the URL in config
            
        Returns:
            URL string or None if not found
        """
        return self.urls.get(url_name)
    
    def get_element_config(self, element_name):
        """
        Get element configuration by name
        
        Args:
            element_name: Name of the element in config
            
        Returns:
            Dictionary with element config or None if not found
        """
        return self.elements.get(element_name)
    
    def list_urls(self):
        """List all available URLs"""
        return list(self.urls.keys())
    
    def list_elements(self):
        """List all available elements"""
        return list(self.elements.keys())

