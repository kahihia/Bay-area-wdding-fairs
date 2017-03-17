from django.core.management.base import NoArgsCommand
from yapjoy_files.views import check_for_invoices, check_for_invoices_automatic
class Command(NoArgsCommand):
    help = 'Sending Invoices'

    def handle_noargs(self, **options):
        check_for_invoices(None)
        check_for_invoices_automatic(None)