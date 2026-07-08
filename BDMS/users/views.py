from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core import signing
from django.urls import reverse
import logging

from .forms import SignUpForm, LoginForm, PasswordLoginForm, UserProfileForm, UserLoginForm, UserRegistrationForm
from .models import UserProfile
from .utils import create_user_profile, get_client_ip

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Direct login view using Email and Password"""
    if request.user.is_authenticated:
        return redirect('documents:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Check if user exists by email lookup
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                messages.error(request, "Account does not exist. Please register first.")
                return render(request, 'users/login.html', {'form': form, 'page_title': 'Login'})
            
            # Authenticate using Django auth with actual username field
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user is not None:
                if not authenticated_user.is_active:
                    messages.error(request, "This account is inactive. Please verify your email first.")
                    return render(request, 'users/login.html', {'form': form, 'page_title': 'Login'})
                
                login(request, authenticated_user)
                
                # Check if this user is using a temporary password
                if hasattr(authenticated_user, 'profile') and authenticated_user.profile.is_temp_password:
                    request.session['show_password_change_popup'] = True
                    
                messages.success(request, f"Welcome back, {authenticated_user.first_name or authenticated_user.profile.username}!")
                return redirect('documents:dashboard')
            else:
                messages.error(request, "Incorrect password. Please try again.")
    else:
        form = UserLoginForm()
        
    return render(request, 'users/login.html', {'form': form, 'page_title': 'Login'})


@require_http_methods(["GET"])
def verify_link_view(request, token):
    """Stage 2: Verify signed token from link, generate temporary password, and email it"""
    if request.user.is_authenticated:
        return redirect('documents:dashboard')

    # Decode and verify the link token (valid for 30 minutes)
    try:
        data = signing.loads(token, max_age=1800)
        email = data['email']
    except signing.SignatureExpired:
        messages.error(request, "This verification link has expired. Please request a new one.")
        return redirect('users:login')
    except signing.BadSignature:
        messages.error(request, "Invalid verification link. Please check the URL and try again.")
        return redirect('users:login')

    # Check if user exists in the database by email
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        messages.error(request, "Account details associated with this link were not found. Please register again.")
        return redirect('users:login')

    if user.is_active and not user.profile.is_temp_password:
        messages.info(request, "This account is already verified and active. Please log in.")
        return redirect('users:login')

    # Generate a random 10-character temporary password
    import random
    import string
    chars = string.ascii_letters + string.digits
    temp_password = ''.join(random.choices(chars, k=10))

    # Update User and UserProfile password, activate user
    user.set_password(temp_password)
    user.is_active = True
    user.save()

    profile = user.profile
    profile.password = temp_password
    profile.is_active = True
    profile.is_temp_password = True
    profile.save()

    logger.info(f"Verified and activated user '{profile.username}'. Generated temporary password.")

    # Send temporary password via email
    subject = 'SmartTrack IIMS - Portal Temporary Password'
    message = (
        f"Hello {profile.username},\n\n"
        f"Your email address has been verified successfully. Your account is now active.\n\n"
        f"Your temporary password to log in:\n"
        f"Temporary Password: {temp_password}\n\n"
        f"Please go to the login page and sign in using your username, email, and this temporary password:\n"
        f"{request.build_absolute_uri(reverse('users:login'))}\n\n"
        f"Upon logging in, you will be prompted to change your password.\n\n"
        f"Thank you,\n"
        f"IT Directorate, RDSO Ministry of Railways"
    )
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@rdso.railnet.gov.in')
    
    email_failed = False
    try:
        send_mail(
            subject,
            message,
            from_email,
            [email],
            fail_silently=False,
        )
        logger.info(f"Temporary password sent to {email} successfully.")
    except Exception as e:
        logger.error(f"Failed to send temporary password email to {email}: {e}")
        email_failed = True

    if email_failed:
        return render(request, 'users/verification_success.html', {
            'username': profile.username,
            'email': email,
            'temp_password': temp_password,
            'page_title': 'Account Verified'
        })
    else:
        messages.success(request, "Email verified successfully! We have sent your temporary login password to your registered email.")
        return redirect('users:login')


@login_required(login_url='users:login')
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')


@require_http_methods(["GET", "POST"])
def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('documents:dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            
            # Check if email already exists
            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, "Account with this email address already exists. Please sign in.")
                return render(request, 'users/signup.html', {'form': form, 'page_title': 'Register'})
                
            try:
                # Create user as inactive, using email as the Django username
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    password=None,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=False
                )
                
                # Retrieve profile (created by signal) and set username/email/is_active
                profile = user.profile
                profile.username = username
                profile.email = email
                profile.phone = phone
                profile.password = ""  # Initial password is not set
                profile.is_active = False
                profile.is_temp_password = False
                profile.save()
                
                logger.info(f"Created inactive user '{username}' with email '{email}'.")
            except Exception as e:
                logger.error(f"Failed to create user account: {e}")
                messages.error(request, f"Failed to create account: {str(e)}")
                return render(request, 'users/signup.html', {'form': form, 'page_title': 'Register'})
            
            # Generate signed token valid for 30 minutes
            token = signing.dumps({
                'email': email
            })
            
            # Build absolute verification link
            verify_url = request.build_absolute_uri(
                reverse('users:verify_link', args=[token])
            )
            
            # Send verification link via email
            subject = 'SmartTrack IIMS - Portal Email Verification'
            message = (
                f"Hello {username},\n\n"
                f"Thank you for registering on the SmartTrack portal. Please click the link below to verify your email address:\n"
                f"{verify_url}\n\n"
                f"This link is valid for 30 minutes.\n\n"
                f"Thank you,\n"
                f"IT Directorate, RDSO Ministry of Railways"
            )
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@rdso.railnet.gov.in')
            
            email_failed = False
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [email],
                    fail_silently=False,
                )
                logger.info(f"Verification email sent to {email} successfully.")
            except Exception as e:
                logger.error(f"Failed to send verification email to {email}: {e}")
                email_failed = True
                
            return render(request, 'users/link_sent.html', {
                'email': email,
                'verify_url': verify_url,
                'email_failed': email_failed,
                'page_title': 'Verification Link Sent'
            })
    else:
        form = UserRegistrationForm()
        
    return render(request, 'users/signup.html', {'form': form, 'page_title': 'Register'})



@login_required(login_url='users:login')
def user_profile(request):
    """View and edit user profile"""
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            # Update user first and last name
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            
            # Sync email and password back to the standard auth User model
            if profile.email:
                request.user.email = profile.email
                request.user.username = profile.email
            if profile.password and not request.user.check_password(profile.password):
                request.user.set_password(profile.password)
                profile.is_temp_password = False
                profile.save()
                # Keep user session active after updating password
                update_session_auth_hash(request, request.user)
                
            request.user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)
    
    context = {
        'form': form,
        'profile': profile,
        'page_title': 'User Profile',
    }
    return render(request, 'users/profile.html', context)


@login_required(login_url='users:login')
@require_http_methods(["GET", "POST"])
def complete_profile_view(request):
    """Stage 3: Complete profile details for newly registered users"""
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        
        if not first_name or not last_name:
            messages.error(request, "First Name and Last Name are required.")
            return render(request, 'users/complete_profile.html', {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'email': email or request.user.email,
                'page_title': 'Complete Registration'
            })
            
        # Update User model fields
        request.user.first_name = first_name
        request.user.last_name = last_name
        if email:
            request.user.email = email
            request.user.username = email
        request.user.save()
        
        # Update UserProfile model fields
        if profile:
            profile.phone = phone
            if email:
                profile.email = email
            profile.save()
            
        messages.success(request, "Registration completed successfully! Welcome to SmartTrack.")
        return redirect('documents:dashboard')
        
    context = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': profile.phone if profile else '',
        'email': request.user.email,
        'page_title': 'Complete Registration'
    }
    return render(request, 'users/complete_profile.html', context)


@login_required(login_url='users:login')
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    """Change user password from dashboard"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Sync new password to UserProfile
            if hasattr(user, 'profile'):
                new_pwd = form.cleaned_data.get('new_password1')
                if new_pwd:
                    user.profile.password = new_pwd
                user.profile.is_temp_password = False
                user.profile.save()
            # Keep user session active after updating password
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('documents:dashboard')
        else:
            messages.error(request, 'Failed to update password. Please check form parameters.')
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'users/change_password.html', {
        'form': form,
        'page_title': 'Change Password'
    })



