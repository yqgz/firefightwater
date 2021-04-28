from django.shortcuts import render, redirect
from .models import Project, ProjectTable, Table, Column, Value, Module, ModuleTable, ColumnDropdown, Dropdown, \
    DropdownItem
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.admin.forms import AdminAuthenticationForm
from .forms import *
from firefightwater.common.response import json_response, json_error, read_file
from .helper import *
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q
import json
from urllib import parse
import re
from docxtpl import DocxTemplate, RichText
import os


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


# 替换公式和默认值的参数值
def getValue(fo, p):
    for val in ['a_flow', 'sum_pra', 'a_pl', 'max_sdfc', 'sum_prc', 'c_mp', 'c_ptp', 'c_rsp', 'c_rp', 'i_flow',
                'sum_pri', 'i_mp', 'i_pl', 'i_rsp', 'i_rp', 'o_flow', 'sum_prn', 'max_sdf', 'max_prs', 't_flow',
                'sum_prt', 't_pl', 'sum_pr']:
        fo = re.sub(val, getattr(p, val), fo)
    return fo


# 获取当前用户的所有项目列表
@login_required(redirect_field_name='', login_url='/login/')
def project(request):
    q = None
    if 'q' in request.GET:
        q = request.GET['q']
        project_list = Project.objects.filter(user=request.user).filter(Q(project_name__contains=q) |
                                                                        Q(project_text__contains=q))
    else:
        project_list = Project.objects.filter(user=request.user)
    # 获取所有模块列表
    module_list = Module.objects.all()
    context = {'project_list': project_list, 'module_list': module_list, 'q': q}
    return render(request, 'project.html', context)


# 新增项目
@login_required(redirect_field_name='', login_url='/login/')
def project_add(request):
    context = {}
    if request.POST:
        post = parse.parse_qs(request.POST['data'])
        msg = ''
        module_list = Module.objects.all()
        if 'project_name' not in post.keys() or post['project_name'][0] == '':
            msg = '项目名称不能为空'
        elif 'project_num' not in post.keys() or post['project_num'][0] == '':
            msg = '项目编号不能为空'
        elif 'project_text' not in post.keys() or post['project_text'][0] == '':
            msg = '项目概况不能为空'
        elif 'designer'not in post.keys() or post['designer'][0] == '':
            msg = '设计人不能为空'
        elif 'proofreader' not in post.keys() or post['proofreader'][0] == '':
            msg = '校对人不能为空'
        elif 'chief' not in post.keys() or post['chief'][0] == '':
            msg = '专业负责人不能为空'
        elif 'approver' not in post.keys() or post['approver'][0] == '':
            msg = '审批人不能为空'
        elif 'version' not in post.keys() or post['version'][0] == '':
            msg = '版本号不能为空'
        if msg == '':
            p = Project(user=request.user,
                        project_name=post['project_name'][0],
                        project_num=post['project_num'][0],
                        project_text=post['project_text'][0],
                        designer=post['designer'][0],
                        proofreader=post['proofreader'][0],
                        chief=post['chief'][0],
                        approver=post['approver'][0],
                        version=post['version'][0],
                        )
            p.save()
            ProjectTable.objects.filter(project=p.id).delete()
            md = 0  # 存储第一个模块
            pts = []  # 所有项目表
            for var in module_list:
                if var.module_en_name in post.keys() and post[var.module_en_name][0] == 'on':
                    if md == 0:
                        md = var.id.__str__()
                    if var.id == 3 and 'hydrant' in post.keys() and post['hydrant'][0] == 'on':
                        tables = ModuleTable.objects.filter(module=var.id, have='是')
                    elif var.id == 3:
                        tables = ModuleTable.objects.filter(module=var.id, have='否')
                    else:
                        tables = ModuleTable.objects.filter(module=var.id)
                    for t in tables:
                        pt = ProjectTable(project=p, table=t.table, module=t.module)
                        pts.append(pt)
            ProjectTable.objects.bulk_create(pts)

            return json_response(data={'msg': '新项目创建成功！', 'url': '/module/' + str(p.id) + '/' + str(md) + '/'})
        else:
            return json_error(data=msg)
    else:
        module_list = Module.objects.all()
        context['module_list'] = module_list
        return render(request, 'project_add.html', context)


