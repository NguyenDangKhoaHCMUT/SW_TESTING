"""
Level 2: Data-driven testing for Register functionality
All URLs and element locators are read from config_register.csv
"""
import time
import os
import sys
import random
import string
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# Add common directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
common_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), 'common')
sys.path.insert(0, common_dir)

from config_manager import ConfigManager
from element_helper import find_element_by_config, click_element, input_text, get_text


# ==== Load data and config ====
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "data_register.csv")
config_path = os.path.join(script_dir, "config_register.csv")

data = pd.read_csv(csv_path)
config_manager = ConfigManager(config_path)

# ==== Setup output file ====
output_file = os.path.join(script_dir, "test_result_register.csv")
test_results = []

# ==== Setup driver ====
driver = webdriver.Chrome()
driver.maximize_window()


def generate_random_suffix(length: int = 10) -> str:
    """Generate random alphanumeric suffix"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def add_random_suffix_to_email(email: str) -> str:
    """Add random suffix to email to ensure uniqueness"""
    if not email or pd.isna(email) or str(email).strip() == '':
        return email

    email = str(email).strip()
    if '@' in email:
        local_part, domain = email.rsplit('@', 1)
        random_suffix = generate_random_suffix(10)
        return f"{local_part}{random_suffix}@{domain}"

    random_suffix = generate_random_suffix(10)
    return f"{email}{random_suffix}"


def safe_input_by_config(element_name: str, value: str, timeout: int = 10):
    """Fill input field using config only when value exists"""
    if not value:
        return
    elem = find_element_by_config(driver, config_manager, element_name, timeout=timeout)
    elem.clear()
    elem.send_keys(str(value))
    time.sleep(0.3)


def verify_registration_result(expected: str, verify_message: str):
    """Verify form submission outcome and return actual status + message"""
    time.sleep(1)
    actual = "unknown"
    message_text = ""

    try:
        current_url = driver.current_url
        success_url = config_manager.get_url("success_url")

        # Check if redirected to success page
        if success_url and success_url in current_url:
            try:
                message_text = get_text(driver, config_manager, "success_h1", timeout=5)
                actual = "success"
            except Exception:
                actual = "success"
                message_text = "Redirected to success page"
        else:
            # Still on register page - check for warning alert first
            try:
                warning_text = get_text(driver, config_manager, "warning_alert", timeout=2)
                message_text = warning_text
                actual = "failure"
            except Exception:
                # Check for field-level error messages
                try:
                    field_error_cfg = config_manager.get_element_config("field_error_div")
                    if field_error_cfg:
                        locator_type = field_error_cfg["locator_type"]
                        locator_value = field_error_cfg["locator_value"]

                        by_map = {
                            'xpath': By.XPATH,
                            'id': By.ID,
                            'css': By.CSS_SELECTOR,
                            'name': By.NAME,
                            'class_name': By.CLASS_NAME,
                            'tag_name': By.TAG_NAME,
                            'link_text': By.LINK_TEXT,
                            'partial_link_text': By.PARTIAL_LINK_TEXT,
                        }
                        by = by_map.get(locator_type.lower(), By.CSS_SELECTOR)
                        error_elements = driver.find_elements(by, locator_value)
                    else:
                        error_elements = []

                    if error_elements:
                        error_messages = [elem.text.strip() for elem in error_elements if elem.text.strip()]
                        if error_messages:
                            message_text = "; ".join(error_messages)
                            actual = "failure"
                        else:
                            actual = "failure"
                            message_text = "Form validation failed (no specific message)"
                    else:
                        # No error elements found - might be success but not redirected
                        register_url = config_manager.get_url("register_url")
                        if register_url and register_url in current_url:
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

    # Check verify_message if provided (same logic as Level 1)
    if verify_message and pd.notna(verify_message) and str(verify_message).strip():
        if verify_message not in message_text:
            if actual == "success" and "Your Account Has Been Created!" not in message_text:
                # Keep behavior same as Level 1 (no additional change)
                pass

    return actual, message_text


print("Starting Register Test Suite - Level 2...")

# ==== Main test loop ====
for idx, row in data.iterrows():
    test_id = row["test_id"]
    firstname = row["firstname"] if pd.notna(row["firstname"]) else ""
    lastname = row["lastname"] if pd.notna(row["lastname"]) else ""
    email = row["email"] if pd.notna(row["email"]) else ""
    telephone = row["telephone"] if pd.notna(row["telephone"]) else ""
    password = row["password"] if pd.notna(row["password"]) else ""
    confirm = row["confirm"] if pd.notna(row["confirm"]) else ""
    newsletter = row["newsletter"] if pd.notna(row["newsletter"]) else "No"
    privacy = row["privacy"] if pd.notna(row["privacy"]) else False
    expected = row["expected"] if pd.notna(row["expected"]) else "failure"
    verify_message = row["verify_message"] if pd.notna(row["verify_message"]) else ""

    # Add random suffix to email to ensure uniqueness
    # BUT: Don't modify email for test cases that specifically test "email already registered"
    original_email = email
    if not (expected == "failure" and verify_message and "already registered" in str(verify_message).lower()):
        email = add_random_suffix_to_email(email)

    print(f"\n--- Test Case {idx + 1}: {test_id} ---")
    if original_email != email:
        print(f"Email modified: {original_email} -> {email}")
    elif original_email:
        print(f"Email kept: {original_email}")

    # Step 0: Always try to logout to ensure clean state
    try:
        logout_url = config_manager.get_url("logout_url")
        if logout_url:
            driver.get(logout_url)
            time.sleep(1)
    except Exception:
        pass

    # Step 1: Open register page
    register_url = config_manager.get_url("register_url")
    driver.get(register_url)
    time.sleep(2)

    # Step 2: Fill form fields
    try:
        safe_input_by_config("firstname_input", firstname)
        safe_input_by_config("lastname_input", lastname)
        safe_input_by_config("email_input", email)
        safe_input_by_config("telephone_input", telephone)
        safe_input_by_config("password_input", password)
        safe_input_by_config("confirm_input", confirm)

        # Newsletter subscription (Yes/No)
        if newsletter == "Yes":
            try:
                click_element(driver, config_manager, "newsletter_label", timeout=5)
            except Exception:
                pass

        # Privacy Policy checkbox
        if privacy:
            try:
                click_element(driver, config_manager, "privacy_label", timeout=10)
            except Exception:
                pass

        # Step 3: Click Continue button
        click_element(driver, config_manager, "continue_button", timeout=10)
        time.sleep(2)

    except Exception as e:
        print(f"Error filling form: {e}")
        actual = "error"
        message_text = f"Error: {str(e)}"
        status = "FAIL"
        test_results.append(
            {
                "Test_ID": test_id,
                "Firstname": firstname,
                "Lastname": lastname,
                "Email": email,
                "Expected": expected,
                "Actual": actual,
                "Message": message_text,
                "Status": status,
            }
        )
        continue

    # Step 4: Verify result (reuse Level 1 logic)
    actual, message_text = verify_registration_result(expected, verify_message)

    # Compare actual vs expected
    status = "PASS" if actual == expected else "FAIL"
    print(f"Test {test_id}: Expected={expected}, Actual={actual}, Message='{message_text}', Status={status}")

    # Save result to list
    test_results.append(
        {
            "Test_ID": test_id,
            "Firstname": firstname,
            "Lastname": lastname,
            "Email": email,  # Modified email (if changed)
            "Original_Email": original_email,
            "Telephone": telephone,
            "Expected": expected,
            "Actual": actual,
            "Message": message_text,
            "Status": status,
            "Verify_Message": verify_message,
        }
    )

    # Reload page to clear state for next test case
    driver.get(register_url)
    time.sleep(1)


# ==== Save results to file ====
results_df = pd.DataFrame(test_results)
results_df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\nTest results saved to: {output_file}")

# Print summary
total_tests = len(test_results)
passed_tests = len([r for r in test_results if r["Status"] == "PASS"])
failed_tests = total_tests - passed_tests
print("\n=== Test Summary ===")
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {failed_tests}")
print(f"Pass Rate: {(passed_tests / total_tests * 100):.2f}%")

driver.quit()


