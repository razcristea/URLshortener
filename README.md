<h1 align="center"> URLshortener</h>
<h3 align="center">simple URL shortening application using Django<h3>

<p align="center">
  <img src="https://img.shields.io/github/repo-size/razcristea/URLshortener?color=green" /> <img src="https://img.shields.io/github/license/razcristea/URLshortener" /> <img src="https://img.shields.io/badge/python-3.7-green?logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/debian-VPS-red?logo=debian&logoColor=white" /> <img src="https://img.shields.io/badge/Django-framework-red?logo=django&logoColor=white" />
</p>

<p align="center"><a href="http://www.razvancristea.ro/URLshorten/" target="_blank"><img src="https://i.postimg.cc/sxGMNFrh/urlshorten.png" width="500px"/></a></p>

## Description
<a href="http://www.razvancristea.ro/URLshorten/" target="_blank">URLshortener</a> is a basic URL shortener app created in Django.

A step-by-step explanation of implementation is described in `views.py`:

```python
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
```
## Production deployment

The production server is a debian VPS with Apache server that has mod_wsgi installed using CMMI method (configure, make, make install) in order to reduce the possible incompatibilities with Apache and/or python3. 

The server runs also other flask applications, so mod_wsgi is configured so that each application runs in Daemon Mode. Furthermore, each application has its own virtualenv - that way each application has its own modules installed and activated. As a caution measure, virtualenv is activated from within WSGI file for each application, but the main WSGI file also has `python-home` directive declared, but it points to an empty python virtual environment (with no modules installed other than standard). The reason for that configuration choice is that if one forgets to specify some package in `requirements.txt` to be installed using `pip install -r requirements.txt`, but the package is installed under the main python installation, there might be the wrong version or have dependencies on versions you have different package versions installed.

This is how the virtualenv is activated from wsgi.py on the production server:

```python
python_home='/path/to/the/djangoproject/venv'
activate_this=python_home+'/bin/activate_this.py'
with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))
```
and the file continues with regular import of the application, as described in django documentation:
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoproject.settings')
application = get_wsgi_application()
```
Note that because mod_wsgi is configured to run in Daemon Mode, there was no need to alter the `os.environ` line.

After starting the server I got some error, so I had to add those lines to `wsgi.py` file:
```python
import sys
sys.path.append('/path/to/the/djangoproject')
```
Note that there is `/path/to/the/djangoproject` , not `/path/to/the/djangoproject/djangoproject` as this will return some ImportError!

Another challenge was the Server Error when clicking the "Shorten" button - that was because the app was trying to write a readonly database file. Of course that for a real production environment a database server would've been used, but for testing purposes I moved the database file inside a folder and `chown` both the file and folder to `www-data`. There was no need to change permissions using `chmod 777`(DO NOT do that!) or `chmod 664`, so I left the 644 permissions in place.

Also, when deploying and setting `DEBUG = False`, one should edit `ALLOWED_HOSTS = []` and add your domain name (it's a good practice to add it as `'.domain.com'` with a dot in front - as a wildcard)