# 项目概述页面
@login_required(redirect_field_name='', login_url='/login/')
def introduction(request, pk):
    context = {}
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
        context['module_list'] = module_list
        context['p'] = p
        return render(request, 'Introduction.html', context)


# 项目编辑页面
@login_required(redirect_field_name='', login_url='/login/')
def introduction_edit(request, pk):
    context = {}
    if request.POST:
        msg = ''
        module_list = Module.objects.all()
        # pk = request.POST['pk']
        p = Project.objects.get(id=pk, user=request.user)
        p.project_name = request.POST['project_name']
        p.project_num = request.POST['project_num']
        p.project_text = request.POST['project_text']
        p.designer = request.POST['designer']
        p.proofreader = request.POST['proofreader']
        p.chief = request.POST['chief']
        p.approver = request.POST['approver']
        p.version = request.POST['version']
        if request.POST['project_name'] == '':
            msg = '项目名称不能为空'
        elif request.POST['project_num'] == '':
            msg = '项目编号不能为空'
        elif request.POST['project_text'] == '':
            msg = '项目概况不能为空'
        elif request.POST['designer'] == '':
            msg = '设计人不能为空'
        elif request.POST['proofreader'] == '':
            msg = '校对人不能为空'
        elif request.POST['chief'] == '':
            msg = '专业负责人不能为空'
        elif request.POST['approver'] == '':
            msg = '审批人不能为空'
        elif request.POST['version'] == '':
            msg = '版本号不能为空'
        if msg == '':
            p.save()
            post = request.POST
            projectTables = ProjectTable.objects.filter(project=p.id)
            pts = []
            for var in module_list:
                if var.module_en_name in post.keys() and post[var.module_en_name] == 'on':
                    if var.id == 3 and 'hydrant' in post.keys() and post['hydrant'] == 'on':
                        tables = ModuleTable.objects.filter(module=var.id, have='是')
                    elif var.id == 3:
                        tables = ModuleTable.objects.filter(module=var.id, have='否')
                    else:
                        tables = ModuleTable.objects.filter(module=var.id)
                    for t in tables:
                        have = projectTables.filter(table=t.table, module=t.module)

                        if not have.exists(): # 不存在添加
                            pt = ProjectTable(project=p, table=t.table, module=t.module)
                            pts.append(pt)
                        else:  # 存在不添加
                            projectTables = projectTables.exclude(table=t.table, module=t.module)

            projectTables.delete()
            ProjectTable.objects.bulk_create(pts)
            return redirect('introduction', pk=p.id)
        else:
            context['data'] = msg
            context['type'] = 'error'
            context['module_list'] = module_list
            context['p'] = p
            return render(request, 'introduction_edit.html', context)
    else:
        module_list = Module.objects.all()
        p = Project.objects.get(id=pk, user=request.user)
        select_module = p.projecttable_set
        for m in module_list:
            if hasattr(m, 'select') and m.select == True:
                continue
            m.select = False  # 是否勾选
            have = select_module.filter(module=m)
            if have:
                m.select = True
                m.have = False  # 是否有水栓
                moduletables = ModuleTable.objects.filter(module=have[0].module, table=have[0].table)
                if moduletables[0].have == '是':
                    m.have = 1
        context['select_module'] = getselectmodule(pk, request.user)
        context['module_list'] = module_list
        context['p'] = p
        return render(request, 'introduction_edit.html', context)


