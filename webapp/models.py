# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ProductInscope(models.Model):
    nam_prod = models.CharField(max_length=8000, blank=True, null=True)
    bdt = models.CharField(max_length=8000, blank=True, null=True)
    cas_no = models.CharField(max_length=8000, blank=True, null=True)
    spec_id = models.CharField(max_length=8000, blank=True, null=True)
    material_no = models.CharField(max_length=8000, blank=True, null=False, primary_key=True)

    class Meta:
        managed = False
        db_table = '[momentive].[product_inscope]'
    def __str__(self):
        return (self.material_no)
