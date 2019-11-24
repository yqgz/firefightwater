from django.shortcuts import render, redirect
from .models import Project, ProjectTable, Table, Column, Value, Module, ModuleTable
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.admin.forms import AdminAuthenticationForm
from .forms import *
from firefightwater.common.response import json_response
from .helper import *
import json


# 获取项目模块
def getselectmodule(pk, user):
    # 获取所有模块列表
    module_list = Module.objects.all()
    # 获取当前项目
    p = Project.objects.get(id=pk, user=user)
    select_module = p.projecttable_set  # 获取当前所有projecttable_set
    selects = []
    for m in module_list:
        have = select_module.filter(module=m)
        if have and m not in selects:
            selects.append(m)
    return selects  # 返回当前项目选择的module


@login_required(redirect_field_name='', login_url='/login/')
def project(request):
    # 获取当前用户的所有项目列表
    project_list = Project.objects.filter(user=request.user)
    # 获取所有模块列表
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
                m.select = False  # 是否勾选
                have = select_module.filter(module=m)
                if have:
                    m.select = True
                    m.have = False  # 是否有水栓
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


# 模块
@login_required(redirect_field_name='', login_url='/login/')
def module(request, pk, md):
    module_list = Module.objects.all()
    cur = module_list.filter(id=md)
    p = Project.objects.get(id=pk, user=request.user)

    pts = ProjectTable.objects.filter(project=pk, module=md)
    tables = []
    for pt in pts:  # 循环模块里面的每张表
        table = pt.table
        data = Value.objects.filter(project_table=pt.id).values()
        columns = Column.objects.filter(table=table)
        cols = {}
        for key, column in enumerate(columns):
            cols[column.id] = key
        values = []
        line = 1
        if data:
            vals = []
            for val in data:  # 遍历数据
                if val['line'] != line:  # 换行就保存到values里面
                    values.append(vals)
                    vals = []
                    line = val['line']
                if val['formula'] is not None:  # 如果是公式就选择公式
                    vals.append(val['formula'])
                else:
                    vals.append(val['value'])
            values.append(vals)  # 保存最后一行
        else:
            values = []

        # 合计行单独添加
        vals = []
        have_sum = Value.objects.filter(project_table=pt.id, value='合计')  # 防止重复插入合计行
        have_max = Value.objects.filter(project_table=pt.id, value='最大值')  # 防止重复插入最大值行
        if table.total == '合计' and not have_sum:
            for key, column in enumerate(columns):
                if key == 0:
                    vals.append(table.total)
                else:
                    vals.append('')
            values.append(vals)
        elif table.total == '最大值' and not have_max:
            for key, column in enumerate(columns):
                if key == 0:
                    vals.append(table.total)
                else:
                    vals.append('')
            values.append(vals)
        table.data = values
        # 增加tal
        tal =[]
        if table.total == '合计':
            tal.append('SUM')
            for key, column in enumerate(columns):
                if column.aggregation:
                    tal.append(num2Capital(key))
        elif table.total == '最大值':
            tal.append('MAX')
            for key, column in enumerate(columns):
                if column.aggregation:
                    tal.append(num2Capital(key))
        table.tal = tal
        c = []  # 每个表中的列
        f = []  # 显示公式
        par = [] # 参数名
        nested_header = []
        com = []  # 注释字段
        fo = [] # 展示公式
        f_cnt = 0  # 是否有公式的标志
        for key, column in enumerate(columns):
            c.append({'type': column.type, 'title': column.column_name, 'width': column.width})
            if column.c_formula is not None:
                fo.append([num2Capital(key), column.c_formula])
            if column.prompt is not None:
                com.append([num2Capital(key), column.prompt])
            if column.formula is None:
                column.formula = ''
            else:
                f_cnt = 1
            if column.parameter is None:
                column.parameter = ''
            f.append({'title': column.formula, 'colspan': 1})
            par.append({'title': column.parameter, 'colspan': 1})
        if f_cnt == 1:  # 确定有公式再添加
            nested_header.append(f)
        nested_header.append(par)
        table.columns = c
        table.pid = pt.id
        table.nested_header = nested_header
        table.com = com
        table.fo = fo
        tables.append(table)
    context = {'module_list': module_list, 'p': p, 'cur': cur, 'tables': tables, 'select_module':
        getselectmodule(pk, request.user)}

    return render(request, cur[0].module_en_name + '.html', context, )


# 表格
@login_required(redirect_field_name='', login_url='/login/')
def excel(request, pk):
    pt = ProjectTable.objects.filter(id=pk)
    # module_list = Module.objects.all()
    # cur = module_list.filter(id=pt[0].module_id)
    # p = pt[0].project '[["dd","","","","","","","",""]]'

    if request.POST:
        data = request.POST['data']
        true = 'true'  # 防止name 'true' is not defined
        false = 'false'
        data = eval(data)
        table = pt[0].table
        columns = Column.objects.filter(table=table)
        Value.objects.filter(project_table=pt[0]).delete()

        for r_key, row in enumerate(data):
            for c_key, val in enumerate(row):
                if isinstance(val, list):
                    value = Value(project_table=pt[0], value=val[0], formula=val[1], column=columns[c_key],
                                  line=r_key + 1)
                else:
                    value = Value(project_table=pt[0], value=val, column=columns[c_key], line=r_key+1)
                value.save()
        return json_response('保存成功！')
    # else:
    #     data = Value.objects.filter(project_table=pt[0])
    #     if data:
    #         data = data[0].value
    #     else:
    #         data = json.dumps("[[]]")
    # c = []
    #
    # columns = Column.objects.filter(table=pt[0].table)
    # for column in columns:
    #     c.append({'title': column.column_name})
    # context = {'module_list': module_list, 'p': p, 'cur': cur,
    #            'select_module': getselectmodule(pt[0].project_id, request.user), 'data': data,
    #            'columns': json.dumps(c)}
    # return render(request, 'nestedheader.html', context)


# 登录
def login(request):
    if request.POST:
        form = loginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            request.session.set_expiry(0)
            if user is not None:
                auth.login(request, user)
                return redirect('/')
    return render(request, 'login.html')


# 登出
def logout(request):
    auth.logout(request)
    return redirect('/login/')


def nestedheader(request):
    return render(request, 'nestedheader.html')
