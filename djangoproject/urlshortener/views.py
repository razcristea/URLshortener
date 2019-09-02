import random, string, json
from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import render, redirect
from django.contrib import messages


from urlshortener.models import URLs
from urlshortener.forms import URLsForm, URLsFormPartial
# Create your views here.
def index(request):
    # If there is a POST call:
    if request.method == 'POST':
        # We instantiate an object of the URLsForm class, taking as argument the POST request
        form = URLsForm(request.POST)
        # and if the form is valid (there is a URL)
        if form.is_valid():
            # we assign the value from the form corresponding to "long_url"
            long_url = request.POST.get("long_url")
            # and we check to see if there is already a record of the same long_url in our db
            check_long = URLs.objects.filter(long_url=long_url).first()
            # and if we find a record,
            if check_long is not None:
                # we assign it's short_url value to short_url variable
                # no need to call form.save() as we don't want to enter another record in db for the same long_url
                short_url=check_long.short_url
            # if no record was found
            else:
                # we take the short_url value that was generated when the page loaded (hidden from browser)
                short_url = request.POST.get("short_url")
                # and we save to db the long_url&short_url pair values
                form.save()
            # now, it's time to get ready for delivering the URL for the user
            # by combining the 'http://domain.com/' with the short_url
            short_url = request.META['HTTP_REFERER']+short_url
            # we create a copy of the form data (as it is stored in a readonly dict)
            form.data = form.data.copy()
            # so we can alter the short_url and give it the full short URL we created earlier
            form.data['short_url']=short_url
            # we set the copy value to True, because in our template we have condition "if copy"
            copy = True
            # and we render index template, by passing the form containing the long_url entered by the user
            # and our full path short URL we created using str concatenation, and the value for copy being True
            return render(request, "urlshortener/index.html", {'form':form, 'copy':copy})
        else:
            # if there are errors (there is no url entered, we send a INFO message - could've been ERROR or SUCCESS)
            messages.add_message(request, messages.INFO, "URL invalid")
    # every time the page loads, a random string is generated and stored as
    random_string = str(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
)
    # as short_url in the form, but it is hidden from the user (can be seen using View Page Source)
    form = URLsFormPartial(initial = {'short_url': random_string })
    # and a template with the form is rendered every time there is a GET request
    return render(request, "urlshortener/index.html", {'form':form})


def goto(request, short_url):
    # This is the redirect function that takes the /short_url value as a parameter
    try:
        # we check to see if we have such a short_url in our database
        check_url = URLs.objects.get(short_url=short_url)
    # and if we don't
    except URLs.DoesNotExist:
        # we raise a 404 Not Found error
        raise Http404('Url does not match to any record in database')
    # but if we have that short_url, we take the corresponding long_url and redirect user to
    return redirect(to=check_url.long_url)
