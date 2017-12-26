from stark.service import router
from crm import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import redirect, HttpResponse, render
from crm.configs.student import StudentConfig


class DepartmentConfig(router.StarkConfig):
    list_display = ['id', 'title', 'code']
    edit_link = ['title', ]


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
    edit_link = ['username', ]


router.site.register(models.UserInfo, UserInfoConfig)


class CourseConfig(router.StarkConfig):
    list_display = ['id', 'name', ]
    edit_link = ['name', ]


router.site.register(models.Course, CourseConfig)


class SchoolConfig(router.StarkConfig):
    list_display = ['id', 'title']

    edit_link = ['title', ]


router.site.register(models.School, SchoolConfig)


class ClassListConfig(router.StarkConfig):
    def course_semester(self, obj=None, is_header=False):
        if is_header:
            return '班级'

        return "%s(%s期)" % (obj.course.name, obj.semester,)

    def num(self, obj=None, is_header=False):
        if is_header:
            return '人数'
        # obj是班级对象
        # 学生和班级的关系 M2M
        # ############## 作业1：列举班级的人数 #############
        # ############## 作业2：组合搜索（校区、课程） #############
        # ############## 作业3：popup增加时，是否将新增的数据显示到页面中（获取条件） #############

        return obj.student_set.count()

    list_display = ['school', course_semester, num, 'start_date']
    edit_link = [course_semester, ]
    comb_filter = [
        router.FilterOption('school'),
        router.FilterOption('course'),
    ]


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

    # def changelist_view(self, request, *args, **kwargs):
    #     customer = request.GET.get('customer')
    #     # session中获取当前用户ID
    #     current_login_user_id = 0
    #     ct = models.Customer.objects.filter(consultant=current_login_user_id, id=customer).count()
    #     if not ct:
    #         return HttpResponse('别抢客户呀...')
    #
    #     return super(ConsultRecordConfig, self).changelist_view(request, *args, **kwargs)
    edit_link = ['customer']


router.site.register(models.ConsultRecord, ConsultRecordConfig)

# class StudentConfig(router.StarkConfig):
#     def course_semester(self, obj=None, is_header=False):
#         if is_header:
#             return '班级'
#         return obj.class_list.first()
#
#     list_display = ['customer', 'username', course_semester]
#     edit_link = ['username']
#

router.site.register(models.Student, StudentConfig)


class PaymentRecordConfig(router.StarkConfig):
    list_display = ['customer']
    edit_link = ['customer']


router.site.register(models.PaymentRecord, PaymentRecordConfig)


class CourseRecordConfig(router.StarkConfig):
    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        url_list = [
            url(r'^(\d+)/score_list/$', self.wrap(self.score_list), name="%s_%s_score_list" % app_model_name),
        ]
        return url_list

    def score_list(self, request, record_id):
        """
        :param request:
        :param record_id:老师上课记录ID
        :return:
        """
        if request.method == "GET":
            # 方式一
            # study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            # score_choices = models.StudyRecord.score_choices
            # return render(request,'score_list.html',{'study_record_list':study_record_list,'score_choices':score_choices})
            # 方式二
            from django.forms import Form
            from django.forms import fields
            from django.forms import widgets

            # class TempForm(Form):
            #     score = fields.ChoiceField(choices=models.StudyRecord.score_choices)
            #     homework_note = fields.CharField(widget=widgets.Textarea())

            data = []
            study_record_list = models.StudyRecord.objects.filter(course_record_id=record_id)
            # print(study_record_list)
            for obj in study_record_list:
                # obj是对象
                TempForm = type('TempForm', (Form,), {
                    'score_%s' % obj.pk: fields.ChoiceField(choices=models.StudyRecord.score_choices),
                    'homework_note_%s' % obj.pk: fields.CharField(widget=widgets.Textarea(attrs={'cols': 50, 'rows': 10,'style':"margin: 0px; height: 30px; width: 500px;"}),)
                })
                data.append({'obj': obj, 'form': TempForm(
                    initial={'score_%s' % obj.pk: obj.score, 'homework_note_%s' % obj.pk: obj.homework_note})})

                # print(data)
            return render(request, 'score_list.html',
                          {'data': data})

        else:
            data_dict = {}
            for key, value in request.POST.items():
                if key == "csrfmiddlewaretoken":
                    continue
                name, nid = key.rsplit('_', 1)
                if nid in data_dict:
                    data_dict[nid][name] = value
                else:
                    data_dict[nid] = {name: value}

            for nid, update_dict in data_dict.items():
                models.StudyRecord.objects.filter(id=nid).update(**update_dict)

            return redirect('/stark/crm/courserecord/')

    def kaoqin(self, obj=None, is_header=False):
        if is_header:
            return '考勤'

        return mark_safe("<a href='/stark/crm/studyrecord/?course_record=%s'>考勤管理</a>" % obj.pk)

    def display_score_list(self, obj=None, is_header=False):
        if is_header:
            return '成绩录入'
        from django.urls import reverse
        rurl = reverse("stark:crm_courserecord_score_list", args=(obj.pk,))
        return mark_safe("<a href='%s'>成绩录入</a>" % rurl)

    list_display = ['class_obj', 'day_num', kaoqin, display_score_list]

    def multi_init(self, request):
        """
        自定义执行批量初始化方法
        :param request:
        :return:
        """
        # 上课记录ID列表
        pk_list = request.POST.getlist('pk')

        # 上课记录对象
        record_list = models.CourseRecord.objects.filter(id__in=pk_list)
        for record in record_list:
            # day1,day2,day3
            # record.class_obj # 关联的班级
            exists = models.StudyRecord.objects.filter(course_record=record).exists()
            if exists:
                continue

            student_list = models.Student.objects.filter(class_list=record.class_obj)
            bulk_list = []
            for student in student_list:
                # 为每一个学生创建dayn的学习记录
                bulk_list.append(models.StudyRecord(student=student, course_record=record))
            models.StudyRecord.objects.bulk_create(bulk_list)
            # for record in record_list:
            #     student_list = models.Student.objects.filter(class_list=record.class_obj)
            #     bulk_list = []
            #     for student in student_list:
            #         # 为每一个学生创建dayn的学习记录
            #         exists = models.StudyRecord.objects.filter(student=student,course_record=record).exists()
            #         if exists:
            #             continue
            #         bulk_list.append(models.StudyRecord(student=student,course_record=record))
            #     models.StudyRecord.objects.bulk_create(bulk_list)

            # return redirect('http://www.baidu.com')

    multi_init.short_desc = "学生初始化"
    actions = [multi_init, ]

    show_actions = True


router.site.register(models.CourseRecord, CourseRecordConfig)


class StudyRecordConfig(router.StarkConfig):
    def display_record(self, obj=None, is_header=False):
        if is_header:
            return '出勤'
        return obj.get_record_display()

    list_display = ['course_record', 'student', display_record]

    comb_filter = [
        router.FilterOption('course_record')
    ]

    def action_checked(self, request):
        pass

    action_checked.short_desc = "签到"

    def action_vacate(self, request):
        pass

    action_vacate.short_desc = "请假"

    def action_late(self, request):
        pass

    action_late.short_desc = "迟到"

    def action_noshow(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='noshow')

    action_noshow.short_desc = "缺勤"

    def action_leave_early(self, request):
        pass

    action_leave_early.short_desc = "早退"

    actions = [action_checked, action_vacate, action_late, action_noshow, action_leave_early]

    show_actions = True

    show_add_btn = False
    edit_link = ['course_record']


router.site.register(models.StudyRecord, StudyRecordConfig)
