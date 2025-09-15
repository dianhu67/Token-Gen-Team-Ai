from selenium_driverless import webdriver
from selenium_driverless.types.by import By
import asyncio
from openai import OpenAI
import time
import random 
import os
import string
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import imaplib
import email
from colorama import Fore, Style, init
init(autoreset=True)
import re
import tls_client
import httpx
import time
import base64
import json
import random
from urllib.parse import urlparse, parse_qs
import requests
from itertools import cycle
import re
from selenium.webdriver.common.by import By
import asyncio
import datetime
from playwright.async_api import async_playwright
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import asyncio
from playwright.async_api import async_playwright
from openai import OpenAI
import random
import string
import requests
import json
import datetime
import json
import imaplib
import email
from email.header import decode_header
import re
import asyncio
import asyncio
from time import sleep



SOLVER_API_KEY = "Team-Ai-XXXXX-rpkcfy"  
PROXY = "http://PROXY" 
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"


def randomgen(length=20):
    return ''.join(random.choices(string.ascii_letters, k=length))

def randomsub():
    return ''.join(random.choices(string.ascii_lowercase, k=6))

def create_inbox():
    mail = randomgen()
    password = randomgen()
    domain = "detroid.shop"
    email = f"{mail}@{domain}"

    headers = {
        'accept': 'application/json',
        'X-API-Key': '5YC8E-316701-F09213-17E434-39B659',
        'Content-Type': 'application/json'
    }

    data = {
        "active": "1",
        "domain": domain,
        "local_part": mail,
        "name": mail,
        "password": mail,
        "password2": mail,
        "quota": "0",
        "tls_enforce_in": "1",
        "sogo_access": "1",
        "tls_enforce_out": "1"
    }

    try:
        response = requests.post("https://mail.detroid.shop/api/v1/add/mailbox", headers=headers, json=data)
        if response.status_code != 200:
            return {"email": None, "token": None, "error": f"Create failed: {response.text}"}

        change_data = {
            "attr": {
                "password": password,
                "password2": password
            },
            "items": [email]
        }

        change_response = requests.post("https://mail.detroid.shop/api/v1/edit/mailbox", headers=headers, json=change_data)

        if change_response.status_code == 200:
            return {"email": email, "token": password, "error": None}
        else:
            requests.post(
                "https://mail.detroid.shop/api/v1/delete/mailbox",
                headers=headers,
                json={"username": email}
            )
            return {"email": None, "token": None, "error": f"Password change failed: {change_response.text}"}

    except requests.exceptions.RequestException as e:
        return {"email": None, "token": None, "error": str(e)}


async def solve_captcha_api(data, proxy):
    payload = {
        "site_key": data["captcha_sitekey"],
        "site_url": "discord.com",
        "rqd": data["captcha_rqdata"],
        "key": SOLVER_API_KEY,
        "proxy": proxy,
        "service": data["captcha_service"],
        "session_id": data["captcha_session_id"],
        "rqtoken": data["captcha_rqtoken"]
    }

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post("http://captcha.aiclientz.com:1234/solve_basic", json=payload, timeout=None)
            now = time.strftime("%H:%M:%S")
            try:
                j = r.json()
            except Exception as json_err:
                print(f"[{now}] ERROR parsing JSON: {json_err}")
                print(f"[{now}] Response Text: {r.text}")
                return None

            if j.get("code") == "201":
                cap = j.get("captcha")
                return cap

            # Unexpected result, print full response
            print(f"[{now}] WARNING: Captcha not solved. Full response:")
            print(j)

    except Exception as e:
        now = time.strftime("%H:%M:%S")
        print(f"[{now}] ERROR CAPTCHA API: {e}")

    return None