# 项目模块对应的表展示
@login_required(redirect_field_name='', login_url='/login/')
def module(request, pk, md):
    module_list = Module.objects.all()
    cur = module_list.filter(id=md)
    p = Project.objects.get(id=pk, user=request.user)
    context = {}
    pts = ProjectTable.objects.filter(project=pk, module=md)
    # 室外消火栓系统
    if md == 3:
        table_id_ = pts[0].table_id
        module_table = ModuleTable.objects.filter(module_id=md, table_id=table_id_)
        if module_table[0].have == '是':
            cur.have = '是'
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
                # elif val['value'] == '' and columns[cols[val['column_id']]].defaultv is not None: # 添加默认值
                #     vals.append(columns[cols[val['column_id']]].defaultv)
                else:
                    vals.append(val['value'])
            values.append(vals)  # 保存最后一行
        else:
            vals = []
            # for col in columns:
            #     if col.defaultv is not None: # 添加默认值
            #         vals.append(col.defaultv)
            #     else:
            #         vals.append('')
            values.append(vals)

        # 合计行单独添加
        vals = []
        have_sum = Value.objects.filter(project_table=pt.id, value='合计')  # 防止重复插入合计行
        have_max = Value.objects.filter(project_table=pt.id, value='最大值')  # 防止重复插入最大值行
        if table.total == '合计' and not have_sum or table.total == '最大值' and not have_max:
            for key, column in enumerate(columns):
                if key == 0:
                    vals.append(table.total)
                else:
                    vals.append('')
            values.append(vals)
        table.data = values
        # 增加tal
        tal = []
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
        par = []  # 参数名
        nested_header = []
        com = []  # 注释字段
        fo = []  # 展示公式
        de = []  # 默认值
        f_cnt = 0  # 是否有公式的标志
        p_cnt = 0  # 是否有参数的标志
        for key, column in enumerate(columns):
            col = {'type': column.type, 'title': column.column_name, 'width': column.width}
            # 添加下拉菜单
            column_dropdown = ColumnDropdown.objects.filter(column_id=column.id)
            if column_dropdown.exists() and column.type == 'dropdown':
                dropdown_id = column_dropdown[0].dropdown_id
                items = DropdownItem.objects.filter(dd_name_id=dropdown_id)
                source = []
                for item in items:
                    if item.group is None:
                        item.group = ''
                    if item.title is None:
                        item.title = ''
                    source.append({'id': item.name, 'name': item.name, 'group': item.group, 'title': item.title})
                col['source'] = source
            c.append(col)
            if column.c_formula is not None:
                fo.append([num2Capital(key), getValue(column.c_formula, p)])
            if column.c_formula is None and column.defaultv is not None:  # 添加默认值
                de.append([num2Capital(key), getValue(column.defaultv, p)])
            if column.prompt is not None:
                com.append([num2Capital(key), column.prompt])
            if column.formula is None:
                column.formula = ''
            else:
                f_cnt = 1
            if column.parameter is None:
                column.parameter = ''
            else:
                p_cnt = 1
            f.append({'title': column.formula, 'colspan': 1})
            par.append({'title': column.parameter, 'colspan': 1})
        if f_cnt == 1:  # 确定有公式再添加
            nested_header.append(f)
        if p_cnt == 1:
            nested_header.append(par)
        table.columns = c
        table.pid = pt.id
        table.nested_header = nested_header
        table.com = com
        table.fo = fo
        table.de = de
        tables.append(table)
        select_module = getselectmodule(pk, request.user)
        pre_module = None
        next_module = None
        for key, module in enumerate(select_module):
            if cur[0] == module:
                pre_module = select_module[key-1]
                if module == select_module[-1]:
                    next_module = None
                else:
                    next_module = select_module[key+1]
                if key == 0:
                    pre_module = None

                break

        context = {'module_list': module_list, 'p': p, 'cur': cur, 'tables': tables, 'select_module': select_module,
                   'next': next_module, 'pre': pre_module}

    return render(request, cur[0].module_en_name + '.html', context)


