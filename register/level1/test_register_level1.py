"""
Level 1: Data-driven testing for Register functionality
Test cases extracted from Register.krecorder file
"""
import time
import os
import random
import string
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==== Load data ====
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "data_register.csv")
data = pd.read_csv(csv_path)

# ==== Setup output file ====
output_file = os.path.join(script_dir, "test_result_register.csv")
test_results = []

# ==== Setup driver ====
driver = webdriver.Chrome()
driver.maximize_window()

# Register page URL
register_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/register"
success_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/success"
# Logout URL to ensure clean state before each test
logout_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/logout"

print("Starting Register Test Suite...")

def generate_random_suffix(length=10):
    """Generate random alphanumeric suffix"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_random_suffix_to_email(email):
    """Add random suffix to email to ensure uniqueness"""
    if not email or pd.isna(email) or email.strip() == '':
        return email
    
    email = str(email).strip()
    if '@' in email:
        local_part, domain = email.rsplit('@', 1)
        random_suffix = generate_random_suffix(10)
        return f"{local_part}{random_suffix}@{domain}"
    random_suffix = generate_random_suffix(10)
    return f"{email}{random_suffix}"


def safe_input(field_id, value, wait_time=10):
    """Fill input field only when value exists"""
    if not value:
        return
    elem = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    elem.clear()
    elem.send_keys(str(value))
    time.sleep(0.3)


def click_element(xpath, wait_time=10):
    """Click element if available"""
    elem = WebDriverWait(driver, wait_time).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    elem.click()
    time.sleep(0.3)
    return elem


def verify_registration_result(expected, verify_message):
    """Verify form submission outcome and return actual status + message"""
    time.sleep(1)
    actual = "unknown"
    message_text = ""

    try:
        current_url = driver.current_url
        if "route=account/success" in current_url:
            try:
                success_h1 = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='content']/h1"))
                )
                message_text = success_h1.text.strip()
                actual = "success"
            except Exception:
                actual = "success"
                message_text = "Redirected to success page"
        else:
            try:
                warning_alert = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.alert.alert-danger"))
                )
                message_text = warning_alert.text.strip()
                actual = "failure"
            except Exception:
                try:
                    error_elements = driver.find_elements(By.CSS_SELECTOR, "div.text-danger")
                    if error_elements:
                        error_messages = [elem.text.strip() for elem in error_elements if elem.text.strip()]
                        if error_messages:
                            message_text = "; ".join(error_messages)
                            actual = "failure"
                        else:
                            actual = "failure"
                            message_text = "Form validation failed (no specific message)"
                    else:
                        if "route=account/register" in current_url:
                            actual = "failure"
                            message_text = "Still on register page - registration failed"
                        else:
                            actual = "unknown"
                            message_text = "Unexpected page state"
                except Exception as inner_e:
                    actual = "failure"
                    message_text = f"Error checking validation messages: {str(inner_e)}"
    except Exception as e:
        actual = "error"
        message_text = f"Error verifying result: {str(e)}"

    if verify_message and pd.notna(verify_message) and str(verify_message).strip():
        if verify_message not in message_text:
            if actual == "success" and "Your Account Has Been Created!" not in message_text:
                pass

    return actual, message_text

# ==== Main test loop ====
for idx, row in data.iterrows():
    test_id = row['test_id']
    firstname = row['firstname'] if pd.notna(row['firstname']) else ''
    lastname = row['lastname'] if pd.notna(row['lastname']) else ''
    email = row['email'] if pd.notna(row['email']) else ''
    telephone = row['telephone'] if pd.notna(row['telephone']) else ''
    password = row['password'] if pd.notna(row['password']) else ''
    confirm = row['confirm'] if pd.notna(row['confirm']) else ''
    newsletter = row['newsletter'] if pd.notna(row['newsletter']) else 'No'
    privacy = row['privacy'] if pd.notna(row['privacy']) else False
    expected = row['expected'] if pd.notna(row['expected']) else 'failure'
    verify_message = row['verify_message'] if pd.notna(row['verify_message']) else ''

    # Add random suffix to email to ensure uniqueness
    # BUT: Don't modify email for test cases that specifically test "email already registered"
    original_email = email
    should_modify_email = True
    
    # Check if this test case is designed to test "email already registered" scenario
    if expected == 'failure' and verify_message and 'already registered' in str(verify_message).lower():
        should_modify_email = False
        print(f"\n--- Test Case {idx+1}: {test_id} ---")
        print(f"Note: This test case checks for 'email already registered' - keeping original email")
    else:
        # For success cases or other failure cases, add random suffix to ensure uniqueness
        email = add_random_suffix_to_email(email)
        print(f"\n--- Test Case {idx+1}: {test_id} ---")
        if original_email != email:
            print(f"Email modified: {original_email} -> {email}")

    # Step 0: Always try to logout to ensure clean state (avoid being logged-in from previous test)
    try:
        driver.get(logout_url)
        time.sleep(1)
    except Exception:
        pass

    # Step 1: Open register page
    driver.get(register_url)
    time.sleep(2)

    # Step 2: Fill form fields
    try:
        safe_input("input-firstname", firstname)
        safe_input("input-lastname", lastname)
        safe_input("input-email", email)
        safe_input("input-telephone", telephone)
        safe_input("input-password", password)
        safe_input("input-confirm", confirm)

        # Newsletter subscription (Yes/No)
        if newsletter == 'Yes':
            try:
                click_element("//div[@id='content']/form/fieldset[3]/div/div/div/label", wait_time=5)
            except:
                pass

        # Privacy Policy checkbox
        if privacy:
            try:
                click_element("//div[@id='content']/form/div/div/div/label", wait_time=10)
            except:
                pass

        # Step 3: Click Continue button
        click_element("//input[@value='Continue']", wait_time=10)
        time.sleep(2)

    except Exception as e:
        print(f"Error filling form: {e}")
        actual = "error"
        message_text = f"Error: {str(e)}"
        status = "FAIL"
        test_results.append({
            'Test_ID': test_id,
            'Firstname': firstname,
            'Lastname': lastname,
            'Email': email,
            'Expected': expected,
            'Actual': actual,
            'Message': message_text,
            'Status': status
        })
        continue

    # Step 4: Verify result
    actual, message_text = verify_registration_result(expected, verify_message)

    # Compare actual vs expected
    status = "PASS" if actual == expected else "FAIL"
    print(f"Test {test_id}: Expected={expected}, Actual={actual}, Message='{message_text}', Status={status}")

    # Save result to list (use modified email)
    test_results.append({
        'Test_ID': test_id,
        'Firstname': firstname,
        'Lastname': lastname,
        'Email': email,  # This is the modified email with random suffix
        'Original_Email': original_email,  # Original email from CSV
        'Telephone': telephone,
        'Expected': expected,
        'Actual': actual,
        'Message': message_text,
        'Status': status,
        'Verify_Message': verify_message
    })
    
    # Reload page to clear state for next test case
    driver.get(register_url)
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
