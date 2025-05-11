import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import IntegrityError
from matches.models import Cvar  # Assuming Cvar model is in matches.models

class Command(BaseCommand):
    help = 'Parses cvars.json from the src/ directory and creates or updates Cvar objects.'

    def handle(self, *args, **options):
        cvars_json_path = os.path.join(settings.BASE_DIR, 'cvars.json')

        try:
            with open(cvars_json_path, 'r') as f:
                cvars_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: {cvars_json_path} not found. Please ensure the file exists at the root of the "src" directory.'))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(f'Error: Could not decode JSON from {cvars_json_path}. Please check its format.'))
            return

        if not isinstance(cvars_data, list):
            self.stdout.write(self.style.ERROR(f'Error: Expected a list of cvar objects in {cvars_json_path}, but got {type(cvars_data).__name__}.'))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for i, cvar_item in enumerate(cvars_data):
            if not isinstance(cvar_item, dict):
                self.stdout.write(self.style.WARNING(f'Skipping item at index {i}: not a dictionary. Data: {cvar_item}'))
                skipped_count += 1
                continue

            cvar_name = cvar_item.get('name')
            cvar_value_type = cvar_item.get('value_type')

            if not cvar_name:
                self.stdout.write(self.style.WARNING(f'Skipping item at index {i} due to missing "name". Data: {cvar_item}'))
                skipped_count += 1
                continue

            if not cvar_value_type:
                self.stdout.write(self.style.WARNING(f'Skipping cvar "{cvar_name}" (item at index {i}) due to missing "value_type". Data: {cvar_item}'))
                skipped_count += 1
                continue

            try:
                cvar, created = Cvar.objects.get_or_create(
                    name=cvar_name,
                    defaults={'value_type': cvar_value_type}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created Cvar: "{cvar_name}" (Type: {cvar_value_type})'))
                    created_count += 1
                else:
                    if cvar.value_type != cvar_value_type:
                        old_value_type = cvar.value_type
                        cvar.value_type = cvar_value_type
                        cvar.save()
                        self.stdout.write(self.style.NOTICE(f'Cvar "{cvar_name}" already existed. Updated value_type from "{old_value_type}" to "{cvar_value_type}".'))
                        updated_count += 1
                    else:
                        self.stdout.write(self.style.HTTP_INFO(f'Cvar "{cvar_name}" already exists with the same value_type. No action taken.'))
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f'Database integrity error for cvar "{cvar_name}": {e}'))
                error_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing cvar "{cvar_name}": {e}'))
                error_count += 1
        
        summary_message = f"Finished processing {cvars_json_path}. "
        summary_parts = []
        if created_count > 0:
            summary_parts.append(f"Created: {created_count}")
        if updated_count > 0:
            summary_parts.append(f"Updated: {updated_count}")
        if skipped_count > 0:
            summary_parts.append(f"Skipped (due to data issues): {skipped_count}")
        if error_count > 0:
            summary_parts.append(f"Errors: {error_count}")
        
        if not summary_parts:
            summary_message += "No cvars processed or no changes made."
        else:
            summary_message += ", ".join(summary_parts) + "."
            
        self.stdout.write(self.style.SUCCESS(summary_message))
