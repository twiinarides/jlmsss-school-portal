"""
admissions/translations.py

Translation dictionary for the admissions portal.
Supports: English (en), Luganda (lg), Runyakore-Rukiga (rk).

Note: Luganda and Runyakore-Rukiga translations marked with [~] are
reasonable approximations and should be reviewed by a native speaker.
"""

TRANSLATIONS = {
    # -------------------------------------------------------------------------
    # ENGLISH
    # -------------------------------------------------------------------------
    'en': {
        # Portal / General
        'portal_title': 'Admissions Portal',
        'apply_now': 'Apply Now',
        'application_portal': 'Online Application Portal',
        'open_windows': 'Open Admission Windows',
        'no_open_windows': 'There are currently no open admission windows. Please check back later.',
        'status_check': 'Check Application Status',
        'check_status': 'Track Your Application',
        'application_number': 'Application Number',
        'enter_app_number': 'Enter your application number',
        'enter_email': 'Enter your email address',
        'closed': 'Closed',
        'open': 'Open',
        'seats_available': 'Seats Available',
        'no_seats': 'No seats available',
        'deadline': 'Deadline',
        'fee_required': 'Application Fee Required',
        'no_fee': 'No Application Fee',
        'interview_required': 'Interview Required',

        # Auth
        'login': 'Log In',
        'register': 'Register',
        'logout': 'Log Out',
        'my_applications': 'My Applications',
        'dashboard': 'Dashboard',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'create_account': 'Create Account',
        'already_have_account': 'Already have an account?',
        'login_link': 'Log in here',
        'no_account_yet': "Don't have an account yet?",
        'register_link': 'Register here',
        'forgot_password': 'Forgot Password?',

        # Personal info fields
        'full_name': 'Full Name',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'date_of_birth': 'Date of Birth',
        'gender': 'Gender',
        'phone': 'Phone Number',
        'email': 'Email Address',
        'district': 'District',
        'nationality': 'Nationality',
        'religion': 'Religion',
        'next_of_kin': 'Next of Kin / Guardian',
        'relationship': 'Relationship',

        # Form navigation
        'save_draft': 'Save Draft',
        'next_step': 'Next Step',
        'previous_step': 'Previous Step',
        'submit_application': 'Submit Application',
        'review_application': 'Review Application',
        'confirm_submit': 'Confirm Submission',
        'cancel': 'Cancel',
        'back': 'Back',

        # Payment
        'payment_instructions': 'Payment Instructions',
        'payment_reference': 'Payment Reference Number',
        'enter_reference': 'Enter Transaction Reference',
        'upload_document': 'Upload Document',

        # File upload
        'file_too_large': 'File is too large. Maximum allowed size is',
        'invalid_file_type': 'Invalid file type. Allowed types are',
        'required_field': 'This field is required.',
        'optional': 'Optional',
        'upload_here': 'Upload here',

        # Form steps
        'step_personal': 'Personal Information',
        'step_academic': 'Academic Background',
        'step_transfer': 'Transfer Information',
        'step_documents': 'Documents',
        'step_payment': 'Payment',
        'step_review': 'Review & Submit',

        # Application status labels
        'status_draft': 'Draft',
        'status_submitted': 'Submitted',
        'status_payment_pending': 'Payment Pending Verification',
        'status_under_review': 'Under Review',
        'status_shortlisted': 'Shortlisted',
        'status_interview_scheduled': 'Interview Scheduled',
        'status_accepted': 'Accepted',
        'status_rejected': 'Rejected',
        'status_waitlisted': 'Waitlisted',
        'status_withdrawn': 'Withdrawn',

        # Transfer specific
        'transfer_question': 'Are you transferring from another school?',
        'previous_school': 'Previous School Name',
        'previous_district': 'Previous School District',
        'headteacher_name': "Headteacher's Name",
        'school_contact': 'School Contact Number',
        'date_last_attended': 'Date Last Attended',
        'reason_leaving': 'Reason for Leaving',
        'disciplinary_issues': 'Any Disciplinary Issues?',
        'outstanding_fees': 'Are There Outstanding Fees?',

        # Class / window selection
        'select_class': 'Select Class to Join',
        'select_window': 'Select Admission Window',

        # Language labels
        'english_label': 'English',
        'luganda_label': 'Luganda',
        'runyakore_label': 'Runyakore-Rukiga',

        # Confirmation
        'application_submitted': 'Application Submitted Successfully',
        'congratulations': 'Congratulations!',
        'your_app_number': 'Your Application Number',
        'what_next': 'What Happens Next?',
        'print_confirmation': 'Print Confirmation',
        'download_confirmation': 'Download Confirmation',

        # Academic fields
        'ple_results': 'PLE Results',
        'uce_results': 'UCE Results',
        'uneb_index': 'UNEB Index Number',
        'former_school': 'Former/Current School',
        'current_school': 'Current School',
        'current_class': 'Current Class / Year',
        'subject_combination': 'Subject Combination (for S5/S6)',
        'career_goals': 'Career Goals / Interests',
        'academic_performance': 'Academic Performance',

        # Document types
        'report_card': 'School Report Card',
        'transfer_letter': 'Transfer Letter',
        'recommendation_letter': 'Recommendation Letter',
        'discipline_record': 'Discipline Record / Conduct Report',
        'birth_certificate': 'Birth Certificate',
        'passport_photo': 'Passport-size Photo',
        'conduct_report': 'Conduct Report',
        'academic_transcript': 'Academic Transcript',
    },

    # -------------------------------------------------------------------------
    # LUGANDA [~] = approximate translation – please verify with a native speaker
    # -------------------------------------------------------------------------
    'lg': {
        # Portal / General
        'portal_title': 'Oluggya lw\'Okuyingira Essomero [~]',
        'apply_now': 'Saba Kati [~]',
        'application_portal': 'Oluggya lw\'Okusaba Eri Internet [~]',
        'open_windows': 'Ebiseera by\'Okuyingira Ebyagulwa [~]',
        'no_open_windows': 'Tewali bisera by\'okuyingira ebyagulwa kati. Ddayo olabe oluvannyuma. [~]',
        'status_check': 'Kebera Essengo ly\'Okusaba Kwo [~]',
        'check_status': 'Goberera Okusaba Kwo [~]',
        'application_number': 'Ennamba y\'Okusaba [~]',
        'enter_app_number': 'Yingiza ennamba y\'okusaba kyo [~]',
        'enter_email': 'Yingiza aadresi yo ey\'imeyili [~]',
        'closed': 'Ggaliridde [~]',
        'open': 'Yagulwa [~]',
        'seats_available': 'Ensi Ziriwo [~]',
        'no_seats': 'Tewali nsi ziyo [~]',
        'deadline': 'Olunaku lw\'Enkomerero [~]',
        'fee_required': 'Musolo gw\'Okusaba Gukwetaagisa [~]',
        'no_fee': 'Tewali Musolo gw\'Okusaba [~]',
        'interview_required': 'Olugendo lw\'Okukebera Kukwetaagisa [~]',

        # Auth
        'login': 'Yingira [~]',
        'register': 'Weewandiisa [~]',
        'logout': 'Fuluma [~]',
        'my_applications': 'Okusaba Kwange [~]',
        'dashboard': 'Oluggya lw\'Okukola [~]',
        'password': 'Ekigambo ky\'Okulinda [~]',
        'confirm_password': 'Kakasa Ekigambo ky\'Okulinda [~]',
        'create_account': 'Tonda Akawunti [~]',
        'already_have_account': 'Olina Akawunti Nate? [~]',
        'login_link': 'Yingira Wano [~]',
        'no_account_yet': 'Tolina Akawunti Nate? [~]',
        'register_link': 'Weewandiisa Wano [~]',
        'forgot_password': 'Oweereza Ekigambo ky\'Okulinda? [~]',

        # Personal info fields
        'full_name': 'Erinnya Lyona [~]',
        'first_name': 'Erinnya Erya Ntandikwa [~]',
        'last_name': 'Erinnya Erya Ttaka [~]',
        'date_of_birth': 'Olunaku lw\'Okuzaalibwa [~]',
        'gender': 'Ekika [~]',
        'phone': 'Ennamba y\'Essimu [~]',
        'email': 'Aadresi y\'Imeyili [~]',
        'district': 'Disitulikiti [~]',
        'nationality': 'Obuwangwa [~]',
        'religion': 'Okusinza [~]',
        'next_of_kin': 'Owooluganda / Omwoyo [~]',
        'relationship': 'Enkolagana [~]',

        # Form navigation
        'save_draft': 'Tereka Ddaawe [~]',
        'next_step': 'Ennyingo Entandikwa [~]',
        'previous_step': 'Ennyingo Eyayita [~]',
        'submit_application': 'Waayo Okusaba [~]',
        'review_application': 'Kebera Okusaba [~]',
        'confirm_submit': 'Kakasa Okuwaayo [~]',
        'cancel': 'Sazaamu [~]',
        'back': 'Ddayo Eggya [~]',

        # Payment
        'payment_instructions': 'Amateeka g\'Okulipira [~]',
        'payment_reference': 'Ennamba y\'Okulipira [~]',
        'enter_reference': 'Yingiza Ennamba y\'Ekikolwa [~]',
        'upload_document': 'Yisa Ekitabo wamu ne Internet [~]',

        # File upload
        'file_too_large': 'Fayiro Enkulu Ennyo. Obunene obwa nkomanyi bwa [~]',
        'invalid_file_type': 'Ekika kya Fayiro Tekizuulika. Ebika byazuulika nga [~]',
        'required_field': 'Ekifo kino kikwetaagisa. [~]',
        'optional': 'Kiziyiza [~]',
        'upload_here': 'Yisa Wano [~]',

        # Form steps
        'step_personal': 'Ebikwata ku Muntu [~]',
        'step_academic': 'Nteekateeka y\'Okusoma [~]',
        'step_transfer': 'Ebikwata ku Kukyuka Essomero [~]',
        'step_documents': 'Ebitabo [~]',
        'step_payment': 'Okulipira [~]',
        'step_review': 'Kebera era Waayo [~]',

        # Application status labels
        'status_draft': 'Ddaawe [~]',
        'status_submitted': 'Yaayibwa [~]',
        'status_payment_pending': 'Okulipira Kukwegomba Okukakasibwa [~]',
        'status_under_review': 'Mu Kukebera [~]',
        'status_shortlisted': 'Galidde mu Kalamu [~]',
        'status_interview_scheduled': 'Olugendo lw\'Okukebera Luteekeddwa [~]',
        'status_accepted': 'Wakirizibwa [~]',
        'status_rejected': 'Gaanibwa [~]',
        'status_waitlisted': 'Erinnya lyo Lirinzirira mu Kalamu [~]',
        'status_withdrawn': 'Ggibwa [~]',

        # Transfer specific
        'transfer_question': 'Okyuka okuva mu ssomero lya mazima? [~]',
        'previous_school': 'Erinnya ly\'Essomero Eryayita [~]',
        'previous_district': 'Disitulikiti w\'Essomero Eryayita [~]',
        'headteacher_name': 'Erinnya ly\'Omulabirizi [~]',
        'school_contact': 'Ennamba y\'Essimu y\'Essomero [~]',
        'date_last_attended': 'Olunaku lw\'Okugenda ku Nkomerero [~]',
        'reason_leaving': 'Ensonga y\'Okuvaamu [~]',
        'disciplinary_issues': 'Waliwo Eby\'Okunyiigira? [~]',
        'outstanding_fees': 'Waliwo Musolo ogukyama? [~]',

        # Class / window selection
        'select_class': 'Londa Kisomero ky\'Oyagala Kuyingira [~]',
        'select_window': 'Londa Ekiseera ky\'Okuyingira [~]',

        # Language labels
        'english_label': 'Olungereza',
        'luganda_label': 'Oluganda',
        'runyakore_label': 'Runyakore-Rukiga [~]',

        # Confirmation
        'application_submitted': 'Okusaba Kwaaibwa mu Bulungi [~]',
        'congratulations': 'Nkwagalira! [~]',
        'your_app_number': 'Ennamba y\'Okusaba Kwo [~]',
        'what_next': 'Kiki Ekijja? [~]',
        'print_confirmation': 'Drukuma Ekakasibwa [~]',
        'download_confirmation': 'Kulula Ekakasibwa [~]',

        # Academic fields
        'ple_results': 'Ebikolwa bya PLE [~]',
        'uce_results': 'Ebikolwa bya UCE [~]',
        'uneb_index': 'Ennamba ya UNEB [~]',
        'former_school': 'Essomero Eryayita/Eriri Kati [~]',
        'current_school': 'Essomero Eriri Kati [~]',
        'current_class': 'Kisomero / Mwaka gw\'Oluvanyuma [~]',
        'subject_combination': 'Okukunganya kw\'Ebyokusomesebwa (S5/S6) [~]',
        'career_goals': 'Ebiragiro/Ebyemiri by\'Omukutu [~]',
        'academic_performance': 'Omulimu gw\'Okusoma [~]',

        # Document types
        'report_card': 'Ripoti y\'Essomero [~]',
        'transfer_letter': 'Ebbaluwa y\'Okukyuka [~]',
        'recommendation_letter': 'Ebbaluwa y\'Okusigala Bulungi [~]',
        'discipline_record': 'Endagaano y\'Enzikiriza [~]',
        'birth_certificate': 'Sitifikeeti y\'Okuzaalibwa [~]',
        'passport_photo': 'Foto ya Pasipoti [~]',
        'conduct_report': 'Ripoti y\'Enduga [~]',
        'academic_transcript': 'Endagaano y\'Okusoma [~]',
    },

    # -------------------------------------------------------------------------
    # RUNYAKORE-RUKIGA [~] = approximate translation – please verify with a native speaker
    # -------------------------------------------------------------------------
    'rk': {
        # Portal / General
        'portal_title': 'Orugyendo rw\'Okwongyera Abanyeshuri [~]',
        'apply_now': 'Saba Hano Hano [~]',
        'application_portal': 'Orugyendo rw\'Okusaba kuri Internet [~]',
        'open_windows': 'Ebiseera by\'Okwongyera Ebyaguruwe [~]',
        'no_open_windows': 'Nta biseera by\'okwongyera ebyaguruwe hano hano. Garuka hanyuma. [~]',
        'status_check': 'Rora Embeera y\'Okusaba Kwaawe [~]',
        'check_status': 'Goberera Okusaba Kwaawe [~]',
        'application_number': 'Omutono gw\'Okusaba [~]',
        'enter_app_number': 'Handika omutono gw\'okusaba kwawe [~]',
        'enter_email': 'Handika aadresi yawe y\'imeyili [~]',
        'closed': 'Nifungirwe [~]',
        'open': 'Yaaguriwe [~]',
        'seats_available': 'Ensi Ziribaho [~]',
        'no_seats': 'Nta nsi ziribaho [~]',
        'deadline': 'Oruhande rw\'Enkomerero [~]',
        'fee_required': 'Emirimo y\'Okusaba Erikwetaagisibwa [~]',
        'no_fee': 'Nta Mirimo y\'Okusaba [~]',
        'interview_required': 'Okubuuzibwa Kukwetaagisibwa [~]',

        # Auth
        'login': 'Ingira [~]',
        'register': 'Ihandikire [~]',
        'logout': 'Sohoka [~]',
        'my_applications': 'Okusaba Kwange [~]',
        'dashboard': 'Orugyendo rw\'Okukora [~]',
        'password': 'Ekigambo ky\'Okurinda [~]',
        'confirm_password': 'Kakasa Ekigambo ky\'Okurinda [~]',
        'create_account': 'Hanga Akawunti [~]',
        'already_have_account': 'Oine Akawunti Nariho? [~]',
        'login_link': 'Ingira Hano [~]',
        'no_account_yet': 'Torine Akawunti Nariho? [~]',
        'register_link': 'Ihandikire Hano [~]',
        'forgot_password': 'Wiire Ekigambo ky\'Okurinda? [~]',

        # Personal info fields
        'full_name': 'Orutuuro Rwona [~]',
        'first_name': 'Orutuuro rw\'Okutandikira [~]',
        'last_name': 'Orutuuro rw\'Eka [~]',
        'date_of_birth': 'Eizooba ry\'Okuzaarwa [~]',
        'gender': 'Ekicweka [~]',
        'phone': 'Omutono gwa Simu [~]',
        'email': 'Aadresi y\'Imeyili [~]',
        'district': 'Disiturikiti [~]',
        'nationality': 'Obwenegura [~]',
        'religion': 'Obusingwa [~]',
        'next_of_kin': 'Omufurwa / Omushomborwa [~]',
        'relationship': 'Enkoragana [~]',

        # Form navigation
        'save_draft': 'Bika Baaruwa y\'Okutandika [~]',
        'next_step': 'Ekigera Ekiri Aho Hejuru [~]',
        'previous_step': 'Ekigera Ekiyahoire [~]',
        'submit_application': 'Reeta Okusaba [~]',
        'review_application': 'Rora Okusaba [~]',
        'confirm_submit': 'Kakasa Okureetera [~]',
        'cancel': 'Sazaamu [~]',
        'back': 'Garuka Enyuma [~]',

        # Payment
        'payment_instructions': 'Amateeka g\'Okuriha [~]',
        'payment_reference': 'Omutono gw\'Okuriha [~]',
        'enter_reference': 'Handika Omutono gw\'Ekikolwa [~]',
        'upload_document': 'Teekaaho Pepa kuri Internet [~]',

        # File upload
        'file_too_large': 'Fairu Nkuru Ennyo. Obunene bw\'Enkomerero bwa [~]',
        'invalid_file_type': 'Ekicweka ky\'Efairu Kyiremeire. Ebicweka byemeire nga [~]',
        'required_field': 'Ekifo eki kikwetaagisibwa. [~]',
        'optional': 'Eki Nikiremwa [~]',
        'upload_here': 'Teekaaho Hano [~]',

        # Form steps
        'step_personal': 'Ebirikwata ku Muntu [~]',
        'step_academic': 'Amaani g\'Okuiga [~]',
        'step_transfer': 'Ebirikwata ku Kukyura Eishooto [~]',
        'step_documents': 'Ebitabo/Amapepa [~]',
        'step_payment': 'Okuriha [~]',
        'step_review': 'Rora no Reeta [~]',

        # Application status labels
        'status_draft': 'Baaruwa y\'Okutandika [~]',
        'status_submitted': 'Yareetwa [~]',
        'status_payment_pending': 'Okuriha Kukwetaagira Kakaswa [~]',
        'status_under_review': 'Mu Kurora [~]',
        'status_shortlisted': 'Bagabiirwe mu Rukaramu [~]',
        'status_interview_scheduled': 'Okubuuzibwa Kuteekwa [~]',
        'status_accepted': 'Yakiririwe [~]',
        'status_rejected': 'Yakyamiriwe [~]',
        'status_waitlisted': 'Orutuuro Rwawe Rurikureeba mu Rukaramu [~]',
        'status_withdrawn': 'Yakigwa [~]',

        # Transfer specific
        'transfer_question': 'Oja kukyura okuva mu ishuri rya mazima? [~]',
        'previous_school': 'Eizina ry\'Ishuri Eryahoire [~]',
        'previous_district': 'Disiturikiti y\'Ishuri Eryahoire [~]',
        'headteacher_name': 'Eizina ry\'Omukuru w\'Ishuri [~]',
        'school_contact': 'Omutono gwa Simu y\'Ishuri [~]',
        'date_last_attended': 'Eizooba ry\'Okugenda Ery\'Enkomerero [~]',
        'reason_leaving': 'Empamvu y\'Okuva [~]',
        'disciplinary_issues': 'Mwariho Eby\'Emitwaro Mibii? [~]',
        'outstanding_fees': 'Mwariho Oruhande rw\'Emirimo? [~]',

        # Class / window selection
        'select_class': 'Handura Ekibiina ky\'Oyagira Kwingira [~]',
        'select_window': 'Handura Ekiseera ky\'Okwongyerwa [~]',

        # Language labels
        'english_label': 'Icongereza [~]',
        'luganda_label': 'Oluganda [~]',
        'runyakore_label': 'Runyakore-Rukiga',

        # Confirmation
        'application_submitted': 'Okusaba Kwaareetwa Bworogyerwe [~]',
        'congratulations': 'Niikukunda! / Ishimwe! [~]',
        'your_app_number': 'Omutono gw\'Okusaba Kwaawe [~]',
        'what_next': 'Orikora Eki Hanyuma? [~]',
        'print_confirmation': 'Drukuma Ekakasiibwe [~]',
        'download_confirmation': 'Kulula Ekakasiibwe [~]',

        # Academic fields
        'ple_results': 'Ebikolwa bya PLE [~]',
        'uce_results': 'Ebikolwa bya UCE [~]',
        'uneb_index': 'Omutono gwa UNEB [~]',
        'former_school': 'Ishuri Eryahoire / Eriri Hano Hano [~]',
        'current_school': 'Ishuri Eriri Hano Hano [~]',
        'current_class': 'Ekibiina / Omwaka Omuhoire [~]',
        'subject_combination': 'Okukunganya kw\'Ebyokusomeswa (S5/S6) [~]',
        'career_goals': 'Ebiragiro by\'Omukutu [~]',
        'academic_performance': 'Omukoro gw\'Okuiga [~]',

        # Document types
        'report_card': 'Ripoti y\'Ishuri [~]',
        'transfer_letter': 'Baruwa y\'Okukyura [~]',
        'recommendation_letter': 'Baruwa y\'Okusiimibwa [~]',
        'discipline_record': 'Endagaano y\'Emitwaro [~]',
        'birth_certificate': 'Sitifikeeti y\'Okuzaarwa [~]',
        'passport_photo': 'Foto ya Pasipoti [~]',
        'conduct_report': 'Ripoti y\'Enduga [~]',
        'academic_transcript': 'Endagaano y\'Okuiga [~]',
    },
}
