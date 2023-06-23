from django.db import models

class Employee(models.Model):
    # here
    emp_id = models.AutoField(primary_key=True)
    emp_name = models.CharField(max_length=20)
    emp_birth = models.DateField()
    emp_gender = models.CharField(max_length=1)
    emp_address = models.CharField(max_length=45)
    emp_phone = models.CharField(max_length=45)
    emp_account = models.CharField(max_length=45)
    emp_email = models.EmailField()  # email
    emp_plus = models.IntegerField(default=0)

    def __str__(self):
        return self.emp_name


class Schedulefix(models.Model):
    # here
    sch_id = models.AutoField(primary_key=True)
    sch_start = models.DateTimeField()
    sch_finish = models.DateTimeField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column="emp_id")

class Schedule_exchange(models.Model):
    # write here
    employee1 = models.ForeignKey(Employee, related_name="exchange_employee1", on_delete=models.CASCADE, db_column="emp_id1")
    employee2 = models.ForeignKey(Employee, related_name="exchange_employee2", on_delete=models.CASCADE, db_column="emp_id2")
    start1 = models.DateTimeField(null=True)
    start2 = models.DateTimeField()
    end1 = models.DateTimeField(null=True)
    end2 = models.DateTimeField()
    approval = models.BooleanField(default=False)



class Wage_hourly(models.Model):
    # write here
    wag_id = models.AutoField(primary_key=True)
    wag_info = models.CharField(max_length=10)
    wag_price = models.IntegerField(default=0)


# absenteeism 모델 변경 : finish,wageinfo none값 가능
class Absenteeism(models.Model):
    # wrtie here
    abs_id = models.AutoField(primary_key=True)
    abs_start = models.DateTimeField()
    abs_finish = models.DateTimeField(blank=True, null=True)
    abs_totalmin = models.IntegerField(default=0)
    abs_totalwage = models.IntegerField(default=0)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column="emp_id")
    wageinfo = models.ForeignKey(Wage_hourly, on_delete=models.CASCADE, db_column="wag_id", blank=True, null=True)

    def calculate_totalhour(self):
        if self.abs_finish:
            time_difference = self.abs_finish - self.abs_start
            self.abs_totalmin = int(time_difference.total_seconds() // 60)

    def calculate_totalwage(self):
        if self.abs_finish and self.wageinfo:
            wage_price = self.wageinfo.wag_price + self.employee.emp_plus
            self.abs_totalwage = int(self.abs_totalmin * (wage_price / 60))

    def save(self, *args, **kwargs):
        self.calculate_totalhour()
        self.calculate_totalwage()
        super().save(*args, **kwargs)


class Notice(models.Model):
    # write here
    not_id = models.AutoField(primary_key=True)
    not_writer = models.CharField(max_length=128, verbose_name='작성자')
    not_title = models.CharField(max_length=128, verbose_name='제목')
    not_content = models.TextField(verbose_name='내용')
    not_date = models.DateTimeField(auto_now_add=True,verbose_name='등록시간')

    def __str__(self):
        return self.not_title
