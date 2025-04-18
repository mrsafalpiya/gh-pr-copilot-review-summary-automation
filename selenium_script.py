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
        if not is_sync:  # New PR is created
            # Find and click the Copilot Re-Request Review button using XPath
            copilot_rerequest_review_btn_xpath = (
                "//button[@id='re-request-review-copilot-pull-request-reviewer']"
            )
            try:
                # Wait up to 15 seconds for the copilot review button to be present and clickable
                wait = WebDriverWait(driver, 15)
                copilot_rerequest_review_btn = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, copilot_rerequest_review_btn_xpath)
                    )
                )
                copilot_rerequest_review_btn.click()

            except TimeoutException:
                print(
                    f"Error: Timeout waiting for the copilot re-request review button element to be clickable.",
                    file=sys.stderr,
                )
                print(f"XPath used: {copilot_review_btn_xpath}", file=sys.stderr)
            except NoSuchElementException:
                print(
                    f"Error: Could not find the copilot re-request review button element using the XPath.",
                    file=sys.stderr,
                )
                print(f"XPath used: {copilot_review_btn_xpath}", file=sys.stderr)
            except Exception as e:
                print(
                    f"An unexpected error occurred while trying to click the copilot re-request review button: {e}",
                    file=sys.stderr,
                )
        else:
            # Find and click the Copilot Review button using XPath
            # This XPath translates the JS: find link, go to parent, go to previous sibling, get first child
            copilot_review_btn_xpath = "//a[@href='/apps/copilot-pull-request-reviewer']/../preceding-sibling::*[1]/*[1]"

            try:
                # Wait up to 15 seconds for the copilot review button to be present and clickable
                wait = WebDriverWait(driver, 15)
                copilot_btn_elem = wait.until(
                    EC.element_to_be_clickable((By.XPATH, copilot_review_btn_xpath))
                )
                copilot_btn_elem.click()

            except TimeoutException:
                print(
                    f"Error: Timeout waiting for the copilot review button element to be clickable.",
                    file=sys.stderr,
                )
                print(f"XPath used: {copilot_review_btn_xpath}", file=sys.stderr)
            except NoSuchElementException:
                print(
                    f"Error: Could not find the copilot review button element using the XPath.",
                    file=sys.stderr,
                )
                print(f"XPath used: {copilot_review_btn_xpath}", file=sys.stderr)
            except Exception as e:
                print(
                    f"An unexpected error occurred while trying to click the copilot review button: {e}",
                    file=sys.stderr,
                )

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
