import xadmin

from apps.organizations.models import Teacher, CourseOrg, City


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company']
    search_fields = ['org', 'name', 'work_years', 'work_company']
    list_filter = ['org', 'name', 'work_years', 'work_company']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums']
    style_fields = {
        "desc": "ueditor"
    }


class CityAdmin(object):
    list_display = ["id", "name", "desc"]   #后台显示的列
    search_fields = ["name", "desc"]   #搜索框
    list_filter = ["name", "desc", "add_time"]  #过滤器
    list_editable = ["name", "desc"]  #列表直接修改


xadmin.site.register(Teacher, TeacherAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(City, CityAdmin)