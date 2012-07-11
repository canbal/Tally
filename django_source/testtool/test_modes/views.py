from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from testtool.models import *
import json


def validate_method_choice(method):
    if method not in [x[0] for y in range(0,len(METHOD_CHOICES)) for x in METHOD_CHOICES[y][1]]:
        raise Exception('validate_method_choice: invalid choice.') 


def get_score_choices(method):
    validate_method_choice(method)
    if method == 'SSCQE':
        return [(5,'Excellent'), (4,'Good'), (3,'Fair'), (2,'Poor'), (1,'Bad')]
    elif method == 'DSIS':
        return [(5,'Imperceptible'), (4,'Perceptible, but not annoying'), (3,'Slightly annoying'), (2,'Annoying'), (1,'Very annoying')]
    elif method == 'DSCQS':
        return [(5,'Excellent'), (4,'Good'), (3,'Fair'), (2,'Poor'), (1,'Bad')]
        
        
def get_score(request,method):
    validate_method_choice(method)
    if method == 'SSCQE':
        return {'value': request.POST['value']}
    elif method == 'DSIS':
        return {'value': request.POST['value']}
    elif method == 'DSCQS':
        return {'value1': request.POST['value1'], 'value2': request.POST['value2']}

        
def create_score_object(method,selection,tci,subject):
    validate_method_choice(method)
    if method == 'SSCQE':
        score = ScoreSSCQE(test_case_instance=tci, subject=subject, value=selection['value'])
    elif method == 'DSIS':
        score = ScoreDSIS(test_case_instance=tci, subject=subject, value=selection['value'])
    elif method == 'DSCQS':
        score = ScoreDSCQS(test_case_instance=tci, subject=subject, value1=selection['value1'], value2=selection['value2'])
    score.save()
    return score        # don't need to return object, just for debugging right now for continuous mode
        

def already_submitted_score(method,tci,subject):
    validate_method_choice(method)
    try:
        if method == 'SSCQE':
            pass
        elif method == 'DSIS':
            sc = subject.scoredsis_set.get(test_case_instance=tci)
        elif method == 'DSCQS':
            sc = subject.scoredscqs_set.get(test_case_instance=tci)
    except ObjectDoesNotExist:
        return False
    else:
        return True

        
def get_template(method):
    validate_method_choice(method)
    if method == 'SSCQE':
        return 'testtool/test_modes/vote_SSCQE.html'
    elif method == 'DSIS':
        return 'testtool/test_modes/vote_DSIS.html'
    elif method == 'DSCQS':
        return 'testtool/test_modes/vote_DSCQS.html'
        
        
def tally_continuous(request,ti,subject):
    try:
        tci = ti.testcaseinstance_set.get(play_order=ti.counter)
    except TestCaseInstance.DoesNotExist:
        return render_to_response('testtool/main/status.html', {'test_instance': ti})
    header = 'Test %d/%d' % (ti.counter, ti.testcaseinstance_set.count())
    
    if request.method == 'POST':
        messages = {'0': 'Error: Could not read score',
                    '1': 'Redirecting to status page...',
                    '2': 'Score recorded: pk = ',
                    '3': 'Redirecting to tally page...'}
        try:
            selection = get_score(request, ti.test.method)
            current_count = int(request.POST['current_count'])
        except KeyError:
            status = 0
        if current_count == ti.counter:
            if tci.is_media_done:
                status = 1
            else:
                status = 2
                score = create_score_object(ti.test.method,selection,tci,subject)
                return HttpResponse(json.dumps({'status':status, 'message':messages[str(status)]+str(score.pk), 'header':header}))
        else:
            status = 3
        return HttpResponse(json.dumps({'status':status, 'message':messages[str(status)], 'header':header}))
    else:
        return render_to_response(get_template(ti.test.method),
                                  {'test_instance': ti, 'header': header, 'choices': get_score_choices(ti.test.method)},
                                  context_instance=RequestContext(request))


