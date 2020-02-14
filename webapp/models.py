# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ProductInformation(models.Model):
    type = models.CharField(db_column='Type', max_length=20)  # Field name made lowercase.
    text1 = models.CharField(db_column='Text1', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    text2 = models.CharField(db_column='Text2', max_length=255)  # Field name made lowercase.
    text3 = models.CharField(db_column='Text3', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    text4 = models.CharField(db_column='Text4', max_length=40, blank=True, null=True)  # Field name made lowercase.
    subct = models.CharField(db_column='SUBCT', max_length=10, primary_key=True)  # Field name made lowercase.

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'product_information'
