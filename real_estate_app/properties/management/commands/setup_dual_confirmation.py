from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Add dual confirmation columns to PropertyBooking table'

    def handle(self, *args, **options):
        self.stdout.write('Adding dual confirmation columns...')
        
        with connection.cursor() as cursor:
            try:
                with transaction.atomic():
                    # Check if columns exist first
                    cursor.execute("PRAGMA table_info(properties_propertybooking)")
                    columns = [column[1] for column in cursor.fetchall()]
                    
                    if 'agent_confirmed_completion' not in columns:
                        cursor.execute("""
                            ALTER TABLE properties_propertybooking 
                            ADD COLUMN agent_confirmed_completion BOOLEAN DEFAULT 0 NOT NULL
                        """)
                        self.stdout.write(self.style.SUCCESS('✅ Added agent_confirmed_completion column'))
                    else:
                        self.stdout.write('⚠️ agent_confirmed_completion column already exists')
                    
                    if 'customer_confirmed_completion' not in columns:
                        cursor.execute("""
                            ALTER TABLE properties_propertybooking 
                            ADD COLUMN customer_confirmed_completion BOOLEAN DEFAULT 0 NOT NULL
                        """)
                        self.stdout.write(self.style.SUCCESS('✅ Added customer_confirmed_completion column'))
                    else:
                        self.stdout.write('⚠️ customer_confirmed_completion column already exists')
                    
                    if 'agent_confirmation_at' not in columns:
                        cursor.execute("""
                            ALTER TABLE properties_propertybooking 
                            ADD COLUMN agent_confirmation_at DATETIME NULL
                        """)
                        self.stdout.write(self.style.SUCCESS('✅ Added agent_confirmation_at column'))
                    else:
                        self.stdout.write('⚠️ agent_confirmation_at column already exists')
                    
                    if 'customer_confirmation_at' not in columns:
                        cursor.execute("""
                            ALTER TABLE properties_propertybooking 
                            ADD COLUMN customer_confirmation_at DATETIME NULL
                        """)
                        self.stdout.write(self.style.SUCCESS('✅ Added customer_confirmation_at column'))
                    else:
                        self.stdout.write('⚠️ customer_confirmation_at column already exists')
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding columns: {e}'))
                return
        
        self.stdout.write(self.style.SUCCESS('🎉 Dual confirmation setup complete!'))
