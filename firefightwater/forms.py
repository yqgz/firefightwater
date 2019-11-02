from django import forms

class loginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=150)
    password = forms.CharField(label='密码', max_length=150)