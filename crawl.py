import csv
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright
from time import sleep

def load_accounts(filepath: str):
    accounts = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append((row["username"], row["password"]))
    return accounts


def run(playwright: Playwright) -> None:
    accounts = load_accounts("accounts.csv")
    output_dir = Path('output/html')
    output_dir.mkdir(parents=True, exist_ok=True)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://app.tas-annotools.com/")


    for username, password in accounts:
        print(f'{username=}')
        page.get_by_role("textbox", name="ユーザー名").fill(username)
        page.get_by_role("textbox", name="パスワード").fill(password)
        page.get_by_role("button", name="Sign In").click()
        page.get_by_role("button", name="📹 Select Video").click()
        sleep(2)

        video_list = page.locator("#root > div > div > div > div.video-list")
        video_count = video_list.locator(":scope > *").count()
        page.get_by_role("button", name="✕ Close").click()
        print(f"{video_count=}")

        output_dir_by_user = Path(output_dir / username)
        output_dir_by_user.mkdir(exist_ok=True)

        for i in range(video_count):
            output_file = output_dir_by_user / f"{username}_{i}.html"
            if output_file.exists():
                print(f'{output_file} is already exists.')
                continue

            page.get_by_role("button", name="📹 Select Video").click()
            sleep(1)

            video_list = page.locator("#root > div > div > div > div.video-list")
            video_list.locator(":scope > *").nth(i).click()
            sleep(2)

            html = page.content()
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"saved {output_file}")

        page.get_by_role("button", name="Sign Out").click()
        sleep(1)

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
