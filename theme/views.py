from django.shortcuts import render,redirect
from .forms import RegistrationForm, LoginForm, ResetPasswordForm,FilterWorkExperienceForm,AdvancedFilterForm
from django.contrib import messages
from .forms import ResetPasswordForm,LoginForm
from django.contrib.auth import authenticate,login as auth_login,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from account.models import UserWorkExperience,UserJobExperience,UserJobExperienceDetails,UserNotification,UserPreference,UserNotification,UserDocuments,UserNotification
from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
import requests
from django.db.models import Prefetch

# Create your views here.
@login_required(login_url='/')
def index(request):
    return render(request, 'ltr/index.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out', extra_tags='bg-success')
    return redirect('/')

def about(request):
    return render(request, 'ltr/about.html')

def accordion(request):
    return render(request, 'ltr/accordion.html')

def alerts(request):
    return render(request, 'ltr/alerts.html')

def avatarradius(request):
    return render(request, 'ltr/avatarradius.html')

def avatarround(request):
    return render(request, 'ltr/avatarround.html')

def avatarsquare(request):
    return render(request, 'ltr/avatarsquare.html')

def badge(request):
    return render(request, 'ltr/badge.html')

def blog(request):
    return render(request, 'ltr/blog.html')

def breadcrumbs(request):
    return render(request, 'ltr/breadcrumbs.html')

def buttons(request):
    return render(request, 'ltr/buttons.html')

def calendar(request):
    return render(request, 'ltr/calendar.html')

def calendar2(request):
    return render(request, 'ltr/calendar2.html')

def cards(request):
    return render(request, 'ltr/cards.html')

def carousel(request):
    return render(request, 'ltr/carousel.html')

def cart(request):
    return render(request, 'ltr/cart.html')

def chart(request):
    return render(request, 'ltr/chart.html')

def chartchartist(request):
    return render(request, 'ltr/chartchartist.html')

def chartdonut(request):
    return render(request, 'ltr/chartdonut.html')

def chartechart(request):
    return render(request, 'ltr/chartechart.html')

def chartflot(request):
    return render(request, 'ltr/chartflot.html')

def chartline(request):
    return render(request, 'ltr/chartline.html')

def chartmorris(request):
    return render(request, 'ltr/chartmorris.html')

def chartnvd3(request):
    return render(request, 'ltr/chartnvd3.html')

def chartpie(request):
    return render(request, 'ltr/chartpie.html')

def charts(request):
    return render(request, 'ltr/charts.html')

def chat(request):
    return render(request, 'ltr/chat.html')

def checkout(request):
    return render(request, 'ltr/checkout.html')

def colors(request):
    return render(request, 'ltr/colors.html')

def construction(request):
    return render(request, 'ltr/construction.html')

def counters(request):
    return render(request, 'ltr/counters.html')

def cryptocurrencies(request):
    return render(request, 'ltr/cryptocurrencies.html')

def datatable(request):
    return render(request, 'ltr/datatable.html')

def dropdown(request):
    return render(request, 'ltr/dropdown.html')

def editprofile(request):
    return render(request, 'ltr/editprofile.html')

def email(request):
    return render(request, 'ltr/email.html')

def emailservices(request):
    return render(request, 'ltr/emailservices.html')

def empty(request):
    return render(request, 'ltr/empty.html')

def error400(request):
    return render(request, 'ltr/error400.html')

def error401(request):
    return render(request, 'ltr/error401.html')

def error403(request):
    return render(request, 'ltr/error403.html')

def error404(request):
    return render(request, 'ltr/error404.html')

def error500(request):
    return render(request, 'ltr/error500.html')

def error503(request):
    return render(request, 'ltr/error503.html')

def faq(request):
    return render(request, 'ltr/faq.html')

def footers(request):
    return render(request, 'ltr/footers.html')

def forgotpassword(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            return redirect('login')
    else:
        form = ResetPasswordForm()
    return render(request, 'ltr/forgotpassword.html', {'form': form})

def formadvanced(request):
    return render(request, 'ltr/formadvanced.html')

def formelements(request):
    return render(request, 'ltr/formelements.html')

def formvalidation(request):
    return render(request, 'ltr/formvalidation.html')

def formwizard(request):
    return render(request, 'ltr/formwizard.html')

def gallery(request):
    return render(request, 'ltr/gallery.html')

def headers(request):
    return render(request, 'ltr/headers.html')

def icons(request):
    return render(request, 'ltr/icons.html')

def icons2(request):
    return render(request, 'ltr/icons2.html')

def icons3(request):
    return render(request, 'ltr/icons3.html')

def icons4(request):
    return render(request, 'ltr/icons4.html')

def icons5(request):
    return render(request, 'ltr/icons5.html')

def icons6(request):
    return render(request, 'ltr/icons6.html')

def icons7(request):
    return render(request, 'ltr/icons7.html')

def icons8(request):
    return render(request, 'ltr/icons8.html')

def icons9(request):
    return render(request, 'ltr/icons9.html')

def icons10(request):
    return render(request, 'ltr/icons10.html')

def invoice(request):
    return render(request, 'ltr/invoice.html')

def list(request):
    return render(request, 'ltr/list.html')

def loaders(request):
    return render(request, 'ltr/loaders.html')

def lockscreen(request):
    return render(request, 'ltr/lockscreen.html')

User = get_user_model() 
def login(request):
    
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':

        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                
                form.add_error('email', "User with this email does not exist.")
                return render(request, 'ltr/login.html', {'form': form})
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'You have successfully logged in')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                
                form.add_error('password', "Incorrect password.")
        else:
            
            return render(request, 'ltr/login.html', {'form': form})
    else:
        form = LoginForm()

    return render(request, 'ltr/login.html', {'form': form})

