from django.shortcuts import render, redirect
from page.pager import Pagination
from django.http import QueryDict
# Create your views here.
HOST_LIST = []

for i in range(1, 1040):
    HOST_LIST.append("c%s.com" % i)


def hosts(request):
    # 第一版
    # try:
    #     current_page = int(request.GET.get('page',1))
    # except:
    #     current_page = 1
    # per_page_count =10
    #
    # start = (current_page-1)*per_page_count
    # end = current_page*per_page_count
    # host_list = HOST_LIST[start:end]
    #
    # total_count = len(HOST_LIST)
    #
    # max_page_num,div= divmod(total_count,per_page_count)
    # if div:
    #     max_page_num+=1
    #     page_html_list =[]
    #     for i in range(1,max_page_num+1):
    #         if i ==current_page:
    #             temp = '<a class="active" href="/hosts/?page=%s">%s</a>' %(i,i,)
    #         else:
    #             temp ='<a href="/hosts/?page=%s">%s</a>' %(i,i,)
    #
    #         page_html_list.append(temp)
    #     page_html = ''.join(page_html_list)
    #     return render(request,'hosts.html',{'host_list':host_list,'page_html':page_html})

    # 第二版
    # pager_obj = Pagination(request.GET.get('page', 1), len(HOST_LIST), request.path_info)
    # host_list = HOST_LIST[pager_obj.start:pager_obj.end]
    # html = pager_obj.page_html()
    # return render(request, 'hosts.html', {'host_list': host_list, "page_html": html})

    # 第三版
    pager_obj = Pagination(request.GET.get('page', 1), len(HOST_LIST), request.path_info, request.GET)
    host_list = HOST_LIST[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    # list_condition = request.GET.urlencode()
    # print(list_condition)
    params = QueryDict(mutable=True)
    params['_list_filter'] = request.GET.urlencode()
    list_condition = params.urlencode()
    return render(request, 'hosts.html', {'host_list': host_list, "page_html": html, 'list_condition': list_condition})


def edit_host(request, pk):
    if request.method == "GET":
        return render(request, 'edit_host.html')
    else:
        # 修改成功 /hosts/?page=5&id__gt=4
        url = "/hosts/?%s" % (request.GET.get('_list_filter'))
        return redirect(url)


USER_LIST = []
for i in range(1, 1040):
    USER_LIST.append("bbbb%s" % i)

def user(request):
    pager_obj = Pagination(request.GET.get('page', 1), len(USER_LIST), request.path_info)
    user_list = USER_LIST[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    return render(request, 'user.html', {'user_list': user_list, "page_html": html})