async def fetch_verification_link(imap_email, imap_pass):
    try:
        # Convert blocking IMAP calls to async
        mail = imaplib.IMAP4_SSL("mail.detroid.shop", 993)
        await asyncio.to_thread(mail.login, imap_email, imap_pass)
        await asyncio.to_thread(mail.select, 'inbox')
        
        max_wait = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status, messages = await asyncio.to_thread(mail.search, None, '(FROM "discord.com")')
            if status != 'OK' or not messages[0]:
                await asyncio.sleep(5)
                continue
            
            email_ids = messages[0].split()
            if not email_ids:
                await asyncio.sleep(5)
                continue
            
            latest_id = email_ids[-1]
            status, msg_data = await asyncio.to_thread(mail.fetch, latest_id, '(RFC822)')
            if status != 'OK':
                continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            body = ''
            
            if msg.is_multipart():
                for part in msg.get_payload():
                    if part.get_content_type() == 'text/html':
                        body = part.get_payload(decode=True).decode(errors='ignore')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
            
            link_pattern = r'https://click\.discord\.com/[^\'" ]+'
            links = re.findall(link_pattern, body)
            if len(links) >= 2:
                await asyncio.to_thread(mail.close)
                await asyncio.to_thread(mail.logout)
                return links[1]
                
            await asyncio.sleep(5)
        
        await asyncio.to_thread(mail.close)
        await asyncio.to_thread(mail.logout)
        return None
        
    except Exception as e:
        now = time.strftime("%H:%M:%S")
        print(f"[{now}] IMAP ERROR: {e}")
        try:
            await asyncio.to_thread(mail.close)
            await asyncio.to_thread(mail.logout)
        except:
            pass
        return None

def resolve_link(click_link, delay=2):
    attempt = 1
    while True:
        try:
            httpx_session = httpx.Client(proxy=PROXY, follow_redirects=True, timeout=10)
            response = httpx_session.get(click_link)
            return str(response.url)  # The final redirected URL (real verification link)
        except Exception as e:
            attempt += 1
            time.sleep(delay)


def extract_token_from_url(url):
    parsed = urlparse(url)
    fragment = parsed.fragment
    if fragment.startswith("token="):
        return fragment.split("token=")[1]
    return None

async def verify_token(token):
    token_retry_done = False  # Track if we've retried TOKEN_INVALID once
    
    while True:  # Infinite retry loop
        try:
            # Initialize session fresh each attempt
            session = tls_client.Session(client_identifier="chrome_107")
            session.headers.update({"user-agent": UA})
            session.proxies = {"http": PROXY, "https": PROXY}
            
            # Initial request with retry
            while True:
                try:
                    await asyncio.to_thread(session.get, "https://discord.com/")
                    break
                except Exception as e:
                    if "EOF" in str(e) or "tls" in str(e).lower():
                        print(f"⚠️ Connection error, retrying... ({str(e)})")
                        await asyncio.sleep(2)
                        continue
                    raise

            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "priority": "u=1, i",
                "referer": "https://discord.com/channels/1339615714113486908/1339654133384482929",
                "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "Windows",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "x-debug-options": "bugReporterEnabled",
                "x-discord-locale": "en-US",
                "x-discord-timezone": "Asia/Calcutta",
                "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZSwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTM0LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjozODIzNTUsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
            }

            payload = {"token": token}

            # Verification attempt with retry
            while True:
                try:
                    response = await asyncio.to_thread(
                        session.post,
                        "https://discord.com/api/v9/auth/verify",
                        headers=headers,
                        json=payload
                    )
                    break
                except Exception as e:
                    if "EOF" in str(e) or "tls" in str(e).lower():
                        print(f"⚠️ Request failed, retrying... ({str(e)})")
                        await asyncio.sleep(2)
                        continue
                    raise

            if response.status_code == 200:
                response_json = response.json()
                auth_token = response_json.get('token')
                print(f"[{Fore.BLUE}+{Style.RESET_ALL}]{Style.RESET_ALL} {Fore.BLUE}Successfully Verified{Style.RESET_ALL} | {Fore.BLUE}[{Style.RESET_ALL}{auth_token}{Fore.BLUE}]{Style.RESET_ALL}")
                return auth_token

            try:
                response_json = response.json()
            except:
                response_json = {}

            if "captcha_sitekey" in response_json:
                captcha_token = await solve_captcha_api(response_json, PROXY)
                
                if captcha_token:
                    headers.update({
                        "x-captcha-key": captcha_token,
                        "x-captcha-rqtoken": response_json.get("captcha_rqtoken", ""),
                        "x-captcha-session-id": response_json.get("captcha_session_id", "")
                    })
                    
                    # Captcha retry loop
                    while True:
                        try:
                            response = await asyncio.to_thread(
                                session.post,
                                "https://discord.com/api/v9/auth/verify",
                                headers=headers,
                                json=payload
                            )
                            break
                        except Exception as e:
                            if "EOF" in str(e) or "tls" in str(e).lower():
                                print(f"⚠️ Captcha retry failed, retrying... ({str(e)})")
                                await asyncio.sleep(2)
                                continue
                            raise

                    if response.status_code == 200:
                        response_json = response.json()
                        auth_token = response_json.get('token')
                        print(f"[{Fore.BLUE}+{Style.RESET_ALL}]{Style.RESET_ALL} {Fore.BLUE}Successfully Verified{Style.RESET_ALL} | {Fore.BLUE}[{Style.RESET_ALL}{auth_token}{Fore.BLUE}]{Style.RESET_ALL}")
                        return auth_token
                    print(f"❌ Verification failed after captcha: {response.text}")
                else:
                    print("❌ Failed to solve captcha")
                    await asyncio.sleep(5)
                    continue  # Retry entire process if captcha fails
            else:
                # Handle TOKEN_INVALID with single retry
                if "TOKEN_INVALID" in response.text:
                    if not token_retry_done:
                        token_retry_done = True
                        print("⚠️ TOKEN_INVALID detected. Retrying once...")
                        await asyncio.sleep(3)
                        continue  # Retry once
                    else:
                        print(f"❌ Verification failed (TOKEN_INVALID): {response.text}")
                        return None  # Stop after one retry
                else:
                    print(f"❌ Verification failed: {response.text}")
                    await asyncio.sleep(5)
                    continue  # Retry on other verification failures
                
        except Exception as e:
            if "EOF" in str(e) or "tls" in str(e).lower():
                print(f"🔥 Verification error (retrying): {str(e)}")
                await asyncio.sleep(2)
                continue
            print(f"🔥 Critical error: {str(e)}")
            await asyncio.sleep(5)
            continue

