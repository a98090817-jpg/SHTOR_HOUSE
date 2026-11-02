from contextlib import closing
from datetime import timezone as datetime_timezone
from pathlib import Path
import shutil
import sqlite3
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create a ZIP backup of the SQLite database and uploaded media.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=Path,
            default=settings.BASE_DIR / 'backups',
            help='Directory where the backup archive will be written.',
        )

    def handle(self, *args, **options):
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('backup_site currently supports the configured SQLite database only.')

        database_path = Path(settings.DATABASES['default']['NAME'])
        if not database_path.is_file():
            raise CommandError(f'SQLite database does not exist: {database_path}')

        output_dir = options['output_dir'].expanduser().resolve()
        media_root = Path(settings.MEDIA_ROOT).resolve()
        if output_dir == media_root or media_root in output_dir.parents:
            raise CommandError('Backup output directory must not be inside MEDIA_ROOT.')

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = timezone.now().astimezone(datetime_timezone.utc).strftime('%Y%m%d-%H%M%S')
        archive_path = output_dir / f'shtor-house-backup-{timestamp}.zip'

        try:
            with tempfile.TemporaryDirectory(prefix='.site-backup-', dir=output_dir) as temp_dir:
                temporary_dir = Path(temp_dir)
                database_snapshot = temporary_dir / 'db.sqlite3'
                temporary_archive = temporary_dir / archive_path.name

                with closing(sqlite3.connect(database_path)) as source, closing(
                    sqlite3.connect(database_snapshot)
                ) as snapshot:
                    source.backup(snapshot)

                with ZipFile(temporary_archive, 'w', compression=ZIP_DEFLATED) as archive:
                    archive.write(database_snapshot, arcname='db.sqlite3')
                    if media_root.is_dir():
                        for media_file in media_root.rglob('*'):
                            if media_file.is_file() and not media_file.is_symlink():
                                archive.write(
                                    media_file,
                                    arcname=Path('media') / media_file.relative_to(media_root),
                                )

                shutil.move(str(temporary_archive), archive_path)
        except (OSError, sqlite3.Error) as error:
            raise CommandError(f'Could not create site backup: {error}') from error

        self.stdout.write(self.style.SUCCESS(f'Site backup created: {archive_path}'))
