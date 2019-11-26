from django.contrib import admin

# Register your models here.
from .models import Project, Table, Module, Column, ModuleTable, ProjectTable, ColumnDropdown, Dropdown


class TagInline(admin.TabularInline):
    model = ProjectTable


class TableAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'table_en_name', 'catalog', 'total')  # list


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_en_name')  # list


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_num', 'project_text', 'designer', 'proofreader', 'chief',
                    'approver', 'version', 'user')  # list
    inlines = [TagInline]


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('column_name', 'table', 'parameter', 'formula', 'c_formula', 'dropdown', 'defaultv', 'prompt', 'must',
                    'aggregation', 'type', 'width')  # list


class ModuleTableAdmin(admin.ModelAdmin):
    list_display = ('module', 'table', 'have')  # list


class ProjectTableAdmin(admin.ModelAdmin):
    list_display = ('project', 'module', 'table')  # list


class ColumnDropdownAdmin(admin.ModelAdmin):
    list_display = ('column', 'dd_name')


class DropdownAdmin(admin.ModelAdmin):
    list_display = ('dd_name', 'name', 'group', 'title')


admin.site.register(Table, TableAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Column, ColumnAdmin)
admin.site.register(ModuleTable, ModuleTableAdmin)
admin.site.register(ProjectTable, ProjectTableAdmin)
admin.site.register(ColumnDropdown, ColumnDropdownAdmin)
admin.site.register(Dropdown, DropdownAdmin)
admin.site.site_header = '消防系统计算平台'
admin.site.site_title = '系统管理'
