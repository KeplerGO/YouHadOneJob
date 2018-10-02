"""Merges metadata of K2 observing programs into a single csv table.

The output table contains the following fields:
program_id
pi_first_name
pi_middle_name
pi_last_name
pi_institution
pi_email
coi_names
title
summary
"""
import pandas as pd
import re


DESIRED_COLUMNS = ['program_id', 'campaign',
                   'pi_first_name', 'pi_middle_name', 'pi_last_name',
                   'pi_institution', 'pi_email', 'title', 'summary']


def cleanup_summary(summary):
    """Make a proposal summary suitable for the web."""
    # Some abstracts contain control characters, remove these
    summary = summary.translate(dict.fromkeys(range(14, 32)))
    # Also remove excessive whitespace
    summary = summary.replace("\n\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
    # Only allow two whitespaces after a period
    summary = re.sub("(?<!\.)(\n\n)", " ", summary)
    # ... unless it's a numeric listing
    summary = re.sub("(\n\n)(\d)", "\n\\2", summary)
    return summary


def parse_excel_file(filename, campaign):
    """Returns a dataframe."""
    df = pd.read_excel(filename)
    df.loc[:, 'campaign'] = int(campaign)
    df = df[~df["Response seq number"].isnull()]

    newtable = df[["Response seq number", "campaign", "PI First name", "PI Middle name", "PI Last name", "Company name", "Email", "Title", "Summary"]].copy()
    newtable.columns = DESIRED_COLUMNS

    # Reformat proposal id
    for rowidx in newtable.index:
        newtable.loc[rowidx, "program_id"] = 'GO{}{:03d}'.format(campaign, int(newtable.loc[rowidx, "program_id"]))

    # Clean up PI institution names
    newtable['pi_institution'].fillna('', inplace=True)
    for rowidx in newtable.index:
        if newtable.loc[rowidx, "pi_institution"] == "":
            newtable.loc[rowidx, "pi_institution"] = df["Linked Org"].fillna('')[rowidx]
        # In early K2 days proposals for foreign PIs listed BAERI as institute
        if newtable.loc[rowidx, "pi_institution"].startswith("Bay Area"):
            newtable.loc[rowidx, "pi_institution"] = ""

    # Add a column with the co-investigator names separated by semi-colons
    if 'coi_names' in df.columns:
        newtable['coi_names'] = df['coi_names']
    else:
        newtable['coi_names'] = None
        for rowidx in newtable.index:
            co_investigators = []
            for idx in range(1, 99):  # Number of "Member" columns is variable
                try:
                    field = df.loc[rowidx]["Member - {} Member name; Role; Email; Organization; Phone".format(idx)]
                    if field != "" and not pd.isnull(field):
                        co_investigators.append(field.split(";")[0].strip())
                except KeyError:
                    continue  # Max number of "Member" columns reached
            newtable.loc[rowidx, 'coi_names'] = "; ".join(co_investigators)

    # Remove unwanted characters from the proposal summaries
    newtable['summary'].fillna('', inplace=True)
    for rowidx in newtable.index:
        newtable.loc[rowidx, 'summary'] = cleanup_summary(newtable.loc[rowidx, 'summary'])

    return newtable


def parse_file(filename, campaign):
    if filename.endswith('xls'):
        df = parse_excel_file(filename, campaign)
    else:
        df = pd.read_csv(filename)
        if campaign != 'ddt':
            df.loc[:, 'campaign'] = int(campaign)
    return df


if __name__ == '__main__':
    campaigns = {'0': 'input/k2-c0-programs.csv',
                 '1': 'input/k2-c1-programs.csv',
                 '2': 'input/k2-c2-programs.csv',
                 '3': 'input/k2-c3-programs.csv',
                 '4': 'input/K2GO1_programs_geert_edit.xls',
                 '5': 'input/K2GO1_programs_geert_edit.xls',
                 '6': 'input/K2GO2_1 Updated Investigation Report 1_28.xls',
                 '7': 'input/K2GO2_1 Updated Investigation Report 1_28.xls',
                 '8': 'input/K2GO3_2 Investigation Report.xls',
                 '9': 'input/k2-c9-programs.csv',
                 '10': 'input/K2GO3_2 Investigation Report.xls',
                 '11': 'input/K2GO4 Step 2 Investigation Report.xls',
                 '12': 'input/K2GO4 Step 2 Investigation Report.xls',
                 '13': 'input/K2GO4 Step 2 Investigation Report.xls',
                 '14': 'input/K2GO5 Step 2 Investigation Report.xls',
                 '15': 'input/K2GO5 Step 2 Investigation Report.xls',
                 '16': 'input/K2GO5 Step 2 Investigation Report.xls',
                 '17': 'input/k2go6-proposals-with-rank.xls',
                 '18': 'input/k2go6-proposals-with-rank.xls',
                 '19': 'input/k2go6-proposals-with-rank.xls',
                 '20': 'input/K2GO7.csv',
                 'ddt': 'input/k2-ddt-programs.csv'}
    programs = [parse_file(filename, campaign)
                for campaign, filename in campaigns.items()]
    df = pd.concat(programs).sort_values(["campaign", "program_id"])
    df[DESIRED_COLUMNS].to_csv('k2-programs.csv', index=False)
    df[DESIRED_COLUMNS].to_excel('k2-programs.xls', index=False)
