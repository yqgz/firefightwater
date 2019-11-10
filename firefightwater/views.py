from django.shortcuts import render, redirect
from .models import Project, ProjectTable, Table, Column, Value, Module, ModuleTable
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.admin.forms import AdminAuthenticationForm
from .forms import *
from firefightwater.common.response import json_response
import json


# 获取项目模块
def getselectmodule(pk, user):
    module_list = Module.objects.all()
    p = Project.objects.get(id=pk, user=user)
    select_module = p.projecttable_set
    selects = []
    for m in module_list:
        have = select_module.filter(module=m)
        if have and m not in selects:
            selects.append(m)
    return selects


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
            for m in module_list:
                m.select = False
                have = select_module.filter(module=m)
                if have:
                    m.select = True
                    m.have = False
                    moduletables = ModuleTable.objects.filter(module=have[0].module, table=have[0].table)
                    if moduletables[0].have == '是':
                        m.have = 1
            context['select_module'] = getselectmodule(pk, request.user)
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


# 模型
@login_required(redirect_field_name='', login_url='/login/')
def module(request, pk, md):
    module_list = Module.objects.all()
    cur = module_list.filter(id=md)
    p = Project.objects.get(id=pk, user=request.user)
    tables = ProjectTable.objects.filter(project=pk, module=md)

    if request.POST:
        data = request.POST['data']
        value = Value(value=json.dumps(data), project_table=tables[0])
        value.save()
        return json_response('保存成功！')
    else:
        data = Value.objects.filter(project_table=tables[0])
        if data:
            data = data[0].value
        else:
            data = json.dumps("[[]]")

    c = []
    f = []
    par = []
    columns = Column.objects.filter(table=1)
    for column in columns:
        c.append({'type': column.type, 'title': column.column_name, 'width': column.width})
        f.append({'title': column.formula, 'colspan': 1})
        par.append({'title': column.parameter, 'colspan': 1})
    context = {'module_list': module_list, 'p': p, 'cur': cur, 'tables': tables, 'data': data,
               'select_module': getselectmodule(pk, request.user), 'columns': json.dumps(c), 'formula': json.dumps(f), 'parameter': json.dumps(par)}

    return render(request, cur[0].module_en_name + '.html', context, )


# 表格
@login_required(redirect_field_name='', login_url='/login/')
def excel(request, pk):
    pt = ProjectTable.objects.filter(id=pk)
    module_list = Module.objects.all()
    cur = module_list.filter(id=pt[0].module_id)
    p = pt[0].project

    if request.POST:
        data = request.POST['data']
        value = Value(value=json.dumps(data), project_table=pt[0])
        value.save()
        return json_response('保存成功！')
    else:
        data = Value.objects.filter(project_table=pt[0])
        if data:
            data = data[0].value
        else:
            data = json.dumps("[[]]")
    c = []

    columns = Column.objects.filter(table=pt[0].table)
    for column in columns:
        c.append({'title': column.column_name})
    context = {'module_list': module_list, 'p': p, 'cur': cur,
               'select_module': getselectmodule(pt[0].project_id, request.user), 'data': data, 'columns': json.dumps(c)}
    return render(request, 'nestedheader.html', context)


# 登录
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
                return redirect('/')
    return render(request, 'login.html')


# 登出
def logout(request):
    auth.logout(request)
    return redirect('/login/')
