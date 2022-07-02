"""Send a daily witchy email to Emily"""

from datetime import datetime
import threading
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yagmail
import schedule

ordinal = lambda n: "%d%s" % (
    n,
    "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
)


class Horoscope:
    """A daily pisces horoscope"""

    def __init__(self, website: str) -> None:
        self._request = requests.get(website)
        self.text = ""

    def get_text(self):
        """Get the horoscope text from the internet

        Returns:
            object: self
        """
        soup = BeautifulSoup(self._request.content, "html.parser")
        s = soup.find("div", class_="horoscope-content-wrapper")
        content = s.find_all("p")
        for line in content:
            self.text += f"{line.text} "
        return self

    def __call__(self) -> str:
        return self.text


class NextMoon:
    """When is the next full moon?"""

    def __init__(self, csv: str) -> None:
        self._csv = pd.read_csv(csv)
        self._today = datetime.now()
        self.days = None

    def when(self) -> None:
        """Figure out when"""
        next_moon = datetime.strptime(
            self._csv[self._csv["Month"] == self._today.strftime("%B")]["Date"].values[
                0
            ],
            r"%m/%d/%Y",
        )
        time_between = self._today - next_moon
        self.days = abs(time_between.days)
        return self

    def __call__(self) -> str:
        if self.days == 0:
            return "\U0001F315   CHECK IT OUT. There's a full moon today!   \U0001F315"
        if self.days == 1:
            return "\U0001F391   There will be a full moon tomorrow   \U0001F391"
        else:
            return f"\U00002653   {self.days} days until next full moon   \U00002653"


class Email:
    """Send an email to Emily"""

    def __init__(
        self,
        *,
        contents: str,
    ) -> None:
        self._sender = "dailynuggetnews@gmail.com"
        self._recipient = "sjdalecki@gmail.com"
        intro = "Emily's Daily Witchy Email --- " + datetime.today().strftime("%B %d")
        day = ordinal(int(intro[-2:]))
        self._subject = intro[:-2] + day
        self._contents = f"Dearest Emily,\n\n{contents}"

    def send_email(self) -> None:
        """Send the actual email"""
        yag = yagmail.SMTP(self._sender, oauth2_file=path.joinpath("credentials.json"))
        yag.send(to=self._recipient, subject=self._subject, contents=self._contents)

    def __str__(self) -> str:
        summary = (
            f"From : {self._sender}\n"
            + f"To : {self._recipient}\n\n"
            + f"Subject : {self._subject}\n\n"
            + f"Body : {self._contents}\n\n"
            + "Love,\n   Stefan\n"
        )
        return summary


class Scheduler(threading.Thread):
    """When should the email be sent"""

    def __init__(self) -> None:
        super().__init__()
        self.__stop_running = threading.Event()

    def schedule_daily(self, job):
        """Send the email each day"""
        schedule.clear()
        schedule.every().day.at("16:12").do(job)

    def run(self):
        """Do the actual job"""
        self.__stop_running.clear()
        while not self.__stop_running.is_set():
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """Stop doing the job"""
        self.__stop_running.set()


if __name__ == "__main__":
    path = Path.cwd()

    site = r"https://www.astrology.com/horoscope/daily/pisces.html"
    daily_horoscope = Horoscope(site).get_text()

    moon_csv = path.joinpath(r"full_moons.csv")
    upcoming_moon = NextMoon(moon_csv).when()

    body = f"{daily_horoscope()}\n\n{upcoming_moon()}\nLove,\n   Stefan"
    email = Email(contents=body)

    scheduler = Scheduler()
    scheduler.start()
    scheduler.schedule_daily(email.send_email)
    scheduler.run()
