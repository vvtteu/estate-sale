from django.shortcuts import render, get_object_or_404
from .models import *
from django.db.models import Q

def index_page(request):
    properties = Property.objects.filter(
        is_published=True
    ).prefetch_related('translations', 'images').order_by('-created_at')
    
    site_settings = SiteSettings.objects.first()

    context = {
        'properties': properties,
        'settings': site_settings
    }
    return render(request, 'properties/index.html', context)


def catalog_view(request):
    queryset = (
        Property.objects.filter(is_published=True)
        .select_related("deal_type", "property_type", "status")
        .prefetch_related("images", "translations", "attribute_values__attribute")
        .order_by("-created_at")
    )
 
    deal_type = request.GET.get("deal_type")
    if deal_type:
        queryset = queryset.filter(deal_type__slug=deal_type)
 
    property_type = request.GET.get("property_type")
    if property_type:
        queryset = queryset.filter(property_type_id=property_type)
 
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)
 
    search_query = request.GET.get("search")
    if search_query:
        queryset = queryset.filter(
            Q(address__icontains=search_query)
            | Q(city__icontains=search_query)
            | Q(district__icontains=search_query)
            | Q(translations__title__icontains=search_query)
        ).distinct()
 
    rooms = request.GET.get("rooms")
    if rooms:
        if rooms == "4":
            queryset = queryset.filter(
                attribute_values__attribute__slug="rooms",
                attribute_values__value_integer__gte=4,
            )
        else:
            queryset = queryset.filter(
                attribute_values__attribute__slug="rooms",
                attribute_values__value_integer=rooms,
            )
 
    min_area = request.GET.get("min_area")
    max_area = request.GET.get("max_area")
    if min_area:
        queryset = queryset.filter(area_total__gte=min_area)
    if max_area:
        queryset = queryset.filter(area_total__lte=max_area)
 
    property_types = PropertyType.objects.filter(is_active=True)
 
    context = {
        "properties": queryset,
        "property_types": property_types,
    }
    return render(request, "properties/catalog.html", context)


def property_detail_view(request, slug):
    property_obj = get_object_or_404(
        Property.objects.filter(is_published=True)
        .select_related("deal_type", "property_type", "status")
        .prefetch_related("images", "translations", "attribute_values__attribute"),
        slug=slug
    )
    
    similar_properties = (
        Property.objects.filter(is_published=True, property_type=property_obj.property_type)
        .exclude(id=property_obj.id)
        .select_related("deal_type", "property_type", "status")
        .prefetch_related("images", "translations")
        .order_by("-created_at")[:3]
    )

    latest_rate = ExchangeRate.objects.order_by("-effective_date").first()
 
    price_usd, price_gel = None, None
    if property_obj.currency == Currency.GEL:
        price_gel = property_obj.price
        if latest_rate:
            price_usd = round(property_obj.price / latest_rate.usd_to_gel, 2)
    else:  # USD
        price_usd = property_obj.price
        if latest_rate:
            price_gel = round(property_obj.price * latest_rate.usd_to_gel, 2)
 
    context = {
        "property": property_obj,
        "similar_properties": similar_properties,
        "site_settings": SiteSettings.objects.first(),
        "price_usd": price_usd,
        "price_gel": price_gel,
    }
    return render(request, "properties/detail.html", context)