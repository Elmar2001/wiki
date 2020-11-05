from django.shortcuts import render, redirect
import random as rndm
from markdown2 import Markdown

markdowner = Markdown()

from django import forms
from . import util


class NewPageForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))


class NewEditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    print(util.get_entry(title))
    if util.get_entry(title) is None:
        return render(request, "encyclopedia/error.html",
                      {"error": title + " doesn't exist"
                       })

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": markdowner.convert(util.get_entry(title))
    })


def search(request):
    query = request.POST.get("q")
    print(query)
    if util.get_entry(query):
        return redirect('entry', title=query)
    else:
        found = []
        entries = util.list_entries()
        query = str(query).lower()

        for e in entries:
            if query in str(e).lower():
                found.append(e)

        if len(found) != 0:
            return render(request, "encyclopedia/found.html", {
                "found": found
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "error": "could not find " + query
            })


def random(request):
    entries = util.list_entries()
    i = rndm.randint(0, len(entries) - 1)
    return redirect('entry', title=util.list_entries()[i])


def newpage(request):
    if request.method == "POST":
        frm = NewPageForm(request.POST)
        if frm.is_valid():

            title = frm.cleaned_data["title"]
            content = frm.cleaned_data["content"]

            if util.get_entry(title) is None:
                util.save_entry(title, content)
                return redirect('entry', title=title)
            else:
                return render(request, "encyclopedia/error.html", {
                    "error": title + " already exists."
                })
        else:
            return render(request, "encyclopedia/newpage.html", {
                "form": frm
            })
    else:
        return render(request, "encyclopedia/newpage.html", {
            "form": NewPageForm()
        })


def edit(request, title):
    if request.method == "POST":
        frm = NewEditForm(request.POST)
        if frm.is_valid():
            content = frm.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect('entry', title=title)
        else:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "form": frm
            })
    else:
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": NewEditForm(initial={'content': content})
        })
