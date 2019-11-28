from django.contrib import admin
from .models import Project, Table, Module, Column, ModuleTable, ProjectTable, ColumnDropdown, Dropdown


# 装饰器注册Model
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'table_en_name', 'catalog', 'total')  # list


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_en_name')  # list


class TagInline(admin.TabularInline):
    model = ProjectTable


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_num', 'project_text', 'designer', 'proofreader', 'chief',
                    'approver', 'version', 'user')  # list
    inlines = [TagInline]


@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = (
        'column_name', 'table', 'parameter', 'formula', 'c_formula', 'dropdown', 'defaultv', 'prompt', 'must',
        'aggregation', 'type', 'width')  # list


@admin.register(ModuleTable)
class ModuleTableAdmin(admin.ModelAdmin):
    list_display = ('module', 'table', 'have')  # list


@admin.register(ProjectTable)
class ProjectTableAdmin(admin.ModelAdmin):
    list_display = ('project', 'module', 'table')  # list


@admin.register(ColumnDropdown)
class ColumnDropdownAdmin(admin.ModelAdmin):
    list_display = ('column', 'dd_name')


@admin.register(Dropdown)
class DropdownAdmin(admin.ModelAdmin):
    list_display = ('dd_name', 'name', 'group', 'title')


admin.site.site_header = '消防系统计算平台'
admin.site.site_title = '系统管理'
