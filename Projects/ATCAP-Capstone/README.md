# ATCAP Home Healthcare Solutions: Senior Capstone

Team project (M&T Solutions, Team 5) for the George Mason University IT capstone, completed over two semesters (Aug 2025 to May 2026). I was the team lead on a five-person team.

Live site: https://www.atcaphomehealthcare.com/

## The client

ATCAP Home Healthcare Solutions is a home health care agency in Woodbridge, VA, founded in 2013 by a nurse. It assigns nurses to care for homebound people and has 31 employees: 4 in the office and 27 nurses.

## The business problems

| Area | Problem before the project |
|---|---|
| Website | The WordPress site often returned a fatal error, with about 25% uptime. Visitors who hit the error had to call the office to learn more, and a receptionist spent up to about 60 minutes of phone time on those calls. |
| Job applications | Applicants had to email a resume or walk in and fill out a form. There was no structured way to apply. |
| Application review | The owner reviewed applications by hand, one email at a time. The process was repetitive and made it easy to miss new talent. |

## What we delivered

1. **A reliable website.** We moved the site to Squarespace.
2. **A structured job application form** on the website. Applications arrive in the same format, which makes them quicker to review.
3. **An automated review process.** A Python script pulls application data from Google Sheets, sorts applications by position, and generates structured application documents the owner can open and review.

## How it helped the business

Figures are from our final presentation. Where noted they are estimates.

| Measure | Before | After |
|---|---|---|
| Website uptime | ~25% | ~99.9% (based on Squarespace uptime logs) |
| Website monthly cost | $248.33 (hosting plus the phone time spent on website-error calls) | $23.00 |
| Time on website-error calls | up to ~60 minutes | none, so the receptionist can spend it on other work |
| Application intake | unstructured email, about 1 minute each | structured web form, about 0.5 minutes |
| Application review | ~35 minutes per review | ~30 minutes per review (estimated from a review of two applications) |

The new site also improved search visibility, and the application system is reachable around the clock.

## Security

- Input validation on the form to reduce the risk of invalid data or malicious input
- HTTPS encryption and SSL certificate verification between visitors and the site
- User authentication, with multi-factor authentication as an added layer

## Testing and rollout

- **Alpha, Beta, and UAT testing.** Alpha testing found a link failure that was documented, fixed, and retested. In Beta every link passed, and the sponsor confirmed navigation in UAT.
- **A script failure found in UAT.** It came from an environment dependency: Python had to be installed on the office computer. We installed it, re-ran the script successfully, and the sponsor confirmed the result.
- **Training.** We ran a training session and provided training materials so the owner can run the process independently.

## My role: Team Lead

The team had five roles: Team Lead (me), Verification and Validation Manager, Documentation and Training Manager, Data Manager, and Time and Product Manager.

As team lead I:

- Led the team and managed the project across two semesters, including pivots in scope and approach.
- Was the main point of contact with the sponsor, running the meetings and keeping her needs at the center of the work.
- Presented the original business process analysis for the final presentation: the sponsor and company background, how the website, job application, and application review processes worked before, and how each was measured in time and cost.
- Defined the areas for improvement we targeted: less website downtime, a structured application process, and automated application data processing.
- Presented the overview of the technical solutions for the website, the job application process, and application review.

## Skills used

Team leadership, stakeholder communication, business process analysis, cost and time quantification, project management, Python, web form and website platforms, security controls (HTTPS, input validation, MFA)
