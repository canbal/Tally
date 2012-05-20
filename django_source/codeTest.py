from testtool.models import *
from django.contrib.auth.models import Group
from registration.models import UserProfile


def export1():
    test_instance_ran = TestInstance.objects.exclude(run_time=None)                 # all test instances that have been run
    test_id_ran = test_instance_ran.values_list('test__pk',flat=True).distinct()    # pk's of all tests that have test instances that have been run
    up = UserProfile.objects.get(pk=1)
    # of these, find the ones of which the user is an owner or collaborator
    t_valid = []
    ti_valid = []
    t_valid_id = []
    ti_valid_id = []
    for id in test_id_ran:                              # for each run test, find its run instances
        t_ran = Test.objects.get(pk=id)
        t_ran_ti = test_instance_ran.filter(test=t_ran)
        tmp_list = []
        tmp_list_pk = []
        for ti in t_ran_ti:
            if (up == ti.owner) or (up in ti.collaborator.all()) or (up == ti.test.owner) or (up in ti.test.collaborator.all()):
                tmp_list.append(ti)
                tmp_list_pk.append(ti.pk)
        if len(tmp_list) > 0:
            t_valid.append(t_ran)
            ti_valid.append(tmp_list)
            ti_valid_id.append(tmp_list_pk)
            t_valid_id.append(t_ran.pk)
    