def maps(request):
    return render(request, 'ltr/maps.html')

def maps1(request):
    return render(request, 'ltr/maps1.html')

def maps2(request):
    return render(request, 'ltr/maps2.html')

def mediaobject(request):
    return render(request, 'ltr/mediaobject.html')

def modal(request):
    return render(request, 'ltr/modal.html')

def navigation(request):
    return render(request, 'ltr/navigation.html')

def notify(request):
    return render(request, 'ltr/notify.html')

def pagination(request):
    return render(request, 'ltr/pagination.html')

def panels(request):
    return render(request, 'ltr/panels.html')

def pricing(request):
    return render(request, 'ltr/pricing.html')

@login_required
def profile(request):
    user = request.user
    user_notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')
    documents = UserDocuments.objects.filter(user=request.user)

    work_preferences = UserPreference.objects.filter(user=request.user)
   
    latest = AggregatedContent.objects.latest('created_at')
    serializer = AggregatedContentSerializer(latest, many=False)
    aggregated_data = serializer.data
    content = aggregated_data.get('content')
    english_content = content.get('en')
    
    work_preferenece_step_one = english_content.get('workPreferenceStepOne')
    work_preference_step_one_questions = work_preferenece_step_one.get('form_questions')
    work_preferenece_step_two = english_content.get('workPreferenceStepTwo')
    work_preference_step_two_questions = work_preferenece_step_two.get('form_questions')
    preference_questions = work_preference_step_one_questions + work_preference_step_two_questions
    
    work_experiences = UserWorkExperience.objects.filter(user=user).prefetch_related(
        Prefetch(
            'crop_experiences',
            queryset=UserJobExperience.objects.prefetch_related(
                Prefetch(
                    'job_experience_details',
                    queryset=UserJobExperienceDetails.objects.filter(is_attachment=False)
                )
            )
        )
    )
    
    context = {
        'first_name': user.first_name if user.first_name else None,
        'last_name': user.last_name if user.last_name else None,
        'middle_name': user.middle_name if user.middle_name else None,
        'email': user.email if user.email else None,
        'dob': user.dob if user.dob else None,
        'gender': user.gender if user.gender else None,
        'telephone': user.telephone if user.telephone else None,
        'address_line_1': user.address_line_1 if user.address_line_1 else None,
        'address_line_2': user.address_line_2 if user.address_line_2 else None,
        'city': user.city if user.city else None,
        'user_notifications': user_notifications,
        'documents': documents,
        'work_preferences': work_preferences,
        'preference_questions': preference_questions,
        'user_notifications': user_notifications,
        'work_experiences': work_experiences,
        
    }

    return render(request, 'ltr/profile.html', context)

def progress(request):
    return render(request, 'ltr/progress.html')

def rangeslider(request):
    return render(request, 'ltr/rangeslider.html')

def rating(request):
    return render(request, 'ltr/rating.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            return redirect('login')
        else:
            messages.error(request, form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'ltr/register.html', {'form': form})

def scroll(request):
    return render(request, 'ltr/scroll.html')

def search(request):
    return render(request, 'ltr/search.html')

def services(request):
    return render(request, 'ltr/services.html')

def shop(request):
    return render(request, 'ltr/shop.html')

def shopdescription(request):
    return render(request, 'ltr/shopdescription.html')

def sweetalert(request):
    return render(request, 'ltr/sweetalert.html')

def tables(request):
    return render(request, 'ltr/tables.html')

def tabs(request):
    return render(request, 'ltr/tabs.html')

def tags(request):
    return render(request, 'ltr/tags.html')

def terms(request):
    return render(request, 'ltr/terms.html')

def thumbnails(request):
    return render(request, 'ltr/thumbnails.html')

def timeline(request):
    return render(request, 'ltr/timeline.html')

def tooltipandpopover(request):
    return render(request, 'ltr/tooltipandpopover.html')

def treeview(request):
    return render(request, 'ltr/treeview.html')

def typography(request):
    return render(request, 'ltr/typography.html')

def userslist(request):
    return render(request, 'ltr/userslist.html')

def widgets(request):
    return render(request, 'ltr/widgets.html')

def wishlist(request):
    return render(request, 'ltr/wishlist.html')

def wysiwyag(request):
    return render(request, 'ltr/wysiwyag.html')

def employer_list(request):
    return render(request, 'employer-list/employer-list.html')




def users(request):
    return render(request, 'users/users.html')


def add_worker(request):
    return render(request, 'workers/add-workers.html')
  
def worker_request_form(request):
    return render(request, 'workers/worker-request-form.html')

@login_required
def work_experience(request):
    return render(request, 'workers/work-experience.html')

def edit_experience(request):
    return render(request, 'workers/edit-work-experience.html')

@login_required
def user_documents(request):
    return render(request,'ltr/userdocuments.html')

@login_required
def work_preferences(request):
    
    return render(request,'ltr/workpreferences.html')


def notifications(request):
    return render(request,'ltr/notifications.html')

def custom_password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                html_email_template_name='ltr/password_reset_email.html',
                
            )
            return redirect(reverse_lazy('password_reset_done'))
    else:
        form = PasswordResetForm()
    
    return render(request, 'ltr/password_reset_form.html', {'form': form})
