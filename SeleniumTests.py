import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


class SeleniumTests(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('http://localhost:5000')
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    # Test data arrays
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
        }
    ]

    dynamic_content_tests = [
        {
            'name': 'Content Loads Successfully',
            'check_type': 'content',
            'expected_element': 'delayedText',
            'expected_text': 'This content was loaded dynamically',
            'should_be_visible': True
        },
        {
            'name': 'Loading Indicator Appears',
            'check_type': 'loading',
            'expected_element': 'loading',
            'expected_text': 'Loading content',
            'should_be_visible': True
        },
        {
            'name': 'Loading Indicator Disappears',
            'check_type': 'loading_disappears',
            'expected_element': 'loading',
            'expected_text': '',
            'should_be_visible': False
        },
        {
            'name': 'Content Updates on Multiple Loads',
            'check_type': 'multiple_loads',
            'expected_element': 'delayedText',
            'expected_text': 'This content was loaded dynamically',
            'should_be_visible': True
        },
        {
            'name': 'Button State During Loading',
            'check_type': 'button_state',
            'expected_element': 'loadButton',
            'button_class': 'btn-secondary',
            'should_be_enabled': True
        }
    ]

    def test_registration_cases(self):
        """Run all registration test cases from the array"""
        for test_case in self.registration_tests:
            with self.subTest(test_case['name']):
                # If this is a duplicate test that requires previous registration
                if test_case.get('requires_previous_registration'):
                    self.perform_registration('duplicate_user', 'student', False)
                    time.sleep(1)  # Wait for first registration to complete

                self.perform_registration(
                    test_case['username'],
                    test_case['role'],
                    test_case['newsletter']
                )

                if test_case['should_succeed']:
                    success_message = self.wait.until(
                        EC.visibility_of_element_located((By.ID, 'formSuccess'))
                    )
                    self.assertIn(test_case['expected_message'], success_message.text)
                else:
                    error_message = self.wait.until(
                        EC.visibility_of_element_located((By.ID, 'formError'))
                    )
                    self.assertIn(test_case['expected_message'], error_message.text)

    def test_dynamic_content_cases(self):
        """Run all dynamic content test cases from the array"""
        for test_case in self.dynamic_content_tests:
            with self.subTest(test_case['name']):
                load_button = self.driver.find_element(By.ID, 'loadButton')
                load_button.click()

                if test_case['check_type'] == 'content':
                    element = self.wait.until(
                        EC.visibility_of_element_located((By.ID, test_case['expected_element']))
                    )
                    self.assertTrue(element.is_displayed())
                    self.assertIn(test_case['expected_text'], element.text)

                elif test_case['check_type'] == 'loading':
                    element = self.wait.until(
                        EC.visibility_of_element_located((By.ID, test_case['expected_element']))
                    )
                    self.assertTrue(element.is_displayed())
                    self.assertIn(test_case['expected_text'], element.text)

                elif test_case['check_type'] == 'loading_disappears':
                    self.wait.until(
                        EC.invisibility_of_element_located((By.ID, test_case['expected_element']))
                    )

                elif test_case['check_type'] == 'multiple_loads':
                    # First load
                    self.wait.until(
                        EC.visibility_of_element_located((By.ID, test_case['expected_element']))
                    )
                    # Second load
                    load_button.click()
                    element = self.wait.until(
                        EC.visibility_of_element_located((By.ID, test_case['expected_element']))
                    )
                    self.assertTrue(element.is_displayed())
                    self.assertIn(test_case['expected_text'], element.text)

                elif test_case['check_type'] == 'button_state':
                    button = self.driver.find_element(By.ID, test_case['expected_element'])
                    self.assertTrue(test_case['button_class'] in button.get_attribute('class'))
                    self.assertEqual(button.is_enabled(), test_case['should_be_enabled'])

    def perform_registration(self, username, role, newsletter):
        """Helper method to perform registration"""
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


if __name__ == '__main__':
    unittest.main(verbosity=2)