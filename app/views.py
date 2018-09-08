import datetime
import json
from io import BytesIO

from django import forms
from django.db.models import Q
from django.forms import fields
from django.forms import widgets
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.views import View

from app import email_send
from app import models
from utils.check_code import create_validate_code
from utils.draw_image import draw_gragh


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = models.EmailVerifyRecord.objects.filter(code=active_code)
        print(active_code)
        print(active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = models.User.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


class AddCommentView(View):
    def post(self, request):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail"}', content_type='application/json')


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['name', 'content', 'wlibrary']


class User(forms.Form):
    #Login in interface, error_messages is the parameter of fields. If the username and password is null, prompt it. widget is the attributes of the input tag
    username = fields.CharField(error_messages={'required': 'Username is not null.'},
                                widget=widgets.Input(attrs={'type': "text", 'class': "form-control", 'name': "username",
                                                            'id': "username", 'placeholder': "Please input Username"}))
    # For Passsword
    password = fields.CharField(error_messages={'required': 'Password is not null.'},
                                widget=widgets.Input(
                                    attrs={'type': "password", 'class': "form-control", 'name': "password",
                                           'id': "password",
                                           'placeholder': "Please input Password"}))


class Newuser(forms.Form):
    #register interface, Username is not more 9, not less 3, not null.
    username = fields.CharField(max_length=9, min_length=3,
                                error_messages={'required': 'Username is not null.', 'max_length': 'Username is not more 9.',
                                                'min_length': 'Username is not less 3'},
                                widget=widgets.Input(attrs={'type': "text", 'class': "form-control", 'name': "username",
                                                            'id': "username", 'placeholder': "Please input Username"}))
    email = fields.EmailField(error_messages={'required': 'Email address is not null', 'invalid': 'Email format is incorrect '}, widget=widgets.Input(
        attrs={'type': "email", 'class': "form-control", 'name': "email", 'id': "email", 'placeholder': "Please enter your email address"}))

    # In the registration interface, the maximum length of password box is not more 12, the minimum cannot be less than 6, and cannot be null
    password = fields.CharField(max_length=12, min_length=6,
                                error_messages={'required': 'The password cannot be null.', 'max_length': 'password is not more 12',
                                                'min_length': 'password is not less 6'},
                                widget=widgets.Input(
                                    attrs={'type': "password", 'class': "form-control", 'name': "password",
                                           'id': "password",
                                           'placeholder': "Please input your password"})
                                )
    # In the registration interface, the maximum length of the password box can't be more than 9, and the content of the password box is compared with the previous one. The inconsistency of two times indicates "inconsistency of two passwords", and the minimum cannot be less than 3 and cannot be empty
    confirm_password = fields.CharField(max_length=12, min_length=6,
                                        error_messages={'required': 'not null.', 'max_length': 'The two passwords differ. ',
                                                        'min_length': 'The two passwords differ. '},
                                        widget=widgets.Input(
                                            attrs={'type': "password", 'class': "form-control",
                                                   'name': "confirm_password",
                                                   'id': "confirm_password",
                                                   'placeholder': "Please input the password"})
                                        )


def check_code(request):
    """
   verification code
    :param request:
    :return:
    """
    # stream = BytesIO()
    # img, code = create_validate_code()
    # img.save(stream, 'PNG')
    # request.session['CheckCode'] = code
    # return HttpResponse(stream.getvalue())

    # data = open('static/imgs/avatar/20130809170025.png','rb').read()
    # return HttpResponse(data)

    # 1. Create a picture pip3 install Pillow
    # 2. Write random strings in the image
    # obj = object ()
    # 3. Write the picture to the development file
    # 4.Open the make directory file and read the contents
    # 5. HttpResponse(data)

    stream = BytesIO()
    img, code = create_validate_code()
    # f=open('cc.png','wb')
    # img.save(f,'PNG')
    img.save(stream, 'PNG')
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue())
    # return HttpResponse(open('cc.png','rb').read())