# 项目表格保存
@login_required(redirect_field_name='', login_url='/login/')
def excel(request, pk):
    pt = ProjectTable.objects.filter(id=pk)

    if request.POST:
        data = request.POST['data']
        true = 'true'  # 防止name 'true' is not defined
        false = 'false'
        null = ''
        data = eval(data)
        len1 = len(data) - 1
        table = pt[0].table
        columns = Column.objects.filter(table=table)
        # 不为空判断
        for r_key, row in enumerate(data):
            for c_key, val in enumerate(row):
                if isinstance(val, list):
                    value = val[0]
                else:
                    value = val
                if (table.total is not None and r_key < len1) or table.total is None:
                    if columns[c_key].must and value == '':
                        msg = columns[c_key].column_name + '的所有行不能为空！'
                        return json_error(msg)
        # 存储project属性
        project_set(table, data, pt[0].project)
        Value.objects.filter(project_table=pt[0]).delete()
        values = []
        for r_key, row in enumerate(data):
            for c_key, val in enumerate(row):
                if isinstance(val, list):
                    value = Value(project_table=pt[0], value=val[0], formula=val[1], column=columns[c_key],
                                  line=r_key + 1)
                else:
                    value = Value(project_table=pt[0], value=val, column=columns[c_key], line=r_key + 1)
                values.append(value)
        Value.objects.bulk_create(values)
        return json_response('保存成功！')


# 获取单元格数值
def getVal(val):
    if isinstance(val, list):
        value = val[0]
    else:
        value = val
    return value


# 存储project属性
def project_set(table, data, p):
    if table.id == 1:
        col = capital2Num('D')
        for r_key, row in enumerate(data):
            if row[0] == '1':
                p.o_flow = getVal(row[col])
            elif row[0] == '2':
                p.i_flow = getVal(row[col])
            elif row[0] == '3':
                p.a_flow = getVal(row[col])
    elif table.id == 3:
        row = len(data) - 1
        col = capital2Num('J')
        p.sum_pr = getVal(data[row][col])
    elif table.id == 8:
        row = len(data) - 1
        col = capital2Num('J')
        p.sum_prn = getVal(data[row][col])
    elif table.id == 10:
        row = len(data) - 1
        col = capital2Num('J')
        p.sum_pri = getVal(data[row][col])
    elif table.id == 11:
        row = 0
        col = capital2Num('G')
        p.i_mp = getVal(data[row][col])
        col = capital2Num('I')
        p.i_pl = getVal(data[row][col])
    elif table.id == 13:
        row = 0
        col = capital2Num('B')
        p.i_rsp = getVal(data[row][col])
        col = capital2Num('D')
        p.i_rp = getVal(data[row][col])
    elif table.id == 16:
        row = len(data) - 1
        col = capital2Num('K')
        p.sum_pra = getVal(data[row][col])
    elif table.id == 17:
        row = 0
        col = capital2Num('I')
        p.a_pl = getVal(data[row][col])
    elif table.id == 22:
        row = len(data) - 1
        col = capital2Num('J')
        p.sum_prt = getVal(data[row][col])
    elif table.id == 23:
        row = 0
        col = capital2Num('I')
        p.t_pl = getVal(data[row][col])
    elif table.id == 25:
        row = len(data) - 1
        col = capital2Num('J')
        p.max_sdf = getVal(data[row][col])
    elif table.id == 26:
        row = len(data) - 1
        col = capital2Num('K')
        p.max_prs = getVal(data[row][col])
    elif table.id == 37:
        row = len(data) - 1
        col = capital2Num('I')
        p.max_sdfc = getVal(data[row][col])
    elif table.id == 38:
        row = len(data) - 1
        col = capital2Num('K')
        p.sum_prc = getVal(data[row][col])
    elif table.id == 39:
        row = 0
        col = capital2Num('G')
        p.c_mp = getVal(data[row][col])
        col = capital2Num('K')
        p.c_ptp = getVal(data[row][col])
    elif table.id == 41:
        row = 0
        col = capital2Num('B')
        p.c_rsp = getVal(data[row][col])
        col = capital2Num('D')
        p.c_rp = getVal(data[row][col])
    p.save()


# 项目消防转输系统供水泵流量保存
@login_required(redirect_field_name='', login_url='/login/')
def project_save(request, pk):
        context = {}
        if request.POST:
            p = Project.objects.get(id=pk, user=request.user)
            name = request.POST['name']
            value = request.POST['value']
            setattr(p, name, value)
            p.save()
            return json_response(data='保存成功！')


