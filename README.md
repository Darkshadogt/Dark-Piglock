<p align="center">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/Darkshadogt/Dark-Piglock/assets/122583206/dafa2884-6087-427a-9305-1c408b214789">
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Darkshadogt/Dark-Piglock/assets/122583206/0b7daee8-6990-49f1-910d-28237145f817">
    <img src="https://github.com/Darkshadogt/Dark-Piglock/assets/122583206/dafa2884-6087-427a-9305-1c408b214789">
  </picture>
</p>
<p align="center">Where Pigs Keep Your Secrets Safe</p>


---
<br>
<br>

# Dark Piglock

Built on Django, this password manager provides users with a seamless platform to securely store passwords, notes, and credit card information, while also facilitating the generation of robust passwords. Additionally, it incorporates advanced features such as two-factor authentication and password reset functionalities to bolster the security of user data. All essential data undergoes encryption via the cryptography module.

<br>

>[!NOTE]
>Dark Piglock may not offer the same level of security as other password managers. Please use with caution.


<br>
<br>

## Running this Project


To set up this project, you'll need Python and virtual environment installed.


```  pip install virtualenv ```

<br>
Create a clone of this project and execute the following command in the project's root directory.


``` git clone https://github.com/Darkshadogt/Dark-Piglock.git ```


``` virtualenv env ```

<br>
Active the virtual environment using the following:


``` source venv/bin/activate ```

<br>
After activation, proceed to install the project dependencies using the following command:


``` pip install -r requirements.txt ```

<br>
Now you can run the project using the following command:


``` python manage.py runserver ```

<br>


>[!IMPORTANT]
>Please note that you'll need to create a .env file and insert a new secret key and an encryption key. You can generate a secret key and an encryption key using the following command:


>```
>from django.core.management.utils import get_random_secret_key
>from cryptography.fernet import Fernet
>
>secret_key = get_random_secret_key()
>print(secret_key)
>
>encryption_key = Fernet.generate_key()
>print(encryption_key)
>```

<br>


## Features

- Storing Passwords
- Storing Notes
- Storing Cards
- Two Factor Authentication
- Password Reset

<br>


## Attributions


- Credit Card Background Image by [Arrandera on Freepik](https://www.freepik.com/free-vector/background-luxury-minimalist-gradient-style-design_32582886.htm#page=2&query=dark%20vector%20background&position=30&from_view=search&track=ais&uuid=0b077dd1-421b-47da-a2d2-b748ddbd193a)
- Sign Up Page, Log In Page, Verification Page, Forgot Password Page Background Image by [Freepik](https://www.freepik.com/free-vector/gradient-black-background-with-wavy-lines_19852122.htm#query=dark%20theme%20vector%20background&position=8&from_view=search&track=ais&uuid=5fa2d0fc-99ae-437f-a630-cc21610266c7)
- Credit Card Chip Icon by [Freepik on Flaticon](https://www.flaticon.com/free-icon/chip_9405771?term=credit+card+chip&page=1&position=20&origin=search&related_id=9405771)
- Password Page Icon by [Freepik](https://www.freepik.com/icon/animal-rights_2865584#fromView=search&term=pig+lock&track=ais&page=1&position=31&uuid=3f7dfbf6-5dbb-4b17-812a-f2923c1652ca)
- Favicon by [Vitaly Gorbachev on Icons8](https://icons8.com/icon/qudcNstH1hBC/pig)
- Note Page Icon by [Flowicon on Freepik](https://www.freepik.com/icon/book_6153987#fromView=search&term=pig+with+notebook&track=ais&page=1&position=17&uuid=06c214f7-3f84-4666-9a1f-06e42c4b8deb)
- Home Page Background Image by [Freepik](https://www.freepik.com/free-vector/gradient-black-background-with-wavy-lines_19852128.htm#query=dark%20theme%20vector&position=12&from_view=search&track=ais&uuid=5c4ba701-a1f6-4f83-bbda-6470cbea0ae8)
- Home Page Illustration Image by [Storyset](https://storyset.com/illustration/secure-login/rafiki)
- History Page Icon by [Freepik](https://www.freepik.com/icon/no-pork_9958719)
- Every Other Icons by [Boxicons](https://boxicons.com/)

>[!NOTE]
>Attributions can also be found within the credits section of the dropdown menu upon logging in.