async def ask_openai_combined(question, mode="answer"):
    client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
    
    if mode == "language":
        content = f'Is the following sentence written in Dutch or English? Answer only with "dutch" or "english" and nothing else:\n\n"{question}"'
    else:
        content = f"Vraag: {question}. Antwoord alleen met 'ja' of 'nee' in kleine letters zonder punten of uitleg."

    completion = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": content}]
    )
    return completion.choices[0].message.content.strip().lower()

async def solve_captcha(driver, attempt_count):
    try:


        await asyncio.sleep(2)
        question_element = await driver.find_element(By.ID, "prompt-text")
        question = await question_element.text

        # Solve the question
        answer = await ask_openai_combined(question, mode="answer")

        input_field = await driver.find_element(By.CSS_SELECTOR, "input.input-field")
        await driver.execute_script("""
            const el = arguments[0], val = arguments[1];
            el.value = val;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        """, input_field, answer)

        submit_button = await driver.find_element(By.CSS_SELECTOR, "div.button-submit")
        await submit_button.click()
        return True

    except Exception as e:
        return False

async def set_react_select(driver, selector_id, value, timeout=10):
    element = await wait_for_element(driver, By.ID, selector_id, timeout)
    await driver.execute_script("""
        const el = arguments[0], val = arguments[1];
        el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, key: 'Enter', code: 'Enter' }));
    """, element, value)
    await asyncio.sleep(0.2)

async def wait_for_element(driver, by, selector, timeout=10):
    for _ in range(timeout * 2):  # Checks every 0.5s up to timeout seconds
        try:
            element = await driver.find_element(by, selector)
            if element:
                return element
        except:
            pass
        await asyncio.sleep(0.5)
    raise TimeoutException(f"Element not found: {selector}")


async def fast_fill(driver, selector, value, by=By.NAME, timeout=10):
    element = await wait_for_element(driver, by, selector, timeout)
    await driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", element, value)
    await asyncio.sleep(0.2)


