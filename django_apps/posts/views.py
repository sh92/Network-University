from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages

from .models import Post
from .forms import PostForm
# Create your views here.
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        title = form.cleaned_data.get("title")
        print(title)
        instance.save()
        return HttpResponseRedirect(instance.get_absoulte_url())
    else:
        messages.error(request,"Not Successfully Created")
    # if request.method == "POST":
    #     print(request.POST.get("content"))
    #     title=request.POST.get("title")
    #     Post.objects.create(title=title)
    context = {
        "form": form,
    }
    return render(request,"posts/post_form.html",context)
def post_detail(request, id=None):
    # instance = Post.objects.get(id=1)
    instance = get_object_or_404(Post,id=id)
    context = {
        "title" : "Detail",
        "instance":instance,
    }
    return render(request, 'posts/detail.html',context)
def post_list(request):
    queryset = Post.objects.all()
    if request.user.is_authenticated():
        context ={
            "object_list":queryset,
            "title": "My User List"
        }
    else:
        context={
            "title": "List"
        }
    return render(request, 'posts/post_list.html',context)

def post_update(request, id=None):
    instance = get_object_or_404(Post,id=id)
    form = PostForm(request.POST or None,instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request,"<a href='#'>Item</a> Saved", extra_tags='html_safe')
        messages.success(request,"Item2 Saved")
        messages.success(request,"Item3 Saved")
        messages.success(request,"Item4 Saved")
        return HttpResponseRedirect(instance.get_absoulte_url())

    context = {
        "title" : "Detail",
        "instance":instance,
        "form":form,
    }
    return render(request, 'posts/post_form.html',context)

def post_delete(request,id =None):
    instance = get_object_or_404(Post,id=id)
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")
