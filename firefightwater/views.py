from django.shortcuts import render
from .models import Project, ProjectTable, Table, Column, Value
from django.contrib.auth.decorators import login_required
from firefightwater.common.response import json_response
import json


@login_required(redirect_field_name='', login_url='/admin/login/')
def project(request):
    project_list = Project.objects.filter(user=request.user)
    context = {'list': project_list}
    return render(request, 'project.html', context)


@login_required(redirect_field_name='', login_url='/admin/login/')
def table(request, pk, md):
    tables = ProjectTable.objects.filter(project=pk, module=md).all()
    # ？不显示页面，只获取对应的表格列表？
    return render(request, 'tables.html', {'list': tables})


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
