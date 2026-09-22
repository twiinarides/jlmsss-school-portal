"""
admissions/forms.py — Django forms for JLMSSS Admission Portal v2
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    ApplicantAccount, StudentProfile, Application, ApplicationDocument,
    AdminFeedback, AdmissionWindow, ENTRY_CLASS_CHOICES, APPLICATION_STATUS_CHOICES,
    GENDER_CHOICES, LANGUAGE_CHOICES, FEEDBACK_TYPE_CHOICES,
)


# ============================================================================
# AUTH FORMS
# ============================================================================

class RegistrationForm(forms.Form):
    """Account registration form for parents/students."""
    first_name = forms.CharField(
        max_length=150, label='First Name',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'First name', 'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        max_length=150, label='Last Name',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Last name', 'autocomplete': 'family-name'}),
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'adm-input', 'placeholder': 'your@email.com', 'autocomplete': 'email'}),
    )
    phone = forms.CharField(
        max_length=20, label='Phone Number',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': '+256 700 000 000', 'autocomplete': 'tel'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'adm-input', 'placeholder': 'Create a strong password'}),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'adm-input', 'placeholder': 'Repeat your password'}),
    )
    agree_terms = forms.BooleanField(
        label='I agree to the Terms of Use and Privacy Policy',
        widget=forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists. Please log in instead.')
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match.')
        if len(p1) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        return p2

    def save(self):
        email = self.cleaned_data['email'].strip().lower()
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=self.cleaned_data['first_name'].strip(),
            last_name=self.cleaned_data['last_name'].strip(),
            password=self.cleaned_data['password1'],
            is_active=True,  # Active but email not verified — enforced at login
        )
        ApplicantAccount.objects.create(
            user=user,
            phone=self.cleaned_data.get('phone', ''),
            email_verified=False,
        )
        return user


class LoginForm(forms.Form):
    """Login by email + password."""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'adm-input', 'placeholder': 'your@email.com', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'adm-input', 'placeholder': 'Your password'}),
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
        label='Keep me logged in for 30 days',
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'adm-input', 'placeholder': 'Enter your registered email'}),
    )


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'adm-input', 'placeholder': 'New password (min 8 chars)'}),
    )
    password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'adm-input', 'placeholder': 'Repeat new password'}),
    )

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Passwords do not match.')
        if len(p1) < 8:
            raise ValidationError('Password must be at least 8 characters.')
        return p2


# ============================================================================
# STUDENT PROFILE FORM
# ============================================================================

class StudentProfileForm(forms.ModelForm):
    """Add / edit a student profile (child of the account holder)."""

    class Meta:
        model = StudentProfile
        exclude = ['account', 'created_at', 'updated_at']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Last name'}),
            'other_names': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Any other names (optional)'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'adm-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'adm-select'}),
            'nationality': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Ugandan'}),
            'district_of_origin': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'District'}),
            'religion': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Christianity, Islam'}),
            'passport_photo': forms.FileInput(attrs={'class': 'adm-file-input', 'accept': 'image/*'}),
            'has_special_needs': forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
            'special_needs_details': forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 3, 'placeholder': 'Describe any special needs or disabilities'}),
            'medical_conditions': forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 3, 'placeholder': 'Any medical conditions we should know about'}),
            'blood_group': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. O+, A-, B+'}),
            'guardian_name': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Full name of parent/guardian'}),
            'guardian_relationship': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Mother, Father, Uncle'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': '+256 700 000 000'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'adm-input', 'placeholder': 'Guardian email (optional)'}),
            'guardian_occupation': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Occupation (optional)'}),
            'guardian_address': forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 2, 'placeholder': 'Physical address'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Emergency contact name (optional)'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Emergency contact phone (optional)'}),
            'cocurricular_interests': forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 3, 'placeholder': 'e.g. Football, Drama, Music, Debate Club'}),
            'previous_school_name': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Name of last school attended'}),
            'previous_school_district': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'District of that school'}),
            'last_class_attended': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. P.7, S.3'}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = timezone.now().date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if dob > today:
                raise ValidationError('Date of birth cannot be in the future.')
            if age > 25:
                raise ValidationError('Please verify the date of birth — the age seems unusual for a secondary school student.')
            if age < 8:
                raise ValidationError('The student appears too young for secondary school.')
        return dob


# ============================================================================
# APPLICATION FORMS
# ============================================================================

class StartApplicationForm(forms.Form):
    """Form to start a new application — select class."""
    entry_class = forms.ChoiceField(
        label='Class Applying For',
        choices=[('', '— Select a class —')] + list(ENTRY_CLASS_CHOICES),
        widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    is_transfer = forms.BooleanField(
        required=False,
        label='I am transferring from another school',
        widget=forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
    )

    def __init__(self, *args, window=None, **kwargs):
        super().__init__(*args, **kwargs)
        if window:
            open_classes = window.entry_classes.filter(is_open=True).values_list('entry_class', flat=True)
            class_map = dict(ENTRY_CLASS_CHOICES)
            available = [(code, class_map[code]) for code in open_classes if code in class_map]
            self.fields['entry_class'].choices = [('', '— Select a class —')] + available


class PaymentReferenceForm(forms.Form):
    payment_reference = forms.CharField(
        max_length=100, label='Payment Reference Number',
        help_text='Enter the MTN, Airtel, or bank transaction reference exactly as it appears on your receipt.',
        widget=forms.TextInput(attrs={
            'class': 'adm-input',
            'placeholder': 'e.g. MTN1234567890 or REF-2026-000123',
        }),
    )


class TransferInfoForm(forms.Form):
    """Transfer student extra details."""
    transfer_school_name = forms.CharField(
        max_length=300, label='Previous School Name',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Full name of previous school'}),
    )
    transfer_school_district = forms.CharField(
        max_length=100, label='School District',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'District of previous school'}),
    )
    transfer_school_contact = forms.CharField(
        max_length=50, required=False, label='School Contact Number',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': '+256 700 000 000 (optional)'}),
    )
    transfer_headteacher = forms.CharField(
        max_length=200, required=False, label="Previous Headteacher's Name",
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': "Headteacher's name (optional)"}),
    )
    transfer_last_class = forms.CharField(
        max_length=50, required=False, label='Last Class Attended',
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'e.g. Senior 3'}),
    )
    transfer_date_last = forms.DateField(
        required=False, label='Date Last Attended',
        widget=forms.DateInput(attrs={'class': 'adm-input', 'type': 'date'}),
    )
    transfer_reason = forms.CharField(
        label='Reason for Leaving',
        widget=forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 4, 'placeholder': 'Explain why you are leaving your previous school'}),
    )
    transfer_disciplinary = forms.BooleanField(
        required=False, label='Were there any disciplinary issues at the previous school?',
        widget=forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
    )
    transfer_disciplinary_details = forms.CharField(
        required=False, label='Disciplinary Details',
        widget=forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 3, 'placeholder': 'Provide details if yes'}),
    )
    transfer_outstanding_fees = forms.BooleanField(
        required=False, label='Are there outstanding fees at the previous school?',
        widget=forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
    )


# ============================================================================
# ADMIN STAFF FORMS
# ============================================================================

class ApplicationFilterForm(forms.Form):
    """Filter/search form for staff applicant directory."""
    window = forms.ModelChoiceField(
        queryset=AdmissionWindow.objects.all().order_by('-opening_date'),
        required=False, empty_label='All Windows',
        widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    entry_class = forms.ChoiceField(
        choices=[('', 'All Classes')] + list(ENTRY_CLASS_CHOICES),
        required=False, widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(APPLICATION_STATUS_CHOICES),
        required=False, widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    payment_verified = forms.ChoiceField(
        choices=[('', 'Any Payment'), ('1', 'Verified'), ('0', 'Not Verified')],
        required=False, widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    search = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={
            'class': 'adm-input',
            'placeholder': 'Search by App #, name, email, phone…',
        }),
    )


class SendFeedbackForm(forms.ModelForm):
    """Staff form to send feedback / action required to an applicant."""
    class Meta:
        model = AdminFeedback
        fields = ['feedback_type', 'subject', 'message']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'adm-select'}),
            'subject': forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Subject line'}),
            'message': forms.Textarea(attrs={
                'class': 'adm-textarea', 'rows': 6,
                'placeholder': 'Write your message to the applicant here. Be specific about what needs to be corrected or provided.',
            }),
        }

    QUICK_TEMPLATES = [
        ('missing_docs', 'Missing required documents — please upload all required files and resubmit.'),
        ('blurry_docs', 'One or more documents are too blurry or illegible. Please upload clearer copies.'),
        ('wrong_docs', 'Incorrect documents were uploaded. Please check the requirements and upload the correct files.'),
        ('fee_verify', 'Your payment reference could not be verified. Please confirm the transaction reference number.'),
        ('interview', 'You have been shortlisted for an interview. Please log in for details about the interview schedule.'),
    ]


class ChangeStatusForm(forms.Form):
    """Staff form to change application status."""
    new_status = forms.ChoiceField(
        choices=APPLICATION_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'adm-select'}),
        label='New Status',
    )
    note = forms.CharField(
        required=False, label='Internal Note (not sent to applicant)',
        widget=forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 3}),
    )
    notify_applicant = forms.BooleanField(
        required=False, initial=True, label='Send email notification to applicant',
        widget=forms.CheckboxInput(attrs={'class': 'adm-checkbox'}),
    )


class FlagDocumentForm(forms.Form):
    """Staff form to flag a document."""
    admin_note = forms.CharField(
        label='Reason for flagging',
        widget=forms.Textarea(attrs={
            'class': 'adm-textarea', 'rows': 3,
            'placeholder': 'Explain what is wrong with this document (visible to applicant)',
        }),
    )


class BulkActionForm(forms.Form):
    """Staff bulk action form."""
    ACTION_CHOICES = [
        ('email', 'Send Email to Selected'),
        ('status', 'Change Status for Selected'),
        ('export', 'Export Selected to CSV'),
    ]
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    new_status = forms.ChoiceField(
        choices=[('', '— Select status —')] + list(APPLICATION_STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'adm-select'}),
    )
    email_subject = forms.CharField(
        max_length=300, required=False,
        widget=forms.TextInput(attrs={'class': 'adm-input', 'placeholder': 'Email subject'}),
    )
    email_body = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'adm-textarea', 'rows': 5, 'placeholder': 'Email body'}),
    )
    application_ids = forms.CharField(widget=forms.HiddenInput(), required=False)
