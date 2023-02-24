from django.db import models

#database column table
class DataSeller(models.Model):
    class Meta:
        db_table = 'rule'

    key = models.CharField(max_length=20, primary_key=True)

    name = models.CharField(max_length=1000, null=True)
    avatar = models.CharField(max_length=500, null=True)
    # file = models.FileField() 
    # file_br_hk = models.CharField(max_length=500, null=True)
    # company_name_abbreviation = models.CharField(max_length=200, db_index=True, null=True)
    # company_name_chinese = models.CharField(max_length=500, null=True)

    # description = models.CharField(max_length=1000, null=True)
    # address = models.CharField(max_length=1000, null=True)

    # in_degree = models.IntegerField(db_index=True, null=True)
    # out_degree = models.IntegerField(db_index=True, null=True)

    def setSeller(self, name, name_hk, company_name_abbreviation, company_name_chinese,
                    description, address,
                    in_degree, out_degree):
        self.name = name

        # self.file_br_hk = file_br_hk
        # self.company_name_chinese = company_name_chinese

        # self.description = description
        # self.address = address

        # self.in_degree = in_degree
        # self.out_degree = out_degree
    