def login(request):
    """
    login
    :param request:
    :return:
    """
    # if request.method == "POST":
    #     if request.session['CheckCode'].upper() == request.POST.get('check_code').upper():
    #         pass
    #     else:
    #         print('Verify code entered is wrong')
    er = ''
    s = ''
    if request.method == 'GET':
        obj = User()
        return render(request, 'login.html', {'obj': obj})
    if request.method == 'POST':
        obj = User(request.POST)
        code = request.POST.get('check_code')
        auto = request.POST.get('auto')
        if auto:
            request.session.set_expiry(2419200)
        else:
            pass
        if code.upper() == request.session['CheckCode'].upper():
            u = request.POST.get('username')
            t1 = models.User.objects.filter(username=u)
            if t1:
                pwd = request.POST.get('password')
                if pwd == t1[0].pwd:
                    request.session['user'] = u
                    request.session['is_login'] = True
                    request.session['pwd'] = pwd
                    return redirect('/views/')
                else:
                    s = '''
                  <script>alert('Password error,Please re-type.');</script>
                  '''
            else:
                s = '''
           <script>alert('this username does not exist,Please check if it is correct.');</script>
                                '''

        else:
            er = 'Verify code entered is wrong.'
        return render(request, 'login.html', {'obj': obj, 'er': er, 's': s})


