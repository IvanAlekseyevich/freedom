from django import forms
from .models import Post


#  создадим собственный класс для формы регистрации
#  сделаем его наследником предустановленного класса UserCreationForm
class PostForm(forms.ModelForm):
    class Meta:
        # укажем модель, с которой связана создаваемая форма
        model = Post
        # укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ('text', 'group')
        labels = {'text':'Введите текст', 'group':'Выберите группу'}

    # def clean_subject(self):
    #     data = self.cleaned_data['text']
    #     # Если пользователь не ввел текст считаем это ошибкой
    #     if data == '':
    #         raise forms.ValidationError('Это поле обязательно к заполнению')
    #     # Метод-валидатор обязательно должен вернуть очищенные данные, 
    #     # даже если не изменил их
    #     return data 