# 下载项目概述
def download_report(request, pk):
    p = Project.objects.get(id=pk, user=request.user)
    if p:
        try:
            select_module = getselectmodule(pk, request.user)
            rt = RichText()
            modules = ''
            for module in select_module:
                modules += module.module_name + '、'
                rt.add(module.module_name, style='header1')
                rt.add('\a')
                tables = ProjectTable.objects.filter(project=pk, module=module)
                for table in tables:
                    rt.add(table.table.table_name, style='header2')
                    rt.add('\a')
                    data = list(Value.objects.filter(project_table=table.id).values())
                    columns = Column.objects.filter(table=table.table)
                    line = 1
                    if data:
                        vals = []
                        for key,val in enumerate(data):  # 遍历数据
                            if val['line'] != line:  # 换行
                                rt.add('。\a')
                                line = val['line']
                            separater = '，'
                            if (key + 1 < len(data) and data[key + 1]['line'] != line):
                                separater = ''
                            elif (key + 1 == len(data)):
                                separater = '。'
                            # 生成单元格内容
                            column = columns.filter(id=val['column_id'])[0]
                            value = column.column_name
                            if column.parameter is not None:
                                value += '(参数名：' + column.parameter + ')'
                                if column.formula is not None:
                                    #  有参数名，又有公式的情况
                                    value += '的计算公式为：' + column.formula + separater
                                    value += '计算结果是' + val['value'] + separater
                                else:
                                    value += '是' + val['value'] + separater
                            #  没有参数名，有公式的情况
                            elif column.formula is not None:
                                value += '的计算公式为：' + column.formula + separater
                                value += '计算结果是' + val['value'] + separater
                            else:
                                #  没有参数名，没有公式的情况
                                value += '是' + val['value'] + separater
                            rt.add(value, style='标题 4')
                        rt.add('\a')

            data = {
                'project_name': p.project_name,
                'project_num': p.project_num,
                'project_text': p.project_text,
                'designer': p.designer,
                'proofreader': p.proofreader,
                'chief': p.chief,
                'approver': p.approver,
                'version': p.version,
                'select_module': modules.strip('、'),
                'rt': rt,
            }


        except Exception as e:
            return json_error(e)

        # 删除生成的报告
        filepath = os.getcwd() + '/templates/project'
        filename = '项目报告.docx'  # 所生成的word文档需要以.docx结尾，文档格式需要
        # delete_docx_file(filepath)       # 收到每个请求后，会将文件当中的非模板文件删除
        template_path = filepath + '/project_tpl.docx'
        template = DocxTemplate(template_path)
        template.render(context=data)
        template.save(os.path.join(filepath, filename))
        response = StreamingHttpResponse(read_file(os.path.join(filepath, filename), 512))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
        # time.sleep(10)
        return response
    else:
        return json_error('项目不存在')
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
            else:
                return render(request, 'login.html', context={"status": 'failed'})
    return render(request, 'login.html')


# 登出
def logout(request):
    auth.logout(request)
    return redirect('/login/')


# 获取table下面的column
def get_column(request, id):
    columns = Column.objects.filter(table_id=id)
    result = []
    for i in columns:
        result.append({'id': i.id, 'name': i.column_name})
    return HttpResponse(json.dumps(result), content_type="application/json")


def nestedheader(request):
    return render(request, 'nestedheader.html')


def test_page(request):
    return render(request, 'test_page.html')


def gas_test(request):
    return render(request, 'Gas_test.html')


def sprinkle_test(request):
    return render(request, 'Sprinkle_test.html')

def model_test(request):
    objs = Project.objects.all()
    obj = Project.objects.all().first()
    obj1 = Project.objects.filter(id=1)
    objg = Project.objects.get(id=1)
    print(objg)
    return render(request, 'Sprinkle_test.html')


def module1(request):
    return render(request, 'module.html')