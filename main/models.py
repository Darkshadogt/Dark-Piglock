from django.db import models
from django.contrib.auth.models import User
from passwordmanager.settings import cipher_suite

#Model for user profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor_auth = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    
    #Renaming the profile object
    def __str__(self):
        return str(self.user) + "'s Profile"

#Model for user passwords
class PasswordModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    website_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    website_url = models.CharField(blank=True, null=True, max_length=255)
    email = models.CharField(blank=True, null=True, max_length=255)
    short_description = models.CharField(max_length=25, blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True, max_length=255)
    is_deleted = models.BooleanField(default=False)

    #Renaming the password object
    def __str__(self):
        return str(self.user) + "'s Password"
    
    #Saving the encrypted information
    def save(self, *args, **kwargs):
        encrypted_username = cipher_suite.encrypt(self.username.encode())
        self.username = encrypted_username.decode()
        encrypted_password = cipher_suite.encrypt(self.password.encode())
        self.password = encrypted_password.decode()
        encrypted_email = cipher_suite.encrypt(self.email.encode())
        self.email = encrypted_email.decode()
        super().save(*args, **kwargs)
    
    #Soft deleting the password
    def soft_delete(self):
        self.is_deleted = True
        super(PasswordModel, self).save(update_fields=['is_deleted'])

    #Recover the deleted password
    def recover(self):
        self.is_deleted = False
        super(PasswordModel, self).save(update_fields=['is_deleted'])

    #Decrypting the username and returning it
    def get_username(self):
        decrypted_username = cipher_suite.decrypt(self.username).decode()
        return decrypted_username

    #Decrypting the password and returning it
    def get_password(self):
        decrypted_password = cipher_suite.decrypt(self.password).decode()
        return decrypted_password
    
    #Decrypting the email and returning it
    def get_email(self):
        decrypted_email = cipher_suite.decrypt(self.email).decode()
        return decrypted_email
    
    #Returns the model name
    def get_model_name(self):
        return "password"
    
    class Meta:
        verbose_name = "Password"
        verbose_name_plural = "Passwords"

#Model for user cards
class CardModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    card_number = models.CharField(max_length=255)
    card_type = models.CharField(max_length=255)
    cardholder_name = models.CharField(max_length=255)
    expiration_date = models.CharField(max_length=255)
    cvv = models.CharField(max_length=255)
    card_brand = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    #Renaming the password object
    def __str__(self):
        return str(self.user) + "'s Card"
    
    #Saving the encrypted information
    def save(self, *args, **kwargs):
        encrypted_card_number = cipher_suite.encrypt(self.card_number.encode())
        self.card_number = encrypted_card_number.decode()
        encrypted_cardholder_name = cipher_suite.encrypt(self.cardholder_name.encode())
        self.cardholder_name = encrypted_cardholder_name.decode()
        encrypted_expiration_date = cipher_suite.encrypt(self.expiration_date.encode())
        self.expiration_date = encrypted_expiration_date.decode()
        encrypted_cvv = cipher_suite.encrypt(self.cvv.encode())
        self.cvv = encrypted_cvv.decode()
        super().save(*args, **kwargs)
    
    #Soft deleting the card
    def soft_delete(self):
        self.is_deleted = True
        super(CardModel, self).save(update_fields=['is_deleted'])

    #Recover the deleted card
    def recover(self):
        self.is_deleted = False
        super(CardModel, self).save(update_fields=['is_deleted'])

    #Decrypting the card number and returning it
    def get_card_number(self):
        decrypted_card_number = cipher_suite.decrypt(self.card_number).decode()
        return decrypted_card_number
    
    #Decrypting the cardholder name and returning it
    def get_cardholder_name(self):
        decrypted_cardholder_name = cipher_suite.decrypt(self.cardholder_name).decode()
        return decrypted_cardholder_name
    
    #Decrypting the expiration date and returning it
    def get_expiration_date(self):
        decrypted_expiration_date = cipher_suite.decrypt(self.expiration_date).decode()
        return decrypted_expiration_date
    
    #Decrypting the cvv and returning it
    def get_cvv(self):
        decrypted_cvv = cipher_suite.decrypt(self.cvv).decode()
        return decrypted_cvv

    #Formats the card number by adding space every four digit
    def formatted_card_number(self):
        formatted_card_number = ""
        for x in self.get_card_number():
            if len(formatted_card_number) == 4 or len(formatted_card_number) == 11 or len(formatted_card_number) == 18:
                formatted_card_number += "   "
            formatted_card_number += x
        return formatted_card_number
    
    #Returns the model name
    def get_model_name(self):
        return "card"
    
    class Meta:
        verbose_name = "Card"
        verbose_name_plural = "Cards"

#Model for user notes
class NoteModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    #Renaming the password object
    def __str__(self):
        return str(self.user) + "'s Note"

    #Saving the encrypted information
    def save(self, *args, **kwargs):
        encrypted_content = cipher_suite.encrypt(self.content.encode())
        self.content = encrypted_content.decode()
        super().save(*args, **kwargs)
    
    #Soft deleting the note
    def soft_delete(self):
        self.is_deleted = True
        super(NoteModel, self).save(update_fields=['is_deleted'])

    #Recover the deleted note
    def recover(self):
        self.is_deleted = False
        super(NoteModel, self).save(update_fields=['is_deleted'])

    #Decrypting the content and returning it
    def get_content(self):
        decrypted_content = cipher_suite.decrypt(self.content).decode()
        return decrypted_content
    
    #Returns the model name
    def get_model_name(self):
        return "note"
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
