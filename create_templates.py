import os

base_dir = r"c:\Users\matsi\Desktop\Janun_Luwum_backup\Janun_Luwum\Janun_Luwum\templates\admissions"

directories = [
    "",
    "admin",
    "emails"
]

templates = {
    "base_admission.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JLMSSS Admissions Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary-blue: #0B1F3A; --secondary-blue: #D4AF37; }
        body { font-family: 'Poppins', sans-serif; background-color: #f8f9fa; }
        .adm-navbar { background-color: var(--primary-blue); }
        .adm-navbar .navbar-brand, .adm-navbar .nav-link { color: #fff !important; }
        .adm-card { border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .adm-btn-primary { background-color: var(--primary-blue); border-color: var(--primary-blue); color: #fff; }
        .adm-btn-primary:hover { background-color: #071529; border-color: #071529; color: #fff; }
        .adm-btn-gold { background-color: var(--secondary-blue); border-color: var(--secondary-blue); color: var(--primary-blue); font-weight: 600; }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg adm-navbar mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{% url 'admissions:landing' %}">JLMSSS Admissions</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#admNav">
                <span class="navbar-toggler-icon" style="filter: invert(1)"></span>
            </button>
            <div class="collapse navbar-collapse" id="admNav">
                <ul class="navbar-nav ms-auto">
                    {% if request.user.is_authenticated %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'admissions:dashboard' %}">Dashboard</a></li>
                        <li class="nav-item"><a class="nav-link" href="{% url 'admissions:logout' %}">Logout</a></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link" href="{% url 'admissions:login' %}">Login</a></li>
                        <li class="nav-item"><a class="nav-link btn adm-btn-gold ms-2 px-4" href="{% url 'admissions:register' %}">Apply Now</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mb-5">
        {% if messages %}
            {% for msg in messages %}
                <div class="alert alert-{{ msg.tags }}">{{ msg }}</div>
            {% endfor %}
        {% endif %}
        {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
""",
    "landing.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h1>Welcome to the Admissions Portal</h1><a href='{% url \"admissions:login\" %}'>Login to Apply</a>{% endblock %}",
    "login.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<div class='card adm-card p-4 mx-auto' style='max-width: 400px;'><h2>Login</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button class='btn adm-btn-primary w-100'>Login</button></form></div>{% endblock %}",
    "register.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<div class='card adm-card p-4 mx-auto' style='max-width: 500px;'><h2>Register</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button class='btn adm-btn-primary w-100'>Register</button></form></div>{% endblock %}",
    "verify_email.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Email Verification</h2><p>Check your messages above.</p>{% endblock %}",
    "dashboard.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Parent Dashboard</h2><a href='{% url \"admissions:add_student\" %}' class='btn adm-btn-primary'>Add Student</a>{% endblock %}",
    "add_student.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>{{ title }}</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button class='btn adm-btn-primary'>Save Profile</button></form>{% endblock %}",
    "start_application.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Start Application</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button class='btn adm-btn-primary'>Continue</button></form>{% endblock %}",
    "application_form.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Application Form</h2><p>Form sections go here. Proceed to upload when ready.</p><a href='{% url \"admissions:document_upload\" application.application_number %}' class='btn adm-btn-primary'>Next: Documents</a>{% endblock %}",
    "document_upload.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Document Upload</h2><p>Upload files here.</p><a href='{% url \"admissions:transfer_info\" application.application_number %}' class='btn adm-btn-primary'>Next</a>{% endblock %}",
    "transfer_info.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Transfer Info</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button class='btn adm-btn-primary'>Save & Continue</button></form>{% endblock %}",
    "payment.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Payment</h2><form method='post'>{% csrf_token %}{{ form.as_p }}<button class='btn adm-btn-primary'>Verify & Submit</button></form>{% endblock %}",
    "submit.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Review & Submit</h2><form method='post'>{% csrf_token %}<button class='btn adm-btn-gold'>Submit Application</button></form>{% endblock %}",
    "status_detail.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Application Status: {{ application.get_status_display }}</h2><a href='{% url \"admissions:dashboard\" %}' class='btn btn-secondary'>Back to Dashboard</a>{% endblock %}",
    "offer_accept.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Accept Offer</h2><form method='post'>{% csrf_token %}<button class='btn adm-btn-primary'>Accept Offer</button></form>{% endblock %}",
    
    # Admin templates
    "admin/dashboard.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Staff Dashboard</h2><a href='{% url \"admissions:staff_directory\" %}' class='btn adm-btn-primary'>View Applications</a>{% endblock %}",
    "admin/directory.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Applications Directory</h2><ul>{% for app in applications %}<li><a href='{% url \"admissions:staff_review\" app.application_number %}'>{{ app.application_number }}</a></li>{% endfor %}</ul>{% endblock %}",
    "admin/review.html": "{% extends 'admissions/base_admission.html' %}{% block content %}<h2>Review Application</h2><p>Status: {{ application.get_status_display }}</p>{% endblock %}",
    
    # Emails
    "emails/verification.html": "<h3>Verify Email</h3><a href='{{ verify_url }}'>Click here</a>",
    "emails/welcome.html": "<h3>Welcome</h3>",
    "emails/password_reset.html": "<h3>Reset Password</h3><a href='{{ reset_url }}'>Click here</a>",
    "emails/submission_confirmation.html": "<h3>Application Submitted</h3>",
    "emails/status_change.html": "<h3>Status Update</h3>",
    "emails/action_required.html": "<h3>Action Required</h3>",
    "emails/offer_letter.html": "<h3>Congratulations</h3>",
    "emails/rejection.html": "<h3>Decision</h3>",
    "emails/bulk_message.html": "<h3>Message from Admissions</h3>",
}

for d in directories:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)
    
for filename, content in templates.items():
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Scaffolded templates.")
