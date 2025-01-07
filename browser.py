from playwright.sync_api import sync_playwright
import random
import os
from datetime import datetime
import winsound
import sys
from logger import log_message

def get_playwright_path():
    """Get the correct path for Playwright resources when bundled"""
    if getattr(sys, 'frozen', False):
        return {
            'browser_path': sys._MEIPASS  # Just use the base directory
        }
    return None

def slot_found(page):
    log_message("🎉 SLOT FOUND! 🎉")
    print("🎉 SLOT FOUND! 🎉")
    winsound.Beep(1000, 500)
    winsound.Beep(2000, 500)
    winsound.Beep(1000, 500)
    winsound.Beep(2000, 500)
    winsound.Beep(1000, 500)
    winsound.Beep(2000, 500)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = os.path.join("screenshots", f"slot_found_{timestamp}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    log_message(f"Screenshot saved: {screenshot_path}")


def run_automation_rvsq(config, search_running):
    # Create screenshots directories
    for directory in ["screenshots", "error_screenshots"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    with sync_playwright() as playwright:
        browser = None
        context = None
        while search_running.get():
            try:
                log_message("[DEBUG] Starting browser automation...")
                
                # Simplified path handling
                playwright_paths = get_playwright_path()
                launch_args = {
                    'headless': False,
                    'args': ['--disable-redirect-limits']
                }
                
                if playwright_paths:
                    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_paths['browser_path']
                
                browser = playwright.chromium.launch(**launch_args)
                
                log_message("[RVSQ] Creating new context...")
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                )
                context.set_default_timeout(60000) # increase from 30 sec to 60 secs for general timeout
                page = context.new_page()

                log_message("[RVSQ] Navigating to form page...")
                page.goto(
                    'https://rvsq.gouv.qc.ca/prendrerendezvous/Principale.aspx',
                    timeout=60000,
                    wait_until='networkidle'
                )
                
                log_message("[RVSQ] Accepting cookies...")
                page.locator('#btnToutAccepter').click()
                
                log_message("[RVSQ] Filling form fields...")
                personal_info = config['personal_info']
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_FirstName', personal_info['first_name'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_LastName', personal_info['last_name'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_NAM', personal_info['nam'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_CardSeqNumber', personal_info['card_seq_number'])
                
                # Fill birth date fields
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_Day', personal_info['birth_day'])
                page.select_option('#ctl00_ContentPlaceHolderMP_AssureForm_Month', personal_info['birth_month'])
                page.fill('#ctl00_ContentPlaceHolderMP_AssureForm_Year', personal_info['birth_year'])
                
                log_message("[RVSQ] Checking consent checkbox...")
                page.check('#AssureForm_CSTMT')
                
                log_message("[RVSQ] Waiting for Continue button...")
                page.wait_for_selector('#ctl00_ContentPlaceHolderMP_myButton:not([disabled])')
                
                log_message("[RVSQ] Clicking Continue button...")
                page.click('#ctl00_ContentPlaceHolderMP_myButton')
                
                log_message("[RVSQ] Waiting for navigation...")
                page.wait_for_load_state('networkidle')
                
                log_message("[RVSQ] Checking if user has a family doctor...")
                
                # Wait a moment for the page to load
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(2000)
                
                # Check for family doctor
                has_family_doctor = page.locator("a.h-SelectAssureBtn.ctx-changer[data-type='1']").is_visible()
                no_family_doctor = page.locator("text=pas de médecin de famille").is_visible()
                
                if no_family_doctor:
                    log_message("[RVSQ] No family doctor detected, proceeding with appointment search...")
                    log_message("[RVSQ] Clicking proximity button for no family doctor case...")
                    page.click("a.h-SelectAssureBtn.ctx-changer[data-type='3']")
                elif has_family_doctor:
                    log_message("[RVSQ] Family doctor detected, proceeding with appointment search...")
                    page.click("a.h-SelectAssureBtn.ctx-changer[data-type='1']")
                else:
                    log_message("[RVSQ] Could not determine family doctor status")
                    return
                
                log_message("[RVSQ] Waiting for dropdown...")
                page.wait_for_selector('#consultingReason', state='visible', timeout=60000)
                page.wait_for_timeout(2000)
                
                log_message("[RVSQ] Selecting 'Consultation Urgente'...")
                page.click('#consultingReason')
                page.select_option('#consultingReason', 'ac2a5fa4-8514-11ef-a759-005056b11d6c')
                
                if not has_family_doctor:
                    log_message("[RVSQ] Setting 50km radius...")
                    page.wait_for_selector('#perimeterCombo', state='visible')
                    page.wait_for_timeout(1000)
                
                log_message("[RVSQ] Clicking 'Rechercher' button...")
                page.click('button:has-text("Rechercher")')
                page.wait_for_load_state('networkidle')
                
                if has_family_doctor:
                    log_message("[RVSQ] Clicking GMF button...")
                    page.click('div.thumbnail.tmbArrow.tmbBtn.h-butType2dot2:has-text("Prendre rendez-vous avec un professionnel de la santé de mon groupe de médecine de famille (GMF)")')
                    
                    log_message("[RVSQ] Clicking 'Rechercher' again...")
                    page.click('button:has-text("Rechercher")')
                    page.wait_for_load_state('networkidle')
                    page.click('div.thumbnail.tmbArrow.tmbBtn.h-butType3:has-text("Prendre rendez-vous dans une clinique à proximité")')
                
                elif not has_family_doctor:
                    page.wait_for_load_state('networkidle')
                
                    log_message("[RVSQ] Clicking 'Rechercher' again...")
                    page.click('button:has-text("Rechercher")')
                    page.wait_for_load_state('networkidle')
                
                
                
                try:
                    page.select_option('#perimeterCombo', '4')
                except:
                    try:
                        page.click('#perimeterCombo')
                        page.select_option('#perimeterCombo', value='4')
                    except:
                        page.evaluate('document.getElementById("perimeterCombo").value = "4"')


                while search_running.get():  # Check if we should continue running
                    log_message("[RVSQ] Searching for slots...")
                    page.fill('#PostalCode', personal_info['postal_code'])
                    page.click('button.h-SearchButton.btn.btn-primary:has-text("Rechercher")')
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(5000)
                    
                    no_slots_element = page.locator('#clinicsWithNoDisponibilities')
                    no_slots_text = page.locator('text=Aucun rendez-vous rpondant')
                    no_slots_full_text = page.locator('text=Aucun rendez-vous répondant à vos critères de recherche n\'est disponible pour le moment.')
                    clinic_section = page.locator('text=Les cliniques suivantes offrent des disponibilités pour votre rendez-vous :')
                    
                    has_negative_indicators = (
                        no_slots_text.is_visible() or 
                        no_slots_element.is_visible() or
                        no_slots_full_text.is_visible()
                    )
                    
                    if has_negative_indicators:
                        log_message("[RVSQ] No slots available")
                    elif clinic_section.is_visible():
                        slot_found(page)
                        page.wait_for_timeout(240000) # wait 4 minutes
                    
                    if not search_running.get():
                        break
                        
                    page.wait_for_timeout(random.randint(1000, 5000))
                        
                    
            except Exception as e:
                log_message(f"\n[ERROR] An error occurred: {str(e)}")
                print(f"\n[ERROR] An error occurred: {str(e)}")
                if page:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    error_path = os.path.join("error_screenshots", f"rvsq_error_{timestamp}.png")
                    page.screenshot(path=error_path, full_page=True)
            finally:
                context.close()
                browser.close()

def run_automation_bonjoursante(config, search_running, autobook):
    # Create screenshots directories
    for directory in ["screenshots", "error_screenshots"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    with sync_playwright() as playwright:
        browser = None
        context = None
        while search_running.get():
            try:
                log_message("[BonjourSante] Starting browser automation...")
                
                # Simplified path handling
                playwright_paths = get_playwright_path()
                launch_args = {
                    'headless': False,
                    'args': ['--disable-redirect-limits']
                }
                
                if playwright_paths:
                    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = playwright_paths['browser_path']
                
                browser = playwright.chromium.launch(**launch_args)
                
                log_message("[BonjourSante] Creating new context...")
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                )
                context.set_default_timeout(60000) # increase from 30 sec to 60 secs for general timeout
                page = context.new_page()
                
                log_message("[BonjourSante] Navigating to form page...")
                page.goto(
                    'https://bonjour-sante.ca/uno/clinique',
                    timeout=60000
                )
                
                log_message("[BonjourSante] Accepting cookies...")
                page.locator('#didomi-notice-agree-button').click()
                
                page.locator("div[data-test='postalCodeCategoryButton']").click() # click on region clinic
                log_message("[BonjourSante] Filling form fields...")
                personal_info = config['personal_info']
                page.fill('#patient-nam-input', personal_info['card_seq_number'])
                page.fill('#postal-code-search-input', personal_info['postal_code'])
                page.locator("button[data-test='searchPostalCodeButton']").click()

                # Wait a moment for the page to load
                page.wait_for_selector("iframe[src*='hub.bonjour-sante.ca']")
                
                # Fill fields
                log_message("[BonjourSante] Filling form fields part 2...")
                frameLocator = page.frame_locator("iframe[src*='hub.bonjour-sante.ca']")
                frameLocator.locator('input#healthInsuranceNumber').fill("".join(personal_info['nam'].split()))
                frameLocator.locator('input#healthInsuranceNumberSequence').fill(personal_info['card_seq_number'])
                frameLocator.locator('input#firstName').fill(personal_info['first_name'])
                frameLocator.locator('input#lastName').fill(personal_info['last_name'])
                frameLocator.locator('button#confirm').click()
                # Wait a moment for the page to load
                page.wait_for_selector("iframe[src*='hub.bonjour-sante.ca']")
                log_message("[BonjourSante] Select Options")
                frameLocator = page.frame_locator("iframe[src*='hub.bonjour-sante.ca']")
                frameLocator.locator('mat-radio-button#mat-radio-2').click()
                date = datetime.today().strftime('%Y-%m-%d')
                frameLocator.locator('#mat-input-0').fill(date)
                slider = frameLocator.locator("input[type='range']")
                slider.evaluate("(element, value) => element.value = value", "2") # set range to 50km
                slider.evaluate("(element) => element.dispatchEvent(new Event('input'))")
                slider.evaluate("(element) => element.dispatchEvent(new Event('change'))")
                frameLocator.locator('button#confirm').click()
                frameLocator.locator('button#continue').click()
                while search_running.get(): 
                    frameLocator.locator('div.title-criteria-container').wait_for(state = 'visible') # wait for "Résultats de recherche" to load
                    log_message("[BonjourSante] Searching for slots...")
                    iframe_content = page.query_selector("iframe[src*='hub.bonjour-sante.ca']").content_frame().content()
                    # print('Aucun rendez-vous ne correspond à vos critères de recherche' in iframe)
                    if frameLocator.locator('app-locked-walkin-availability[data-test="locked-walkin-availability"]').count() > 0 or 'Consultation réservée pour vous' in iframe_content  :
                        slot_found(page)
                        if (autobook):
                            frameLocator.locator('button[data-test="confirm-selection-button"]').click()
                            #load the next page
                            frameLocator.locator('#confirmation-checkbox-input').wait_for(state='visible')
                            frameLocator.locator('input#cellPhone').fill(format_phone_number(personal_info['cellphone']))
                            frameLocator.locator('input#email').fill((personal_info['email']))
                            frameLocator.locator('select#reasons').select_option(value='28') # Reason : Autres
                            frameLocator.locator('#confirmation-checkbox-input').check()
                            frameLocator.locator('#confirm').click()
                            frameLocator.locator('button[data-test="registration-dialog-submit-btn"]').click()
                            frameLocator.locator('lib-alert').wait_for(state='visible')
                            search_running.set(False)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            screenshot_path = os.path.join("screenshots", f"slot_confirmed_{timestamp}.png")
                            page.screenshot(path=screenshot_path, full_page=True)
                            log_message(f"Screenshot saved: {screenshot_path}")
                            # context.set_default_timeout(240000) # wait for 4 imnutes
                            # page.wait_for_timeout(240000)
                            log_message("Booking Confirmed")
                            break
                        else:
                            context.set_default_timeout(240000) # wait for 4 imnutes
                            page.wait_for_timeout(240000)
                            log_message('[BonjourSante] Failed to book slot Bonjour Sante, timer expired')
                            raise RuntimeError('Failed to book slot Bonjour Sante, timer expired')
                    elif frameLocator.locator('div.t-alert-content').count() > 0 :
                        log_message("[BonjourSante] Une erreur est survenue lors de la recherche de consultations.")
                        frameLocator.locator('a.link').click()
                        frameLocator.locator('button#confirm').click()
                        page.wait_for_timeout(random.randint(2000, 10000)) # Wait some time before clicking
                        frameLocator.locator('button#continue').click()
                    elif 'Aucun rendez-vous ne correspond à vos critères de recherche' in frameLocator.locator("span.label-message").inner_text():
                        log_message("[BonjourSante] No slots available")
                        # print("[BonjourSante] No slots available")
                        frameLocator.locator('[data-test="make-new-search"]').click() #click on Modifier les critères de recherche
                        # date = datetime.today().strftime('%Y-%m-%d')
                        # frameLocator.locator('#mat-input-' + str(loops)).fill(date) # get new date
                        frameLocator.locator('button#confirm').click()
                        page.wait_for_timeout(random.randint(2000, 10000)) # Wait some time before clicking
                        frameLocator.locator('button#continue').click()
                    else:
                        print('[BonjourSante] Failed to parse Bonjour Sante response')
                        log_message('[BonjourSante] Failed to parse Bonjour Sante response')
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = os.path.join("screenshots", f"bonjour_sante_error_{timestamp}.png")
                        page.screenshot(path=screenshot_path, full_page=True)
                        log_message(f"Screenshot saved: {screenshot_path}")
                        raise RuntimeError('Failed to parse Bonjour Sante response')


            except Exception as e:
                log_message(f"\n[ERROR1] An error occurred: {str(e)}")
                print(f"\n[ERROR1] An error occurred: {str(e)}")
                if page:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    error_path = os.path.join("error_screenshots", f"bonjour_sante_error_{timestamp}.png")
                    page.screenshot(path=error_path, full_page=True)
            finally:
                context.close()
                browser.close()


def format_phone_number(number):
    if len(number) == 10 and number.isdigit():
        return f"({number[:3]}) {number[3:6]}-{number[6:]}"
    raise ValueError("Invalid phone number format")