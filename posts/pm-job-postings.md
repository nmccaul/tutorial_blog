---
title: "What Do Tech Companies Want From Product Managers? A Dataset of 482 Job Postings"
---

# What Do Tech Companies Want From Product Managers? A Dataset of 482 Job Postings

*Nathan McCauley · STAT 386 · November 2026*

I'm co-president of BYU's Product Management Association, and our members want to know what skills to build before they apply for PM jobs. Job postings are the most direct record of what companies actually ask for, so I built a dataset of them.

## The question

What do tech companies ask for in product manager job postings right now? I broke that into three parts:

- How many PM postings ask for AI skills?
- How much do postings push technical skills (SQL, coding, a CS degree) compared to soft skills (communication, leadership, collaboration)?
- How do pay and skill requirements change from entry-level to senior roles?

## Where the data comes from

A lot of tech companies run their careers pages on [Greenhouse](https://www.greenhouse.com/), and Greenhouse has a public [Job Board API](https://developers.greenhouse.io/job-board.html) that returns every open job on a company's board. You don't need a key. One request gets you every posting with its title, location, department, date and full description:

```python
import requests

url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
jobs = requests.get(url, params={"content": "true"}).json()["jobs"]
```

The part of the URL after `/boards/` is the company's board name, which is usually just the company name. You can find it by going to a company's careers page and clicking on a job: if the link goes to `job-boards.greenhouse.io/<name>`, that company uses Greenhouse.

## Is this allowed?

Before collecting anything, I checked a few things:

- The API is public and built so companies can show their listings on other sites. It doesn't require an account or key.
- The API's [robots.txt](https://boards-api.greenhouse.io/robots.txt) only blocks `/embed/`, not the job board endpoints.
- I waited one second between requests, sent a User-Agent that says it's a class project, and saved each company's response so I'd only request it once.
- Some postings name a recruiter, and the descriptions are the companies' own writing, so I don't publish the description text. Each row links to the original posting instead.

## How I built the dataset

If you want to do something similar, here's the process in four steps.

1. Find companies. I tried about 110 board names and kept the 54 that returned at least one PM posting. I made a small table with each company's industry.
2. Download each board once with `requests` and save the JSON (`collect.py` in the repo).
3. Keep the PM jobs. I kept titles matching `product manag`, `product owner` or `associate product manager`. My first version also matched "APM," but that pulled in an engineering job at Elastic, since APM also means "application performance monitoring."
4. Turn text into columns (`clean.py`). The descriptions come back as HTML, so I used BeautifulSoup to get plain text and then regular expressions to pull out pay ranges, years of experience, seniority from the title, and yes/no flags for 11 skills and for AI.

Here's what steps 3 and 4 look like for one board, using `jobs` from the request above. The filter is one regex on the title:

```python
import re

pm = re.compile(r"product manag|product owner|associate product manager", re.I)
pm_jobs = [j for j in jobs if pm.search(j["title"])]
```

Then each feature is a search on the description text. For example, the pay range:

```python
import html
from bs4 import BeautifulSoup

job = pm_jobs[0]
text = BeautifulSoup(html.unescape(job["content"]), "html.parser").get_text(" ")
pay = re.search(r"\$([\d,]+)\s*[-–—]\s*\$([\d,]+)", text)
if pay:
    low, high = (int(x.replace(",", "")) for x in pay.groups())
```

Not every posting lists pay (Stripe's don't, for example), so check for a match before using it.

The most useful trick was searching only the requirements section of each posting ("What you bring," "Qualifications," and so on) instead of the whole thing. Otherwise a posting at an AI company counts as "asking for AI" just because the "About us" paragraph says the company builds AI. 84% of postings mention AI somewhere, but only 58% mention it in the requirements.

This doesn't work for every posting, though. 60 postings (12%) don't have a section I could find, so for those I fall back to searching the full text. That brings the "About us" problem back: 90% of those 60 get flagged for AI, compared to 53% of postings where I did find a requirements section. So the 58% is probably a little high. Counting only postings with a requirements section, it's 53%.

Check your regexes by reading real postings. I only caught that "intern" was matching "Internal" (labeling a Staff PM role as an internship) by doing that.

## The final dataset

The dataset has 482 postings from 54 companies and 33 columns, pulled on November 6, 2026.

| Level | Postings | Median years of experience | Median listed pay* |
| --- | ---: | ---: | ---: |
| Intern / Associate | 17 | 1.5 | $142k |
| Product Manager | 96 | 5 | $236k |
| Senior | 150 | 5 | $194k |
| Staff / Principal | 153 | 8 | $248k |
| Group / Manager | 34 | 8 | $265k |
| Director+ | 32 | 10 | $310k |

*Midpoint of the listed annual base pay range. Only 2 of the intern/associate postings list annual pay.

Level comes from the job title. "Product Manager" means the title had no level in it (no "Senior," "Staff," etc.), so it also includes senior roles at companies that don't put levels in their titles.

- Industries: Fintech (124), Data & AI (113), Consumer (68), Software & dev tools (65), Security & infrastructure (53), Gaming (38), other (21)
- Work mode: 122 remote, 137 hybrid, 223 onsite or not stated
- 73% of postings are in the US. 63% list annual pay, and 79% list a number of years of experience.
- For the 303 postings with annual pay, the midpoint of the range has a median of $224k, and the middle half falls between $193k and $265k.
- Years of experience asked for ranges from 0 to 15, with a median of 6.

## What I found

### Soft skills show up more than technical ones

![Horizontal bar chart of the share of PM postings that mention each skill in their requirements. Collaboration 61%, stakeholders 59%, communication 58%, data and analytics 58%, leadership 49%, APIs 27%, customer empathy 24%, CS or engineering degree 24%, technical background 22%, SQL 10%, coding 9%.](images/skill_frequency.png)

The top three are all soft skills, and 60% of postings mention more soft skills than technical ones. The one technical skill that keeps up is working with data: analytics, metrics and running experiments show up in 58% of postings. Hands-on technical skills are rare. Only 10% mention SQL and 9% mention coding, and only 24% ask for a CS or engineering degree.

The mix changes with level. Intern and associate postings are the only level that lists more technical skills than soft ones on average (2.0 vs 1.9). Directors list the fewest technical skills (1.1) and the most soft skills (2.7).

### AI is in most postings, but mostly mid-level

![Grouped bar chart of AI in requirements by level. The share asking for AI knowledge is 47% for intern/associate, 55% for PM, 59% for senior, 62% for staff/principal, 59% for group/manager, and 38% for director+. The share asking candidates to use AI tools themselves is between 18% and 33% at every level.](images/ai_by_level.png)

58% of postings ask for AI knowledge or experience in the requirements, and 28% go further and ask that you use AI tools in your own work (things like "use AI tools in your workflow" or naming tools like Cursor or Claude). Director postings ask about AI the least. Industry matters more than level: 78% of software and dev tools postings ask for AI, compared to 21% of gaming postings.

### Entry-level PM jobs are rare

Only 17 of 482 postings (4%) are internships, associate PM or new grad roles, and 11 of those are from just two companies (Databricks and Cloudflare).

### Pay rises with level, but titles don't line up across companies

![Box plots of the midpoint of listed annual base pay by level. Medians are about $236k for product manager, $194k for senior, $248k for staff/principal, $265k for group/manager, and $310k for director+. The product manager box is very wide, from about $196k to $345k.](images/pay_by_level.png)

Pay mostly goes up with level, except that plain "Product Manager" has a higher median than "Senior" because of company mix. Anthropic titles all 16 of its PM roles just "Product Manager" and those have a median of $345k, while companies like Databricks use "Senior" a lot at lower pay. Titles aren't a clean measure of seniority.

Postings that ask for AI list more pay within most levels ($251k vs $225k for staff/principal), but that's also tangled up with which companies are hiring, so it doesn't show AI skills cause higher pay.

## Limitations

- The data only covers companies that use Greenhouse, which leans toward venture-backed tech companies, and only the jobs open on one day.
- Skill flags come from keyword searches, so some are wrong, and they can't tell "required" from "nice to have."
- 12% of postings have no requirements section I could find, so their flags come from the full text and are more likely to count company blurbs as requirements.
- Pay is mostly from US postings (81% of US postings list it, compared to 13% of non-US postings) because of state pay transparency laws.

## Links

- [Code and dataset on GitHub](https://github.com/nmccaul/pm-job-postings-dataset)
- [Greenhouse Job Board API documentation](https://developers.greenhouse.io/job-board.html)
- [Lever's postings API](https://github.com/lever/postings-api), a similar public API if you want more companies
- [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python regular expression HOWTO](https://docs.python.org/3/howto/regex.html)
