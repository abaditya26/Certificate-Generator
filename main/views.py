import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template, render_to_string
from django.utils.datastructures import MultiValueDictKeyError
from xhtml2pdf import pisa

from main.models import UserModel, CertificateRequestModel, AdminModel


def sign_out(request):
    logout(request)
    return redirect('/')


def validate_admin_sign_in(request):
    if request.user.is_staff:
        return True
    else:
        return False


def validate_sign_in(request):
    if not request.user.is_authenticated:
        return False
    else:
        if not request.user.has_usable_password():
            logout(request)
            return False
        else:
            return True


# Create your views here.
def homepage(request):
    if validate_sign_in(request):
        return redirect("/dash")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('./dash')
        else:
            print("User Invalid")
            messages.info(request, "User Credentials Not Match")
    return render(request, 'homepage.html')


def dash(request):
    if not validate_sign_in(request):
        return redirect("/")
    if validate_admin_sign_in(request):
        return redirect("/admin")
    user = UserModel.objects.filter(uid=request.user.username).first()
    certificate_list = CertificateRequestModel.objects.filter(student_id=request.user.username)
    if len(certificate_list) == 0:
        no_certificates = True
    else:
        no_certificates = False
    return render(request, 'dashboard.html', {'user': user, 'certificates': certificate_list,
                                              'no_certificates': no_certificates})


def certificates(request):
    if request.method == "POST":
        print(request.POST["uid"])
        print(request.POST["certificate"])
        cer = CertificateRequestModel.objects.create(student_id=request.POST["uid"],
                                                     name=request.POST["certificate"],
                                                     request_date=datetime.date.today(), )
        cer.save()
        return redirect("/certificates")
    if not validate_sign_in(request):
        return redirect("/")
    if validate_admin_sign_in(request):
        return redirect("/admin")
    if request.method == "POST":
        print(request.POST["certificate"])
        # return
    user = UserModel.objects.filter(uid=request.user.username).get()
    certificate_list = CertificateRequestModel.objects.filter(student_id=request.user.username)
    if len(certificate_list) == 0:
        no_certificates = True
    else:
        no_certificates = False
    print("")
    return render(request, 'certificates.html', {'user': user, 'certificates': certificate_list,
                                                 'no_certificates': no_certificates})


def admin(request):
    try:
        user = AdminModel.objects.filter(uid=request.user.username).get()
        certificate_list = CertificateRequestModel.objects.filter(approved=False).filter(status="Pending").order_by(
            'request_date')
        if len(certificate_list) == 0:
            no_certificates = True
        else:
            no_certificates = False
        return render(request, 'admin.html',
                      {'user': user, 'certificates': certificate_list, 'no_certificates': no_certificates})
    except AdminModel.DoesNotExist:
        return redirect('/')


def admin_certificates_page(request):
    certificate_list = CertificateRequestModel.objects.order_by('request_date').order_by('approved').all()
    if len(certificate_list) == 0:
        no_certificates = True
    else:
        no_certificates = False
    return render(request, 'admin_view_certificates.html', {'certificates': certificate_list,
                                                            'no_certificates': no_certificates})


def certificate_request_details(request):
    if request.method == "POST":
        certificate = CertificateRequestModel.objects.filter(id=request.POST["id"]).get()
        certificate.comment = request.POST["comment"]
        certificate.last_update_date = datetime.date.today()
        try:
            if request.POST["accept"]:
                certificate.approved = True
                certificate.status = "approved"
                certificate.url="./view_certificate?c_id="+request.POST["id"]
        except MultiValueDictKeyError:
            certificate.approved = False
            certificate.status = "rejected"
        certificate.save()
    try:
        certificate = CertificateRequestModel.objects.filter(id=request.GET["c_id"]).get()
        user = UserModel.objects.filter(uid=certificate.student_id).get()
        return render(request, 'cer_details.html', {'user': user, 'certificate': certificate})
    except UserModel.DoesNotExist:
        print("Error")
    except CertificateRequestModel.DoesNotExist:
        print("Np Certificate Found")
    return redirect('/')


def html_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def view_certificate(request):
    if not validate_sign_in(request):
        return redirect("/")
    if validate_admin_sign_in(request):
        return redirect("/admin")
    certificate = CertificateRequestModel.objects.filter(id=request.GET["c_id"]).get()
    user = UserModel.objects.filter(uid=certificate.student_id).get()
    # validate the certificate is of the current user
    if not certificate.approved:
        return redirect('/dash')
    if not certificate.student_id == request.user.username:
        return redirect("/dash")
    if certificate.name == "bonafide":
        open('templates/temp.html', "w").write(render_to_string('certificates/bonafide.html',
                                                                {'user': user, 'certificate': certificate}))
    else:
        open('templates/temp.html', "w").write("<h1>Certificate Template Unavailable. Please Contact Coordinator.</h1>")
    pdf = html_to_pdf('temp.html')
    return HttpResponse(pdf, content_type='application/pdf')


from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get


def user_list(request):
    if request.method == "POST":
        print(request.FILES["user-file"])
        try:
            excel_file = request.FILES["user-file"]
        except MultiValueDictKeyError:
            print("ERROR")
            return None
        if str(excel_file).split('.')[-1] == "xls":
            data = xls_get(excel_file)
        elif str(excel_file).split(".")[-1] == "xlsx":
            data = xlsx_get(excel_file)
        else:
            print("No File found")
            return None
        users = data["users"]
        for user in users:
            if user[0] == "id":
                # check if format is maintained
                if format_maintained(user):
                    continue
                else:
                    print("format not maintained")
                    return None
            user_data = map_to_user_model(user)
            print(user_data.uid)
            # check if the user exists

            # if exists then compare values and update if required
            # else if user not exists then do insertion of data
            add_new_user(user_data, str(user[2]))
    return render(request, 'users.html')


def add_new_user(user, password):
    user = User.objects.create_user(username=user.uid,
                                    email=user.email,
                                    password=password)
    user.save()


def map_to_user_model(user):
    user_data = UserModel.objects.create(
        uid=user[1],
        name=user[3] + " " + user[4],
        email=user[5],
        gender=user[6],
        category=user[7],
        caste=user[8],
        sub_caste=user[9],
        nationality=user[10],
        regNo=user[11],
        mobile=user[12],
        div=user[13],
        profile=user[14],
        year=user[15],
        degree=user[16],
        course=user[17],
        duration=user[18]
    )
    return user_data


def format_maintained(user):
    if user[0] == "id" and user[1] == "uid" and user[2] == "password" and user[3] == "f_name" and \
            user[4] == "l_name" and user[5] == "email" and user[6] == "gender" and user[7] == "category" and \
            user[8] == "caste" and user[9] == "sub_caste" and user[10] == "nationality" and user[11] == "regNo" and \
            user[12] == "mobile" and user[13] == "div" and user[14] == "profile" and \
            user[15] == "year" and user[16] == "degree" and user[17] == "course" and user[18] == "duration":
        return True
    return False
