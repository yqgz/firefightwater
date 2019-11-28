from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    project_name = models.CharField('项目名称', max_length=50)
    project_num = models.CharField('项目编号', max_length=20)
    project_text = models.TextField('项目概况')
    designer = models.CharField('设计人', max_length=50)
    proofreader = models.CharField('校对人', max_length=50)
    chief = models.CharField('专业负责人', max_length=50)
    approver = models.CharField('审批人', max_length=50)
    version = models.CharField('版本号', max_length=50)
    pub_date = models.DateTimeField('date published', auto_now=True)

    def __str__(self):
        return self.project_name


class Table(models.Model):
    table_name = models.CharField('表名', max_length=50)
    table_en_name = models.CharField('英文名', max_length=50)
    catalog = models.CharField('所属模块', max_length=50)
    subtitle1 = models.CharField('小标题一', max_length=50, null=True, blank=True)
    subtitle2 = models.CharField('小标题二', max_length=50, null=True, blank=True)
    # 填写"合计："等文字
    SUM = '合计'
    MAX = '最大值'
    ACHOICES = (
        (SUM, '合计'),
        (MAX, '最大值'),
    )
    total = models.CharField('合计', max_length=20, choices=ACHOICES, null=True, blank=True)
    pub_date = models.DateTimeField('date published', auto_now=True)

    def __str__(self):
        return self.table_name


class Module(models.Model):
    module_name = models.CharField('模块名', max_length=50)
    module_en_name = models.CharField('英文模块名', max_length=50)

    def __str__(self):
        return self.module_name


class ModuleTable(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, db_index=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, db_index=True)
    YES = '是'
    NO = '否'
    CHOICES = (
        (YES, '是'),
        (NO, '否'),
    )
    have = models.CharField(max_length=2, choices=CHOICES, default=NO)


class ProjectTable(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_index=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, db_index=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, db_index=True)


class Column(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, db_index=True)
    column_name = models.CharField('列名', max_length=50)
    title = models.CharField('标题', max_length=20, null=True, blank=True)
    column_en_name = models.CharField('英文名', max_length=50)
    parameter = models.CharField('参数名', max_length=10, null=True, blank=True)
    formula = models.CharField('公式', max_length=100, null=True, blank=True)
    c_formula = models.CharField('计算公式', max_length=100, null=True, blank=True)  # 正则提取
    dropdown = models.CharField('下拉列表', max_length=10, null=True, blank=True)
    defaultv = models.CharField('默认值', max_length=100, null=True, blank=True)
    prompt = models.CharField('提示', max_length=100, null=True, blank=True)
    must = models.BooleanField('是否必填', default=True)
    # 填写"SUM"、"MAX"等
    SUM = 'SUM'
    MAX = 'MAX'
    AVG = 'AVG'
    ACHOICES = (
        (SUM, 'SUM'),
        (MAX, 'MAX'),
        (AVG, 'AVG'),
    )
    aggregation = models.CharField('合计方式', max_length=10, choices=ACHOICES, null=True, blank=True)
    # 填写
    TEXT = 'text'
    CHECKBOX = 'checkbox'
    DROPDOWN = 'dropdown'
    ACHOICES = (
        (TEXT, 'text'),
        (CHECKBOX, 'checkbox'),
        (DROPDOWN, 'dropdown'),
    )

    type = models.CharField('类型', max_length=10, choices=ACHOICES, default='text')
    width = models.IntegerField('列宽度', default=100)
    pub_date = models.DateTimeField('date published', auto_now=True)

    def __str__(self):
        return self.column_name


class Dropdown(models.Model):
    dd_name = models.CharField('下拉列表名', max_length=100)

    def __str__(self):
        return self.dropdown


class ColumnDropdown(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, db_index=True)
    dropdown = models.ForeignKey(Dropdown, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return self.dropdown + self.table


class DropdownItem(models.Model):
    dd_name = models.ForeignKey(Dropdown, on_delete=models.CASCADE, db_index=True)
    name = models.CharField('下拉列表项', max_length=100)
    group = models.CharField('列表项分组', max_length=100, null=True, blank=True)
    title = models.CharField('列表项描述', max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name


class Value(models.Model):
    project_table = models.ForeignKey(ProjectTable, on_delete=models.CASCADE, db_index=True)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    line = models.IntegerField('第几行', null=True, blank=True)
    value = models.CharField('值', max_length=255)
    formula = models.CharField('公式', max_length=200, null=True, blank=True)
    pub_date = models.DateTimeField('date published', auto_now=True)

    def __str__(self):
        return self.value
