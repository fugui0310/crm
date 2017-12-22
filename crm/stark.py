from stark.service import router
from crm import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import redirect, HttpResponse


class DepartmentConfig(router.StarkConfig):
    list_display = ['id', 'title', 'code']


router.site.register(models.Department, DepartmentConfig)


class UserInfoConfig(router.StarkConfig):
    show_add_btn = True

    show_search_form = True
    search_fields = ['name__contains', 'email__contains']

    show_actions = True

    def multi_del(self, request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        # return HttpResponse('删除成功')
        return redirect(self.get_list_url())

    multi_del.short_desc = "批量删除"

    def multi_init(self, request):
        pk_list = request.POST.getlist('pk')

    multi_init.short_desc = "初始化"

    actions = [multi_del, multi_init]
    list_display = ['id', 'username', 'email', 'depart']


router.site.register(models.UserInfo, UserInfoConfig)


class CourseConfig(router.StarkConfig):
    list_display = ['id', 'name', ]


router.site.register(models.Course, CourseConfig)


class SchoolConfig(router.StarkConfig):
    list_display = ['id', 'title']


router.site.register(models.School, SchoolConfig)


class ClassListConfig(router.StarkConfig):
    list_display = ['id', 'school', 'course', 'semester', 'price', 'start_date', 'graduate_date', 'tutor']


router.site.register(models.ClassList, ClassListConfig)


class CustomerConfig(router.StarkConfig):
    def display_gender(self, obj=None, is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()

    def display_education(self, obj=None, is_header=False):
        if is_header:
            return '学历'
        return obj.get_education_display()

    def display_course(self, obj=None, is_header=False):
        if is_header:
            return '咨询课程'
        course_list = obj.course.all()
        html = []
        # self.request.GET
        # self._query_param_key
        # 构造QueryDict
        # urlencode()
        for item in course_list:
            temp = "<a style='display:inline-block;padding:3px 5px;border:1px solid blue;margin:2px;' href='/stark/crm/customer/%s/%s/dc/'>%s X</a>" % (
                obj.pk, item.pk, item.name)
            html.append(temp)

        return mark_safe("".join(html))

    def display_status(self, obj=None, is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()

    def record(self, obj=None, is_header=False):
        if is_header:
            return '跟进记录'
        # /stark/crm/consultrecord/?customer=11
        return mark_safe("<a href='/stark/crm/consultrecord/?customer=%s'>查看跟进记录</a>" % (obj.pk,))

    list_display = ['qq', 'name', display_gender, display_education, display_course, display_status, record]
    edit_link = ['qq']

    def delete_course(self, request, customer_id, course_id):
        """
        删除当前用户感兴趣的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        """
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        # 跳转回去时，要保留原来的搜索条件
        return redirect(self.get_list_url())

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/dc/$', self.wrap(self.delete_course), name="%s_%s_dc" % app_model_name),
        ]
        return patterns

    show_search_form = True
    search_fields = ['name__contains', 'email__contains']

    show_actions = True

    def multi_del(self, request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        # return HttpResponse('删除成功')
        return redirect(self.get_list_url())

    multi_del.short_desc = "批量删除"

    def multi_init(self, request):
        pk_list = request.POST.getlist('pk')

    multi_init.short_desc = "初始化"

    actions = [multi_del, multi_init]

    comb_filter = [
        router.FilterOption('gender', is_choice=True),
        router.FilterOption('education', is_choice=True),
        router.FilterOption('experience', is_choice=True),
        router.FilterOption('source', is_choice=True),
    ]


router.site.register(models.Customer, CustomerConfig)


class ConsultRecordConfig(router.StarkConfig):
    list_display = ['customer', 'consultant', 'date']

    comb_filter = [
        router.FilterOption('customer')
    ]

    def changelist_view(self, request, *args, **kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 1
        ct = models.Customer.objects.filter(consultant=current_login_user_id, id=customer).count()
        if not ct:
            return HttpResponse('别抢客户呀...')

        return super(ConsultRecordConfig, self).changelist_view(request, *args, **kwargs)


router.site.register(models.ConsultRecord, ConsultRecordConfig)
