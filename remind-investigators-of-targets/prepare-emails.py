"""Prepare e-mails to send PIs to remind them of targets allocated."""
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
import pandas as pd

j2env = Environment(loader=FileSystemLoader("."))

programs = pd.read_csv("pi-contact-details.csv")
grouped = programs.groupby("pi_email")

for programgroup in grouped:
    pi_email = programgroup[0]
    pi_name = programgroup[1]['pi_name'].iloc[0]

    email = j2env.get_template('email-template.txt').render(
                pi_email=pi_email,
                pi_name=pi_name,
                programs=programgroup[1]
                )
    with open("output/email-for-{}.txt".format(pi_email), "w") as out:
        out.write(email)
        out.close()
