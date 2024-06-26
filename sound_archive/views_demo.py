import os
from dotenv import load_dotenv

from django.http import Http404
from django.shortcuts import render, redirect

from .views import (
    get_genres,
    get_subgenres,
    encode_characters,
    get_artists_of_selected_subgenre,
    get_tracks_of_artist,
    get_featured_tracks_of_artist,
    get_loose_tracks_for_subgenre)


load_dotenv()
DEMO_USER_ID = os.getenv("DEMO_USER_ID")


def demo_archive(request):

    genres = get_genres(DEMO_USER_ID)
    if request.method == "POST":
        selected_genre = request.POST["selected_genre"]
        return redirect(
            'sound_archive:demo_archive_genres',
            selected_genre = selected_genre
        )
    return render(
        request,
        "demo_archive.html",
        {"genres": genres}
    )


def demo_archive_genres(request, selected_genre):

    genres = get_genres(DEMO_USER_ID)
    if selected_genre not in genres:
        raise Http404
    subgenres = get_subgenres(DEMO_USER_ID, selected_genre)
    if request.method == "POST":
        new_selected_genre = request.POST.get("selected_genre", None)
        selected_subgenre = request.POST.get("selected_subgenre", None)
        if new_selected_genre:
            return redirect(
                'sound_archive:demo_archive_genres',
                selected_genre = new_selected_genre)
        else:
            return redirect(
                'sound_archive:demo_archive_subgenres',
                selected_genre = selected_genre,
                selected_subgenre = selected_subgenre)
    return render(request, "demo_archive.html", {
        "genres": genres,
        "subgenres": subgenres,
        "selected_genre": selected_genre
        })


def demo_archive_subgenres(request, selected_genre, selected_subgenre):

    genres = get_genres(DEMO_USER_ID)
    if selected_genre not in genres:
        raise Http404
    subgenres = get_subgenres(DEMO_USER_ID, selected_genre)
    if selected_subgenre not in subgenres:
        raise Http404
    artists = get_artists_of_selected_subgenre(
        DEMO_USER_ID, selected_genre, selected_subgenre)

    if request.method == "POST":
        new_selected_genre = request.POST.get("selected_genre", None)
        new_selected_subgenre = request.POST.get("selected_subgenre", None)
        selected_artist_uri = request.POST.get("selected_artist_uri", None)
        if new_selected_genre:
            return redirect(
                'sound_archive:demo_archive_genres',
                selected_genre = new_selected_genre
                )
        elif new_selected_subgenre:
            return redirect(
                'sound_archive:demo_archive_subgenres',
                selected_genre = selected_genre,
                selected_subgenre = new_selected_subgenre
                )
        else:
            request.session["selected_artist_uri"] = selected_artist_uri
            selected_artist_name = request.POST.get("selected_artist_name")
            request.session["selected_artist_name"] = selected_artist_name
            selected_artist_name = encode_characters(selected_artist_name)
            return redirect(
                'sound_archive:demo_archive_tracks',
                selected_genre = selected_genre,
                selected_subgenre = selected_subgenre,
                selected_artist_name = selected_artist_name
            )
    return render(request, "demo_archive.html", {
        "genres": genres,
        "subgenres": subgenres,
        "artists": artists,
        "selected_genre": selected_genre,
        "selected_subgenre": selected_subgenre
        })


def demo_archive_tracks(request, selected_genre, selected_subgenre, selected_artist_name):

    genres = get_genres(DEMO_USER_ID)
    if selected_genre not in genres:
        raise Http404
    subgenres = get_subgenres(DEMO_USER_ID, selected_genre)
    if selected_subgenre not in subgenres:
        raise Http404

    selected_artist_name = request.session["selected_artist_name"]
    artists = get_artists_of_selected_subgenre(
        DEMO_USER_ID,
        selected_genre,
        selected_subgenre)
    selected_artist_uri = request.session["selected_artist_uri"]
    if (selected_artist_uri, selected_artist_name) not in artists:
        raise Http404

    if (selected_artist_uri,
        selected_artist_name) != ("Loose tracks", "Loose tracks"):
        tracklist = get_tracks_of_artist(DEMO_USER_ID, selected_artist_uri)
        tracklist_featured = []
        tracklist_featured = get_featured_tracks_of_artist(
            DEMO_USER_ID, selected_artist_name)
    else:
        tracklist = get_loose_tracks_for_subgenre(
            DEMO_USER_ID, selected_genre, selected_subgenre)
        tracklist_featured = []

    if request.method == "POST":
        new_selected_genre = request.POST.get("selected_genre", None)
        new_selected_subgenre = request.POST.get("selected_subgenre", None)
        new_selected_artist_uri = request.POST.get("selected_artist_uri", None)

        del request.session["selected_artist_uri"]
        del request.session["selected_artist_name"]

        if new_selected_genre:
            return redirect(
                'sound_archive:demo_archive_genres',
                selected_genre = new_selected_genre
            )
        elif new_selected_subgenre:
            return redirect(
                'sound_archive:demo_archive_subgenres',
                selected_genre = selected_genre,
                selected_subgenre = new_selected_subgenre
            )
        else:
            request.session["selected_artist_uri"] = new_selected_artist_uri
            selected_artist_name = request.POST.get("selected_artist_name")
            request.session["selected_artist_name"] = selected_artist_name
            new_selected_artist_name = encode_characters(selected_artist_name)
            return redirect(
                'sound_archive:demo_archive_tracks',
                selected_genre = selected_genre,
                selected_subgenre = selected_subgenre,
                selected_artist_name = new_selected_artist_name
            )

    return render(request, "demo_archive.html", {
        "genres": genres,
        "subgenres": subgenres,
        "artists": artists,
        "tracklist": tracklist,
        "tracklist_featured": tracklist_featured,
        "selected_genre": selected_genre,
        "selected_subgenre": selected_subgenre,
        "selected_artist_uri": selected_artist_uri,
        "selected_artist_name": selected_artist_name
        })
