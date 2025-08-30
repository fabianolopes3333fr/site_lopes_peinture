from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Setup sites for allauth'

    def handle(self, *args, **options):
        # Criar ou atualizar o site padrão
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'Lopes Peinture'
            }
        )
        
        if not created:
            # Se já existe, atualizar os valores
            site.domain = 'localhost:8000'
            site.name = 'Lopes Peinture'
            site.save()
            
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Site created: {site.domain} - {site.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Site updated: {site.domain} - {site.name}')
            )