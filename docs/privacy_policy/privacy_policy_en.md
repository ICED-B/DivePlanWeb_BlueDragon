# Privacy Policy — DivePlanWeb

**Version:** 2.1
**Last updated:** March 9, 2026


## 1. Introduction

This Privacy Policy describes how the **DivePlanWeb** application handles information
entered by users.

DivePlanWeb is a **non-commercial, open-source web application** developed as part of
a diploma thesis. It is designed for recording, analyzing, and planning scuba dives,
and is provided free of charge.

The application is **not intended for commercial use**. The project author is an individual —
the creator of this diploma thesis.


## 2. Data Controller

The data controller is the **author of the DivePlanWeb project** (individual): **Jan Hronek**

This project is non-commercial and open-source. The web application is a standalone project
hosted locally or via Microsoft Azure cloud services. The author does not act as a commercial
entity or platform operator in the legal or business sense.


## 3. What Data the Application Collects

The application only stores data that the user voluntarily enters during registration
and use of the application:

### Registration and Profile Data
- **Username (login)** — required
- **Password** — stored exclusively as a secure hash (never in plaintext)
- **Email address** — optional
- **First and last name** — optional
- **Phone number** — optional

### Dive Records (entered by the user)
- Dive logs (date, depth, time, temperature, sites, notes)
- Equipment, cylinders, gas mix data
- Buddies, tags, certifications, devices
- Photographs and files (optional)

### Technical Data
- Audit records of administrator actions (not user behavioral tracking)
- Revoked JWT tokens (security blacklist)


## 4. Fictitious and Invented Data

Users are **not required to provide real personal information**.
The application can be fully used with invented or test data
(a nickname as login, a fictional email, made-up names, etc.).

The project author does not verify whether submitted data is real or fictitious.
Entered personal data may be fictitious, and users are solely responsible for the data they share.


## 5. Purpose of Data Processing

Data entered by the user is processed solely for the purpose of:

- Providing application features (dive logbook, planner, statistics)
- Verifying identity during login (authentication)
- Securing access to the user account

Data is **not** processed for commercial purposes, advertising, profiling,
or shared with third parties.


## 6. Consent to Data Processing

By registering and using the application, the user consents to the processing
of their submitted data to the extent and for the purposes described in this Policy.

The user acknowledges that:
- Providing personal information is **voluntary** — fictitious data may be used
- Submitted data may be stored on the operator's servers
- Upon account deletion, data may be removed or anonymized


## 7. Data Security

The application implements the following security measures:

- **Passwords** are stored as a secure hash (pbkdf2:sha256) — never in plaintext
- **JWT authentication** — access restricted to logged-in users with a valid token
- **Token blacklist** — token revocation upon logout or password change
- **RBAC** — access to data management based on user role (user / administrator)
- **Rate limiting** — protection against brute-force attacks
- **CORS policy** — restricting access from unauthorized domains
- **Input validation** — all submitted data is validated
- **Audit logging** — recording of administrator operations


## 8. Sharing Data with Third Parties

DivePlanWeb **does not share data with third parties** for advertising, marketing,
or sales purposes.

Data may technically be processed by cloud services used to operate the application
(Microsoft Azure — servers, database, storage). These services are contractually bound
to protect data in accordance with GDPR standards.

The application **does not use Google Analytics, Facebook Pixel, or similar tracking tools**.


## 9. Cookies and Tracking

DivePlanWeb **does not use analytical cookies or third-party tracking technologies**.

The application uses browser storage for technically necessary purposes only:
- **`sessionStorage`**: JWT tokens (login state) — data is cleared when the tab or browser is closed
- **`localStorage`**: theme and language preferences — data persists between sessions

This data is stored only in the user's browser and is not transmitted to third parties.


## 10. Data Retention

Data is retained for the duration of the user account.
Upon account deletion, data may be deleted or anonymized based on technical capabilities.

This project is academic in nature; stored data serves primarily academic research purposes.


## 11. Liability

The application is provided **"as is"** without warranties of any kind.

The author **assumes no responsibility** for:
- Data loss caused by technical error or outage
- Damage caused by improper use of planning calculations during actual diving
- Content submitted by users to the application

The results of calculators and planning algorithms are for **informational purposes only**
and cannot replace certified training or assessment by a qualified instructor.


## 12. Changes to This Policy

The author reserves the right to update this Policy at any time.
The date of the last update is shown in the document header.
Continued use of the application after a Policy change constitutes acceptance of the new version.


## 13. Contact

**DivePlanWeb project author:**
Jan Hronek


*This Policy is part of the open-source DivePlanWeb project — a diploma thesis.
It is not a legal document. Legal consultation is recommended for any commercial deployment.*