def nickname(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        u = request.session.get('user', None)
        user = models.User.objects.filter(username=u).first()
        user.nickname = nickname
        user.save()
    return HttpResponseRedirect('/my/')


def description(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        u = request.session.get('user', None)
        user = models.User.objects.filter(username=u).first()
        user.description = description
        user.save()
    return HttpResponseRedirect('/my/')


def register(request):
    """
    register
    :param request:
    :return:
    """
    er = ''
    if request.method == 'GET':
        obj = Newuser()
        return render(request, 'register.html', {'obj': obj, 'er': er})
    if request.method == 'POST':
        try:
            obj = Newuser(request.POST)
            r = obj.is_valid()
            if r:
                code = request.POST.get('check_code')
                if code.upper() == request.session['CheckCode'].upper():
                    user = request.POST.get('username')
                    email = request.POST.get('email')
                    nickname = email_send.random_str(5)
                    u = models.User.objects.filter(username=user)
                    ue = models.User.objects.filter(email=email)
                    un = models.User.objects.filter(nickname=nickname)
                    if u:
                        s = '''
                    <script>alert('The username already exists, please input the username again!');
                    </script>
                     '''

                    elif ue:
                        s = '''
                    <script>alert('Email has been registered, please re-enter email!');
                    </script>
                    '''
                    elif un:
                        s = '''
                        <script>alert('The nickname already exists, please try again!');
                        </script>
                        '''
                    else:
                        pwd1 = request.POST.get('password')
                        pwd2 = request.POST.get('confirm_password')
                        if pwd1 != pwd2:
                            s = '''
                        <script>alert('Two passwords do not match, please check and re-enter!');</script>'''
                        else:

                            description = email_send.random_str(10)
                            models.User.objects.create(username=user, pwd=pwd1, email=email, nickname=nickname,
                                                       description=description)
                            email_send.send_register_email(email, "register")
                            s = '''
                        <script>alert('registered successfully ');
                        </script>'''
                    return render(request, 'register.html', {'obj': obj, 'er': er, 's': s})
                else:
                    er = 'Verify code entered is wrong. '
                    return render(request, 'register.html', {'obj': obj, 'er': er})

            else:
                s = '''
            <script>alert('Incorrect information format, registration failed!');
                </script>'''
                return render(request, 'register.html', {'obj': obj, 'er': er, 's': s})
        except Exception as e:
            print(e)

            s = '''
           <script>alert('error, please try again.');</script>'''
            obj = Newuser()
            return render(request, 'register.html', {'s': s, 'obj': obj})


def views(request):
    u = request.session.get('user', None)
    if request.method == 'GET':
        obj = None
        return render(request, 'views.html', {'obj': obj, 'u': u})
    elif request.method == 'POST':
        data = request.POST['content']
        objs = models.Wlibrary.objects.filter(name__icontains=data)
        obj_list = [each.name for each in objs]
        res_dict = {
            "massage": "success",
            "code": 0,
            "successful": True,
            "data": obj_list
        }
        return JsonResponse(res_dict)
        # ret = {'status': True, 'data': None, 'error': None, 'relations': True, 'data2': None, 'exp': None, 'type': None,
        #        'display_type': True}
        # contents = request.POST.get('content', None)
        # content_split = contents.split('/')
        # if len(content_split) != 1:
        #     ret['display_type'] = False
        # if len(content_split) == 1:
        #     # print(content_split)
        #     aims = []
        #     for content in content_split:
        #         aim = models.Wlibrary.objects.filter(name__icontains=content)
        #         aims.extend(aim)
        #     if aims:
        #         datas = []
        #         datas2 = []
        #         exps = []
        #         types = []
        #         for a in aims:
        #             obj = models.Relation.objects.filter(Q(t1_id=a.id) | Q(t2_id=a.id)).distinct().order_by('t1_id')
        #             objs = obj
        #             # print('Length',len(obj))
        #             if objs:
        #                 for row in objs:
        #                     if row.t1.name in datas and row.t2.name in datas2 and row.l_name_exp in exps:
        #                         pass
        #                     else:
        #                         datas.append(row.t1.name)
        #                         datas2.append(row.t2.name)
        #                         exps.append(row.l_name_exp)
        #                         types.append(row.l_name_r_id)
        #         ret['exp'] = json.dumps(exps)
        #         ret['data'] = json.dumps(datas)
        #         ret['data2'] = json.dumps(datas2)
        #         ret['type'] = json.dumps(types)
        #         if ret['data'] == None:
        #             ret['relations'] = False
        #             for row in aim:
        #                 datas.append(row.name)
        #             ret['data'] = json.dumps(datas)
        #
        #     else:
        #         obj = None
        #         ret['status'] = False
        #         ret['error'] = '未找到相关定理！！！'
        # elif len(content_split) >= 1:
        #     aims = []
        #     for content in content_split:
        #         aim = models.Wlibrary.objects.filter(name__icontains=content)
        #         aims.extend(aim)
        #     if aims:
        #         datas = []
        #         datas2 = []
        #         exps = []
        #         types = []
        #         for a in aims:
        #             for b in aims:
        #                 obj = models.Relation.objects.filter(Q(t1_id=a.id) & Q(t2_id=b.id)).distinct().order_by('t1_id')
        #                 objs = obj
        #                 if objs:
        #                     for row in objs:
        #                         if row.t1.name in datas and row.t2.name in datas2 and row.l_name_exp in exps:
        #                             pass
        #                         else:
        #                             datas.append(row.t1.name)
        #                             datas2.append(row.t2.name)
        #                             exps.append(row.l_name_exp)
        #                             types.append(row.l_name_r_id)
        #         ret['exp'] = json.dumps(exps)
        #         ret['data'] = json.dumps(datas)
        #         ret['data2'] = json.dumps(datas2)
        #         ret['type'] = json.dumps(types)
        #         if ret['data'] == None:
        #             ret['relations'] = False
        #             for row in aim:
        #                 datas.append(row.name)
        #             ret['data'] = json.dumps(datas)
        #
        #     else:
        #         obj = None
        #         ret['status'] = False
        #         ret['error'] = '未找到相关定理！！！'
        # else:
        #     ret['status'] = False
        #     ret['error'] = '搜索格式不正确！！！'
        # return HttpResponse(json.dumps(ret))


def add(request):
    f = request.session.get('is_login', None)
    u = request.session.get('user', None)
    error = ''
    if f:
        if request.method == 'GET':
            return render(request, 'add.html', {'u': u, 'error': error})
        elif request.method == 'POST':
            t_name = request.POST.get('t_name', None)
            # t_label=request.POST.get('t_label',None)
            t_exp = request.POST.get('t_exp', None)
            t_ref = request.POST.get('t_ref', None)
            mcdc_1 = request.POST.get('mcdc1')
            mcdc_2 = request.POST.get('mcdc2')
            if t_name and t_exp and t_ref:
                if models.Wlibrary.objects.filter(name=t_name):
                    error = '''<script>alert('The theorem already exists!!!Can not be added repeatedly！！！');</script>'''
                else:
                    u_id = models.User.objects.filter(username=u).first().id
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    models.Wlibrary.objects.create(name=t_name, ref=t_ref, exp=t_exp, publish=time, user_id=u_id,
                                                   mcdc_1=mcdc_1, mcdc_2=mcdc_2)
                    error = '''<script>alert('add successfully！！！');</script>'''
            else:
                error = '''<script>alert('Please fill in all the information of the theorem！！！');</script>'''
            return render(request, 'add.html', {'u': u, 'error': error})
    else:
        obj = User()
        return render(request, 'login.html', {'obj': obj})


def logout(request):
    request.session.clear()
    return render(request, 'views.html')


def my(request):
    f = request.session.get('is_login', None)
    u = request.session.get('user', None)
    print('---')
    print(u)
    print(f)
    if f:
        u_id = models.User.objects.filter(username=u).first().id
        user = models.User.objects.filter(username=u).first()
        obj = models.Wlibrary.objects.filter(user_id=u_id)
        return render(request, 'my.html', {'obj': obj, 'u': user})
    else:
        obj = User()
        return render(request, 'login.html', {'obj': obj})


def add_r(request):
    f = request.session.get('is_login', None)
    u = request.session.get('user', None)

    error = ''
    if f:
        if request.method == 'GET':
            obj = models.Wlibrary.objects.all()
            nexus = models.Nexus.objects.all()
            return render(request, 'add_r.html', {'u': u, 'obj': obj, 'error': error, 'nexus': nexus})
        elif request.method == 'POST':
            obj = models.Wlibrary.objects.all()
            t1 = request.POST.get('t1')
            t2 = request.POST.get('t2')
            t_ref = request.POST.get('t_ref')
            t_relation_exp = request.POST.get('t_relation_exp')
            t_relation_r = request.POST.get('t_relation')
            if t1 and t2 and t_relation_exp and t_relation_r:
                if t1 == t2:
                        error = '''<script>alert('You cannot select the same theorem to add a relation！！！');</script>'''
                else:
                    models.Relation.objects.create(t1_id=t1, t2_id=t2, ref=t_ref, l_name_exp=t_relation_exp,
                                                   l_name_r_id=t_relation_r, user=u)
                    error = '''<script>alert('successfully added ！！！');</script>'''
            else:
                error = '''<script>alert('Relationships cannot be null');</script>'''
            return render(request, 'add_r.html', {'u': u, 'obj': obj, 'error': error})
    else:
        obj = User()
        return render(request, 'login.html', {'obj': obj})


def detail(request):
    u = request.session.get('user', None)
    print(u)
    title = request.path
    t = title[7:-1]
    print(t)
    obj = models.Wlibrary.objects.filter(name=t).first()
    comments = models.Comment.objects.filter(wlibrary=obj).all()
    count = models.Comment.objects.filter(wlibrary=obj).count()
    print(obj)
    return render(request, 'detail.html', {'obj': obj, 'u': u, 'comments': comments, 'comment_nums': count})


def users(request):
    u = request.session.get('user', None)
    if request.method == 'GET':
        obj = None
        return render(request, 'view_users.html', {'obj': obj, 'u': u})
    elif request.method == 'POST':
        ret = {'status': True, 'data': None, 'error': None, 'data2': None, 'exp': None, 'type': None, 'relations': True}
        content = request.POST.get('content', None)
        print('----')
        print(content)
        if content:
            aim = models.User.objects.filter(username__icontains=content).first()

            if aim:
                datas = []
                datas2 = []
                exps = []
                types = []
                obj = models.Wlibrary.objects.filter(user_id=aim.id)
                print("****")
                print(obj)
                if obj:
                    for b in obj:
                        objss = models.Relation.objects.filter(Q(t1_id=b.id) | Q(t2_id=b.id))

                        print(objss)
                        objs = objss
                        # print(("length",len(obj)))
                        if objs:
                            for row in objs:
                                if row.t1.name in datas and row.t2.name in datas2 and row.l_name_exp in exps:
                                    pass
                                else:
                                    # print(row.t1.name, row.t2.name)
                                    datas.append(row.t1.name)
                                    datas2.append(row.t2.name)
                                    exps.append(row.l_name_exp)
                                    types.append(row.l_name_r_id)
                    print(exps)
                    print(datas)
                    print(datas2)
                    print(types)
                    ret['exp'] = json.dumps(exps)
                    ret['data'] = json.dumps(datas)
                    ret['data2'] = json.dumps(datas2)
                    ret['type'] = json.dumps(types)
                    # print(datas,datas2,exps,types)
                    if ret['data'] == None:
                        ret['relations'] = False
                        for row in aim:
                            datas.append(row.name)
                        ret['data'] = json.dumps(datas)
                else:
                    ret['status'] = False
                    ret['error'] = 'This user has not published the relevant theorem！！！'
            else:
                obj = None
                ret['status'] = False
                ret['error'] = 'No relevant distributors were found！！！'
        return HttpResponse(json.dumps(ret))
        # return render(request, 'views.html', {'obj': obj})


def draw_image(request):
    u = request.session.get('user', None) or "guest"
    data = request.POST['data']
    data_array = json.loads(data)
    import base64
    r_list = draw_gragh(data_array, u)
    with open(u + '.png', 'rb') as f:  # Open the diagram file in binary mode
        ls_f = base64.b64encode(f.read()) # reads the file content and converts it into base64 encoding
    res_dict = {
        "massage": "success",
        "code": 0,
        "successful": True,
        "data": {
            "image": str(ls_f, encoding='ascii'),
            "relation": r_list
        }
    }
    return JsonResponse(res_dict)

def relation(request):
    id = int(request.GET['id'])
    r = models.Relation.objects.get(id=id)
    res = {
        "t1": r.t1.name,
        "t2": r.t2.name,
        "l_name_r": r.l_name_r.r_name,
        "l_name_exp": r.l_name_exp,
        "ref": r.ref,
        "username": r.user.nickname,
    }
    return render(request, 'relation.html', res)
