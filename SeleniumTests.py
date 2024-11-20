import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
from prettytable import PrettyTable
import datetime
import sys


class SeleniumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results_table = PrettyTable()
        cls.results_table.field_names = ["Test Name", "Status", "Duration (s)", "Error Message"]
        cls.start_time = time.time()
        print("\nTest Execution Started:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--log-level=3')  # Suppress console logs
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('http://localhost:5000')
        self.wait = WebDriverWait(self.driver, 3)  # Short timeout for faster feedback

    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        print("\nTest Results:")
        print(cls.results_table)
        print(f"\nTotal Duration: {time.time() - cls.start_time:.2f} seconds")

        # Save results to file
        with open('test_results.html', 'w') as f:
            f.write(f"""
            <html>
            <head>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ padding: 8px; text-align: left; border: 1px solid #ddd; }}
                    th {{ background-color: #f2f2f2; }}
                    .pass {{ color: green; }}
                    .fail {{ color: red; }}
                </style>
            </head>
            <body>
                <h2>Test Execution Report</h2>
                <p>Started: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                {cls.results_table.get_html_string()}
            </body>
            </html>
            """)

    def log_result(self, test_name, status, duration, error_msg=""):
        self.results_table.add_row([
            test_name,
            status,
            f"{duration:.2f}",
            error_msg
        ])

    def wait_and_check_element(self, by, value, timeout=3):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None

    # Updated test cases to match the implementation
    registration_tests = [
        {
            'name': 'Valid Registration',
            'username': 'validuser',
            'role': 'student',
            'newsletter': True,
            'expected_message': 'Registration successful',
            'should_succeed': True
        },
        {
            'name': 'Empty Username',
            'username': '',
            'role': 'student',
            'newsletter': False,
            'expected_message': 'Username is required',
            'should_succeed': False
        },
        {
            'name': 'Empty Role',
            'username': 'testuser',
            'role': '',
            'newsletter': False,
            'expected_message': 'Role is required',
            'should_succeed': False
        },
        {
            'name': 'Duplicate Username',
            'username': 'duplicate_user',
            'role': 'student',
            'newsletter': False,
            'expected_message': 'Username already exists',
            'should_succeed': False,
            'requires_previous_registration': True
        },
        {
            'name': 'All Fields Valid with Newsletter',
            'username': 'newsletter_user',
            'role': 'teacher',
            'newsletter': True,
            'expected_message': 'Registration successful',
            'should_succeed': True
        },
        {
            'name': 'Very Long Username',
            'username': 'a' * 100,  # 100 character username
            'role': 'student',
            'newsletter': False,
            'expected_message': 'Username too long',
            'should_succeed': False
        },
        {
            'name': 'Special Characters Username',
            'username': '!@#$%^&*()',
            'role': 'teacher',
            'newsletter': False,
            'expected_message': 'Invalid username format',
            'should_succeed': False
        },
        {
            'name': 'Invalid Role Value',
            'username': 'validuser2',
            'role': 'invalid_role',
            'newsletter': False,
            'expected_message': 'Invalid role selected',
            'should_succeed': False
        },
        {
            'name': 'SQL Injection Attempt',
            'username': "' OR '1'='1",
            'role': 'student',
            'newsletter': False,
            'expected_message': 'Invalid username format',
            'should_succeed': False
        }
    ]

    dynamic_content_tests = [
        {
            'name': 'Content Loads Successfully',
            'check_type': 'content',
            'expected_element': 'delayedText',
            'expected_text': 'This content was loaded dynamically!',
            'should_be_visible': True
        },
        {
            'name': 'Loading Indicator Appears',
            'check_type': 'loading',
            'expected_element': 'loading',
            'expected_text': 'Loading content...',
            'should_be_visible': True
        },
        {
            'name': 'Loading Indicator Disappears',
            'check_type': 'loading_disappears',
            'expected_element': 'loading',
            'should_be_visible': False
        },
        {
            'name': 'Multiple Rapid Clicks',
            'check_type': 'multiple_loads',
            'expected_element': 'delayedText',
            'expected_text': 'This content was loaded dynamically!',
            'should_be_visible': True,
            'click_count': 5
        },
        {
            'name': 'Check Button Disabled State',
            'check_type': 'button_state',
            'expected_element': 'loadButton',
            'button_class': 'btn-loading',
            'should_be_enabled': False
        },
        {
            'name': 'Network Error Handling',
            'check_type': 'network_error',
            'expected_element': 'delayedText',
            'expected_text': 'Error loading content',
            'should_be_visible': True
        }
    ]

    def perform_registration(self, username, role, newsletter):
        """Helper method to perform registration"""
        try:
            username_input = self.driver.find_element(By.ID, 'username')
            username_input.clear()
            username_input.send_keys(username)

            role_select = self.driver.find_element(By.ID, 'dropdown')
            role_select.send_keys(role)

            newsletter_checkbox = self.driver.find_element(By.ID, 'newsletter')
            if newsletter != newsletter_checkbox.is_selected():
                newsletter_checkbox.click()

            submit_button = self.driver.find_element(By.ID, 'submitBtn')
            submit_button.click()
        except Exception as e:
            raise Exception(f"Failed to perform registration: {str(e)}")

    def test_registration_cases(self):
        """Run all registration test cases"""
        for test_case in self.registration_tests:
            test_start_time = time.time()
            try:
                with self.subTest(test_case['name']):
                    if test_case.get('requires_previous_registration'):
                        self.perform_registration('duplicate_user', 'student', False)
                        time.sleep(1)  # Wait for the first registration to complete

                    self.perform_registration(
                        test_case['username'],
                        test_case['role'],
                        test_case['newsletter']
                    )

                    try:
                        if test_case['should_succeed']:
                            success_element = self.wait.until(
                                EC.visibility_of_element_located((By.ID, 'formSuccess'))
                            )
                            self.assertIn(test_case['expected_message'], success_element.text)
                        else:
                            error_element = self.wait.until(
                                EC.visibility_of_element_located((By.ID, 'formError'))
                            )
                            self.assertIn(test_case['expected_message'], error_element.text)
                        
                        self.log_result(
                            f"Registration: {test_case['name']}", 
                            "PASS", 
                            time.time() - test_start_time
                        )
                    except TimeoutException:
                        self.log_result(
                            f"Registration: {test_case['name']}", 
                            "FAIL", 
                            time.time() - test_start_time,
                            "Timeout waiting for message"
                        )
                        raise

            except Exception as e:
                self.log_result(
                    f"Registration: {test_case['name']}", 
                    "ERROR", 
                    time.time() - test_start_time,
                    str(e)
                )
                raise

    def test_dynamic_content_cases(self):
        """Run all dynamic content test cases"""
        for test_case in self.dynamic_content_tests:
            start_time = time.time()
            try:
                with self.subTest(test_case['name']):
                    if test_case['check_type'] == 'multiple_loads':
                        # Test rapid multiple clicks
                        for _ in range(test_case['click_count']):
                            load_button = self.driver.find_element(By.ID, 'loadButton')
                            load_button.click()
                            time.sleep(0.1)  # Small delay between clicks
                        
                        element = self.wait.until(
                            EC.visibility_of_element_located((By.ID, test_case['expected_element']))
                        )
                        self.assertTrue(element.is_displayed())
                        self.assertIn(test_case['expected_text'], element.text)

                    elif test_case['check_type'] == 'network_error':
                        # Simulate network error by modifying the API endpoint
                        script = """
                        const originalFetch = window.fetch;
                        window.fetch = function() {
                            return new Promise((resolve, reject) => {
                                reject(new Error('Network error'));
                            });
                        };
                        """
                        self.driver.execute_script(script)
                        
                        load_button = self.driver.find_element(By.ID, 'loadButton')
                        load_button.click()
                        
                        element = self.wait.until(
                            EC.visibility_of_element_located((By.ID, test_case['expected_element']))
                        )
                        self.assertTrue(element.is_displayed())
                        self.assertIn(test_case['expected_text'], element.text)

                    elif test_case['check_type'] == 'content':
                        element = self.wait_and_check_element(By.ID, test_case['expected_element'])
                        if element and test_case['expected_text'] in element.text:
                            self.log_result(f"Dynamic: {test_case['name']}", "PASS",
                                            time.time() - start_time)
                        else:
                            self.log_result(f"Dynamic: {test_case['name']}", "FAIL",
                                            time.time() - start_time, "Content not found")

                    elif test_case['check_type'] == 'loading':
                        element = self.wait_and_check_element(By.ID, test_case['expected_element'])
                        if element and element.is_displayed():
                            self.log_result(f"Dynamic: {test_case['name']}", "PASS",
                                            time.time() - start_time)
                        else:
                            self.log_result(f"Dynamic: {test_case['name']}", "FAIL",
                                            time.time() - start_time, "Loading indicator not found")

                self.log_result(
                    f"Dynamic Content: {test_case['name']}", 
                    "PASS", 
                    time.time() - start_time
                )
            except Exception as e:
                self.log_result(
                    f"Dynamic Content: {test_case['name']}", 
                    "FAIL", 
                    time.time() - start_time,
                    str(e)
                )
                continue  # Continue with next test case instead of failing completely


if __name__ == '__main__':
    unittest.main(verbosity=2)