async def switch_to_hcaptcha_frame(driver, max_attempts=15, delay=2):
    for attempt in range(max_attempts):
        try:
            challenge_iframe = await driver.find_element(By.CSS_SELECTOR, "iframe[title*='hCaptcha challenge']")
            await driver.switch_to.frame(challenge_iframe)
            return True
        except Exception as e:
            await asyncio.sleep(delay)

    return False


async def register_account(email, username, display_name, mail_token):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    password = mail_token
 
    for attempt in range(3):
        try:
            async with webdriver.Chrome(options=options) as driver:
                await driver.get("https://discord.com/register")
                await asyncio.sleep(15)

                await fast_fill(driver, "email", email)
                await fast_fill(driver, "global_name", display_name)
                await fast_fill(driver, "username", username)
                await fast_fill(driver, "password", mail_token)
                await set_react_select(driver, "react-select-2-input", "January")
                await set_react_select(driver, "react-select-3-input", "1")
                await set_react_select(driver, "react-select-4-input", "2000")
                try:
                    checkbox = await driver.find_element(By.CSS_SELECTOR, "div.checkbox_f525d3.box_f525d3")
                    await checkbox.click()
                except Exception:
                    pass
                continue_button = await driver.find_element(By.CSS_SELECTOR, "button[type='submit'] div.contents__201d5")
                await continue_button.click()

                await asyncio.sleep(17)

                switched = await switch_to_hcaptcha_frame(driver)
                if not switched:
                    await asyncio.sleep(5)
                    continue 

                language_selector = None
                for _ in range(5):
                    try:
                        language_selector = await wait_for_element(driver, By.ID, "display-language", timeout=3)
                        if language_selector:
                            await language_selector.click()
                            break
                    except Exception as e:
                        await asyncio.sleep(0.5)
                else:
                    print("❌ Language selector not found — continuing with default")
                
                if language_selector:
                    dutch_selected = False
                    for dutch_attempt in range(5):
                        try:
                            dutch_option = await wait_for_element(driver, By.XPATH, "//div[@class='option']/span[text()='Dutch']/..", timeout=3)
                            if dutch_option:
                                await dutch_option.click()
                                await asyncio.sleep(1)
                                dutch_selected = True
                                break
                        except Exception as e:
                            if dutch_attempt >= 1:  
                                try:
                                    await language_selector.click()
                                except Exception as e:
                                    print(f"⚠️ Failed to re-click language selector: {str(e)}")
                            await asyncio.sleep(0.5)
                    
                    if not dutch_selected:
                        print("❌ Dutch option not found — continuing with current language")
                for _ in range(5):
                    try:
                        continue_btn = await wait_for_element(driver, By.ID, "menu-info", timeout=10)
                        if continue_btn:
                            await asyncio.sleep(1)
                            break
                    except:
                        pass
                    await asyncio.sleep(0.5)
                else:
                    print("❌ menu info not found — retrying...")
                    continue

                text_challenge_selected = False
                for _ in range(3):  
                    for _ in range(2):  
                        try:
                            menu_info = await driver.find_element(By.ID, "menu-info")
                            await menu_info.click()
                            break
                        except Exception as e:
                            print(f"⚠️ Menu click attempt failed: {str(e)}")
                            await asyncio.sleep(0.5)
                    else:
                        print("❌ Could not click menu — retrying...")
                        continue

                    for _ in range(1):
                        try:
                            text_challenge = await wait_for_element(driver, By.ID, "text_challenge", timeout=10)
                            await text_challenge.click()
                            text_challenge_selected = True
                            break
                        except Exception as e:
                            await asyncio.sleep(0.5)
                    
                    if text_challenge_selected:
                        break  
                    
                    await asyncio.sleep(1)

                if not text_challenge_selected:
                    print("❌ Failed to select text challenge after retries — continuing...")
                    continue


                await asyncio.sleep(10)
                for i in range(3):
                    try:
                        success = await solve_captcha(driver, i)
                    except Exception as e:
                        if "no close frame received or sent" in str(e):
                            print("✅ Captcha solved - Registered Token")
                            await asyncio.sleep(10)
                            return True
                        print(f"⚠️ Captcha {i+1}/3 failed with error: {str(e)}")

                await asyncio.sleep(5)

                second_success = False
                for i in range(3):
                    try:
                        success = await solve_captcha(driver, i)
                        if success:
                            second_success = True
                            break
                    except Exception as e:
                        error_msg = str(e)
                        if "no close frame received or sent" in error_msg:
                            await asyncio.sleep(10)
                            return True
                    
                    if not second_success:
                        await asyncio.sleep(3)

                if not second_success:
                    pass
                print(
    f"[{Fore.GREEN}+{Style.RESET_ALL}] "
    f"Solved {Fore.GREEN}Hcap{Style.RESET_ALL} | "
    f"Created Token | "
    f"{Fore.BLUE}Verifying...{Style.RESET_ALL}"
)
                await asyncio.sleep(3)
                return True
            
        except Exception as e:
            print(f"❌ Error during registration: {str(e)}")
            try:
                await driver.save_screenshot("error.png")
                print("📸 Saved error screenshot")
            except:
                print("❌ Could not save screenshot")

        await asyncio.sleep(5)

    print("❌ All 3 registration attempts failed.")
    return False



