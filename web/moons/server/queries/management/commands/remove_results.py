from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from dateutil.relativedelta import relativedelta

from queries.models import ExecuteSQL

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=0)
        parser.add_argument("--hours", type=int, default=0)
        parser.add_argument("--dry-run", action='store_true')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'Dry run: {options["dry_run"]}')
        )
        hours = options['hours']
        days = options['days']
        if not days and not hours:
            self.stdout.write(
               self.style.SUCCESS('No arguments provided')
            )
            return
        
        deleted_files = 0
        max_age = timezone.now() - relativedelta(hours=hours, days=days)
        for query in ExecuteSQL.objects.filter(completed__lte=max_age):
            if query.results_file:
                try:
                    path = Path(query.results_file)
                    self.stdout.write(f'Removing "{path.name}" generated {query.completed}')
                    if not options['dry_run']:
                        path.unlink(missing_ok=True)
                        query.results_file = None
                        query.save()
                    deleted_files += 1
                except:
                    self.stdout.write(
                        self.style.WARNING(f'Error deleting "{path.name}"')
                    )
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted_files} query results files generated before {max_age}')
        )