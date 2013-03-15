from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Initializes Tally system'

    def handle(self, *args, **options):        
        # setup the database
        call_command('syncdb', interactive=True)
        
        # setup database for the Testers group
        try:
            testers = Group.objects.get(name='Testers')
        except Group.DoesNotExist:
            testers = Group(name='Testers')
            testers.save()
    
        # setup the database for the Subjects group
        try:
            subjects = Group.objects.get(name='Subjects')
        except Group.DoesNotExist:
            subjects = Group(name='Subjects')
            subjects.save()
        
        self.stdout.write('Tally is successfully initialized')
        
        # run the development server
        call_command('runserver')