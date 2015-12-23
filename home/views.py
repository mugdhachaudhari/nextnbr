# Create your views here.
from login.forms import *
from home.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from login.models import Blocks
from django.db import connection
from django.contrib.auth.hashers import make_password
import cx_Oracle
from nextnbr.settings import MEDIA_URL
from decimal import Decimal
from profileapp.models import UserProfile
from home.models import Blockmembers

# from django.contrib.gis.geos import polygon



# Create your views here.
@login_required
def homepage(request):
	cursor = connection.cursor()
	m = request.session['userid']
	prfl = request.user.profile
	if not prfl.firstname:
		return HttpResponseRedirect('/accounts/profile/', {'alert' : True})
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	showcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('allthreads', [m,showcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('home.html',{'row':row,'user': request.user})
	#n = notification.objects.filter(user=request.user, viewed=False)
	#return render_to_response(
	#'home.html',
	#{ 'user': request.user,#'notification':n 
	#}
	#)
@login_required	
def msg(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	showcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('allfeeds', [m,x,showcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('msg.html',{'row':row,'user': request.user})


	
@login_required
def home(request):
	u = User.objects.get(username = request.user)
	request.session['userid'] = u.id
	return render_to_response('frame.html',{ 'user': request.user})
	
@login_required
def ho(request):
	prfl = request.user.profile
	return render_to_response('ho.html',{ 'user': request.user, 'MEDIA_URL' : MEDIA_URL, 'prfl' : prfl })

	
def allfeeds(request):
	return render_to_response(
    'allfeeds.html',
    { 'user': request.user }
    )

#def getid(request):
#	cursor=connection.cursor()
#	cursor.execute("select id from auth_user where username=request.user")
#	row=cursor.fetchone()
#	return HttpResponse(row)
	
def friends(request):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	frndscur = cursor.var(cx_Oracle.CURSOR).var
 #     cursor.callproc('showfriends', [21, 'frnds_cursor', err_cd, err_msg])
	result = cursor.callproc('showfriends', [m,frndscur, err_cd, err_msg])
	if result[2] == '0':
		row = result[1].fetchall()
	#	return HttpResponse(row)
		#variables = RequestContext(request, {'id': row})
		#return render_to_response('friends.html',variables,)
		#return render_to_response('friends.html',{'id':row})
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
		#return response
	return render_to_response('friends.html',{'id':row})

	
def neighbours(request):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	neighscur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('showneighbours', [m,neighscur, err_cd, err_msg])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('neighbours.html',{'id':row})
	

def blocks(request):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	neighscur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('showblocks', [m, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[1] == '1':
		return render_to_response('blocks.html',{'row':result[2]})
	if result[1] == '2':
		return render_to_response('blocks.html',{'row':result[2]})
	if result[1] == '3':
		return render_to_response('blocks.html',{'row':result[2]})
	if result[1] == '0':
		lat = request.user.profile.loc.latitude
		lng = request.user.profile.loc.longitude
		listblks = []
		blks = Blocks.objects.all()
		for x in blks:
			ymax = Decimal(x.nec.split(',')[0])
			xmax = Decimal(x.nec.split(',')[1])
			ymin = Decimal(x.swc.split(',')[0])
			xmin = Decimal(x.swc.split(',')[1])
#         rx = range(xmax, xmin)
#         ry = range(ymax, ymin)
			if lng >= xmax and lng <= xmin and lat >= ymax and lat <= ymin :
				listblks.append(x)
# 		return HttpResponse(listblks[0].bid)
#     ne =nec.split(',')[0] request.user.profile.loc.latitude
#     sw = request.user.profile.loc.longitude
#     bbox = ("XMIN = " ,xmin," YMIN = ", ymin, " XMAX  = ", xmax, " YMAX ",  ymax)
#     geom = Polygon.from_bbox(bbox)
#     return HttpResponse(bbox)
		return render_to_response('blocklist.html',{'row':listblks})
		

def friendrequest(request):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	notifycur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('showfrndreq', [m,notifycur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('friendrequest.html',{'row':row})
	
def addnbrlist(request):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	blkmembrs = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('showblkmembers', [m,blkmembrs, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('nbrlist.html',{'row':row})

def addnbr(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	result = cursor.callproc('addnbr', [m,x, err_cd, err_msg])
	if result[2] == '0':
		msg = 'Neighbour added'
#         return HttpResponse(row)
	else:
		msg = 'Error in completing your request'
	return render_to_response('template2.html', {'msg' : msg})
	
def notifications(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	notifycur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('notificationdisplay', [m,notifycur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
		msg=''
	else:
# 		response = HttpResponse()
# 		response.write(result[2])
# 		response.write(" ")
# 		response.write(result[3])
		row = ''
		msg='Error in displaying notifications'
	return render_to_response('notifications.html',{'row':row, 'msg':msg})
	
	
def acceptfrndreq(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	result = cursor.callproc('friendaccept', [x,m,'Y', err_cd, err_msg])
	if result[3] == '0':
		msg = 'Accept request completed'
#         return HttpResponse(row)
	else:
		msg = 'Error in completing your request'
	return render_to_response('template2.html', {'msg' : msg})
	
	
	
def acceptblkreq(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	try:
		cursor = connection.cursor()
		cursor.execute("SELECT bid FROM blockmembers where userid = %s", [m])
		bid = int(cursor.fetchone()[0])
# 		return HttpResponse(bid[0])
# 	return HttpResponse(row)
	except:
		msg = 'Error selecting BlockId'
		html = "<html><body>ERROR %s. <a href='/homepage/'>Home</a></body></html>" % msg
		return HttpResponse(html)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	result = cursor.callproc('blockapproval', [x,bid,m,err_cd,err_msg ])
	if result[3] == '0':
		msg = 'Request completed'
#         return HttpResponse(row)
	else:
		msg = 'Error in completing your request'
	return render_to_response('template2.html', {'msg' : msg})
	
	
def sendblkreq(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	result = cursor.callproc('blockrequest', [m,x, err_cd, err_msg])
	return HttpResponse(result[2])
	if result[2] == '0':
		msg = 'Block request sent'
#         return HttpResponse(row)
	else:
		msg = 'Error in completing your request'
	return render_to_response('template2.html', {'msg' : msg})

	
def unjoinblkreq(request):
	return HttpResponse('Need to complete this functionality')	
	
def declinefrndreq(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	result = cursor.callproc('friendaccept', [x, m, 'D', err_cd, err_msg])
	if result[3] == '0':
		msg = 'Decline request completed'
#         return HttpResponse(row)
	else:
		msg = 'Error in completing your request'
	return render_to_response('template2.html', {'msg' : msg})

	
def messages(request):
	if request.method == 'POST':
		form = MessageForm(request.POST)
		choice = request.POST['choice']
		request.session['choice']=choice
		if choice == 'E' or choice == 'R':
			#if request.method == 'POST':
				#form = NewmessageForm()
				
				#if form.is_valid:
					#choice = request.POST['choice']
					#variables = RequestContext(request, {
	#'form': form,
	#})
					#return render_to_response(
	#'msgsuccess.html',
	#variables,
	#)				
					
			request.session['choice'] = choice 
					
			HttpResponseRedirect("/newmsg/")
			
	else:
		form = NewmessageForm()
				
	variables = RequestContext(request, {
				'form': form,
			})
	return render_to_response(
	'msgsuccess.html',
	variables,
	)
			#return HttpResponseRedirect("/newmsg/")
			
		
	#else:
	#	form = MessageForm()
	#variables = RequestContext(request, {
	#'form': form,
	#})
	#return render_to_response(
	#'msgsuccess.html',
	#variables,
	# )
	
def newmsg(request):
	if request.method == 'POST':
		form = NewmessageForm(request.POST)
		#choice = request.POST['choice']
		#return HttpResponse(choice)
		if form.is_valid:
			form.save()
			
		#request.GET.get('choice')
		return HttpResponseRedirect('/message/')
	else:
		return HttpResponse(request.session['choice'])
		form = NewmessageForm()
		choice = request.session['choice']
		
	variables = RequestContext(request, {
	'form': form,'choice':choice
	})

	return render_to_response(
	'messages.html',
	variables,
	)
	
# def message(request):
	# if request.method == 'POST':
		# form = MessageForm(request.POST)
		# #choice = request.POST['choice']
		# if choice == 'f' or choice == 'n':
			# return HttpResponseRedirect("/newmsg/")
		# else:
			# return HttpResponseRedirect("/newms/")
		
	# else:
		# form = MessageForm()
	# variables = RequestContext(request, {
	# 'form': form,
	# })
	# return render_to_response(
	# 'msgsuccess.html',
	# variables,
	# )
	
def newms(request):
	if request.method == 'POST':
		form = NewmessagesForm(request.POST)
		return HttpResponseRedirect('/messages.html/')
	else:
		form = NewmessagesForm()
	variables = RequestContext(request, {
	'form': form,
	})
 
	return render_to_response(
	'messages.html',
	variables,
	)
	
def frequest(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	cursor.callproc('updatefrnd', [m,x, err_cd, err_msg])
	variables = RequestContext(request, {'x':x})
	return render_to_response('template.html')
	#return HttpResponse(result[2])
	
	
def replymsg(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	frndthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('replymsg', [x,m,frndthreadcur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('.html',{'row':row})
	
	
def reply(request):
	if request.method == 'POST':
		form = NewmessagesForm(request.POST)
		return HttpResponseRedirect('/messages.html/')
	else:
		form = NewmessagesForm()
	variables = RequestContext(request, {
	'form': form,
	})
 
	return render_to_response(
	'messages.html',
	variables,
	)
	
	
#def msgsuccess(request):
#	cursor = connection.cursor()
#	m = request.session['userid']
#	err_cd = cursor.var(cx_Oracle.NUMBER).var
#	err_msg = cursor.var(cx_Oracle.STRING).var
#	showcur = cursor.var(cx_Oracle.CURSOR).var
#	result = cursor.callproc('newmsg', [m,showcur, err_cd, err_msg])
	#return HttpResponse(result[2])
#	if result[2] == '0':
#		row = result[1].fetchall()
#	else:
#		response = HttpResponse()
#		response.write(result[2])
#		response.write(" ")
#		response.write(result[3])
#		row=''
#	return render_to_response('success.html',{'row':row})
	
	
def blockthreads(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	blkthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('blockthreads', [m,blkthreadcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('blockthreads.html',{'row':row})
	
	
def friendthreads(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	frndthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('friendthreads', [m,frndthreadcur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('friendthreads.html',{'row':row})
	
	
def next(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	blkthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('blockfeeds', [m,x,blkthreadcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[3] == '0':
		row = result[2].fetchall()
	else:
		response = HttpResponse()
		response.write(result[3])
		response.write(" ")
		response.write(result[4])
		row=''
	return render_to_response('next.html',{'row':row,'x':x})
	
def togo(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	frndthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('friendfeeds', [m,x,frndthreadcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[3] == '0':
		row = result[2].fetchall()
	else:
		response = HttpResponse()
		response.write(result[3])
		response.write(" ")
		response.write(result[4])
		row=''
	return render_to_response('togo.html',{'row':row,'x':x})
	
	
def neighbourhoodthreads(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	nbthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('neighbourhoodthreads', [m,nbthreadcur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('neighbourhoodthreads.html',{'row':row})
	
	
	
def neighbourthreads(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	nbthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('neighbourthreads', [m,nbthreadcur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('neighbourthreads.html',{'row':row})
	
def allthreads(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	allthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('allthreads', [m,allthreadcur, err_cd, err_msg])
	#return HttpResponse(result[1])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('allthreads.html',{'row':row})
	
	
def to(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	nbthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('neighbourfeeds', [m,x,nbthreadcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[3] == '0':
		row = result[2].fetchall()
	else:
		response = HttpResponse()
		response.write(result[3])
		response.write(" ")
		response.write(result[4])
		row=''
	return render_to_response('to.html',{'row':row,'x':x})
	
	
def go(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	nbthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('neighbourhoodfeeds', [m,x,nbthreadcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[3] == '0':
		row = result[2].fetchall()
	else:
		response = HttpResponse()
		response.write(result[3])
		response.write(" ")
		response.write(result[4])
		row=''
	return render_to_response('go.html',{'row':row,'x':x})
	
	
def oo(request,x):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(x)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	allthreadcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('allfeeds', [m,x,allthreadcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[3] == '0':
		row = result[2].fetchall()
	else:
		response = HttpResponse()
		response.write(result[3])
		response.write(" ")
		response.write(result[4])
		row=''
	return render_to_response('oo.html',{'row':row,'x':x})

	
def show(request):
	cursor = connection.cursor()
	m = request.session['userid']
	#return HttpResponse(m)
	err_cd = cursor.var(cx_Oracle.NUMBER).var
	err_msg = cursor.var(cx_Oracle.STRING).var
	showcur = cursor.var(cx_Oracle.CURSOR).var
	result = cursor.callproc('show', [m,showcur, err_cd, err_msg])
	#return HttpResponse(result[2])
	if result[2] == '0':
		row = result[1].fetchall()
	else:
		response = HttpResponse()
		response.write(result[2])
		response.write(" ")
		response.write(result[3])
		row=''
	return render_to_response('home.html',{'row':row})
	
	
def newmessage(request):
	if request.method == 'POST':
		form = MessageForm(request.POST)
		answer = form.cleaned_data['choices']
		variables = RequestContext(request, {'form': form})
		return render_to_response('next.html',variables)

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            request.session['email'] = form.cleaned_data['email']       
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })
 
    return render_to_response(
    'registration/register.html',
    variables,
    )


def register_success(request):
    return render_to_response(
    'registration/success.html',
    )
 
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

# @login_required
# def home_1(request):
# #     filename = "C:\Users\Vasundhara Patil\Documents\GitHub\next\media\uploaded_files\ab1_1449302455_874656_Frozen_Queen_Elsa_Wallpaper.jpg"
#     u = User.objects.get(username = request.user)
#     request.session['userid'] = u.id
#     prfl = request.user.profile
#     if not prfl.firstname:
#         return HttpResponseRedirect('/accounts/profile/', {'alert' : True})
# #     image_name = "uploaded_files/Frozen_Queen_Elsa_Wallpaper.jpg"
#     return render_to_response('home_1.html',{ 'user': request.user, 'MEDIA_URL' : MEDIA_URL, 'prfl' : prfl })


# def blockrequest(request):
#     lat = request.user.profile.loc.latitude
#     lng = request.user.profile.loc.longitude
#     listblks = []
#     blks = Blocks.objects.all()
#     for x in blks:
#         ymax = Decimal(x.nec.split(',')[0])
#         xmax = Decimal(x.nec.split(',')[1])
#         ymin = Decimal(x.swc.split(',')[0])
#         xmin = Decimal(x.swc.split(',')[1])
# #         rx = range(xmax, xmin)
# #         ry = range(ymax, ymin)
#         if lng >= xmax and lng <= xmin and lat >= ymax and lat <= ymin :
#              listblks.append(x)
# #     ne =nec.split(',')[0] request.user.profile.loc.latitude
# #     sw = request.user.profile.loc.longitude
# #     bbox = ("XMIN = " ,xmin," YMIN = ", ymin, " XMAX  = ", xmax, " YMAX ",  ymax)
# #     geom = Polygon.from_bbox(bbox)
# #     return HttpResponse(bbox)
#     return HttpResponse(listblks)

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cursor = connection.cursor()
            err_cd = cursor.var(cx_Oracle.NUMBER).var
            err_msg = cursor.var(cx_Oracle.STRING).var
            findmsgcur = cursor.var(cx_Oracle.CURSOR).var
#             return HttpResponse(request.POST['search'])
#     cursor.callproc('showfriends', [21, 'frnds_cursor', err_cd, err_msg])
            result = cursor.callproc('findmsg', [request.POST['search'],request.session['userid'], findmsgcur, err_cd, err_msg])
#             result = cursor.callproc('showfriends', [request.session['userid'], findmsgcur, err_cd, err_msg])
#             return HttpResponse(result[2]['msgid'])
            if result[3] == '0':
                row = result[2].fetchall()
#                 return HttpResponse(row[0][0])
                return render_to_response('search_msgs.html', {'msgs' : row})

            else:
                response = HttpResponse()
                response.write(result[3])
                response.write(" ")
                response.write(result[4])
                row = ''
#                 return response
                return render_to_response('search_msgs.html', {'msgs' : row})
    else:
        form = SearchForm(initial = {'search' : ""})
    variables = RequestContext(request, {
    'form': form
    })
  
    return render_to_response(
    'search.html',
    variables,
    )
    
#     
# def viewmsg(request):
#         if request.method == 'POST':
#             return HttpResponse(request.POST)
#         f = 0
#         variables = RequestContext(request, {'form': f})
#   
#     return render_to_response('viewmsg.html',variables,)
        

def checkproccur(request):
    cursor = connection.cursor()
	# l_cursor = cx_Oracle.CURSOR
    err_cd = cursor.var(cx_Oracle.NUMBER).var
    err_msg = cursor.var(cx_Oracle.STRING).var
    frndscur = cursor.var(cx_Oracle.CURSOR).var
#     cursor.callproc('showfriends', [21, 'frnds_cursor', err_cd, err_msg])
    result = cursor.callproc('showfriends', [2,frndscur, err_cd, err_msg])
    if result[2] == '0':
        row = result[1].fetchall()
#         return HttpResponse(row)
    else:
        response = HttpResponse()
        response.write(result[2])
        response.write(" ")
        response.write(result[3])
        row = ''
#         return response
    return render_to_response('checkproccur.html',{'row': row}
    )

	
# def checkproc(request):
	# cursor = connection.cursor()
	# fn = ""
	# row = cursor.callproc('sample2', [21, fn])
	# return HttpResponse(row[1])


# def profile(request):
	# return HttpResponse("Update your profile")
	
# def logout(request):
    # try:
        # del request.session['user_id']
    # except KeyError:
        # pass
    # return HttpResponse("You're logged out.")
