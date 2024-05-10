from django.shortcuts import render
from django.db.models import Subquery, Count, Q, Min
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from spotify_library.models import *


@login_required
def archive(request):

    user_settings = UserSettings.objects.filter(user = request.user)
    if not user_settings:
        is_library_created = False
        genres = None
        if request.method == "POST":
            return redirect("spotify_auth:authorization")
    else:
        is_library_created = True
        genres = get_genres(request)
        if request.method == "POST":
            selected_genre = request.POST["selected_genre"]
            return redirect('sound_archive:archive_genres', selected_genre = selected_genre)
    return render(request, "archive.html", {"genres": genres, "is_library_created": is_library_created})


@login_required
def archive_genres(request, selected_genre):

    user_settings = UserSettings.objects.filter(user = request.user)
    if not user_settings:
        return redirect('sound_archive:archive')
    else:
        is_library_created = True
        genres = get_genres(request)
        # if selected_genre not in genres:
        #     abort(404)
        # print(selected_genre)
        subgenres = get_subgenres(request, selected_genre)
        if request.method == "POST":
            new_selected_genre = request.POST.get("selected_genre", None)
            selected_subgenre = request.POST.get("selected_subgenre", None)
            if new_selected_genre:
                return redirect('sound_archive:archive_genres', selected_genre = new_selected_genre)
            else:
                return redirect('sound_archive:archive_subgenres', selected_genre = selected_genre, selected_subgenre = selected_subgenre)    
    return render(request, "archive.html", {
        "genres": genres,
        "subgenres": subgenres,
        "is_library_created": is_library_created,
        "selected_genre": selected_genre
        })


@login_required
def archive_subgenres(request, selected_genre, selected_subgenre):

    user_settings = UserSettings.objects.filter(user = request.user)
    if not user_settings:
        return redirect('sound_archive:archive')
    else:
        is_library_created = True
        genres = get_genres(request)
        # if selected_genre not in genres:
        #     abort(404)
        # print(selected_genre)
        subgenres = get_subgenres(request, selected_genre)
        # if selected_subgenre not in subgenres:
        #     abort(404)
        artists = get_artists_of_selected_subgenre(request, selected_genre, selected_subgenre)

        if request.method == "POST":
            new_selected_genre = request.POST.get("selected_genre", None)       
            new_selected_subgenre = request.POST.get("selected_subgenre", None)
            selected_artist_uri = request.POST.get("selected_artist_uri", None)
            if new_selected_genre:
                return redirect('sound_archive:archive_genres', selected_genre = new_selected_genre)
            elif new_selected_subgenre:
                return redirect('sound_archive:archive_subgenres', selected_genre = selected_genre, selected_subgenre = selected_subgenre)
            else:
                request.session["selected_artist_uri"] = selected_artist_uri
                selected_artist_name = request.POST.get("selected_artist_name")
                request.session["selected_artist_name"] = selected_artist_name
                selected_artist_name = encode_characters(selected_artist_name)
                return redirect('sound_archive:archive_tracks', selected_genre = selected_genre, selected_subgenre = selected_subgenre, selected_artist_name = selected_artist_name)
    return render(request, "archive.html", {
        "genres": genres,
        "subgenres": subgenres,
        "artists": artists,
        "is_library_created": is_library_created,
        "selected_genre": selected_genre,
        "selected_subgenre": selected_subgenre
        })


@login_required
def archive_tracks(request, selected_genre, selected_subgenre, selected_artist_name):

    user_settings = UserSettings.objects.filter(user = request.user)
    if not user_settings:
        return redirect('sound_archive:archive')
    else:
        is_library_created = True
        genres = get_genres(request)
        # if selected_genre not in genres:
        #     abort(404)
        subgenres = get_subgenres(request, selected_genre)
        # if selected_subgenre not in subgenres:
        #     abort(404)

        selected_artist_name = request.session["selected_artist_name"]
        artists = get_artists_of_selected_subgenre(request, selected_genre, selected_subgenre)
        selected_artist_uri = request.session["selected_artist_uri"]
        # if (selected_artist_uri, selected_artist_name) not in artists:
        #     abort(404)

        if (selected_artist_uri, selected_artist_name) != ("Loose tracks", "Loose tracks"):
            tracklist = get_tracks_of_artist(request, selected_artist_uri)
            tracklist_featured = []
            tracklist_featured = get_featured_tracks_of_artist(request, selected_artist_name)
        else:
            tracklist = get_loose_tracks_for_subgenre(request, selected_genre, selected_subgenre)
            tracklist_featured = []

        if request.method == "POST":
            new_selected_genre = request.POST.get("selected_genre", None)
            new_selected_subgenre = request.POST.get("selected_subgenre", None)
            new_selected_artist_uri = request.POST.get("selected_artist_uri", None)

            del request.session["selected_artist_uri"]
            del request.session["selected_artist_name"]

            if new_selected_genre:
                return redirect('sound_archive:archive_genres', selected_genre = new_selected_genre)
            elif new_selected_subgenre:
                return redirect('sound_archive:archive_subgenres', selected_genre = selected_genre, selected_subgenre = selected_subgenre)
            else:
                request.session["selected_artist_uri"] = new_selected_artist_uri
                selected_artist_name = request.POST.get("selected_artist_name")
                request.session["selected_artist_name"] = selected_artist_name
                new_selected_artist_name = encode_characters(selected_artist_name)
                return redirect('sound_archive:archive_tracks', selected_genre = selected_genre, selected_subgenre = selected_subgenre, selected_artist_name = new_selected_artist_name)       

    return render(request, "archive.html", {
        "genres": genres,
        "subgenres": subgenres,
        "artists": artists,
        "tracklist": tracklist,
        "tracklist_featured": tracklist_featured,
        "is_library_created": is_library_created,
        "selected_genre": selected_genre,
        "selected_subgenre": selected_subgenre,
        "selected_artist_uri": selected_artist_uri,
        "selected_artist_name": selected_artist_name
        })


