"""Send a daily witchy email to Emily"""

from datetime import datetime, date
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
        self._today = date.today()
        self._moon_type = None
        self.days = None

    def when(self) -> None:
        """Figure out when"""
        current_row = self._csv[self._csv["Month"] == self._today.strftime("%B")]
        next_moon = datetime.strptime(
            current_row["Date"].values[0],
            r"%m/%d/%Y",
        ).date()
        time_between = next_moon - self._today
        if time_between.days < 0:
            correct_row = self._csv.iloc[current_row.index.astype(int) + 1]
            next_moon = datetime.strptime(
                correct_row["Date"].values[0], r"%m/%d/%Y"
            ).date()
            time_between = next_moon - self._today
        self.days = time_between.days
        return self

    def __call__(self) -> str:
        if self.days == 0:
            self._moon_type = self._csv[
                self._csv["Month"] == self._today.strftime("%B")
            ]["Name"].values[0]
            return "\U0001F315   CHECK IT OUT. The '{self._moon_type}' is out tonight!   \U0001F315"
        if self.days == 1:
            return "\U0001F391   There will be a full moon tomorrow   \U0001F391"
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
        self._contents = f"Dearest Emily,\n\n{contents}\n\nLove,\n   Stefan\n"

    def send_email(self) -> None:
        """Send the actual email"""
        yag = yagmail.SMTP(self._sender, oauth2_file=path.joinpath("credentials.json"))
        yag.send(to=self._recipient, subject=self._subject, contents=self._contents)

    def __str__(self) -> str:
        summary = (
            f"From : {self._sender}\n"
            + f"To : {self._recipient}\n\n"
            + f"Subject : {self._subject}\n\n"
            + f"Body : {self._contents}"
        )
        return summary


class Scheduler(threading.Thread):
    """When should the email be sent"""

    def __init__(self) -> None:
        super().__init__()
        self.__stop_running = threading.Event()

    def schedule_daily(self, job):
        """Set the email time"""
        schedule.clear()
        schedule.every().day.at("06:30").do(job)

    def run(self):
        """Send the email at the established time"""
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

    body = f"{daily_horoscope()}\n\n{upcoming_moon()}"
    email = Email(contents=body)
    print(email)
    # scheduler = Scheduler()
    # scheduler.start()
    # scheduler.schedule_daily(email.send_email)
    # scheduler.run()
