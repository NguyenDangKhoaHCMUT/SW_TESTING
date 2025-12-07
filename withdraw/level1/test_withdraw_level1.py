import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ==== Load data ====
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "data_withdraw.csv")
data = pd.read_csv(csv_path)

# ==== Setup output file ====
# Create output file with fixed name
output_file = os.path.join(script_dir, "test_result_withdraw.csv")

# Initialize results list
test_results = []

# ==== Setup driver ====
driver = webdriver.Chrome()
driver.maximize_window()

# ==== Setup: Login as customer before testing ====
# Step 1: Open homepage
driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/")
time.sleep(2)

# Step 2: Click Customer Login button
customer_login_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Customer Login')]"))
)
customer_login_btn.click()
time.sleep(1)

# Step 3: Select customer from dropdown (select first customer by default)
customer_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "userSelect"))
)
select = Select(customer_dropdown)
select.select_by_index(1)  # Select first customer (index 1, skip "---Your Name---")
time.sleep(1)

# Step 4: Click Login button
login_btn = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
)
login_btn.click()
time.sleep(2)

# Now we are logged in and can access account page
print("Setup completed: Customer logged in successfully")

# ==== Function to ensure balance is 5096 before each test ====
def ensure_balance_is_5096():
    """Ensure account balance is exactly 5096 before each test case"""
    # Reload page to clear previous state
    driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/#/account")
    time.sleep(1)
    
    # Get current balance from the page
    try:
        # Balance is usually displayed in a strong tag after "Account Number" or similar
        balance_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Please open an account with us.'])[1]/following::strong[2]"))
        )
        current_balance = int(balance_element.text.strip())
    except:
        # Try alternative xpath for balance
        try:
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
        
        # Click Deposit tab
        deposit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Deposit')]"))
        )
        deposit_button.click()
        time.sleep(0.5)
        
        # Input deposit amount
        deposit_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='number']"))
        )
        deposit_input.clear()
        deposit_input.send_keys(str(difference))
        time.sleep(0.3)
        
        # Click Deposit button
        deposit_submit = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        deposit_submit.click()
        time.sleep(1)
        
    elif difference < 0:
        # Need to withdraw (if balance is too high)
        print(f"Current balance: {current_balance}, need to withdraw {abs(difference)} to reach {target_balance}")
        
        # Click Withdrawl tab
        withdraw_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Deposit'])[1]/following::button[1]"))
        )
        withdraw_button.click()
        time.sleep(0.5)
        
        # Input withdraw amount
        withdraw_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='number']"))
        )
        withdraw_input.clear()
        withdraw_input.send_keys(str(abs(difference)))
        time.sleep(0.3)
        
        # Click Withdraw button
        withdraw_submit = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        withdraw_submit.click()
        time.sleep(1)
    
    # Reload page to clear transaction message and verify balance
    driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/#/account")
    time.sleep(1)
    
    # Verify balance is now 5096
    try:
        balance_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Please open an account with us.'])[1]/following::strong[2]"))
        )
        final_balance = int(balance_element.text.strip())
        if final_balance == target_balance:
            print(f"Balance successfully set to {target_balance}")
        else:
            print(f"Warning: Balance is {final_balance}, expected {target_balance}")
    except:
        print("Warning: Could not verify final balance")

for idx, row in data.iterrows():
    amount = row['amount']
    expected = row['expected']
    verify_message = row.get('verify_message', '')

    # Step 0: Ensure balance is 5096 and reload to clear previous state
    print(f"\n--- Test Case {idx+1} ---")
    ensure_balance_is_5096()
    
    # Additional reload to ensure all previous messages are cleared
    driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/#/account")
    time.sleep(1)
    
    # Click on Deposit tab first, then switch to Withdrawl to clear any stale messages
    try:
        deposit_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Deposit')]"))
        )
        deposit_tab.click()
        time.sleep(0.5)
    except:
        pass  # If Deposit tab not found, continue
    
    # Step 2: Click Withdrawl tab (using xpath from krecorder)
    withdraw_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Deposit'])[1]/following::button[1]"))
    )
    withdraw_button.click()
    time.sleep(0.5)

    # Step 3: Click input field to focus (as in krecorder)
    amount_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='number']"))
    )
    amount_input.click()
    time.sleep(0.3)

    # Step 4: Clear and input amount (handle empty and invalid values)
    amount_input.clear()
    if pd.notna(amount) and str(amount).strip() != '':
        amount_input.send_keys(str(amount))
    time.sleep(0.3)

    # Step 5: Click Submit button
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    submit_button.click()
    time.sleep(1)

    # Step 6: Verify result message
    # Wait a bit for message to appear (if any)
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
    
    # Check if message element exists and has text
    try:
        message_element = driver.find_element(By.XPATH, "(.//*[normalize-space(text()) and normalize-space(.)='Withdrawl'])[1]/following::span[1]")
        message_text = message_element.text.strip()
        
        # For invalid inputs, if message contains "Transaction", it's likely from previous test case
        # Invalid inputs (abc, ++, empty) typically don't trigger form submission, so no new message
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
    
    # Reload page to reset status for next test case (clear previous transaction messages)
    driver.get("https://www.globalsqa.com/angularJs-protractor/BankingProject/#/account")
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
