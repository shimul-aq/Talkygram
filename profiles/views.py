from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileModelForm
from django.views.generic import ListView,DetailView
from django.contrib.auth.models import User
from django.db.models import Q

def my_profile_view(request):

    profile = Profile.objects.get(user=request.user)

    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    confirm = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True
    else:
        form = ProfileModelForm(request.POST or None, request.FILES or None, instance=profile)
    



    context =  {
        'profile': profile,
        'form': form,
        'confirm': confirm
    }

     
    return render (request, 'profiles/my_profile.html', context)



def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    queryset = Relationship.objects.invitations_received(profile)
    result = list(map(lambda x: x.sender, queryset))
    is_empty = False
    if len(result)==0:
        is_empty=True
    

    context = {
        'queryset':result, 
        'is_empty':is_empty,
    }

    return render (request, 'profiles/my_invites.html', context)




def accept_invitation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user = request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('profiles:my_invites')
        


def reject_invitation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user = request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)        
        rel.delete()
    return redirect('profiles:my_invites')



def invite_profiles_list_view(request):
    user = request.user
    queryset = Profile.objects.get_all_profiles_to_invite(user)


    context = {
        'queryset':queryset, 
    }

    return render (request, 'profiles/to_invite_list.html', context)


def profiles_list_view(request):
    user = request.user
    queryset = Profile.objects.get_all_profiles(user)


    context = {
        'queryset':queryset, 
    }

    return render (request, 'profiles/profile_list.html', context)




class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/details.html'

    def get_object(self):
        slug = self.kwargs.get('slug')
        profile = Profile.objects.get(slug=slug)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_rec = Relationship.objects.filter(sender=profile)
        rel_sen = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_rec:
            rel_receiver.append(item.receiver.user)
        for item in rel_sen:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_authors_posts()
        context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False
        return context




class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    #context_object_name = 'queryset'


    def get_queryset(self):
        queryset = Profile.objects.get_all_profiles(self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        
        rel_rec = Relationship.objects.filter(sender=profile)
        rel_sen = Relationship.objects.filter(receiver=profile)

        rel_receiver = []
        rel_sender = []

        for item in rel_rec:
            rel_receiver.append(item.receiver.user)

        for item in rel_sen:
            rel_sender.append(item.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context["is_empty"] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] == True
        return context




def send_invitation(request):
    
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)


        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my_profile')
    

def remove_from_friends(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender)))

        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:my_profile')