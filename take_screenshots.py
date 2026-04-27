from playwright.sync_api import sync_playwright
import time

def take_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 1024})
        
        print("Navigating to http://localhost:8502")
        page.goto('http://localhost:8502')
        time.sleep(5)
        
        try:
            print("Clicking Analyse tab")
            page.get_by_role("tab", name="Analyse").click()
            time.sleep(3)
            page.screenshot(path='docs/rapport_assets/app_analyse.png')
            
            print("Clicking Assistant tab")
            page.get_by_role("tab", name="Assistant").click()
            time.sleep(3)
            page.screenshot(path='docs/rapport_assets/app_assistant.png')
            
        except Exception as e:
            print(f"Error clicking tabs: {e}")
            
        browser.close()

if __name__ == "__main__":
    take_screenshots()
