from django.db.transaction import atomic
from django.shortcuts import render, redirect, reverse
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import NewFromURLForm, ListenerSettingsForm, AdminSettingsForm, SiteSettingsForm
from .models import Podcast, Episode, EpisodePlaybackState, Listener, PodcastsSettings
from .utils import refresh_feed, chunks

import json
import urllib


# Create your views here.
def index(request):
    # return render(request, 'index.html')
    return redirect('podcasts:podcasts-list')


def podcasts_list(request):
    queryset = Podcast.objects.order_by('title')

    paginator = Paginator(queryset, 5)

    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    return render(request, 'podcasts-list.html', {'items': items})


def podcasts_new(request):
    if request.method == 'POST':
        form = NewFromURLForm(request.POST, request.FILES)
        if form.is_valid():
            podcast = Podcast.objects.create_from_feed_url(
                form.cleaned_data['feed_url'],
                form.cleaned_data['info'])
            if request.user is not None:
                podcast.add_subscriber(request.user.listener)
                podcast.add_follower(request.user.listener)
            return redirect('podcasts:podcasts-details', slug=podcast.slug)
    else:
        form = NewFromURLForm()

    context = {
        'form': form,
    }
    return render(request, 'podcasts-new.html', context)


def podcasts_details(request, slug):
    podcast = get_object_or_404((
        Podcast.objects
        .prefetch_related('episodes', 'episodes')
        .prefetch_related('subscribers', 'subscribers')),
        slug=slug)

    user_is_subscriber = podcast.subscribers.filter(user=request.user).count() == 1
    episodes = podcast.episodes.order_by('-published')[:10]

    context = {
        'user_is_subscriber': user_is_subscriber,
        'podcast': podcast,
        'episodes': episodes,
    }
    return render(request, 'podcasts-details.html', context)


def podcasts_discover(request):
    url = 'https://rss.itunes.apple.com/api/v1/us/podcasts/top-podcasts/all/25/explicit.json'
    file, header = urllib.request.urlretrieve(url)

    if header['Status'] == '200 OK':
        with open(file) as fp:
            content = json.load(fp)
        feeds = list(chunks(content['feed']['results'], 3))

        context = {
            'content': content,
            'feeds': feeds
        }
        # print(urllib.request.urlretrieve(url)[0])
    else:
        context = {}
    return render(request, 'podcasts-discover.html', context)


def podcasts_refresh_feed(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    info = refresh_feed(object.feed_url)
    podcast.create_episodes(info)

    next = request.GET.get('next', '/')
    return redirect(next)


def settings(request):
    current_site_settings = get_current_site(request)
    current_podcasts_settings = current_site_settings.podcastssettings
    if request.method == 'POST':
        listener_form = ListenerSettingsForm(request.POST, request.FILES, instance=request.user.listener, prefix='listener')
        app_admin_form = AdminSettingsForm(request.POST, request.FILES, instance=current_podcasts_settings, prefix='app')
        site_admin_form = SiteSettingsForm(request.POST, request.FILES, instance=current_site_settings, prefix='site')

        if listener_form.is_valid() and (not request.user.is_superuser or (app_admin_form.is_valid() and site_admin_form.is_valid())):
            listener_form.save()

            if request.user.is_superuser:
                app_admin_form.save()
                site_admin_form.save()

            # do something with the cleaned_data on the formsets.
            next = request.GET.get('next', '/')
            return redirect(next)
    else:
        listener_form = ListenerSettingsForm(instance=request.user.listener, prefix='listener')
        app_admin_form = None
        site_admin_form = None
        if request.user.is_superuser:
            app_admin_form = AdminSettingsForm(instance=current_podcasts_settings, prefix='app')
            site_admin_form = SiteSettingsForm(instance=current_site_settings, prefix='site')

    return render(request, 'podcasts-settings.html', {'listener_form': listener_form,
                                                      'app_admin_form': app_admin_form,
                                                      'site_admin_form': site_admin_form})
