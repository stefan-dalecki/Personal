import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path
import yagmail

ordinal = lambda n: "%d%s" % (
    n,
    "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
)


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

    def __call__(self) -> str:
        return self.text


class NextMoon:
    def __init__(self, csv: str) -> None:
        self._csv = pd.read_csv(csv)
        self._today = datetime.now()
        self.days = None

    def when(self) -> None:
        next_moon = datetime.strptime(
            self._csv[self._csv["Month"] == self._today.strftime("%B")]["Date"].values[
                0
            ],
            r"%m/%d/%Y",
        )
        time_between = self._today - next_moon
        self.days = time_between.days
        return self

    def __call__(self) -> str:
        if self.days == 0:
            return "CHECK IT OUT. There's a full moon today!"
        elif self.days == 1:
            return "There will be a full moon tomorrow"
        else:
            return f"{self.days} days until next full moon"


class Email:
    def __init__(
        self,
        *,
        contents: str,
        attachments: str = None,
    ) -> None:
        self._sender = "my email"
        self._recipient = "emfekk@aol.com"
        intro = "Emily's Daily Witchy Email --- " + datetime.today().strftime("%B %d")
        day = ordinal(int(intro[-2:]))
        self._subject = intro[:-2] + day
        self._contents = f"Dearest Emily,\n\n{contents}"
        self._attachments = attachments

    def send_email(self) -> None:
        yag = yagmail.SMTP(self._sender)
        yag.send(
            to=self._recipient,
            subject=self._subject,
            contents=self._contents,
            attachments=self._attachments,
        )

    def __str__(self) -> str:
        summary = (
            f"From : {self._sender}\n"
            + f"To : {self._recipient}\n\n"
            + f"Subject : {self._subject}\n\n"
            + f"Body : {self._contents}\n\n"
            + "Love,\n   Stefan\n"
        )
        return summary


path = Path.cwd()

site = r"https://www.astrology.com/horoscope/daily/pisces.html"
daily_horoscope = Horoscope(site).get_text()

moon_csv = path.joinpath(r"full_moons.csv")
upcoming_moon = NextMoon(moon_csv).when()

body = f"{daily_horoscope()}\n\n{upcoming_moon()}"
email = Email(contents=body)
print(email)
