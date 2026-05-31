import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Populates the database with collections and products'

    def handle(self, *args, **options):
        print('Populating the database...')
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'seed.sql')
        sql = Path(file_path).read_text()

        with connection.cursor() as cursor:
            # 1. Temporarily disable foreign key checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            # 2. Wipe the tables completely clean
            cursor.execute("TRUNCATE TABLE store_product;")
            cursor.execute("TRUNCATE TABLE store_collection;")
            
            # 3. Turn foreign key checks back on
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            # 4. Insert the data
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database!'))