def tally_discrete(request,ti,subject):
    try:
        tci = ti.testcaseinstance_set.get(play_order=ti.counter)
    except TestCaseInstance.DoesNotExist:
        return render_to_response('testtool/main/status.html', {'test_instance': ti})
    header = 'Test %d/%d' % (ti.counter, ti.testcaseinstance_set.count())
    
    # make sure this subject has not submitted a score for this test case already
    if already_submitted_score(ti.test.method,tci,subject):
        return render_to_response('testtool/main/status.html',
                                 {'test_instance': ti, 'error_message': 'You already selected a choice for this test!'})
    else:
        if request.method == 'POST':
            # ensure that one of the choices was selected before submitting the form
            try:
                selection = get_score(request, ti.test.method)
                current_count = int(request.POST['current_count'])
            except KeyError:
                return render_to_response(get_template(ti.test.method),
                                          {'test_instance': ti, 'header': header, 'choices': get_score_choices(ti.test.method),
                                           'error_message': 'Please select a choice.'},
                                          context_instance=RequestContext(request))
            if current_count == ti.counter:
                create_score_object(ti.test.method,selection,tci,subject)
                return render_to_response('testtool/main/status.html', {'test_instance': ti})
            else:
                return render_to_response(get_template(ti.test.method), 
                                          {'test_instance': ti, 'header': header, 'choices': get_score_choices(ti.test.method)},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response(get_template(ti.test.method),
                                      {'test_instance': ti, 'header': header, 'choices': get_score_choices(ti.test.method)},
                                      context_instance=RequestContext(request))


def status_continuous(request, ti, max_counter):
    messages = {'0': 'Waiting for other participants. Test will begin shortly...',
                '2': 'Choices of all participants are recorded. Test will proceed shortly...',
                '3': 'Thank you for your participation!',
                '4': 'Get ready to vote.',
                '5': 'Server error'}
    if ti:
        if ti.counter == 0:
            status = 0 # 0: means test hasn't started yet
            header = 'Welcome'
        elif ti.counter > 0 and ti.counter <= max_counter:
            header = 'Test %d/%d' % (ti.counter, max_counter)
            try:
                tci = ti.testcaseinstance_set.get(play_order=ti.counter)
            except TestCaseInstance.DoesNotExist:
                status = 5
            else:
                if tci.is_media_done:
                    #tci.is_done = True
                    #tci.save()
                    status = 2      # 2: means all subjects have voted for current test case
                else:
                    status = 4
        else:
            status = 3 # 3: means test has finished
            header = 'Test Complete'
    else:
        status = 5
    return HttpResponse(json.dumps({'status':status, 'message':messages[str(status)], 'header':header}))


def status_discrete(request, ti, max_counter):
    messages = {'0': 'Waiting for other participants. Test will begin shortly...',
                '1': 'Choice is submitted. Waiting for other participants or video to finish...',
                '2': 'Choices of all participants are recorded. Test will proceed shortly...',
                '3': 'Thank you for your participation!',
                '4': 'Get ready to vote.',
                '5': 'Server error'}
    if ti:
        if ti.counter == 0:
            status = 0 # 0: means test hasn't started yet
            header = 'Welcome'
        elif ti.counter > 0 and ti.counter <= max_counter:
            header = 'Test %d/%d' % (ti.counter, max_counter)
            try:
                tci = ti.testcaseinstance_set.get(play_order=ti.counter)
            except TestCaseInstance.DoesNotExist:
                status = 5
            else:
                # update status if current subject has not voted yet
                subject = request.user.get_profile()
                if already_submitted_score(ti.test.method,tci,subject):
                    if tci.is_done:
                        status = 2 # 2: means all subjects have voted for current test case
                    else:
                        # update status if there exist any subjects who has not voted yet
                        all_submitted = True
                        for subject in ti.subjects.all():
                            all_submitted = all_submitted and already_submitted_score(ti.test.method,tci,subject)
                            if not all_submitted:
                                status = 1
                                break
                        if all_submitted:
                            status = 2 # 2: means all subjects have voted for current test case
                            tci.is_done = True
                            tci.save()
                else:
                    status = 4
        else:
            status = 3 # 3: means test has finished
            header = 'Test Complete'
    else:
        status = 5
    return HttpResponse(json.dumps({'status':status, 'message':messages[str(status)], 'header':header}))