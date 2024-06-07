from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    help = 'Install specified packages'

    def add_arguments(self, parser):
        parser.add_argument('packages', nargs='+', type=str, help='List of packages to install')

    def handle(self, *args, **kwargs):
        packages = kwargs['packages']
        for package in packages:
            self.stdout.write(f'Installing {package}...')
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            self.stdout.write(self.style.SUCCESS(f'Successfully installed {package}'))
