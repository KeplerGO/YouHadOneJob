"""Prepare e-mails to send PIs to remind them of targets allocated."""
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import pandas as pd

campaign = 8

j2env = Environment(loader=FileSystemLoader("."))

observed_programs = pd.read_csv("/home/gb/dev/KeplerScienceWebsite/content/pages/"
                                "k2-observing/approved-programs/programlist-c{}.txt".format(campaign))
programs = pd.read_csv('k2-programs.csv')
df = pd.merge(observed_programs, programs)
grouped = df.groupby("pi_email")

for programgroup in grouped:
    pi_email = programgroup[0]
    pi_name = programgroup[1]['pi_last_name'].iloc[0]

    email = j2env.get_template('email-template.txt').render(
                pi_email=pi_email,
                pi_name=pi_name,
                programs=programgroup[1],
                campaign=campaign
                )
    with open("output/for-{}".format(pi_email), "w") as out:
        out.write(email)
        out.close()
