"""
Element Helper for Level 2 - Helper functions to interact with elements using config
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_element_by_config(driver, config_manager, element_name, timeout=10):
    """
    Find element using config
    
    Args:
        driver: Selenium WebDriver instance
        config_manager: ConfigManager instance
        element_name: Name of element in config
        timeout: Maximum time to wait for element (default: 10 seconds)
        
    Returns:
        WebElement if found
        
    Raises:
        ValueError: If element not found in config or unsupported locator type
        TimeoutException: If element not found within timeout
    """
    element_config = config_manager.get_element_config(element_name)
    if not element_config:
        raise ValueError(f"Element '{element_name}' not found in config")
    
    locator_type = element_config['locator_type']
    locator_value = element_config['locator_value']
    wait_type = element_config['wait_type']
    
    # Map locator_type to By enum
    by_map = {
        'xpath': By.XPATH,
        'id': By.ID,
        'css': By.CSS_SELECTOR,
        'name': By.NAME,
        'class_name': By.CLASS_NAME,
        'tag_name': By.TAG_NAME,
        'link_text': By.LINK_TEXT,
        'partial_link_text': By.PARTIAL_LINK_TEXT
    }
    
    by = by_map.get(locator_type.lower())
    if not by:
        raise ValueError(f"Unsupported locator type: {locator_type}")
    
    # Map wait_type to ExpectedCondition
    wait_map = {
        'clickable': EC.element_to_be_clickable,
        'presence': EC.presence_of_element_located,
        'visible': EC.visibility_of_element_located
    }
    
    wait_condition = wait_map.get(wait_type.lower(), EC.presence_of_element_located)
    
    element = WebDriverWait(driver, timeout).until(
        wait_condition((by, locator_value))
    )
    return element


def click_element(driver, config_manager, element_name, timeout=10):
    """
    Click element using config
    
    Args:
        driver: Selenium WebDriver instance
        config_manager: ConfigManager instance
        element_name: Name of element in config
        timeout: Maximum time to wait for element
        
    Returns:
        WebElement that was clicked
    """
    element = find_element_by_config(driver, config_manager, element_name, timeout)
    element.click()
    return element


def input_text(driver, config_manager, element_name, text, timeout=10):
    """
    Input text to element using config
    
    Args:
        driver: Selenium WebDriver instance
        config_manager: ConfigManager instance
        element_name: Name of element in config
        text: Text to input
        timeout: Maximum time to wait for element
        
    Returns:
        WebElement that received text
    """
    element = find_element_by_config(driver, config_manager, element_name, timeout)
    element.clear()
    if text:
        element.send_keys(str(text))
    return element


def get_text(driver, config_manager, element_name, timeout=10):
    """
    Get text from element using config
    
    Args:
        driver: Selenium WebDriver instance
        config_manager: ConfigManager instance
        element_name: Name of element in config
        timeout: Maximum time to wait for element
        
    Returns:
        Text content of element (stripped)
    """
    element = find_element_by_config(driver, config_manager, element_name, timeout)
    return element.text.strip()


def get_element_attribute(driver, config_manager, element_name, attribute, timeout=10):
    """
    Get attribute value from element using config
    
    Args:
        driver: Selenium WebDriver instance
        config_manager: ConfigManager instance
        element_name: Name of element in config
        attribute: Attribute name to get
        timeout: Maximum time to wait for element
        
    Returns:
        Attribute value
    """
    element = find_element_by_config(driver, config_manager, element_name, timeout)
    return element.get_attribute(attribute)

