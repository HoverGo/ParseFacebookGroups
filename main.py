import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import lxml
import time
import tkinter as tk
from tkinter import filedialog, messagebox


def open_file():
    file_path = filedialog.askopenfilename(title="Выберите файл")
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)


def submit_form():
    login = login_entry.get()
    password = password_entry.get()
    file_path = file_entry.get()

    facebook_urls = get_urls(file_path)

    driver = initialize_authorization(
        login, password, "https://www.facebook.com/login/"
    )
    counts, times, urls, status = parse(facebook_urls, driver)
    to_excel(urls, counts, times, status)
    driver.close()
    driver.quit()

    messagebox.showinfo("Success", "Successful Parsing")


MONTH_MAPPING = {
    "январь": 1,
    "февраль": 2,
    "март": 3,
    "апрель": 4,
    "май": 5,
    "июнь": 6,
    "июль": 7,
    "август": 8,
    "сентябрь": 9,
    "октябрь": 10,
    "ноябрь": 11,
    "декабрь": 12,
}


def parse_russian_date(timee):
    parts = timee.split()
    day = int(parts[1])
    month = MONTH_MAPPING[parts[2].lower()]
    year = int(parts[3])
    time = parts[6]

    date_string = f"{day:02d}-{month:02d}-{year} {time}"
    return datetime.strptime(date_string, "%d-%m-%Y %H:%M")


def get_urls(string):
    urls = []
    with open(string, "r", encoding="utf-8") as file:
        for stroka in file:
            urls.append(stroka.strip())
    return urls


def initialize_authorization(username, password, target_url):
    options = webdriver.ChromeOptions()
    options.add_argument("disable-notifications")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors")

    driver = webdriver.Chrome(options=options)

    driver.maximize_window()

    driver.get(target_url)

    driver.find_elements(
        By.XPATH, "//button[contains(string(), 'Разрешить все cookie')]"
    )[0].click()

    username_box = driver.find_element(By.ID, "email")
    username_box.send_keys(username)

    password_box = driver.find_element(By.ID, "pass")
    password_box.send_keys(password)

    login_box = driver.find_element(By.NAME, "login")
    login_box.click()

    time.sleep(2)
    return driver


def parse(facebook_urls, driver):
    counts = []
    times = []
    urls = []
    status = []
    for i in range(len(facebook_urls)):
        try:
            driver.get(facebook_urls[i])

            closed_open = driver.find_element(
                By.CSS_SELECTOR,
                ".x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lkfr7t.x1lbecb7.xk50ysn.xzsf02u",
            ).text

            if closed_open == "Закрытая":
                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")

                count = str(
                    soup.find(
                        "a",
                        class_="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f",
                    ).text.split(" ")[0]
                )

                try:
                    timee = str(
                        soup.find(
                            "span",
                            class_="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1nxh6w3 x1sibtaa xo1l8bm xzsf02u x1yc453h",
                        ).text
                    )

                    timee = parse_russian_date(timee)
                except:
                    timee = "-"

                if "тыс." in count:
                    count = float(count.replace("тыс.", "").replace(",", ".")) * 1000

                counts.append(count)
                times.append(timee)
                urls.append(facebook_urls[i])
                status.append("closed")

            else:
                actions = ActionChains(driver)
                mouse_over = driver.find_element(
                    By.CSS_SELECTOR,
                    ".x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xt0b8zv.xo1l8bm",
                )

                actions.move_to_element(mouse_over).perform()

                time.sleep(1)

                html = driver.page_source
                soup = BeautifulSoup(html, "lxml")

                count = str(
                    soup.find(
                        "a",
                        class_="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f",
                    ).text.split(" ")[0]
                )

                if "тыс." in count:
                    count = float(count.replace("тыс.", "").replace(",", ".")) * 1000

                timee = str(
                    soup.find(
                        "span",
                        class_="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1nxh6w3 x1sibtaa xo1l8bm xzsf02u x1yc453h",
                    ).text
                )

                timee = parse_russian_date(timee)

                counts.append(count)
                times.append(timee)
                urls.append(facebook_urls[i])
                status.append("open")
        except:
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")

            count = str(
                soup.find(
                    "a",
                    class_="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xi81zsa x1s688f",
                ).text.split(" ")[0]
            )
            if "тыс." in count:
                count = float(count.replace("тыс.", "").replace(",", ".")) * 1000
            counts.append(count)
            times.append("-")
            urls.append(facebook_urls[i])
            status.append("closed")
            continue
        finally:
            processed_var.set(f"[+] Processed: {i+1}/{len(facebook_urls)}")
            root.update()
    return (counts, times, urls, status)


def to_excel(urls, counts, times, status):
    parse_dict = {"url": urls, "followers": counts, "date": times, "status": status}
    data_frame = pd.DataFrame(parse_dict)

    data_frame.to_excel("excel.xlsx")


root = tk.Tk()
root.title("Программа с интерфейсом Tkinter")

# Создаем и размещаем виджеты
file_label = tk.Label(root, text="Файл:")
file_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

file_entry = tk.Entry(root, width=40)
file_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=2, sticky=tk.W)

browse_button = tk.Button(root, text="Обзор", command=open_file)
browse_button.grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)

login_label = tk.Label(root, text="Логин:")
login_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

login_entry = tk.Entry(root, width=40)
login_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=3, sticky=tk.W)

password_label = tk.Label(root, text="Пароль:")
password_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

password_entry = tk.Entry(root, show="*", width=40)
password_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=3, sticky=tk.W)

processed_var = tk.StringVar()
processed_var.set("[+] Processed: 0/0")

processed_label = tk.Label(root, textvariable=processed_var)
processed_label.grid(row=3, column=0, columnspan=4, pady=10)

submit_button = tk.Button(root, text="Отправить", command=submit_form)
submit_button.grid(row=4, column=0, columnspan=4, pady=20)

# Запускаем главный цикл обработки событий
root.mainloop()