@require_http_methods(["GET"])
def generate_captcha_view(request):
    """Generate image CAPTCHA dynamically using Pillow"""
    import random
    import string
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    from django.http import HttpResponse
    
    # 1. Generate 5-character uppercase alphanumeric code
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    request.session['captcha_text'] = captcha_text
    
    # 2. Setup image dimensions and basic background
    width, height = 150, 48
    image = Image.new('RGB', (width, height), color='#f4f6f9')
    draw = ImageDraw.Draw(image)
    
    # 3. Draw text (using fallback defaults if standard Windows fonts are missing)
    font_paths = [
        "arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "LiberationSans-Regular.ttf"
    ]
    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, 28)
            break
        except IOError:
            continue
            
    if font is None:
        font = ImageFont.load_default()
        
    # Draw characters with slight rotation/random height changes
    for i, char in enumerate(captcha_text):
        x_pos = 20 + (i * 22)
        y_pos = random.randint(6, 12)
        draw.text((x_pos, y_pos), char, fill='#0b2240', font=font)
        
    # 4. Add Saffron noise lines (#e65100)
    for _ in range(4):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill='#e65100', width=2)
        
    # 5. Add Forest Green noise dots (#1b5e20)
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill='#1b5e20')
        
    # 6. Output image stream
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def change_password_popup_view(request):
    """Directly change user password from dashboard popup without needing old password"""
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')
    
    if not new_password or new_password != confirm_password:
        messages.error(request, "Passwords do not match or are invalid.")
        return redirect('documents:dashboard')
        
    user = request.user
    user.set_password(new_password)
    
    if hasattr(user, 'profile'):
        user.profile.password = new_password
        user.profile.is_temp_password = False
        user.profile.save()
    user.save()
    
    # Keep user session active
    update_session_auth_hash(request, user)
    
    # Clear session flag
    request.session.pop('show_password_change_popup', None)
    
    messages.success(request, "Your password has been changed successfully.")
    return redirect('documents:dashboard')


