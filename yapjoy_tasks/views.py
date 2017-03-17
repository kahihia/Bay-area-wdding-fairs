from django.shortcuts import render, HttpResponseRedirect, Http404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from yapjoy_registration.models import Friends
from yapjoy_registration.models import AllFriends
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import TasksForm
from .models import *
from django.db.models import Q
from django.shortcuts import get_object_or_404
from datetime import datetime

@login_required(login_url='/login/')
def tasks(request):
    tasks_all = None
    name = None
    user = request.user
    profile = user.userprofile
    task_form = TasksForm()
    if 'today' in request.GET:
        tasks_all = Task.objects.filter(user=user, created_at=datetime.today())
    elif 'complete' in request.GET:
        tasks_all = Task.objects.filter(user=user, complete=True)
    elif 'friend' in request.GET:
        friend = request.GET.get('friend')
        name = request.GET.get('name')
        try:
            friend = int(friend)
            print friend
            tasks_assigned = TaskAssign.objects.filter(user=user, task__user_id=friend).values('user')
            print 'Tasks Assigned: ',tasks_assigned
            tasks_all = Task.objects.filter(assign__in=tasks_assigned)
            print tasks_all
        except Exception as e:
            pass
    else:
        user_logged_in = []
        user_logged_in.append(user)
        tasks_all = Task.objects.filter(user=user).order_by('created_at')
    tasks_assigned_to_user = TaskAssign.objects.filter(user=user).select_related('task').order_by('created_at')

    if request.method == "POST":
        if "task_to_delete" in request.POST:
            id = request.POST.get('task_to_delete')
            Task.objects.get(id=id, user=request.user).delete()
            return HttpResponse('success')
        elif 'set_status' in request.POST:
            pass
        else:
            task_form = TasksForm(request.POST)
            if task_form.is_valid():
                data = task_form.cleaned_data
                subject = data['subject']
                due = data['due']
                #complete = data['complete']
              #  assignee = data['assignee']
                notes = data['notes']
                assign = request.POST.getlist('assigned_to_add')
                task = Task.objects.create(
                    user=user,
                    subject=subject,
                    due=due,
                    notes=notes,
                    # assignee=assignee,
                                    )

                for user_id_in_assign in assign:
                    TaskAssign.objects.create(task=task, user_id=user_id_in_assign)
                    user_assigned_task = User.objects.get(id=user_id_in_assign)
                    from yapjoy_registration.models import Notifications
                    from yapjoy_registration.commons import send_email
                    Notifications.objects.create(userprofile=user_assigned_task.userprofile, message="%s have assigned a task to you."%(user.get_full_name()))
                    if profile.notification_tasks:
                        send_email(user_assigned_task.email, message="%s have assigned a task to you."%(user.get_full_name()), title="A task has been assigned to you", subject="You have been assigned a task on Yapjoy")

                return HttpResponseRedirect('/tasks/')

    if request.is_ajax():
        if 'addTodoModalForm' in request.POST:
            print 'asd'

        print 'called by ajax'
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')
        #place a create query here
        #use django form
    #print friends

    assigns = TaskAssign.objects.filter(user=user).distinct('task__user')
    # print 'assigns: ',assigns
    profile = user.userprofile
    completed_task_count = Task.objects.filter(user=user).filter(complete=True).count()
    context = {
        'task_form': task_form,
        'tasks_all': tasks_all,
        'friends': friends,
        'assigns': assigns,
        'name': name,
        'user': user,
        'profile':profile,
        'tasks_assigned_to_user':tasks_assigned_to_user,
        'completed_task_count':completed_task_count,

    }

    return render(request, 'vendroid/tasks/tasks.html', context)

        # if 'delete_task' in request.POST:
        #     print 'asd'
        # print 'called by ajax'

    #submit task foorm
    # if 'createTodoBtn' in request.POST:
    #     task_form = TasksForm(request.POST)
    #
    # #for single task
    # if '.task-listen' in request.POST:
    #     task_form = TasksForm(request.POST)
    #
    # if '.deleteGroupBtn' in request.POST:
    #     task_form = TasksForm(request.POST)
    #
    # if '.editTaskSubmitBtn' in request.POST:
    #     task_form = TasksForm(request.POST)

