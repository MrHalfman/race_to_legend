from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
import settings
import trackopy
import time

accounts = {}
for nickname, acc in settings.trackobot_accounts.items():
  accounts[nickname] = trackopy.Trackobot(acc[0], acc[1])

classes = ["druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior"]
out_file = open(settings.OUTPUT_FILE, "wb")
env = Environment(loader=FileSystemLoader("."))

while True:
  print("Updating stats...")
  now = datetime.now()
  next_refresh = now + timedelta(seconds = settings.REFRESH_TIME)
  stats = []
  classes_stats = []

  for name, acc in accounts.items():
    history = acc.history(query="ranked")
    rank = 25
    for hist in history.get("history"):
      if hist.get("rank") != None:
        rank = hist.get("rank")
        break

    stats.append((
      name,
      acc.stats(time_range="current_month", mode="ranked").get("stats"),
      rank,
      acc.stats(time_range="current_month", mode="ranked", stats_type="classes").get("stats")
    ))

  template = env.get_template("template.html")
  output = template.render(stats=stats, now=now, classes=classes, next_refresh=next_refresh)

  out_file.truncate(0)
  out_file.write(bytes(output, "UTF-8"))
  print("Stats updated!")

  time.sleep(settings.REFRESH_TIME)
