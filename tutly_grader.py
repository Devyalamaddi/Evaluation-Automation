from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import time
import subprocess
import sys

class TutlyGrader:
    def __init__(self):
        """Initialize the TutlyGrader with WebDriver setup"""
        self.driver = None
        self.wait = None
        self.setup_driver()
        
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options"""
        try:
            # First, check if Chrome is installed
            try:
                subprocess.run(['google-chrome', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                print("Error: Google Chrome is not installed. Please install Chrome first.")
                sys.exit(1)

            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--start-maximized')
            # chrome_options.add_argument('--headless')  # Uncomment to run headless
            
            # Use system-installed ChromeDriver
            service = Service('/usr/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)  # Increased wait time for stability
            
        except Exception as e:
            print(f"Failed to setup Chrome driver: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Make sure Google Chrome is installed")
            print("2. Make sure ChromeDriver is installed: sudo dnf install -y chromedriver")
            print("3. Check if your Chrome version matches the ChromeDriver version")
            sys.exit(1)
        
    def safe_click(self, xpath, retries=3, delay=3):
        """Safely click an element with retries"""
        for attempt in range(retries):
            try:
                # Wait for element to be present
                element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                # Wait for element to be clickable
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                # Scroll element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                if delay > 0:
                    time.sleep(delay)  # Wait for scroll
                # Click the element
                element.click()
                return True
            except (StaleElementReferenceException, ElementClickInterceptedException) as e:
                if attempt == retries - 1:  # Last attempt
                    print(f"Failed to click element after {retries} attempts: {str(e)}")
                    raise
                time.sleep(2)  # Wait before retry
                continue
            
    def safe_send_keys(self, xpath, keys):
        """Safely send keys to an element with wait and sleep"""
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        element.clear()  # Clear any existing text
        element.send_keys(keys)
        
    def safe_get_text(self, xpath, retries=3):
        """Safely get text from an element with retries"""
        for attempt in range(retries):
            try:
                element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                return element.text.strip()
            except StaleElementReferenceException:
                if attempt == retries - 1:  # Last attempt
                    raise
                time.sleep(2)  # Wait before retry
                continue
        
    def get_element_color(self, xpath):
        """Get the text color of an element"""
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        color_class = element.get_attribute("class")
        # Check if the element has the green-500 color class
        return "text-green-500" in color_class
        
    def extract_number(self, text):
        """Extract the first number from a text string"""
        try:
            return int(text.split()[0])  # Split by whitespace and take first part
        except (ValueError, IndexError):
            return 0

    def get_assignment_details(self, assignment_index):
        """Get details for a specific assignment by index"""
        base_xpath = f"/html/body/div[2]/main/div/div/div/astro-island/div/div[{assignment_index}]/div/div/div[2]"
        try:
            # Get counts - now properly extracting numbers from text
            evaluated_text = self.safe_get_text(f"{base_xpath}/div[1]/div")
            under_review_text = self.safe_get_text(f"{base_xpath}/div[2]/div")
            submissions_text = self.safe_get_text(f"{base_xpath}/div[3]/div")
            
            evaluated = self.extract_number(evaluated_text)
            under_review = self.extract_number(under_review_text)
            submissions = self.extract_number(submissions_text)
            
            details = {
                'index': assignment_index,
                'evaluated': evaluated,
                'under_review': under_review,
                'submissions': submissions,
                'view_details_xpath': f"{base_xpath}/button"
            }
            
            print(f"Assignment {assignment_index}: {under_review} under review, {evaluated} evaluated, {submissions} submissions")
            return details
            
        except Exception as e:
            print(f"Failed to get assignment details for index {assignment_index}: {str(e)}")
            return None
            
    def grade_submission(self):
        """Handle the grading process for a single submission"""
        try:
            time.sleep(2)  # Wait for submission to load
            
            # Click edit button
            edit_button_xpath = "/html/body/div[2]/main/div/astro-island/div/div[3]/div/div[1]/table/tbody/tr/td[9]/div/button[1]"
            self.safe_click(edit_button_xpath, delay=1)
            
            # Set score to 10
            score_input_xpath = "/html/body/div[2]/main/div/astro-island/div/div[3]/div/div[1]/table/tbody/tr/td[6]/input"
            score_input = self.wait.until(EC.presence_of_element_located((By.XPATH, score_input_xpath)))
            score_input.clear()
            score_input.send_keys("10")
            time.sleep(1)  # Wait after entering score
            
            # Click save button
            save_button_xpath = "/html/body/div[2]/main/div/astro-island/div/div[3]/div/div[1]/table/tbody/tr/td[9]/div/button[1]"
            self.safe_click(save_button_xpath, delay=2)
            
            # Wait for automatic page reload after save
            time.sleep(2)
            
            # Perform two additional reloads with delay
            self.driver.refresh()
            time.sleep(2)  # 2-second delay between reloads
            #self.driver.refresh()
            #time.sleep(2)  # 2-second delay after second reload
            
            print("Successfully graded submission")
            return True
            
        except Exception as e:
            print(f"Error grading submission: {str(e)}")
            return False

    def process_submissions(self):
        """Process the submissions list and find ones that need review"""
        try:
            # Wait for the submissions list to be present
            submissions_list_xpath = "/html/body/div[2]/main/div/astro-island/div/div[1]/div/div[3]"
            self.wait.until(EC.presence_of_element_located((By.XPATH, submissions_list_xpath)))
            time.sleep(3)  # Wait for list to fully load
            
            # Get all submission elements
            i = 1
            while True:
                try:
                    submission_xpath = f"{submissions_list_xpath}/a[{i}]/div"
                    
                    try:
                        # Check if the submission exists
                        self.wait.until(EC.presence_of_element_located((By.XPATH, submission_xpath)))
                    except TimeoutException:
                        print("Reached end of submissions list")
                        return True  # Successfully processed all submissions
                    
                    # Check if the submission needs review (not green)
                    if not self.get_element_color(submission_xpath):
                        print(f"Found submission {i} needing review")
                        self.safe_click(submission_xpath, delay=5)
                        
                        # Grade the submission
                        if not self.grade_submission():
                            return False
                        
                        # Reload the page to refresh the list
                        self.driver.refresh()
                        time.sleep(3)  # Wait for page to reload
                        
                        # Wait for the list to be present again
                        self.wait.until(EC.presence_of_element_located((By.XPATH, submissions_list_xpath)))
                        time.sleep(2)  # Additional wait for list to load
                        
                    i += 1
                    
                except StaleElementReferenceException:
                    # If element becomes stale, refresh and try again
                    self.driver.refresh()
                    time.sleep(5)
                    continue
                    
        except Exception as e:
            print(f"Error processing submissions: {str(e)}")
            return False

    def evaluate_assignment(self, assignment):
        """Evaluate a single assignment"""
        try:
            print(f"Processing assignment {assignment['index']} with {assignment['under_review']} reviews pending")
            # Click view details button
            self.safe_click(assignment['view_details_xpath'], delay=5)
            time.sleep(3)  # Wait for page load
            
            # Scroll to bottom of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # Wait for scroll
            
            # Click the evaluate button
            evaluate_button_xpath = "/html/body/div[2]/main/div/astro-island/div/div[4]/div[2]/div[1]/div[2]/button"
            self.safe_click(evaluate_button_xpath, delay=5)
            time.sleep(1)  # Wait for evaluation page to load
            
            # Process all submissions
            if self.process_submissions():
                print(f"Successfully processed all submissions for assignment {assignment['index']}")
                # Navigate back to assignments list
                self.driver.get("https://learn.tutly.in/tutor/assignments/getByAssignment")
                time.sleep(2)  # Wait for page load
                # Reload twice
                self.driver.refresh()
                time.sleep(2)
                self.driver.refresh()
                time.sleep(2)
            else:
                print(f"Failed to process all submissions for assignment {assignment['index']}")
            
        except Exception as e:
            print(f"Evaluation failed for assignment {assignment['index']}: {str(e)}")
            raise
            
    def navigate_to_assignments(self):
        """Navigate to the assignments page"""
        try:
            print("Navigating to assignments...")
            # Click Assessment tab
            assessment_tab_xpath = "/html/body/div[2]/div/astro-island/div/div/div[2]/div/div[2]/div/ul/li[4]/button"
            self.safe_click(assessment_tab_xpath, delay=0)
            
            # Wait and click Assignments tab
            assignments_tab_xpath = "/html/body/div[2]/div/astro-island/div/div/div[2]/div/div[2]/div/ul/li[4]/div/ul/li[1]/a"
            self.safe_click(assignments_tab_xpath, delay=0)
            
            # Wait and click "Get by assignment?"
            get_by_assignment_xpath = "/html/body/div[2]/main/div/astro-island/div/div[1]/a"
            self.safe_click(get_by_assignment_xpath, delay=0)
            
            print("Navigation successful")
            
        except Exception as e:
            print(f"Navigation failed: {str(e)}")
            raise
            
    def login(self, email, password):
        """Login to Tutly platform"""
        try:
            print("Logging in...")
            self.driver.get("https://learn.tutly.in/sign-in")
            time.sleep(2)  # Wait for page load
            
            # Enter email
            email_xpath = "/html/body/astro-island[2]/div/div/div[2]/form/div[1]/input"
            self.safe_send_keys(email_xpath, email)
            
            # Enter password
            password_xpath = "/html/body/astro-island[2]/div/div/div[2]/form/div[2]/div/input"
            self.safe_send_keys(password_xpath, password)
            
            # Click login button
            login_button_xpath = "/html/body/astro-island[2]/div/div/div[2]/form/button"
            self.safe_click(login_button_xpath)
            
            # Wait for dashboard to load
            time.sleep(2)  # Extended wait after login
            print("Login successful")
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise
            
    def process_all_assignments(self):
        """Main function to process all assignments"""
        try:
            self.navigate_to_assignments()
            time.sleep(2)  # Wait for page load
            
            assignments = self.get_assignments_to_review()
            print(f"Found {len(assignments)} assignments to review")
            
            for assignment in assignments:
                self.evaluate_assignment(assignment)
                time.sleep(1)  # Wait between assignments
                
            # After all assignments are done, navigate to assignments page and logout
            print("\nAll assignments processed. Logging out...")
            self.driver.get("https://learn.tutly.in/tutor/assignments/getByAssignment")
            time.sleep(2)  # Wait for page load
            
            try:
                # Click the profile menu button
                profile_menu = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#radix-\:r3R1i\:")))
                profile_menu.click()
                time.sleep(1)  # Wait for dropdown
                
                # Click the logout option
                logout_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#radix-\:r3R1iH1\: > a > div")))
                logout_button.click()
                print("Successfully logged out")
                
            except Exception as e:
                print(f"Failed to logout: {str(e)}")
                
        except Exception as e:
            print(f"Processing failed: {str(e)}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            
    def get_assignments_to_review(self):
        """Get list of assignments with review count > 0"""
        assignments = []
        try:
            print("Scanning for assignments to review...")
            # Start from index 2 and go up to 29 (for 28 assignments)
            for i in range(2, 30):
                assignment = self.get_assignment_details(i)
                if assignment and assignment['under_review'] > 0:
                    assignments.append(assignment)
                    print(f"Found assignment with {assignment['under_review']} reviews pending")
                #time.sleep(1)  # Small delay between checking assignments
                
        except Exception as e:
            print(f"Failed to get assignments: {str(e)}")
        return assignments
            
def main():
    # Load environment variables
    load_dotenv()
    
    email = os.getenv("TUTLY_EMAIL")
    password = os.getenv("TUTLY_PASSWORD")
    
    if not email or not password:
        print("Please set TUTLY_EMAIL and TUTLY_PASSWORD in .env file")
        return
        
    grader = TutlyGrader()
    try:
        grader.login(email, password)
        grader.process_all_assignments()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        grader.cleanup()
    
if __name__ == "__main__":
    main() 