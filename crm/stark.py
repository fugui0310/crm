from stark.service import router
from crm import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import redirect, HttpResponse, render
from crm.configs.student import StudentConfig
import datetime, time
from django.db.models import Q
from django.forms import ModelForm
from django.db import transaction


class BasePermission(object):
    def get_show_add_btn(self):
        code_list = self.request.permission_code_list
        if "add" in code_list:
            return True

    def get_edit_link(self):
        code_list = self.request.permission_code_list
        if "edit" in code_list:
            return super(BasePermission,self).get_edit_link()
        else:
            return []

    def get_list_display(self):
        code_list = self.request.permission_code_list
        data = []
        if self.list_display:
            data.extend(self.list_display)
            if 'del' in code_list:
                data.append(router.StarkConfig.delete)
            data.insert(0, router.StarkConfig.checkbox)
        return data

        # get...


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

        return obj.student_set.count()

    list_display = ['school', course_semester, num, 'start_date']
    edit_link = [course_semester, ]
    comb_filter = [
        router.FilterOption('school'),
        router.FilterOption('course'),
    ]


router.site.register(models.ClassList, ClassListConfig)


class SingleModelForm(ModelForm):
    class Meta:
        model = models.Customer
        exclude = ['consultant', 'status', 'recv_date', 'last_consult_date']


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
    show_search_form = True
    search_fields = ['name__contains', 'email__contains']

    show_actions = True

    def multi_del(self, request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
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
    order_by = ['-status']

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
            url(r'^public/$', self.wrap(self.public_view), name="%s_%s_public" % app_model_name),
            url(r'^user/$', self.wrap(self.user_view), name="%s_%s_user" % app_model_name),
            url(r'^(\d+)/competition/$', self.wrap(self.competition_view), name="%s_%s_competition" % app_model_name),
            url(r'^single/$', self.wrap(self.single_view), name="%s_%s_single" % app_model_name),

        ]
        return patterns

    def public_view(self, request):
        """
        公共客户资源
        :param request:
        :return:
        """
        # 条件：未报名 并且 （ 15天未成单(当前时间-15 > 接客时间) or  3天未跟进(当前时间-3天>最后跟进日期) ） Q对象
        # status=2

        ctime = datetime.datetime.now().date()
        no_deal = ctime - datetime.timedelta(days=15)
        no_follow = ctime - datetime.timedelta(days=3)
        # models.Customer.objects.filter(Q(recv_date__lt=no_deal)|Q(last_consult_date__lt=no_follow),status=2).exclude(consultant_id=1)
        customer_list = models.Customer.objects.filter(Q(recv_date__lt=no_deal) | Q(last_consult_date__lt=no_follow),
                                                       status=2)
        print(customer_list)
        return render(request, 'public_view.html', {'customer_list': customer_list})

    def competition_view(self, request, cid):
        """
        抢单
        :param request:
        :param nid:
        :return:
        """
        current_user_id = 10
        ctime = datetime.datetime.now().date()
        no_deal = ctime - datetime.timedelta(days=15)
        no_follow = ctime - datetime.timedelta(days=3)
        row_count = models.Customer.objects.filter(Q(recv_date__lt=no_deal) | Q(last_consult_date__lt=no_follow),
                                                   status=2, id=cid).exclude(consultant_id=current_user_id).update(
            recv_date=ctime, last_consult_date=ctime, consultant_id=current_user_id)
        # print(row_count)
        if not row_count:
            return HttpResponse('手速太慢了')

        models.CustomerDistribution.objects.create(user_id=current_user_id, customer_id=cid, ctime=ctime)
        return HttpResponse('抢单成功')

    def user_view(self, request):
        """
        当前登录用户的所有客户
        :param request:
        :return:
        """
        # 去session中获取当前登录用户ID
        current_user_id = 10

        # 当前用户的所有客户列表
        customers = models.CustomerDistribution.objects.filter(user_id=current_user_id).order_by('status')

        return render(request, 'user_view.html', {'customers': customers})

    def single_view(self, request):
        """
        单条录入客户信息
        :param request:
        :return:
        """

        if request.method == "GET":
            form = SingleModelForm()
            return render(request, 'single_view.html', {'form': form})
        else:
            from crm.singleinput import AutoSale
            form = SingleModelForm(request.POST)

            if form.is_valid():
                """客户表新增数据：
                   - 获取该分配的课程顾问id
                   - 当前时间
                客户分配表中新增数据
                   - 获取新创建的客户ID
                   - 顾问ID
               """
                ctime = datetime.datetime.now().date()
                sale_id = AutoSale.get_sale_id()
                if not sale_id:
                    return HttpResponse("无销售顾问，无法进行自动分配")

                try:
                    with transaction.atomic():
                        course = form.cleaned_data.pop('course')
                        customer_obj = models.Customer.objects.create(**form.cleaned_data, consultant_id=sale_id,
                                                                      recv_date=ctime)
                        customer_obj.course.add(*course)
                        models.CustomerDistribution.objects.create(user_id=sale_id, customer=customer_obj, ctime=ctime)
                    #
                    # with transaction.atomic():
                    #     # 创建客户表
                    #     form.instance.consultant_id = sale_id
                    #     form.instance.recv_date = ctime
                    #     form.instance.last_consult_date = ctime
                    #     new_customer = form.save()
                    #     # 创建客户分配表
                    #     models.CustomerDistribution.objects.create(customer=new_customer, user_id=sale_id, ctime=ctime)

                        # 发送消息
                        import message
                        message.send_message('你别走了', '三个月工资太多了','542770353@qq.com', '放哨',)

                except Exception as e:
                    # 创建客户和分配销售异常
                    AutoSale.rollback(sale_id)
                    return HttpResponse('录入异常')

                return HttpResponse('录入成功')

            else:
                return render(request, 'single_view.html', {'form': form})


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
# 另写于study.py文件

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
                    'homework_note_%s' % obj.pk: fields.CharField(widget=widgets.Textarea(
                        attrs={'cols': 50, 'rows': 10, 'style': "margin: 0px; height: 30px; width: 500px;"}), )
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
            return '成绩'
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
        # print(record_list)
        for record in record_list:
            # day1,day2,day3
            # record.class_obj # 关联的班级r
            exists = models.StudyRecord.objects.filter(course_record=record).exists()
            # print(exists)
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
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='checked')

    action_checked.short_desc = "签到"

    def action_vacate(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='vacate')

    action_vacate.short_desc = "请假"

    def action_late(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='late')

    action_late.short_desc = "迟到"

    def action_noshow(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='noshow')

    action_noshow.short_desc = "缺勤"

    def action_leave_early(self, request):
        pk_list = request.POST.getlist('pk')
        models.StudyRecord.objects.filter(id__in=pk_list).update(record='leave_early')

    action_leave_early.short_desc = "早退"

    actions = [action_checked, action_vacate, action_late, action_noshow, action_leave_early]

    show_actions = True

    show_add_btn = False
    edit_link = ['course_record']


router.site.register(models.StudyRecord, StudyRecordConfig)


class SaleRankConfig(router.StarkConfig):
    list_display = ['user', 'num', 'weight']
    edit_link = ['user']


router.site.register(models.SaleRank, SaleRankConfig)


class CustomerDistributionConfig(router.StarkConfig):
    list_display = ['user', 'customer', 'ctime']
    edit_link = ['user']


router.site.register(models.CustomerDistribution, CustomerDistributionConfig)
