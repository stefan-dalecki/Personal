import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path
import yagmail


class Horoscope:
    def __init__(self, website: str) -> None:
        self._request = requests.get(website)
        self.text = ""

    def get_text(self):
        soup = BeautifulSoup(self._request.content, "html.parser")
        s = soup.find("div", class_="horoscope-content-wrapper")
        content = s.find_all("p")
        for line in content:
            self.text += f"{line.text} "
        return self


class NextMoon:
    def __init__(self, csv: str) -> None:
        self._csv = pd.read_csv(csv)
        self._today = datetime.now()
        self.days = None

    def when(self):
        next_moon = datetime.strptime(
            self._csv[self._csv["Month"] == self._today.strftime("%B")]["Date"].values[
                0
            ],
            r"%m/%d/%Y",
        )
        time_between = self._today - next_moon
        self.days = time_between.days


class Email:
    def __init__(
        self,
        horoscope: str,
        until_next: int,
        *,
        contents: str,
        attachments: str = None,
    ) -> None:
        self.horoscope = horoscope
        self.until_next = until_next
        self._sender = "my email"
        self._recipient = "emfekk@aol.com"
        self._subject = "Emily's Daily Witchy Email ---" + datetime.today().strftime(
            "%B %d"
        )
        self._contents = contents
        self._attachments = attachments

    def send_email(self) -> None:
        yag = yagmail.SMTP(self._sender)
        yag.send(
            to=self._recipient,
            subject=self._subject,
            contents=self._contents,
            attachments=self._attachments,
        )


path = Path.cwd()

site = r"https://www.astrology.com/horoscope/daily/pisces.html"
daily_horoscope = Horoscope(site).get_text()

moon_csv = path.joinpath(r"full_moons.csv")
upcoming_moon = NextMoon(moon_csv).when()
