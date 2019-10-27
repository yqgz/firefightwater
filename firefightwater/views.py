from django.shortcuts import render,redirect
from .models import Project, ProjectTable, Table, Column, Value, Module
from django.contrib.auth.decorators import login_required
from firefightwater.common.response import json_response
import json


@login_required(redirect_field_name='', login_url='/admin/login/')
def project(request):
    project_list = Project.objects.filter(user=request.user)
    module_list = Module.objects.all()
    context = {'project_list': project_list, 'module_list': module_list}
    return render(request, 'project.html', context)


@login_required(redirect_field_name='', login_url='/admin/login/')
def project_add(request,pk=''):
    msg = ''
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
    if request.POST:
        module_list = Module.objects.all()
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
        if request.POST['project_name']=='':
            msg = '项目名称不能为空'
        if request.POST['project_num']=='':
            msg = '项目编号不能为空'
        if request.POST['project_text']=='':
            msg = '项目概况不能为空'
        if request.POST['designer']=='':
            msg = '设计人不能为空'
        if request.POST['proofreader']=='':
            msg = '校对人不能为空'
        if request.POST['chief']=='':
            msg = '专业负责人不能为空'
        if request.POST['approver']=='':
            msg = '审批人不能为空'
        if request.POST['version']=='':
            msg = '版本号不能为空'
        if msg == '':
            p.save()

            return redirect('introduction', pk=p.id)
    else:
        p = Project.objects.filter(id=pk)
        module_list = Module.objects.all()
    context = {'module_list': module_list, 'p':p, 'msg':msg}
    return render(request, 'project_add.html', context)


@login_required(redirect_field_name='', login_url='/admin/login/')
def introduction(request, pk):
    if pk == 0:
        module_list = Module.objects.all()
        context = {'module_list': module_list}
    else:
        projects = ProjectTable.objects.filter(project = pk)
        # module_list = projects.module_set()
        context = {'project': projects}
    return render(request, 'introduction.html', context)


@login_required(redirect_field_name='', login_url='/admin/login/')
def excel(request, pk, md):
    context = {}
    project_table = ProjectTable.objects.get(pk=pk, md=md)
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
