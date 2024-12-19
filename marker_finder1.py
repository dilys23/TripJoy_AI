from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re


def main():
    with sync_playwright() as p:
        page_url = f"https://maps.google.com"

        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            locale="vi-VN",
        )
        page = context.new_page()

        page.goto(page_url, timeout=60000)

        # page.pause()

        page.wait_for_selector("canvas")

        page.wait_for_load_state("load")
        page.locator('//input[@id="searchboxinput"]').fill("bà nà Hill")
        time.sleep(1.5)
        # page.press('//input[@id="searchboxinput"]', 'Enter')
        page.locator("//div[@id='ydp1wd-haAclf']/div[1]").click()
        time.sleep(1)

        # for h in range(0, 15):
        #     page.locator('//div[@aria-label="Kết quả cho điểm du lịch ở Đà Nẵng"]').evaluate(
        #         'el => el.scrollTop = el.scrollHeight')
        #     time.sleep(2)

        while page.locator('//button[@id="widget-zoom-in"]').is_enabled():
            page.locator('//button[@id="widget-zoom-in"]').click()
            time.sleep(0.5)

        data_attraction_dict = {}
        map_canvas = page.locator("//canvas[@id]").first
        map_box = map_canvas.bounding_box()
        # data_attraction_province_small = page.locator('//div[@class="Nv2PK THOPZb CpccDe "]').all()
        # for index, data_attraction_province in enumerate(data_attraction_province_small):
        #     data_attraction_dict = {}
        #     map_canvas = page.locator('//canvas[@id]').first
        #     map_box = map_canvas.bounding_box()
        #
        #     if map_box:
        #         # Số lần kéo
        #         drag_times = 5
        #         drag_distance = 200  # Khoảng cách kéo mỗi lần (pixels)
        #
        #         for _ in range(drag_times):
        #             # Di chuyển chuột đến giữa bản đồ
        #             page.mouse.move(map_box['x'] + map_box['width'] / 2, map_box['y'] + map_box['height'] / 2)
        #
        #             # Nhấn giữ chuột (click và giữ)
        #             page.mouse.down()
        #
        #             # Kéo bản đồ sang phải
        #             page.mouse.move(map_box['x'] + map_box['width'] / 2 - drag_distance,
        #                             map_box['y'] + map_box['height'] / 2, steps=10)
        #
        #             # Thả chuột ra để hoàn thành kéo
        #             page.mouse.up()
        #
        #             # Đợi một chút trước khi kéo tiếp lần sau (nếu cần)
        #             page.wait_for_timeout(1000)  # Đợi 1 giây
        #     else:
        #         print("Không tìm thấy bản đồ")
        #
        #     if page.locator('//div[@class="Nv2PK THOPZb CpccDe "]').nth(index).count() > 0:
        #         page.locator('//div[@class="Nv2PK THOPZb CpccDe "]').nth(index).click()
        #         time.sleep(3)
        #     else:
        #         break
        #     if (page.locator('//label[@id="U5ELMd"]').inner_text() != "5 mét"):
        #         while page.locator('//button[@id="widget-zoom-in"]').is_enabled():
        #             page.locator('//button[@id="widget-zoom-in"]').click()
        #             time.sleep(0.5)

        page.mouse.click(
            map_box["x"] + (2.1 * map_box["width"] / 3),  # x-coordinate
            map_box["y"] + (map_box["height"] / 2),  # y-coordinate
            button="right",  # Specify right button click
        )

        coordinators = (
            page.locator('//div[@class="mLuXec"]').first.inner_text().split(", ")
        )
        data_attraction_dict["latitude"] = coordinators[0]
        data_attraction_dict["longitude"] = coordinators[1]

        time.sleep(2)
        print(data_attraction_dict)


if __name__ == "__main__":
    main()
