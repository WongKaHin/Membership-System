# -- coding: utf-8 --**
from email import message
from email.policy import HTTP
from gc import get_referents
from hashlib import new
from http import server
from importlib.metadata import requires
from tabnanny import check
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import LOGIN, App, Exchange, History, Member, Question,Behavior,App
from django.contrib import messages
import datetime,time,requests
from django.views.decorators.csrf import csrf_exempt 
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json




serverngrok= 'https://5858-123-241-222-92.jp.ngrok.io' 
SACCngrok ='https://10eb-1-34-54-152.jp.ngrok.io'
t_ngrok = 'https://e1fa-180-217-33-217.jp.ngrok.io'


#拿個資
def access(request, ruserid, raccess_code):
    results=LOGIN.objects.filter(RuserID = ruserid, Raccess_code = raccess_code)
    ac_code=''
    print(results)
    for result in results:
        ac_code = result.Raccess_code
        print("ac_code : ",ac_code)
    urls = SACCngrok+'/RESTapiApp/Access/?Raccess_code='+ac_code
    header = {'Authorization' : 'Token fc350dd19927a48ed595b15586c7ea616c88a280','ngrok-skip-browser-warning' : '7414'}
    req2 = requests.get(urls,headers = header)


    print("status : ",req2.status_code)
    if (req2.status_code!=200):
        print("===================================")
        messages.error(request,'存取權過期, 請再次登入')
        logout(request)
    else:
        pic =req2.json()['sPictureUrl']
        if pic==None:
            pic="None"
        name = req2.json()['sNickName']
        phone = req2.json()['sPhone']
        return pic,name,phone


# Create your views here.
def index(request):
    return render(request,'index.html')

def member(request):
    if login_check(request) == True:
        current_user = request.session['碳制郎']
        print("current user : ",current_user)
        account = Member.objects.get(memid = current_user)
        exchs = Exchange.objects.all().filter(memid = account.memid)
        orders = History.objects.all().filter(memid = account.memid)
        return render(request,'member.html',locals())
    else:
        return redirect(LineLogin)

@csrf_exempt
def point(request):
    if login_check(request) == True:
        account = Member.objects.get(memid = request.session['碳制郎'])
        behs = Behavior.objects.all()
        exchs = Exchange.objects.all().filter(memid = account.memid)
        point = request.POST.get('itemid',False)
        time = request.POST.get('itemtime',False)
        name = request.POST.get('itemname',False)
        print("point : ",point,"\ntime : ",time,"\nname : ",name)
        if point != False and time != False and name != False:
            if int(account.point)>int(point):
                exchange = Exchange(memid = account.memid, elist = name+"/"+time+"min", npoint = point)
                exchange.save()
                l_point = str(int(account.point)-int(point))
                print("剩下點數 : ",l_point)
                print("type : ",type(l_point))
                account.point = l_point
                account.save()
                messages.success(request,"成功兌換")
                timer(time,request)
                return render(request,'point.html',locals())
            else:
                messages.success(request,"點數不足")
                print("點數不足")
                return render(request,'point.html',locals())
        else:
            return render(request,'point.html',locals())
    else:
        return redirect(LineLogin)

@csrf_exempt
def contact(request):
    if login_check(request) == True:
        if request.method == "POST":
            account = Member.objects.get(memid = request.session['碳制郎'])
            disc = request.POST['message']
            qa = Question(memid = account.memid, rdate = datetime.date.today(),disc = disc)
            qa.save()
            messages.success(request, '成功發送，感謝你提供的意見!')
            return render(request,"contact.html",locals())
        else:
            return render(request,"contact.html")
    else:
        return redirect(LineLogin)


def logout(request):
    try:
        del request.session['碳制郎']
        messages.success(request, '成功登出')
    except:
        return redirect('/')
    return redirect('/')

def range(request):
    if login_check(request) == True:
        current_user = request.session['碳制郎']
        account = Member.objects.get(memid = current_user)
        return render(request,'range.html',locals())
    else:
        return redirect(LineLogin)

def timer(need_time,request):
    n_time = int(need_time)
    n_time *= 60
    while n_time:
        m, s = divmod(n_time, 60)
        min_sec_format = '{:02d}:{:02d}'.format(m, s)
        print(min_sec_format, end='\n')
        time.sleep(1)
        n_time-=1
    messages.success(request, '時間到')

def LineLogin(request):
    new_LineLogin = LOGIN.objects.create()
    FKcheck = new_LineLogin.FKcheck 
    backurl = serverngrok+"/lineback?FKcheck="+FKcheck

    rurl= SACCngrok+"/RESTapiApp/Line_1"
    param = {'Rbackurl':backurl}
    header = {'Authorization' : 'Token fc350dd19927a48ed595b15586c7ea616c88a280', 'ngrok-skip-browser-warning': '7414'}
    resb = requests.get(rurl,param,headers = header)
    print("resb",resb)
    rstate = resb.json()['Rstate']
    LOGIN.objects.filter(FKcheck = FKcheck).update(Rstate = rstate)
    url="https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=1657781063&"+\
        "redirect_uri="+SACCngrok+"/LineLoginApp/callback&state="+rstate+\
        "&scope=profile%20openid%20email&promot=consent&ui_locales=zh-TW"
    print("url",url)
    return HttpResponseRedirect(url)

