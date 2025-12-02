"""
Level 2: Data-driven testing with element locators from config file
All element locators and URLs are read from config_withdraw.csv
"""
import time
import os
import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select

# Add common directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
common_dir = os.path.join(os.path.dirname(script_dir), 'common')
sys.path.insert(0, common_dir)

from config_manager import ConfigManager
from element_helper import find_element_by_config, click_element, input_text, get_text

# ==== Load data and config ====
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "data_withdraw.csv")
config_path = os.path.join(script_dir, "config_withdraw.csv")

data = pd.read_csv(csv_path)
config_manager = ConfigManager(config_path)

# ==== Setup output file ====
output_file = os.path.join(script_dir, "test_result_withdraw.csv")
test_results = []

# ==== Setup driver ====
driver = webdriver.Chrome()
driver.maximize_window()

# ==== Setup: Login as customer before testing ====
# Step 1: Open homepage (using config)
homepage_url = config_manager.get_url("homepage_url")
driver.get(homepage_url)
time.sleep(2)

# Step 2: Click Customer Login button (using config)
click_element(driver, config_manager, "customer_login_button")
time.sleep(1)

# Step 3: Select customer from dropdown (using config)
customer_dropdown = find_element_by_config(driver, config_manager, "user_select_dropdown")
select = Select(customer_dropdown)
select.select_by_index(1)  # Select first customer (index 1, skip "---Your Name---")
time.sleep(1)

# Step 4: Click Login button (using config)
click_element(driver, config_manager, "login_button")
time.sleep(2)

print("Setup completed: Customer logged in successfully")

# ==== Function to ensure balance is 5096 before each test ====
def ensure_balance_is_5096():
    """Ensure account balance is exactly 5096 before each test case"""
    # Reload page to clear previous state (using config)
    account_url = config_manager.get_url("account_page_url")
    driver.get(account_url)
    time.sleep(1)
    
    # Get current balance from the page (using config)
    try:
        balance_element = find_element_by_config(driver, config_manager, "balance_strong")
        current_balance = int(balance_element.text.strip())
    except:
        # Try alternative xpath for balance
        try:
            from selenium.webdriver.common.by import By
            balance_element = driver.find_element(By.XPATH, "//strong[2]")
            current_balance = int(balance_element.text.strip())
        except:
            print("Warning: Could not read current balance, assuming 0")
            current_balance = 0
    
    target_balance = 5096
    difference = target_balance - current_balance
    
    if difference == 0:
        # Balance is already correct
        print(f"Balance is already {target_balance}, no adjustment needed")
        return
    
    # Adjust balance to target
    if difference > 0:
        # Need to deposit
        print(f"Current balance: {current_balance}, need to deposit {difference} to reach {target_balance}")
        
        # Click Deposit tab (using config)
        click_element(driver, config_manager, "deposit_tab")
        time.sleep(0.5)
        
        # Input deposit amount (using config)
        input_text(driver, config_manager, "amount_input", str(difference))
        time.sleep(0.3)
        
        # Click Deposit button (using config)
        click_element(driver, config_manager, "submit_button")
        time.sleep(1)
        
    elif difference < 0:
        # Need to withdraw (if balance is too high)
        print(f"Current balance: {current_balance}, need to withdraw {abs(difference)} to reach {target_balance}")
        
        # Click Withdrawl tab (using config)
        click_element(driver, config_manager, "withdraw_tab")
        time.sleep(0.5)
        
        # Input withdraw amount (using config)
        input_text(driver, config_manager, "amount_input", str(abs(difference)))
        time.sleep(0.3)
        
        # Click Withdraw button (using config)
        click_element(driver, config_manager, "submit_button")
        time.sleep(1)
    
    # Reload page to clear transaction message and verify balance (using config)
    account_url = config_manager.get_url("account_page_url")
    driver.get(account_url)
    time.sleep(1)
    
    # Verify balance is now 5096
    try:
        balance_element = find_element_by_config(driver, config_manager, "balance_strong")
        final_balance = int(balance_element.text.strip())
        if final_balance == target_balance:
            print(f"Balance successfully set to {target_balance}")
        else:
            print(f"Warning: Balance is {final_balance}, expected {target_balance}")
    except:
        print("Warning: Could not verify final balance")

