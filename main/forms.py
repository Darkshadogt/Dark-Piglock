from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import regex
from django.core.validators import MinLengthValidator, RegexValidator, URLValidator
from django.core.exceptions import ValidationError

#Sign up form
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter a username'}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter a password', 'id': 'passwordInput'}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Re-enter the password', 'id': 'confirm_passwordInput'}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter an email'}),
    )
    
    #Checks if email is used
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    
#Log in form
class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        required=True,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your username'}),
    )
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your password', 'id': 'passwordInput', 'autocomplete': 'off'}),
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is None:
            raise forms.ValidationError("Invalid credentials. Try again.")

#Form for adding user passwords
class addPasswordForm(forms.Form):
    website_name = forms.CharField(
        label="Website Name",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the website name', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    username = forms.CharField(
        label="Username",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your username', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your password', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px', 'id': 'add_password_input', 'autocomplete': 'off'}),
    )
    website_url = forms.URLField(
        label="Website_url",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the website link', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    email = forms.CharField(
        label="Email",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your email', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    short_description = forms.CharField(
        label="Short Description",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter a short description', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    detailed_description = forms.CharField(
        label="Detailed Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter a detailed description', 'style': 'width: 400px; height: 300px; margin-top: 10px; margin-left: 50px'}),
    )
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        website_name = self.cleaned_data.get('website_name')
        email = self.cleaned_data.get('email')
        short_description = self.cleaned_data.get('short_description')
        
        if not username:
            self.add_error('username','Username is required.')
        if not password:
            self.add_error('password','Password is required.')
        if not website_name:
            self.add_error('website_name','Website name is required.')
        if not email:
            self.add_error('email','Email is required.')
        if short_description and len(short_description) > 25:
            self.add_error('short_description','Short description must be less than 25 characters.')
        return self.cleaned_data

#Form for updating user passwords
class editPasswordForm(forms.Form):
    website_name = forms.CharField(
        label="Website Name",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    username = forms.CharField(
        label="Username",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    website_url = forms.URLField(
        label="Website_url",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    email = forms.CharField(
        label="Email",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    short_description = forms.CharField(
        label="Short Description",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    detailed_description = forms.CharField(
        label="Detailed Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'input is-family-monospace', 'style': 'width: 400px; height: 300px; margin-top: 10px; margin-left: 50px'}),
    )
    def clean(self):
        validate = URLValidator()
        username = self.cleaned_data.get('username')
        website_name = self.cleaned_data.get('website_name')
        email = self.cleaned_data.get('email')
        website_url = self.cleaned_data.get('website_url')
        short_description = self.cleaned_data.get('short_description')
        
        if not username:
            self.add_error('username','Username is required.')
        if not website_name:
            self.add_error('website_name','Website name is required.')
        if not email:
            self.add_error('email','Email is required.')
        if short_description and len(short_description) > 25:
            self.add_error('short_description', 'Short description must be less than 25 characters.')
        if website_url:
            try:
                validate(website_url)
            except ValidationError:
                self.add_error('website_url', 'Invalid URL.')
        return self.cleaned_data

#Form for adding user cards
class addCardForm(forms.Form):
    card_number = forms.CharField(
        label="Card Number",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the card number', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    cardholder_name = forms.CharField(
        label="Card Holder Name",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your name', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    expiration_date = forms.CharField(
        label="Expiration Date",
        min_length=5,
        required=False,
        max_length=5,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the expiration date', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    cvv = forms.CharField(
        label="CVV",
        required=False,
        min_length=3,
        max_length=4,
        widget=forms.PasswordInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the security code', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px', 'id': 'add_password_input'}),
    )
    card_brand = forms.CharField(
        label="Card Brand",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the card brand', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    card_type = forms.CharField(
        label="Card Type",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the type of card', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )

    def clean(self):
        card_number = self.cleaned_data.get('card_number')
        cardholder_name = self.cleaned_data.get('cardholder_name')
        expiration_date = self.cleaned_data.get('expiration_date')
        cvv = self.cleaned_data.get('cvv')
        card_brand = self.cleaned_data.get('card_brand')
        card_type = self.cleaned_data.get('card_type')
        if not card_number or not cardholder_name or not expiration_date or not cvv or not card_brand or not card_type:
            self.add_error(None, "Please fill in all the fields.")
        if len(card_number)!= 16:
            self.add_error('card_number', "Card number must be 16 digits.")
        if regex.match('^(0[1-9]|1[0-2])\/?([0-9]{2})$', expiration_date) is None:
            self.add_error('expiration_date', "Expiration date must be in MM/YY format.")
        if len(cvv) < 3:
            self.add_error('cvv', "CVV must be 3 to 4 digits.")
        if cvv.isnumeric() is False:
            self.add_error('cvv', "CVV must be numeric.")
        if card_number.isnumeric() is False:
            self.add_error('card_number', "Card number must be numeric.")
        return self.cleaned_data

#Form for editing user cards
class editCardForm(forms.Form):
    card_number = forms.CharField(
        label="Card Number",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the card number', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    cardholder_name = forms.CharField(
        label="Card Holder Name",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter your name', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    expiration_date = forms.CharField(
        label="Expiration Date",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the expiration date', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    card_brand = forms.CharField(
        label="Card Brand",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the card brand', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )
    card_type = forms.CharField(
        label="Card Type",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the type of card', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px'}),
    )

    def clean(self):
        card_number = self.cleaned_data.get('card_number')
        cardholder_name = self.cleaned_data.get('cardholder_name')
        expiration_date = self.cleaned_data.get('expiration_date')
        card_brand = self.cleaned_data.get('card_brand')
        card_type = self.cleaned_data.get('card_type')
        if not card_number or not cardholder_name or not expiration_date or not card_brand or not card_type:
            self.add_error(None, "Please fill in all the fields.")
        if len(card_number)!= 16:
            self.add_error('card_number', "Card number must be 16 digits.")
        if regex.match('^(0[1-9]|1[0-2])\/?([0-9]{2})$', expiration_date) is None:
            self.add_error('expiration_date', "Expiration date must be in MM/YY format.")
        if card_number.isnumeric() is False:
            self.add_error('card_number', "Card number must be numeric.")
        return self.cleaned_data

#Form for adding user notes
class addNoteForm(forms.Form):
    title = forms.CharField(
        label="Title",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the notes title', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px;'}),
    )
    content = forms.CharField(
        label="Content",
        required=False,
        widget=forms.Textarea(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the description', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px; height: 400px;'}),
    )

    def clean(self):
        title = self.cleaned_data.get('title')
        content = self.cleaned_data.get('content')
        if not title or not content:
            self.add_error(None, "Please fill in all the fields.")
        return self.cleaned_data

#Form for editing user notes
class editNoteForm(forms.Form):
    title = forms.CharField(
        label="Title",
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-family-monospace', 'placeholder': 'Enter the notes title', 'style': 'width: 400px; margin-top: 10px; margin-left: 50px;'}),
    )
    def clean(self):
        title = self.cleaned_data.get('title')
        if not title:
            self.add_error(None, "Please fill in all the fields.")
        return self.cleaned_data

    


        