@login_required(login_url='/login/')
def edit_tasks(request, tasks_id):
    edited = None
    user = request.user
    profile = user.userprofile
    task = get_object_or_404(Task, id=tasks_id, user=user)
    if request.method == "POST":
        task_form = TasksForm(request.POST)
        if task_form.is_valid():
            data = task_form.cleaned_data
            subject = data['subject']
            due = data['due']
            #complete = data['complete']
          #  assignee = data['assignee']
            notes = data['notes']
            assign = request.POST.getlist('assigned_to')
            all_users = task.assign.all()
            if all_users:
                c = TaskAssign.objects.filter(user__in=all_users, task=task).delete()
            for user_assign_id in assign:
                TaskAssign.objects.create(user_id=user_assign_id, task=task)
                user_assigned_task = User.objects.get(id=user_assign_id)
                from yapjoy_registration.models import Notifications
                from yapjoy_registration.commons import send_email
                Notifications.objects.create(userprofile=user_assigned_task.userprofile, message="%s have assigned a task to you."%(user.get_full_name()))
                if profile.notification_tasks:
                    send_email(user_assigned_task.email, message="%s have assigned a task to you."%(user.get_full_name()), title="A task has been assigned to you", subject="You have been assigned a task on Yapjoy")
            task.subject = subject
            task.due = due
            task.notes = notes
            task.save()
            edited = "Success"

    initial = {
        'subject':task.subject,
        'due':task.due,
        'notes':task.notes,
    }
    task_form = TasksForm(initial = initial)
    profile = user.userprofile
    friends = None
    # try:
    #     friends = Friends.objects.get(user=user).friends.all()
    # except:
    #     friends = Friends.objects.create(user=user)
    #     friends = friends.friends.all()
    friends = AllFriends.objects.filter(Q(Q(friends__user=user)|Q(user=user))&~Q(status=AllFriends.FOLLWOING)&~Q(status=AllFriends.INVITED)&~Q(status=AllFriends.PENDING)).select_related('user','user__userprofile','friends__user','friends')
    friends_assigned = task.assign.all().select_related('userprofile','userprofile__user')
    friends = friends.exclude(user__in=friends_assigned)
    context = {
        'task':task,
        'task_form':task_form,
        'edited':edited,
        'profile':profile,
        'friends':friends,
        'friends_assigned':friends_assigned,
    }
    return render(request, 'tasks/edit_task.html', context)
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url='/login/')
@csrf_exempt
def complete_tasks(request):
    if request.is_ajax():
        id = request.POST.get('id')
        print 'ID: ',id
        user = request.user
        task = get_object_or_404(Task, pk=id, user=user)
        task.complete = not task.complete
        task.save()
        print 'Done: ',task.complete
        if task.complete:
            return HttpResponse('success')
        else:
            return HttpResponse('successFalse')
    else:
        print "Failed"
        return HttpResponse('Failed')



#----------other functionalities------------#
#-----fix me???
#@login_required(login_url='/login/')
# def delete_tasks(request, tasks_id):
#     c = Task.objects.get(id=tasks_id, user=request.user)
#     send_id = c.task.id
#
#     c.delete()
#     messages.add_message(request, settings.DELETE_MESSAGE, "Your comment was deleted")
#
#     return HttpResponseRedirect("/tasks/get/%s" % send_id)
import json
def taskComplete(request):
    completed_task_count=Task.objects.filter(user=request.user).filter(complete=True).count()
    task_count=Task.objects.filter(user=request.user).count()
    res=[]
    res.append(
            [completed_task_count,task_count]
        )
    data = json.dumps(res)
    return HttpResponse(data, content_type='application/json')