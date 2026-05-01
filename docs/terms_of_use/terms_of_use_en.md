# Terms of Use — DivePlanWeb

**Version:** 2.1
**Last updated:** March 9, 2026


## 1. About the Application

**DivePlanWeb** is a non-commercial, open-source web application developed as part of
a diploma thesis. It is designed for recording, analyzing, and planning scuba dives.

The application is provided **free of charge** and is not commercial in nature.
It is not officially affiliated with any manufacturer of diving equipment or software
(e.g., Suunto, Garmin, Subsurface, etc.).
The web application is designed to run on Microsoft Azure cloud services and local hosting.


## 2. Acceptance of Terms

By registering or using the application, the user agrees to these Terms of Use.
If you do not agree with these terms, please do not use the application.


## 3. Purpose and Scope of Use

The application is intended for **personal, educational, and non-commercial use**.

DivePlanWeb provides:
- User registration and login
- Dive recording and analysis (logbook)
- Dive planning with decompression, CNS%, OTU, and gas consumption calculations
- Statistics and summaries
- Equipment management and service records
- User account and role management (RBAC) — for administrators


## 4. Fictitious and Invented Personal Data

The application can be fully used **without providing real personal information**.
Users may register and use the application with invented or test data
(a nickname, a fictional email address, made-up names and dive records).

Users are responsible for the data they enter into the application. The project author is not responsible for user-submitted content.


## 5. Registration, Login, and Account Security

- Registration requires only a username and password (all other fields are optional)
- Passwords are **never stored in plaintext** — secure hashing is used (pbkdf2:sha256)
- Upon login, the system issues a **JWT access token** and **refresh token**
- The access token has a limited lifespan (approximately 15 minutes)
- The refresh token is used to renew access without re-entering credentials
- The application supports a **token blacklist** — tokens are revoked on logout or password change
- Data access is controlled by **user roles**: standard user, administrator
- Users are responsible for protecting their credentials and securing their devices


## 6. Prohibited Use

Users agree not to:

- Use the application for unlawful purposes
- Upload or process copyrighted content without authorization
- Attempt unauthorized access to other users' accounts or the system
- Intentionally disrupt the operation of the application (DoS attacks, exploiting vulnerabilities)
- Impersonate any other person or entity


## 7. Dive Calculations and Planning

The results of calculators, planning algorithms, and NDL/decompression tables
are for **informational purposes only**.

Users acknowledge that:
- Calculations are approximations — actual conditions may differ
- Results **cannot replace certified diver training**
- Every real dive plan must be verified with a qualified instructor
- The project author bears no responsibility for damages resulting from the use
  of the application's results in real diving situations


## 8. Warranties and Liability

The application is provided **"as is"** without warranties of any kind.

The author **assumes no responsibility** for:
- Errors, outages, or data loss
- Incorrect calculations caused by erroneous input data
- Damages arising from the use or inability to use the application
- Content, data, and files submitted by users

Users use the application **at their own risk**.


## 9. Intellectual Property

- All source code, designs, and documentation of DivePlanWeb are the work of the author
- The project is published as open-source under the **MIT License** (source code)
  and **Creative Commons Attribution 4.0** (documentation)
- Users may study, copy, and modify the code for non-commercial purposes in accordance
  with the MIT License terms
- Logos and names of third parties (Suunto, Garmin, etc.) are trademarks of their
  respective owners and are not part of this project


## 10. Privacy

The processing of personal data is described separately in the:
[**Privacy Policy**](privacy_policy_en.md)


## 11. Changes to Terms

The author reserves the right to modify these Terms at any time.
The date of the last revision is shown in the document header.
Continued use of the application after a change to the Terms constitutes acceptance
of the new version.


## 12. Governing Law

These Terms are governed by the laws of the **Czech Republic**.


## 13. Contact

**DivePlanWeb project author:**
Jan Hronek


*This document does not constitute legal advice. Legal consultation with an expert
in internet law and GDPR is recommended for any commercial deployment of the project.*