def encode_characters(param):
    param = param.replace(' ', "-")
    param = param.replace('&', "and")
    return param


def get_genres(request):

    subquery = Tracks.objects.filter(
        usertracks__user=request.user,
        usertracks__display_in_library=True
    ).values('main_artist_uri')

    query = UserArtists.objects.filter(
        user=request.user,
        artist_uri__in=Subquery(subquery)
    ).values('artist_main_genre_custom').distinct().order_by('artist_main_genre_custom')

    genres_list = list(query)
    genres = [genre['artist_main_genre_custom'] for genre in genres_list]
    if "others" in genres:
        genres.remove("others")
        genres.append("others")
    return genres


def get_subgenres(request, selected_genre):
    '''Select all subgenres for selected genre'''

    subquery = Tracks.objects.filter(
        usertracks__user=request.user,
        usertracks__display_in_library=True
    ).values('main_artist_uri')

    query = UserArtists.objects.filter(
        artist_main_genre_custom = selected_genre,
        user=request.user,
        artist_uri__in=Subquery(subquery)
    ).values('artist_subgenre_custom').distinct().order_by('artist_subgenre_custom')

    subgenres_list = list(query)
    subgenres = [subgenre['artist_subgenre_custom'] for subgenre in subgenres_list]

    if "others" in subgenres:
        subgenres.remove("others")
        subgenres.append("others")
    return subgenres


def get_artists_of_selected_subgenre(request, selected_genre, selected_subgenre):
    '''Select all artists which play particular subgenre and user owns in his library at least 3 songs of this artist'''

    user_settings = UserSettings.objects.get(user = request.user)
    no_of_songs = user_settings.no_of_songs_into_folder

    # User's artists from all genres with more than
    # defined minimum number of songs
    subquery = Tracks.objects.filter(
        usertracks__user=request.user,
        usertracks__display_in_library=True
    ).values('main_artist_uri').annotate(
        track_count=Count('track_uri', distinct = True)
    ).filter(
        Q(track_count__gte=no_of_songs) #gte >=
    ).values('main_artist_uri')

    query = UserArtists.objects.filter(
        user = request.user,
        artist_main_genre_custom = selected_genre,
        artist_subgenre_custom = selected_subgenre,
        artist_uri__in=Subquery(subquery)
    ).values('artist_uri__artist_uri', 'artist_name').distinct().order_by('artist_name')

    artists_list = list(query)
    artists = [(artist['artist_uri__artist_uri'], artist['artist_name']) for artist in artists_list]
    artists.append(("Loose tracks", "Loose tracks"))
    return artists


def get_tracks_of_artist(request, selected_artist_uri):
    '''Select all tracks of an artist'''

    subquery = UserTracks.objects.filter(
        user = request.user,
        display_in_library = True
    ).values('track_uri__track_uri').distinct()

    query = Tracks.objects.filter(
        main_artist_uri__artist_uri=selected_artist_uri,
        track_uri__in=Subquery(subquery)
    ).values('track_title').annotate(
        track_uri=Min('track_uri'),
        album_uri=Min('album_uri')
    ).order_by('track_title')

    tracklist = list(query)
    return tracklist


def get_featured_tracks_of_artist(request, selected_artist_name):
    '''Select all featured tracks of an artist'''

    subquery = UserTracks.objects.filter(
        user = request.user,
        display_in_library = True
    ).values('track_uri__track_uri').distinct()

    query = Tracks.objects.filter(
        Q(track_artist_add1 = selected_artist_name) | Q(track_artist_add2 = selected_artist_name),
        track_uri__in=Subquery(subquery)
    ).values('track_uri', 'track_artist_main', 'track_artist_add1',
             'track_artist_add2', 'track_title', 'album_uri'
    ).order_by('track_title')

    tracklist_featured = list(query)
    return tracklist_featured


def get_loose_tracks_for_subgenre(request, selected_genre, selected_subgenre):

    user_settings = UserSettings.objects.get(user = request.user)
    no_of_songs = user_settings.no_of_songs_into_folder

    # All user's artists for a particular genre and subgenre
    user_artists = UserArtists.objects.filter(
        user = request.user,
        artist_main_genre_custom = selected_genre,
        artist_subgenre_custom = selected_subgenre
    ).values('artist_uri__artist_uri')

    # All user's tracks of artists with less than the defined number of songs
    user_tracks_artists = Tracks.objects.filter(
        usertracks__user=request.user,
        usertracks__display_in_library=True
    ).values('main_artist_uri').annotate(
        track_count=Count('track_uri', distinct = True)
    ).filter(
        Q(track_count__lt=no_of_songs) #lt <
    ).values('main_artist_uri__artist_uri')

    subquery_combined = user_tracks_artists.intersection(user_artists)

    query = Tracks.objects.filter(
        usertracks__user=request.user,
        usertracks__display_in_library=True,      
        main_artist_uri__artist_uri__in=Subquery(subquery_combined)
    ).values('track_artist_main', 'track_uri', 'track_artist_add1',
             'track_artist_add2', 'track_title', 'album_uri', 'main_artist_uri'
    ).distinct().order_by('track_artist_main')

    tracklist = list(query)
    return tracklist