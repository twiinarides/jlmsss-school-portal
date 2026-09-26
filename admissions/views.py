"""
admissions/views.py — Full view controllers for JLMSSS Admission Portal v2
Parent Portal + Admin Staff Portal
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from .models import (
    ApplicantAccount, StudentProfile, Application, AdmissionWindow,
    ApplicationDocument, DocumentSlot, EmailVerificationToken, PasswordResetToken,
    ApplicationStatusLog, FormField, ApplicationResponse, TransferInfo
)
from .forms import (
    RegistrationForm, LoginForm, StudentProfileForm, StartApplicationForm,
    ApplicationFilterForm, ChangeStatusForm, SendFeedbackForm, FlagDocumentForm,
    BulkActionForm, ForgotPasswordForm, ResetPasswordForm, TransferInfoForm,
    PaymentReferenceForm
)
from .email_utils import (
    send_verification_email, send_welcome_email, send_status_change_email,
    send_action_required_email, send_offer_letter_email, send_password_reset_email,
    send_submission_confirmation, send_approval_email_with_pdf, send_rejection_email,
    send_resend_verification_email
)
from .pdf_utils import generate_offer_letter_pdf, generate_payment_receipt_pdf
from .utils import log_audit, get_client_ip, export_applications_csv


def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ============================================================================
# PUBLIC & AUTHENTICATION
# ============================================================================

def landing_view(request):
    """Public portal landing page showing open windows."""
    if request.user.is_authenticated:
        if is_staff(request.user):
            return redirect('admissions:staff_dashboard')
        return redirect('admissions:dashboard')

    from django.utils import timezone as tz
    now = tz.now().date()
    open_windows = AdmissionWindow.objects.filter(
        is_active=True, opening_date__lte=now, closing_date__gte=now
    ).prefetch_related('entry_classes').order_by('closing_date')

    steps = [
        {'icon': 'fas fa-user-plus',    'title': 'Create an Account',      'description': 'Register with your email address and set a secure password. One account covers all your children.'},
        {'icon': 'fas fa-file-alt',     'title': 'Fill in the Application', 'description': 'Complete the multi-step form including bio-data, academic history, guardian details, and medical info. Progress is auto-saved.'},
        {'icon': 'fas fa-cloud-upload-alt', 'title': 'Upload Documents',  'description': 'Attach required documents (birth certificate, report cards, passport photo) using our drag-and-drop uploader.'},
        {'icon': 'fas fa-money-bill-wave', 'title': 'Pay the Application Fee', 'description': 'Pay via MTN Mobile Money, Airtel Money, or bank transfer. Enter your transaction reference to confirm payment.'},
        {'icon': 'fas fa-envelope-open-text', 'title': 'Receive Your Decision', 'description': 'Track your application status in real time. You will receive an email when a decision has been made.'},
    ]

    return render(request, 'admissions/landing.html', {
        'open_windows': open_windows,
        'steps': steps,
        'academic_year': open_windows.first().academic_year if open_windows.exists() else '2025/2026',
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('admissions:dashboard')
        
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            token = EmailVerificationToken.objects.create(user=user)
            send_verification_email(user, token)
            messages.success(request, 'Account created! Please check your email to verify your address.')
            return redirect('admissions:login')
    else:
        form = RegistrationForm()
        
    return render(request, 'admissions/register.html', {'form': form})


def verify_email_view(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        if token_obj.is_valid:
            account = getattr(token_obj.user, 'applicant_profile', None)
            if account:
                account.email_verified = True
                account.save()
            token_obj.used = True
            token_obj.save()
            send_welcome_email(token_obj.user)
            messages.success(request, 'Your email has been verified! You can now log in.')
            return redirect('admissions:login')
        else:
            messages.error(request, 'This verification link has expired or already been used.')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    return render(request, 'admissions/verify_email.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('admissions:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                account = getattr(user, 'applicant_profile', None)
                if account and not account.email_verified:
                    messages.warning(request, 'Please verify your email address before logging in. Check your inbox.')
                    return render(request, 'admissions/login.html', {'form': form})
                
                login(request, user)
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                
                if is_staff(user):
                    return redirect('admissions:staff_dashboard')
                return redirect('admissions:dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
        
    return render(request, 'admissions/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admissions:login')


# ============================================================================
# GUARDIAN / PARENT PORTAL
# ============================================================================

@login_required
def dashboard_view(request):
    if is_staff(request.user):
        return redirect('admissions:staff_dashboard')
        
    account = getattr(request.user, 'applicant_profile', None)
    if not account:
        messages.error(request, 'Applicant profile not found.')
        return redirect('home')
        
    students = account.students.all()
    applications = Application.objects.filter(applicant=account).select_related('student', 'window')
    open_windows = AdmissionWindow.objects.filter(is_active=True)
    
    return render(request, 'admissions/dashboard.html', {
        'account': account,
        'students': students,
        'applications': applications,
        'open_windows': open_windows,
    })


@login_required
def add_student_view(request):
    account = request.user.applicant_profile
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.account = account
            student.save()
            messages.success(request, f'Student profile for {student.first_name} added successfully.')
            return redirect('admissions:dashboard')
    else:
        form = StudentProfileForm(initial={'guardian_name': request.user.get_full_name(), 'guardian_email': request.user.email, 'guardian_phone': account.phone})
    return render(request, 'admissions/add_student.html', {'form': form, 'title': 'Add Student Profile'})


@login_required
def edit_student_view(request, student_id):
    account = request.user.applicant_profile
    student = get_object_or_404(StudentProfile, id=student_id, account=account)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student profile for {student.first_name} updated.')
            return redirect('admissions:dashboard')
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'admissions/add_student.html', {'form': form, 'title': 'Edit Student Profile', 'student': student})


@login_required
def start_application_view(request, window_id, student_id):
    account = request.user.applicant_profile
    window = get_object_or_404(AdmissionWindow, id=window_id, is_active=True)
    student = get_object_or_404(StudentProfile, id=student_id, account=account)
    
    if request.method == 'POST':
        form = StartApplicationForm(request.POST, window=window)
        if form.is_valid():
            entry_class = form.cleaned_data['entry_class']
            is_transfer = form.cleaned_data['is_transfer']
            
            # Check if application already exists
            existing = Application.objects.filter(window=window, student=student, entry_class=entry_class).first()
            if existing:
                return redirect('admissions:application_form', app_number=existing.application_number)
                
            app = Application.objects.create(
                window=window,
                applicant=account,
                student=student,
                entry_class=entry_class,
                is_transfer=is_transfer,
                status='draft'
            )
            ApplicationStatusLog.objects.create(
                application=app, to_status='draft', changed_by=request.user, note='Application started'
            )
            if is_transfer:
                TransferInfo.objects.create(
                    application=app, reason_for_leaving='Pending', previous_school_name='Pending', previous_school_district='Pending'
                )
            
            return redirect('admissions:application_form', app_number=app.application_number)
    else:
        form = StartApplicationForm(window=window)
        
    return render(request, 'admissions/start_application.html', {'form': form, 'window': window, 'student': student})


@login_required
def application_form_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account)
    
    if not app.can_edit and not app.can_resubmit:
        return redirect('admissions:status_detail', app_number=app.application_number)
        
    form_def = app.window.forms.filter(entry_class=app.entry_class, is_active=True).first()
    sections = form_def.sections.filter(is_active=True) if form_def else []
    responses = {r.field_key: r.text_value for r in app.responses.all()}
    
    if request.method == 'POST':
        # AJAX autosave logic
        data = json.loads(request.body)
        for field_key, value in data.items():
            field = FormField.objects.filter(section__form=form_def, field_key=field_key).first()
            if field:
                ApplicationResponse.objects.update_or_create(
                    application=app, field=field,
                    defaults={'field_key': field_key, 'text_value': value}
                )
        return JsonResponse({'status': 'saved'})
        
    return render(request, 'admissions/application_form.html', {
        'application': app,
        'sections': sections,
        'responses': responses,
    })


@login_required
def transfer_info_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account, is_transfer=True)
    
    if not app.can_edit:
        return redirect('admissions:status_detail', app_number=app.application_number)
        
    transfer_info = getattr(app, 'transfer_info', None)
    
    if request.method == 'POST':
        form = TransferInfoForm(request.POST)
        if form.is_valid():
            if not transfer_info:
                transfer_info = TransferInfo(application=app)
            
            transfer_info.previous_school_name = form.cleaned_data['transfer_school_name']
            transfer_info.previous_school_district = form.cleaned_data['transfer_school_district']
            transfer_info.previous_school_contact = form.cleaned_data['transfer_school_contact']
            transfer_info.headteacher_name = form.cleaned_data['transfer_headteacher']
            transfer_info.last_class_attended = form.cleaned_data['transfer_last_class']
            transfer_info.date_last_attended = form.cleaned_data['transfer_date_last']
            transfer_info.reason_for_leaving = form.cleaned_data['transfer_reason']
            transfer_info.any_disciplinary_issues = form.cleaned_data['transfer_disciplinary']
            transfer_info.disciplinary_details = form.cleaned_data['transfer_disciplinary_details']
            transfer_info.outstanding_fees = form.cleaned_data['transfer_outstanding_fees']
            transfer_info.save()
            return redirect('admissions:document_upload', app_number=app.application_number)
    else:
        initial = {}
        if transfer_info:
            initial = {
                'transfer_school_name': transfer_info.previous_school_name,
                'transfer_school_district': transfer_info.previous_school_district,
                'transfer_school_contact': transfer_info.previous_school_contact,
                'transfer_headteacher': transfer_info.headteacher_name,
                'transfer_reason': transfer_info.reason_for_leaving,
                'transfer_disciplinary': transfer_info.any_disciplinary_issues,
                'transfer_disciplinary_details': transfer_info.disciplinary_details,
                'transfer_outstanding_fees': transfer_info.outstanding_fees,
            }
        form = TransferInfoForm(initial=initial)
        
    return render(request, 'admissions/transfer_info.html', {'application': app, 'form': form})


@login_required
def document_upload_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account)

    slots = list(app.window.document_slots.all())
    uploaded_docs = {doc.slot_key: doc for doc in app.documents.all()}

    # Attach uploaded_doc to each slot for easy template access
    for slot in slots:
        slot.uploaded_doc = uploaded_docs.get(slot.slot_key)

    if not app.can_edit and not app.can_resubmit:
        return redirect('admissions:status_detail', app_number=app.application_number)

    return render(request, 'admissions/document_upload.html', {
        'application': app,
        'slots': slots,
        'uploaded_docs': uploaded_docs,
    })


@login_required
@csrf_exempt
def upload_document_ajax(request, app_number, slot_key):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
        
    app = get_object_or_404(Application, application_number=app_number, applicant__user=request.user)
    if not app.can_edit and not app.can_resubmit:
        return JsonResponse({'error': 'Application cannot be edited'}, status=403)
        
    slot = get_object_or_404(DocumentSlot, window=app.window, slot_key=slot_key)
    file_obj = request.FILES.get('file')
    if not file_obj:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
        
    # Validation
    ext = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else ''
    if ext not in slot.accepted_types_list:
        return JsonResponse({'error': f'Invalid file type. Accepted: {slot.accepted_types}'}, status=400)
    
    if file_obj.size > slot.max_size_mb * 1024 * 1024:
        return JsonResponse({'error': f'File too large. Max {slot.max_size_mb}MB'}, status=400)
        
    # Delete existing doc for this slot if any
    ApplicationDocument.objects.filter(application=app, slot_key=slot_key).delete()
    
    doc = ApplicationDocument.objects.create(
        application=app,
        slot=slot,
        slot_key=slot.slot_key,
        slot_name=slot.name,
        file=file_obj,
        original_name=file_obj.name,
        file_size_kb=file_obj.size // 1024,
        status='pending'
    )
    
    return JsonResponse({
        'status': 'success',
        'doc_id': doc.id,
        'url': doc.file.url,
        'name': doc.original_name,
        'is_image': doc.is_image
    })


@login_required
@csrf_exempt
def delete_document_ajax(request, app_number, doc_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    app = get_object_or_404(Application, application_number=app_number, applicant__user=request.user)
    if not app.can_edit and not app.can_resubmit:
        return JsonResponse({'error': 'Cannot delete'}, status=403)
        
    doc = get_object_or_404(ApplicationDocument, id=doc_id, application=app)
    doc.file.delete()
    doc.delete()
    return JsonResponse({'status': 'deleted'})


@login_required
def payment_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account)
    
    if not app.can_edit:
        return redirect('admissions:status_detail', app_number=app.application_number)
        
    from .models import PaymentConfig
    config = PaymentConfig.objects.filter(is_active=True).first()
    fee = app.window.application_fee
    
    if not fee or fee <= 0:
        return redirect('admissions:submit_application', app_number=app.application_number)
        
    if request.method == 'POST':
        form = PaymentReferenceForm(request.POST)
        if form.is_valid():
            app.payment_reference = form.cleaned_data['payment_reference']
            app.save()
            return redirect('admissions:submit_application', app_number=app.application_number)
    else:
        form = PaymentReferenceForm(initial={'payment_reference': app.payment_reference})
        
    return render(request, 'admissions/payment.html', {'application': app, 'config': config, 'form': form, 'fee': fee})


@login_required
def submit_application_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account)
    
    if request.method == 'POST':
        if app.status == 'draft':
            app.status = 'submitted'
            app.submitted_at = timezone.now()
            app.save()
            ApplicationStatusLog.objects.create(application=app, from_status='draft', to_status='submitted', changed_by=request.user)
            send_submission_confirmation(app)
            messages.success(request, 'Application submitted successfully!')
            
        elif app.status == 'action_required':
            app.status = 'docs_resubmitted'
            app.save()
            ApplicationStatusLog.objects.create(application=app, from_status='action_required', to_status='docs_resubmitted', changed_by=request.user)
            messages.success(request, 'Documents resubmitted successfully!')
            
        return redirect('admissions:status_detail', app_number=app.application_number)
        
    return render(request, 'admissions/submit.html', {'application': app})


@login_required
def status_detail_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account)
    logs = app.status_logs.all()
    feedbacks = app.feedbacks.all()
    documents = app.documents.all()
    
    return render(request, 'admissions/status_detail.html', {
        'application': app,
        'logs': logs,
        'feedbacks': feedbacks,
        'documents': documents,
        'pipeline': STATUS_DISPLAY_PIPELINE
    })


@login_required
def accept_offer_view(request, app_number):
    account = request.user.applicant_profile
    app = get_object_or_404(Application, application_number=app_number, applicant=account)
    
    if not app.can_accept_offer:
        messages.error(request, 'Offer cannot be accepted at this time.')
        return redirect('admissions:status_detail', app_number=app.application_number)
        
    if request.method == 'POST':
        app.status = 'enrolled'
        app.offer_accepted_at = timezone.now()
        app.offer_accepted_by_ip = get_client_ip(request)
        app.save()
        ApplicationStatusLog.objects.create(application=app, from_status='provisionally_admitted', to_status='enrolled', changed_by=request.user, note='Parent accepted offer digitally.')
        messages.success(request, 'Congratulations! You have accepted the admission offer.')
        return redirect('admissions:status_detail', app_number=app.application_number)
        
    return render(request, 'admissions/offer_accept.html', {'application': app})


@login_required
def download_receipt_view(request, app_number):
    app = get_object_or_404(Application, application_number=app_number, applicant__user=request.user)
    pdf_bytes = generate_payment_receipt_pdf(app)
    if not pdf_bytes:
        return HttpResponse('PDF generation failed', status=500)
        
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{app.application_number}.pdf"'
    return response


@login_required
def download_offer_letter_view(request, app_number):
    app = get_object_or_404(Application, application_number=app_number, applicant__user=request.user)
    if not app.offer_letter:
        raise Http404("Offer letter not generated yet.")
        
    return redirect(app.offer_letter.url)


# ============================================================================
# ADMIN / STAFF PORTAL
# ============================================================================

@staff_member_required(login_url='admissions:login')
def staff_dashboard_view(request):
    open_apps = Application.objects.exclude(status__in=['draft', 'rejected', 'withdrawn'])
    stats = {
        'total_pending': open_apps.filter(status='submitted').count(),
        'under_review': open_apps.filter(status='under_doc_review').count(),
        'action_required': open_apps.filter(status='action_required').count(),
        'resubmitted': open_apps.filter(status='docs_resubmitted').count(),
        'approved': open_apps.filter(status='approved').count(),
        'enrolled': open_apps.filter(status='enrolled').count(),
    }
    recent_activity = ApplicationStatusLog.objects.exclude(from_status='draft').select_related('application', 'changed_by')[:10]
    
    return render(request, 'admissions/admin/dashboard.html', {'stats': stats, 'recent_activity': recent_activity})


@staff_member_required(login_url='admissions:login')
def staff_directory_view(request):
    qs = Application.objects.exclude(status='draft').select_related('student', 'applicant__user', 'window')
    
    form = ApplicationFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('window'):
            qs = qs.filter(window=form.cleaned_data['window'])
        if form.cleaned_data.get('entry_class'):
            qs = qs.filter(entry_class=form.cleaned_data['entry_class'])
        if form.cleaned_data.get('status'):
            qs = qs.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('payment_verified'):
            val = form.cleaned_data['payment_verified'] == '1'
            qs = qs.filter(payment_verified=val)
        search = form.cleaned_data.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(application_number__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(applicant__user__email__icontains=search) |
                Q(applicant__phone__icontains=search)
            )
            
    return render(request, 'admissions/admin/directory.html', {'applications': qs, 'form': form})


@staff_member_required(login_url='admissions:login')
def staff_review_view(request, app_number):
    app = get_object_or_404(Application, application_number=app_number)
    
    # Auto-move status if it was just submitted
    if app.status == 'submitted':
        app.status = 'under_doc_review'
        app.save()
        ApplicationStatusLog.objects.create(application=app, from_status='submitted', to_status='under_doc_review', changed_by=request.user)
        log_audit(request.user, 'Started Document Review', app, request=request)
        
    responses = app.responses.all()
    documents = app.documents.all()
    feedbacks = app.feedbacks.all()
    logs = app.status_logs.all()
    
    status_form = ChangeStatusForm(initial={'new_status': app.status})
    feedback_form = SendFeedbackForm()
    
    return render(request, 'admissions/admin/review.html', {
        'application': app,
        'responses': responses,
        'documents': documents,
        'feedbacks': feedbacks,
        'logs': logs,
        'status_form': status_form,
        'feedback_form': feedback_form,
    })


@staff_member_required(login_url='admissions:login')
@csrf_exempt
def staff_approve_document_view(request, doc_id):
    if request.method == 'POST':
        doc = get_object_or_404(ApplicationDocument, id=doc_id)
        doc.status = 'approved'
        doc.admin_note = ''
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save()
        log_audit(request.user, f'Approved document: {doc.slot_name}', doc.application, request=request)
        return JsonResponse({'status': 'approved'})


@staff_member_required(login_url='admissions:login')
@csrf_exempt
def staff_flag_document_view(request, doc_id):
    if request.method == 'POST':
        doc = get_object_or_404(ApplicationDocument, id=doc_id)
        note = request.POST.get('note', '')
        doc.status = 'flagged'
        doc.admin_note = note
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save()
        log_audit(request.user, f'Flagged document: {doc.slot_name}', doc.application, details=note, request=request)
        return JsonResponse({'status': 'flagged'})


@staff_member_required(login_url='admissions:login')
def staff_change_status_view(request, app_number):
    app = get_object_or_404(Application, application_number=app_number)
    if request.method == 'POST':
        form = ChangeStatusForm(request.POST)
        if form.is_valid():
            old = app.status
            new = form.cleaned_data['new_status']
            note = form.cleaned_data['note']
            notify = form.cleaned_data['notify_applicant']
            
            app.status = new
            if note:
                app.admin_notes = f"{app.admin_notes}\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {note}"
            app.save()
            
            ApplicationStatusLog.objects.create(application=app, from_status=old, to_status=new, changed_by=request.user, note=note)
            log_audit(request.user, f'Changed status to {new}', app, request=request)
            
            if new == 'approved':
                # Auto-generate offer letter PDF and email it
                try:
                    from django.core.files.base import ContentFile
                    pdf_bytes = generate_offer_letter_pdf(app)
                    if pdf_bytes:
                        fname = f'Offer_Letter_{app.application_number}.pdf'
                        app.offer_letter.save(fname, ContentFile(pdf_bytes))
                        app.offer_generated_at = timezone.now()
                        app.save()
                        send_approval_email_with_pdf(app, pdf_bytes)
                        messages.success(request, 'Application APPROVED. Offer letter generated and emailed to applicant.')
                    else:
                        send_status_change_email(app, old, new, note)
                        messages.warning(request, 'Approved, but PDF generation failed. A status email was sent instead.')
                except Exception as e:
                    send_status_change_email(app, old, new, note)
                    messages.warning(request, f'Approved and status email sent. PDF error: {e}')
            elif new == 'rejected':
                send_rejection_email(app, note)
                messages.success(request, 'Application rejected. Rejection email sent to applicant.')
            elif notify:
                send_status_change_email(app, old, new, note)
                messages.success(request, f'Status updated to {new} and email sent.')
            else:
                messages.success(request, f'Status updated to {new}.')
                
    return redirect('admissions:staff_review', app_number=app.application_number)


@staff_member_required(login_url='admissions:login')
def staff_send_feedback_view(request, app_number):
    app = get_object_or_404(Application, application_number=app_number)
    if request.method == 'POST':
        form = SendFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.application = app
            feedback.sent_by = request.user
            feedback.is_sent = True
            feedback.sent_at = timezone.now()
            feedback.save()
            
            if feedback.feedback_type == 'action_required':
                app.status = 'action_required'
                app.resubmission_deadline = timezone.now() + timezone.timedelta(days=app.window.resubmission_deadline_days)
                app.save()
                ApplicationStatusLog.objects.create(application=app, from_status='under_doc_review', to_status='action_required', changed_by=request.user)
                send_action_required_email(app, feedback)
                log_audit(request.user, 'Sent Action Required Feedback', app, request=request)
                messages.success(request, 'Action Required email sent to applicant.')
            else:
                # Use standard status change for general info
                send_status_change_email(app, app.status, app.status, feedback.message)
                messages.success(request, 'Feedback email sent.')
                
    return redirect('admissions:staff_review', app_number=app.application_number)


@staff_member_required(login_url='admissions:login')
def staff_generate_offer_view(request, app_number):
    app = get_object_or_404(Application, application_number=app_number)
    if request.method == 'POST':
        pdf_bytes = generate_offer_letter_pdf(app)
        if pdf_bytes:
            from django.core.files.base import ContentFile
            filename = f"Offer_Letter_{app.application_number}.pdf"
            app.offer_letter.save(filename, ContentFile(pdf_bytes))
            app.offer_generated_at = timezone.now()
            
            old = app.status
            app.status = 'provisionally_admitted'
            app.save()
            
            ApplicationStatusLog.objects.create(application=app, from_status=old, to_status='provisionally_admitted', changed_by=request.user)
            log_audit(request.user, 'Generated Offer Letter', app, request=request)
            
            # Send Email
            send_offer_letter_email(app, pdf_bytes)
            messages.success(request, 'Offer letter generated and sent to applicant!')
        else:
            messages.error(request, 'Failed to generate PDF. Make sure reportlab is installed.')
            
    return redirect('admissions:staff_review', app_number=app.application_number)


@staff_member_required(login_url='admissions:login')
def staff_export_csv_view(request):
    qs = Application.objects.exclude(status='draft')
    form = ApplicationFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('window'):
            qs = qs.filter(window=form.cleaned_data['window'])
        if form.cleaned_data.get('entry_class'):
            qs = qs.filter(entry_class=form.cleaned_data['entry_class'])
        if form.cleaned_data.get('status'):
            qs = qs.filter(status=form.cleaned_data['status'])
            
    csv_data = export_applications_csv(qs)
    response = HttpResponse(csv_data, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="applications_{timezone.now():%Y%m%d}.csv"'
    log_audit(request.user, 'Exported CSV', details=f'{qs.count()} records', request=request)
    return response

# To prevent import errors in this codebase, adding imports required by urls and others directly here.

# ============================================================================
# PASSWORD RESET VIEWS
# ============================================================================

def forgot_password_view(request):
    """Show form to request a password reset email."""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            try:
                from django.contrib.auth.models import User as AuthUser
                user = AuthUser.objects.get(email__iexact=email)
                # Invalidate old tokens
                PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
                token = PasswordResetToken.objects.create(user=user)
                send_password_reset_email(user, token)
            except Exception:
                pass  # Don't reveal whether email exists
            messages.success(request, 'If an account exists with that email, a password reset link has been sent. Please check your inbox and spam folder.')
            return redirect('admissions:login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'admissions/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    """Handle password reset via token link."""
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
        if not token_obj.is_valid:
            messages.error(request, 'This password reset link has expired or already been used. Please request a new one.')
            return redirect('admissions:forgot_password')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('admissions:forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            token_obj.user.set_password(form.cleaned_data['password1'])
            token_obj.user.save()
            token_obj.used = True
            token_obj.save()
            messages.success(request, 'Password reset successfully! You can now log in with your new password.')
            return redirect('admissions:login')
    else:
        form = ResetPasswordForm()
    return render(request, 'admissions/reset_password.html', {'form': form, 'token': token})


def resend_verification_view(request):
    """Resend email verification link."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            from django.contrib.auth.models import User as AuthUser
            user = AuthUser.objects.get(email__iexact=email)
            account = getattr(user, 'applicant_profile', None)
            if account and not account.email_verified:
                EmailVerificationToken.objects.filter(user=user, used=False).update(used=True)
                token = EmailVerificationToken.objects.create(user=user)
                send_resend_verification_email(user, token)
                messages.success(request, 'A new verification email has been sent. Please check your inbox and spam folder.')
            elif account and account.email_verified:
                messages.info(request, 'Your email is already verified. Please log in.')
            else:
                messages.success(request, 'If an account with that email exists, a new verification link has been sent.')
        except Exception:
            messages.success(request, 'If an account with that email exists, a new verification link has been sent.')
    return redirect('admissions:login')


STATUS_DISPLAY_PIPELINE = [
    ('draft', 'Draft', 'fas fa-pen'),
    ('submitted', 'Submitted', 'fas fa-paper-plane'),
    ('under_doc_review', 'Under Review', 'fas fa-search'),
    ('action_required', 'Action Required', 'fas fa-exclamation-triangle'),
    ('approved', 'Approved', 'fas fa-check-circle'),
    ('provisionally_admitted', 'Provisionally Admitted', 'fas fa-graduation-cap'),
    ('enrolled', 'Enrolled', 'fas fa-school'),
]


# ============================================================================
# PWA VIEWS (Served from root for scope)
# ============================================================================

def sw_view(request):
    import os
    from django.conf import settings
    from django.http import HttpResponse
    file_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'sw.js')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return HttpResponse(f.read(), content_type='application/javascript')
    return HttpResponse('// Service Worker Not Found', content_type='application/javascript')

def manifest_view(request):
    import os
    from django.conf import settings
    from django.http import HttpResponse
    file_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return HttpResponse(f.read(), content_type='application/json')
    return HttpResponse('{}', content_type='application/json')