# ==== Main test loop ====
for idx, row in data.iterrows():
    amount = row['amount']
    expected = row['expected']
    verify_message = row.get('verify_message', '')

    # Step 0: Ensure balance is 5096 and reload to clear previous state
    print(f"\n--- Test Case {idx+1} ---")
    ensure_balance_is_5096()
    
    # Additional reload to ensure all previous messages are cleared (using config)
    account_url = config_manager.get_url("account_page_url")
    driver.get(account_url)
    time.sleep(1)
    
    # Click on Deposit tab first, then switch to Withdrawl to clear any stale messages
    try:
        click_element(driver, config_manager, "deposit_tab", timeout=5)
        time.sleep(0.5)
    except:
        pass  # If Deposit tab not found, continue
    
    # Step 2: Click Withdrawl tab (using config)
    click_element(driver, config_manager, "withdraw_tab")
    time.sleep(0.5)

    # Step 3: Click input field to focus (using config)
    amount_input = find_element_by_config(driver, config_manager, "amount_input")
    amount_input.click()
    time.sleep(0.3)

    # Step 4: Clear and input amount (handle empty and invalid values) (using config)
    amount_input.clear()
    if pd.notna(amount) and str(amount).strip() != '':
        amount_input.send_keys(str(amount))
    time.sleep(0.3)

    # Step 5: Click Submit button (using config)
    click_element(driver, config_manager, "submit_button")
    time.sleep(1)

    # Step 6: Verify result message
    time.sleep(0.5)
    
    actual = "unknown"
    message_text = ""
    
    # Check if this is an invalid input
    is_invalid_input = False
    if pd.isna(amount) or str(amount).strip() == '':
        is_invalid_input = True
    else:
        try:
            float(str(amount))
        except (ValueError, TypeError):
            is_invalid_input = True
    
    # Check if message element exists and has text (using config)
    try:
        message_element = find_element_by_config(driver, config_manager, "message_span", timeout=5)
        message_text = message_element.text.strip()
        
        # For invalid inputs, if message contains "Transaction", it's likely from previous test case
        if is_invalid_input and "Transaction" in message_text:
            # This is a stale message from previous test case, ignore it
            message_text = ""
    except:
        # No message found
        message_text = ""
    
    # Determine actual result based on message and input type
    if pd.notna(verify_message) and str(verify_message).strip() != '':
        # Verify exact message match
        if verify_message in message_text:
            actual = "success" if "Transaction successful" in message_text else "failure"
        else:
            actual = "failure"
    else:
        # Auto-detect based on message content
        if message_text and "Transaction successful" in message_text:
            actual = "success"
        elif message_text and ("Transaction Failed" in message_text or "error" in message_text.lower()):
            actual = "failure"
        elif is_invalid_input:
            # For invalid inputs (abc, ++, empty), no message means invalid input
            actual = "invalid"
        else:
            # Valid number input but no message or unexpected message
            actual = "failure"

    # Compare actual vs expected
    status = "PASS" if actual == expected else "FAIL"
    print(f"Test {idx+1}: Amount='{amount}', Expected={expected}, Actual={actual}, Message='{message_text}', Status={status}")
    
    # Save result to list
    test_results.append({
        'Test_ID': idx + 1,
        'Amount': amount,
        'Expected': expected,
        'Actual': actual,
        'Message': message_text,
        'Status': status,
        'Verify_Message': verify_message if pd.notna(verify_message) else ''
    })
    
    # Reload page to reset status for next test case (using config)
    account_url = config_manager.get_url("account_page_url")
    driver.get(account_url)
    time.sleep(1)

# ==== Save results to file ====
results_df = pd.DataFrame(test_results)
results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\nTest results saved to: {output_file}")

# Print summary
total_tests = len(test_results)
passed_tests = len([r for r in test_results if r['Status'] == 'PASS'])
failed_tests = total_tests - passed_tests
print(f"\n=== Test Summary ===")
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
print(f"Pass Rate: {(passed_tests/total_tests*100):.2f}%")

driver.quit()

