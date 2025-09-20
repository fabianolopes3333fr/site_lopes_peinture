#!/usr/bin/env python
"""
Script pour créer des données d'exemple (produits, projets)
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Configuration Django
sys.path.append("/home/ubuntu/mvp_peinture_django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "peinture_service.settings")

django.setup()
from accounts.models import CustomUser
from projects.models import Project, Product, Devis, DevisLine


def create_sample_products():
    """Créer des produits d'exemple"""
    produits = [
        {
            "code": "PEINTURE-INT-001",
            "name": "Peinture intérieure mate blanche",
            "description": "Peinture acrylique mate pour intérieur, excellent pouvoir couvrant",
            "type_produit": "peinture",
            "price_unit": Decimal("25.90"),
            "unit": "litre",
        },
        {
            "code": "PEINTURE-EXT-001",
            "name": "Peinture extérieure semi-brillante",
            "description": "Peinture acrylique pour façades, résistante aux intempéries",
            "type_produit": "peinture",
            "price_unit": Decimal("32.50"),
            "unit": "litre",
        },
        {
            "code": "SOUS-COUCHE-001",
            "name": "Sous-couche universelle",
            "description": "Primaire d'accrochage pour tous supports",
            "type_produit": "sous_couche",
            "price_unit": Decimal("18.75"),
            "unit": "litre",
        },
        {
            "code": "ROULEAU-001",
            "name": "Rouleau patte de lapin 180mm",
            "description": "Rouleau professionnel pour peinture mate et satinée",
            "type_produit": "materiel",
            "price_unit": Decimal("8.50"),
            "unit": "piece",
        },
        {
            "code": "MAIN-OEUVRE-001",
            "name": "Main d'œuvre peintre",
            "description": "Prestation peinture par un artisan qualifié",
            "type_produit": "main_oeuvre",
            "price_unit": Decimal("35.00"),
            "unit": "heure",
        },
    ]

    for produit_data in produits:
        if not Product.objects.filter(code=produit_data["code"]).exists():
            Product.objects.create(**produit_data)
            print(f"✓ Produit créé: {produit_data['name']}")
        else:
            print(f"- Produit {produit_data['code']} existe déjà")


def create_sample_projects():
    """Créer des projets d'exemple"""
    try:
        cliente = CustomUser.objects.get(username="cliente")
        admin = CustomUser.objects.get(username="admin")
    except CustomUser.DoesNotExist:
        print("Erreur: utilisateurs de test non trouvés")
        return

    projets = [
        {
            "title": "Rénovation salon et cuisine",
            "description": "Repeindre entièrement le salon et la cuisine après rénovation",
            "created_by": cliente,
            "project_type": "peinture_interieure",
            "surface_totale": Decimal("45.50"),
            "nombre_pieces": 2,
            "types_pieces": "Salon, cuisine",
            "etat_support": "renovation_legere",
            "type_finition": "satin",
            "adresse_travaux": "123 Rue de la Paix",
            "code_postal": "75001",
            "ville": "Paris",
            "contact_nom": "Jean Dupont",
            "contact_telephone": "01 98 76 54 32",
            "budget_minimum": Decimal("1500.00"),
            "budget_maximum": Decimal("2500.00"),
            "date_debut_souhaitee": date.today() + timedelta(days=15),
            "date_fin_souhaitee": date.today() + timedelta(days=22),
            "notes_client": "Travaux à prévoir pendant les vacances scolaires",
        },
        {
            "title": "Peinture façade maison",
            "description": "Remise en peinture complète de la façade",
            "created_by": admin,
            "project_type": "peinture_exterieure",
            "surface_totale": Decimal("120.00"),
            "nombre_pieces": 1,
            "types_pieces": "Façade",
            "etat_support": "bon_etat",
            "type_finition": "semi_brillant",
            "adresse_travaux": "456 Avenue des Fleurs",
            "code_postal": "78000",
            "ville": "Versailles",
            "contact_nom": "Marie Martin",
            "contact_telephone": "01 34 56 78 90",
            "budget_minimum": Decimal("3000.00"),
            "budget_maximum": Decimal("4500.00"),
            "date_debut_souhaitee": date.today() + timedelta(days=30),
            "date_fin_souhaitee": date.today() + timedelta(days=35),
            "notes_client": "Prévoir bâchage pour protéger les plantations",
        },
    ]

    for i, projet_data in enumerate(projets, 1):
        if not Project.objects.filter(title=projet_data["title"]).exists():
            projet = Project.objects.create(**projet_data)
            print(f"✓ Projet créé: {projet.title} (#{projet.reference})")

            # Créer un devis pour le premier projet
            if i == 1:
                create_sample_devis(projet)
        else:
            print(f"- Projet '{projet_data['title']}' existe déjà")


def create_sample_devis(projet):
    """Créer un devis d'exemple pour un projet"""
    # Vérifier si un devis existe déjà pour ce projet
    if Devis.objects.filter(project=projet).exists():
        return

    devis = Devis.objects.create(
        project=projet,
        titre=f"Devis pour {projet.title}",
        description="Devis détaillé pour les travaux de peinture",
        terms_conditions="Devis valable 30 jours. Acompte de 30% à la commande.",
        notes="Matériaux de qualité professionnelle inclus",
    )

    # Ajouter des lignes au devis
    produits = [
        ("PEINTURE-INT-001", 3, Decimal("25.90")),
        ("SOUS-COUCHE-001", 2, Decimal("18.75")),
        ("ROULEAU-001", 2, Decimal("8.50")),
        ("MAIN-OEUVRE-001", 16, Decimal("35.00")),
    ]

    for code_produit, quantite, prix in produits:
        try:
            produit = Product.objects.get(code=code_produit)
            DevisLine.objects.create(
                devis=devis,
                produit=produit,
                description=produit.name,
                quantity=quantite,
                price_unit=prix,
            )
        except Product.DoesNotExist:
            print(f"Produit {code_produit} non trouvé")

    print(f"✓ Devis créé pour le projet: {projet.title}")


if __name__ == "__main__":
    print("Création des données d'exemple...")
    create_sample_products()
    print()
    create_sample_projects()
    print("\nDonnées d'exemple créées avec succès!")
