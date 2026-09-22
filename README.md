# Kamuganguzi Janan Luwum Memorial Senior Secondary School — Web Portal

A professional Django-based school website and admissions portal for JLMSSS, Uganda.

## 🌐 Live Sites
- **Main School Website**: [jananluwummemorialsss.sc.ug](https://jananluwummemorialsss.sc.ug)
- **Admissions Portal**: [admission.jananluwummemorialsss.sc.ug](https://admission.jananluwummemorialsss.sc.ug)

## ✨ Features

### Main Website
- School home page with news, events, gallery, academics
- Staff profiles, contact form, helpdesk
- Django admin with Jazzmin theme

### Admissions Portal (Sub-domain)
- Full applicant account registration with **email verification**
- Multi-step application form with **auto-save drafts**
- Document upload engine (drag-and-drop, multi-format)
- **Multiple children** under one parent/guardian account
- Payment reference submission (MTN/Airtel/Bank)
- Real-time status tracking with email notifications
- Staff review portal (approve/flag documents, change status, generate PDF offer letters)
- Audit logging and notification logs

## 🏗 Tech Stack
- **Backend**: Django 6.1 (Python 3.12)
- **Database**: SQLite (development) / PostgreSQL-compatible (production)
- **Email**: Gmail SMTP with App Password
- **PDF Generation**: ReportLab
- **Admin Theme**: Jazzmin
- **Frontend**: Bootstrap 5 + Font Awesome 6

## 🚀 Local Setup
```bash
git clone https://github.com/twiinarides/jlmsss-school-portal.git
cd jlmsss-school-portal
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Access:
- Main site: `http://localhost:8000/`
- Admissions portal: `http://127.0.0.1:8000/`

## 📁 Project Structure
```
Janun_Luwum/           ← Django project root
├── school_website/    ← Main settings & URL conf
├── school/            ← Main school website app
├── admissions/        ← Admissions portal app (subdomain)
│   ├── models.py      ← Full data schema
│   ├── views.py       ← All portal views
│   ├── forms.py       ← Django forms
│   ├── admin.py       ← Rich admin config
│   ├── middleware.py  ← Subdomain routing
│   ├── email_utils.py ← Transactional emails
│   └── pdf_utils.py   ← Offer letters & receipts
├── templates/         ← HTML templates
│   ├── admissions/    ← Portal templates
│   └── school/        ← Main site templates
└── manage.py
```

---
*Maintained by JLMSSS ICT Department*
