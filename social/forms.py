from django import forms
from django.contrib.auth.forms import AuthenticationForm

from social.models import User


class LoginForm(AuthenticationForm):  # AuthenticationForm automatically authenticates password, email ,etc
    username = forms.CharField(max_length=250, required=True, widget=forms.TextInput(),
                               label='نام کاربری، ایمیل یا شماره تماس')
    password = forms.CharField(max_length=250, required=True,
                               widget=forms.PasswordInput(), label='رمز عبور')


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, label='رمز عبور')
    password_2 = forms.CharField(max_length=20, widget=forms.PasswordInput, label='تکرار رمز عبور')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password']

    def clean_password_2(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_2']:
            raise forms.ValidationError('پسوردها مطابقت ندارند!')
        return self.cleaned_data['password_2']

    def clean_phone(self):
        if User.objects.filter(phone=self.cleaned_data['phone']).exists():
            raise forms.ValidationError('کاربر با این شماره تماس قبلا ثبت نام کرده است.')
        return self.cleaned_data['phone']

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('کاربر با این ایمیل قبلا ثبت نام کرده است')
        return self.cleaned_data['email']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'email', 'bio', 'date_of_birth', 'photo', 'job']

    def clean_phone(self):
        if User.objects.exclude(id=self.instance.id).filter(phone=self.cleaned_data['phone']).exists():
            raise forms.ValidationError('شماره تماس قبلا ثبت شده است.')
        return self.cleaned_data['phone']

    def clean_email(self):
        if User.objects.exclude(id=self.instance.id).filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('ایمیل قبلا ثبت شده است.')
        return self.cleaned_data['email']

    def clean_username(self):
        if User.objects.exclude(id=self.instance.id).filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('نام کاربری قبلا ثبت شده است.')
        return self.cleaned_data['username']


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )
    message = forms.CharField(widget=forms.Textarea(), required=True, label='پیام')
    name = forms.CharField(max_length=250, widget=forms.TextInput(), required=True, label='نام')
    email = forms.EmailField(widget=forms.TextInput(), label='ایمیل')
    phone = forms.CharField(max_length=11, widget=forms.TextInput(), required=True, label='شماره تماس')
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label='موضوع')

    def clean_phone(self):
        if self.cleaned_data['phone']:
            if not self.cleaned_data['phone'].isnumeric():
                raise forms.ValidationError("شماره تلفن صحیح وارد نشده است.")
            else:
                return self.cleaned_data['phone']
