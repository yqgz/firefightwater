from django.shortcuts import render, redirect
from .models import Project, ProjectTable, Table, Column, Value, Module, ModuleTable
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .forms import *
from firefightwater.common.response import json_response
import json


@login_required(redirect_field_name='', login_url='/login/')
def project(request):
    project_list = Project.objects.filter(user=request.user)
    module_list = Module.objects.all()
    context = {'project_list': project_list, 'module_list': module_list}
    return render(request, 'project.html', context)


@login_required(redirect_field_name='', login_url='/login/')
def project_add(request):
    pk = ''
    msg = ''
    context = {}
    if request.POST:
        module_list = Module.objects.all()
        pk = request.POST['pk']
        if pk == '':
            p = Project(user=request.user,
                        project_name=request.POST['project_name'],
                        project_num=request.POST['project_num'],
                        project_text=request.POST['project_text'],
                        designer=request.POST['designer'],
                        proofreader=request.POST['proofreader'],
                        chief=request.POST['chief'],
                        approver=request.POST['approver'],
                        version=request.POST['version'],
                        )
        else:
            p = Project.objects.get(id=pk, user=request.user)
        if request.POST['project_name'] == '':
            msg = '项目名称不能为空'
        if request.POST['project_num'] == '':
            msg = '项目编号不能为空'
        if request.POST['project_text'] == '':
            msg = '项目概况不能为空'
        if request.POST['designer'] == '':
            msg = '设计人不能为空'
        if request.POST['proofreader'] == '':
            msg = '校对人不能为空'
        if request.POST['chief'] == '':
            msg = '专业负责人不能为空'
        if request.POST['approver'] == '':
            msg = '审批人不能为空'
        if request.POST['version'] == '':
            msg = '版本号不能为空'
        if msg == '':
            p.save()
            post = request.POST
            ProjectTable.objects.filter(project=p.id).delete()
            for var in module_list:
                if var.module_en_name in post.keys() and post[var.module_en_name] == 'on':
                    if var.id == 3 and 'hydrant' in post.keys() and post['hydrant'] == 'on':
                        tables = ModuleTable.objects.filter(module=var.id, have='是')
                    elif var.id == 3:
                        tables = ModuleTable.objects.filter(module=var.id, have='否')
                    else:
                        tables = ModuleTable.objects.filter(module=var.id)
                    for t in tables:
                        ProjectTable.objects.create(project=p, table=t.table, module=t.module)

            return redirect('module', pk=p.id, md=1)
    else:
        pk = request.GET['pk']
        module_list = Module.objects.all()
        if pk != '':
            p = Project.objects.get(id=pk, user=request.user)
            select_module = p.projecttable_set
            selects = []
            for m in module_list:
                m.select = False
                have = select_module.filter(module=m)
                if have:
                    m.select = True
                    m.have = False
                    moduletables = ModuleTable.objects.filter(module=have[0].module, table=have[0].table)
                    if moduletables[0].have == '是':
                        m.have = 1
            # context['select_module'] = selects
        else:
            p = Project(
                project_name='',
                project_num='',
                project_text='',
                designer='',
                proofreader='',
                chief='',
                approver='',
                version='',
            )
    context['module_list'] = module_list
    context['p'] = p
    context['msg'] = msg
    return render(request, 'project_add.html', context)

<<<<<<< HEAD
=======

>>>>>>> 8235994270ae9a90932d8e481a9587163d309d11
@login_required(redirect_field_name='', login_url='/login/')
def module(request, pk, md):
    module_list = Module.objects.all()
    cur = module_list.filter(id=md)
    p = Project.objects.get(id=pk, user=request.user)
    tables = ProjectTable.objects.filter(project=pk, module=md)
    context = {'module_list': module_list, 'p': p, 'cur': cur, 'tables': tables}
    return render(request, 'module.html', context, )

<<<<<<< HEAD
=======

>>>>>>> 8235994270ae9a90932d8e481a9587163d309d11
@login_required(redirect_field_name='', login_url='/login/')
def excel(request, pk):
    module_list = Module.objects.all()
    pt = ProjectTable.objects.filter(id=pk)
    cur = module_list.filter()
    context = {}
    project_table = ProjectTable.objects.get(id=pk)
    if request.POST:
        data = request.POST['data']
        value = Value(value=json.dumps(data), project_table=project_table)
        value.save()
        return json_response('保存成功！')
    else:
        data = Value.objects.filter(project_table=project_table)
        if data:
            data = data[0].value
        else:
            data = json.dumps("[[]]")
    c = []

    columns = Column.objects.filter(table=project_table.table)
    for column in columns:
        c.append({'title': column.column_name})
    context['columns'] = json.dumps(c)
    context['data'] = data
    return render(request, 'excel.html', context)


def login(request):
    if request.POST:
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                request.session['username'] = username
                return redirect('/project/')
    else:
        form = loginForm()
    return render(request, 'login.html', {'form': form})