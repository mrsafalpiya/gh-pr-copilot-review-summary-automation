from selenium import webdriver
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
# -------------

# IMPORTANT: Download geckodriver from https://github.com/mozilla/geckodriver/releases
# and place it in the current directory or specify the full path below
# chmod +x geckodriver  # Make it executable

# Create a new Firefox profile:
# 1. Run 'firefox -P' in terminal to open the profile manager
# 2. Create a new profile and log in to GitHub
# 3. Find your profile directory by opening Firefox and going to about:profiles
# 4. Look for the "Root Directory" path of your profile

PATH_TO_FIREFOX_PROFILE = os.path.expanduser(
    os.getenv("FIREFOX_PROFILE_PATH", "~/.mozilla/firefox/")
)
PATH_TO_FIREFOX_BINARY = os.getenv("FIREFOX_BINARY_PATH", "/usr/bin/firefox")
PATH_TO_GECKODRIVER = os.getenv("GECKODRIVER_PATH", "./geckodriver")


# Execution
# ---------


def execute(pr_link, is_sync):
    # Configure options to use the specific Firefox profile
    options = Options()
    options.binary_location = PATH_TO_FIREFOX_BINARY
    options.profile = PATH_TO_FIREFOX_PROFILE
    options.add_argument("-headless")

    service = Service(PATH_TO_GECKODRIVER)
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(pr_link)

    # Copilot Review Button
    # ---------------------

    def click_copilot_review_button(is_sync):
        # Find and click the reviewers filter icon, search for copilot and select it for review

        # Find and click the reviewers filter icon

        reviewers_filter_css_selector = (
            "#reviewers-select-menu svg.octicon.octicon-gear"
        )

        try:
            # Wait up to 15 seconds for the reviewers filter button to be present and clickable
            wait = WebDriverWait(driver, 15)
            reviewers_filter_icon_elem = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, reviewers_filter_css_selector)
                )
            )
            reviewers_filter_icon_elem.click()

        except TimeoutException:
            print(
                f"Error: Timeout waiting for the copilot review button element to be clickable.",
                file=sys.stderr,
            )
            print(
                f"CSS selector used: {reviewers_filter_css_selector}", file=sys.stderr
            )
            return
        except NoSuchElementException:
            print(
                f"Error: Could not find the copilot review button element using the CSS selector.",
                file=sys.stderr,
            )
            print(
                f"CSS selector used: {reviewers_filter_css_selector}", file=sys.stderr
            )
            return
        except Exception as e:
            print(
                f"An unexpected error occurred while trying to click the copilot review button: {e}",
                file=sys.stderr,
            )
            return

        # Wait till the query loading is complete

        query_input_id = "review-filter-field"

        try:
            # Wait up to 15 seconds for the filter text field to be present
            wait = WebDriverWait(driver, 15)
            query_input_elem = wait.until(
                EC.visibility_of_element_located((By.ID, query_input_id)),
            )

            # Parent->Parent of the query input element
            parent_parent = query_input_elem.find_element(By.XPATH, "../..")

            # Wait for the loading spinner to disappear (up to 10 seconds)
            wait = WebDriverWait(driver, 10)
            loading_spinner = parent_parent.find_element(
                By.XPATH,
                "following-sibling::*[2]",
            ).find_element(By.CSS_SELECTOR, "svg.anim-rotate")
            wait.until(EC.invisibility_of_element(loading_spinner))

            # Navigate to the next siblings and find element with class js-username that has text "Copilot"
            copilot_username_elem = parent_parent.find_element(
                By.XPATH,
                "following-sibling::*[2]//span[contains(@class, 'js-username') and text()='Copilot']",
            )
        except TimeoutException:
            print(
                f"Error: Timeout waiting for the search results loading spinner to disappear.",
                file=sys.stderr,
            )
            return
        except NoSuchElementException:
            # Loading spinner is already disappeared
            pass
        except Exception as e:
            print(
                f"An unexpected error occurred while trying to wait for the loading spinner to disappear: {e}",
                file=sys.stderr,
            )
            return

        # Filter by "Copilot"

        try:
            # Write the query text "copilot"
            query_input_elem.send_keys("copilot")

        except TimeoutException:
            print(
                f"Error: Timeout waiting for the reviewer filter text field to be present.",
                file=sys.stderr,
            )
            print(f"ID used: {query_input_id}", file=sys.stderr)
            return
        except NoSuchElementException:
            print(
                f"Error: Could not find the reviewer filter text field.",
                file=sys.stderr,
            )
            print(f"ID used: {query_input_id}", file=sys.stderr)
            return
        except Exception as e:
            print(
                f"An unexpected error occurred while trying to enter query in the reviewer filter text field: {e}",
                file=sys.stderr,
            )
            return

        # Select copilot from the results list

        try:
            # Navigate to the next siblings and find element with class js-username that has text "Copilot"
            copilot_username_elem = parent_parent.find_element(
                By.XPATH,
                "following-sibling::*[2]//span[contains(@class, 'js-username') and text()='Copilot']",
            )
        except NoSuchElementException:
            print(
                f"Copilot in the reviewers filter result not found!",
                file=sys.stderr,
            )
            return
        except Exception as e:
            print(
                f"An unexpected error occurred while trying to find the result of copilot: {e}",
                file=sys.stderr,
            )
            return

        # Check if a copilot review is currently requested

        try:
            # Navigate up to find the parent-parent-parent element containing aria-checked attribute
            copilot_option_parent = copilot_username_elem.find_element(
                By.XPATH, "../../.."
            )

            # Check if aria-checked attribute exists and its value
            is_already_requested = False
            if copilot_option_parent.get_attribute("aria-checked"):
                is_already_requested = (
                    copilot_option_parent.get_attribute("aria-checked").lower()
                    == "true"
                )

            if is_already_requested:
                print(f"Copilot review is already requested and is pending response")
            else:
                # Click on the copilot option
                copilot_username_elem.click()

        except Exception as e:
            print(
                f"Error checking if Copilot review is already requested: {e}",
                file=sys.stderr,
            )

        # Close the popup (Send 'q' key to the body)
        body = driver.find_element(By.TAG_NAME, "body")
        body.click()
        body.send_keys("q")
        
        # Wait 1sec for the UI to update
        time.sleep(1)

    click_copilot_review_button(is_sync)

    # Copilot Summary Comment Button
    # ------------------------------

    def click_copilot_summary_comment_btn():
        # Click on the "Copilot actions" button under the new comment form

        try:
            menu_anchor_id = "copilot-md-menu-anchor-new_comment_field"
            wait = WebDriverWait(driver, 10)
            menu_anchor = wait.until(
                EC.element_to_be_clickable((By.ID, menu_anchor_id))
            )
            menu_anchor.click()

        except (TimeoutException, NoSuchElementException) as e:
            print(
                f"[ERROR] Error clicking the copilot actions menu button ({menu_anchor_id}): {e}",
                file=sys.stderr,
            )
            exit(1)

        # Click on the generate summary button

        summary_span_xpath = "//ul[@role='menu']//*[@aria-label='Generate']//span[normalize-space()='Generate a summary of the changes in this pull request.']"
        try:
            # Wait for the specific span element to be clickable (implies it's visible and enabled)
            wait = WebDriverWait(driver, 10)
            summary_span_element = wait.until(
                EC.element_to_be_clickable((By.XPATH, summary_span_xpath))
            )

            summary_span_element.click()

            # Wait for the summary comment loader to disappear
            error_banner_locator = (
                By.XPATH,
                "//div[@data-testid='copilot-summary-error-banner-icon']",
            )
            try:
                wait_for_invisibility = WebDriverWait(driver, 120)
                wait_for_invisibility.until(
                    EC.invisibility_of_element_located(error_banner_locator)
                )
            except TimeoutException:
                print(
                    "[ERROR] The summary comment loader remained visible after the timeout.",
                    file=sys.stderr,
                )
                exit(1)
            except Exception as e:
                print(
                    f"[ERROR] An unexpected error occurred while waiting for error banner invisibility: {e}",
                    file=sys.stderr,
                )
                exit(1)

        except TimeoutException:
            print(
                f"[ERROR] Timeout waiting for the summary span element to be clickable.",
                file=sys.stderr,
            )
            print(f"XPath used: {summary_span_xpath}", file=sys.stderr)
        except NoSuchElementException:
            print(
                f"[ERROR] Could not find the summary span element using the XPath.",
                file=sys.stderr,
            )
            print(f"XPath used: {summary_span_xpath}", file=sys.stderr)
        except Exception as e:
            print(
                f"[ERROR] An unexpected error occurred while trying to click the summary span: {e}",
                file=sys.stderr,
            )

        # Click the "Comment" button

        try:
            # XPath to find the specific submit button within the form
            comment_button_xpath = "//form[@id='new_comment_form']//button[@type='submit' and contains(@class, 'btn-primary') and contains(@class, 'btn') and normalize-space()='Comment']"

            # Wait for the button to be clickable
            wait = WebDriverWait(driver, 15)  # Adjust timeout if needed
            comment_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, comment_button_xpath))
            )

            comment_button.click()

        except TimeoutException:
            print(
                f"[ERROR] Timeout waiting for the Comment button to be clickable.",
                file=sys.stderr,
            )
            print(f"XPath used: {comment_button_xpath}", file=sys.stderr)
        except NoSuchElementException:
            print(
                f"[ERROR] Could not find the Comment button using the XPath.",
                file=sys.stderr,
            )
            print(f"XPath used: {comment_button_xpath}", file=sys.stderr)
        except Exception as e:
            print(
                f"[ERROR] An unexpected error occurred while trying to click the Comment button: {e}",
                file=sys.stderr,
            )

    click_copilot_summary_comment_btn()

    # Optional: Keep the browser open for a bit longer for debugging if needed
    # time.sleep(10000)

    driver.quit()