def lineback(request):
    FKcheck = request.GET.get('FKcheck')
    get_Rstate = LOGIN.objects.get(FKcheck = FKcheck)
    rstate = get_Rstate.Rstate

    rurl = SACCngrok+"/RESTapiApp/Line_2"
    print("rurl", rurl)
    param={'Rstate':rstate}
    header={'Authorization': 'Token fc350dd19927a48ed595b15586c7ea616c88a280','ngrok-skip-browser-warning': '7414'}
    resb = requests.get(rurl,param,headers = header)
    print("resb : ",resb)
    ruserid = resb.json()['RuserID']
    raccess_code = resb.json()['Raccess_code']
    LOGIN.objects.filter(FKcheck = FKcheck , Rstate = rstate).update(Raccess_code=raccess_code, RuserID = ruserid)
    print("Access code : ",raccess_code)
    print("access : ",access(request,ruserid,raccess_code)[1])
    account = Member.objects.filter(memid = ruserid)
    if account:
        return Login_and_AddSession(request, ruserid, raccess_code)
    else:
        
        user = Member(memid = ruserid, pic = access(request,ruserid,raccess_code)[0],name = access(request,ruserid,raccess_code)[1],phone = access(request,ruserid,raccess_code)[2])
        user.save()
    return Login_and_AddSession(request, ruserid, raccess_code)

def Login_and_AddSession(request, ruserid, raccess_code):
    if '碳制郎' in request.session:
        try:
            del request.session['碳制郎']
            del request.session['Raccess_code']
        except:
            pass
    request.session['碳制郎'] = ruserid
    request.session['Raccess_code'] = raccess_code
    request.session.modified = True
    request.session.set_expiry(60*30) #存在30分鐘
    print("userid : ",request.session['碳制郎'])
    return HttpResponseRedirect('/')

def login_check(request):
    if not '碳制郎' in request.session:
        check_return = render(request, 'index.html')
    elif '碳制郎' in request.session:
        check_return = True
    else:
        check_return = HttpResponse("驗證錯誤")
    return check_return

def app(request):
    if login_check(request) == True:
        current_user = request.session['碳制郎']
        account = Member.objects.get(memid = current_user)
        apps = App.objects.all()
        return render(request,'app.html',locals())
    else:
        return redirect(LineLogin)
    
def history_1(user):
    print(user)
    account = Member.objects.get(memid = user)
    userid = account.memid
    print("userid:",userid)
    t_url = serverngrok+'/get?RuserID='+userid
    tesb = requests.get(t_url)
    print("tesb",tesb)
    if tesb.status_code!=200:
        print("123")
        return redirect(member)
    else:
        data = tesb.json()
        print(data)
        check_history = History.objects.filter(cdate = data['cdate'])
        print(check_history)
        if check_history:
            return redirect(member)
        else:
            history = History(memid = data['RuserID'],cdate = data['cdate'],gpoint = data['gpoint'],c_amount = data['c_amount'], amount = data['amount'], appname = data['appname'])
            history.save()
            l_point = account.point+data['gpoint']
            account.point = l_point
            account.save()
            return redirect(member)



class send_history(APIView):
    def get(self,request):
        RuserID = request.GET.get('RuserID')
        if not RuserID:
            return Response({"detail": "RuserID不得為空"},status=status.HTTP_400_BAD_REQUEST)
        try:
            queryset = History.objects.get(memid = RuserID)
            try:
                RuserID = queryset.memid
                date = queryset.cdate
                gpoint = queryset.gpoint
                c_amount = queryset.c_amount
                amount = queryset.amount
                print("RuserID:",RuserID,"\nDate:",date,"\nGpoint:",gpoint,"\nc_amount:",c_amount,"\namount:",amount)
                return Response({"RuserID":RuserID, "cdate":date ,"gpoint":gpoint ,"c_amount":c_amount ,"amount":amount ,"appname" : "智慧洗13"})
            except:
                return Response({"detail": "抓取RESTapi出錯，如果一直出現再跟我說"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response({"detail": "建立出錯LineAPI_record，如果一直出現再跟我說"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class history(APIView):
    def get(self,request):
        RuserID = request.GET.get('user')
        cdate = request.GET.get('date')
        gpoint = request.GET.get('gpoint')
        c_amount = request.GET.get('camount')
        amount = request.GET.get('amount')
        appname = request.GET.get('appname')
        try:
            History(memid = RuserID,cdate=cdate,gpoint = gpoint, c_amount = c_amount, amount = amount,appname = appname)
            History.save()
            return Response({"RuserID":RuserID, "cdate":cdate ,"gpoint":gpoint ,"c_amount":c_amount ,"amount":amount ,"appname" : "智慧洗13"})
        except:
            return Response({"detail": "建立出錯LineAPI_record，如果一直出現再跟我說"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)