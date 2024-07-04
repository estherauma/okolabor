from django.contrib import messages
from django.shortcuts import render,redirect
from .forms import ResetPasswordForm

# Create your views here.
def index(request):
    return render(request, 'ltr/index.html')

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
            print(form.cleaned_data['email'])
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

def login(request):
    return render(request, 'ltr/login.html')

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

def profile(request):
    return render(request, 'ltr/profile.html')

def progress(request):
    return render(request, 'ltr/progress.html')

def rangeslider(request):
    return render(request, 'ltr/rangeslider.html')

def rating(request):
    return render(request, 'ltr/rating.html')

def register(request):
    return render(request, 'ltr/register.html')

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
def workers(request):
    return render(request, 'workers/workers.html')

def worker_details(request):
    return render(request, 'worker-details/worker-details.html')

def employer_list(request):
    return render(request, 'employer-list/employer-list.html')
  
def employer_details(request):
    return render(request, 'employer/employer-details.html')

def worker_requests(request):
    return render(request, 'workers/worker-requests.html')

def worker_requests_details(request):
    return render(request, 'workers/worker-requests-details.html')

def users(request):
    return render(request, 'users/users.html')