async def verify_account(verification_link, email, password):
    try:
        resolved_url = await asyncio.to_thread(resolve_link, verification_link)
        if not resolved_url:
            print("❌ Failed to resolve verification link")
            return None

        token = await asyncio.to_thread(extract_token_from_url, resolved_url)
        if not token:
            print("❌ No token found in URL")
            return None

        auth_token = await verify_token(token)
        return auth_token  

    except Exception as e:
        print(f"💥 Verification error: {str(e)}")
        return None


async def run(verification_link, email, password):
    """Fixed run function that saves successful tokens"""
    try:
        auth_token = await verify_account(verification_link, email, password)
        if auth_token:
            with open("tokens.txt", "a") as f:
                f.write(f"{email}:{password}:{auth_token}\n")
            return True
        return False
    except Exception as e:
        print(f"💥 Error in run: {str(e)}")
        return False



def mask_string(s, visible=3):
    """Mask string except for the first and last visible characters."""
    if len(s) <= visible * 2:
        return '*' * len(s)
    return s[:visible] + '*' * (len(s) - visible * 2) + s[-visible:]

async def main():
    while True:
        try:


            inbox = None
            for attempt in range(3):
                inbox = create_inbox()
                if inbox["email"] and inbox["token"]:
                    masked_email = mask_string(inbox['email'], 3)
                    masked_token = mask_string(inbox['token'], 2)
                    print(f"[{Fore.BLUE}/{Style.RESET_ALL}] Using {Fore.BLUE}|{Style.RESET_ALL} {masked_email}:{masked_token} {Fore.BLUE}|{Style.RESET_ALL} Creating Discord Token...")


                    break
                else:
                    print(f"❌ Failed to create mailbox (attempt {attempt + 1}/3): {inbox['error']}")
                    await asyncio.sleep(3)

            if not inbox or not inbox["email"] or not inbox["token"]:
                print("❌ Giving up after 3 failed attempts to create inbox.")
                await asyncio.sleep(10)
                continue

            email = inbox["email"]
            mail_token = inbox["token"]
            username = randomgen()
            display_name = randomgen()
            password = mail_token

            registration_success = await register_account(email, username, display_name, mail_token)
            if not registration_success:
                await asyncio.sleep(10)
                continue

            await asyncio.sleep(4)

            verification_link = await fetch_verification_link(email, mail_token)
            if not verification_link:
                print("❌ Failed to find verification link")
                await asyncio.sleep(10)
                continue

            verification_success = await run(verification_link, email, password)
            if not verification_success:
                print("❌ Verification failed")
                await asyncio.sleep(10)
                continue

            await asyncio.sleep(10)

        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {str(e)}")
            print("🔄 Retrying in 2 minutes...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n🛑 Script stopped by user")
            break
        except Exception as e:
            print(f"⚠️ Critical error in main loop: {str(e)}")
            print("🔄 Restarting main loop in 2 minutes...")
            sleep(120)
