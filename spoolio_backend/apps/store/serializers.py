from rest_framework import serializers

from . import models


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductCategory
        fields = '__all__'


class ProductSubcategorySerializer(serializers.ModelSerializer):

    category = ProductCategorySerializer(read_only=True)

    class Meta:
        model = models.ProductSubcategory
        fields = '__all__'


class ProductVariationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductVariation
        fields = '__all__'


class ProductVariationOptionSerializer(serializers.ModelSerializer):

    type = ProductVariationSerializer(read_only=True)

    class Meta:
        model = models.ProductVariationOption
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):

    category = ProductCategorySerializer(read_only=True)
    subcategory = ProductSubcategorySerializer(read_only=True)

    productvariationoption_set = ProductVariationOptionSerializer(read_only=True, many=True)
    productimage_set = ProductImageSerializer(read_only=True, many=True)

    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    starting_price = serializers.SerializerMethodField()
    ending_price = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.filter(is_deleted=False).count()

    def get_like_count(self, instance):
        return instance.likes.filter(is_deleted=False).count()

    def get_starting_price(self, instance):
        queryset = instance.productvariationoptioncombination_set.order_by('price')
        cheapest_combination = queryset.first()

        if cheapest_combination:
            return cheapest_combination.price
        return None

    def get_ending_price(self, instance):
        queryset = instance.productvariationoptioncombination_set.order_by('price')
        most_expensive_combination = queryset.last()

        if most_expensive_combination:
            return most_expensive_combination.price
        return None


class ProductVariationOptionCombinationSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    options = ProductVariationOptionSerializer(read_only=True, many=True)

    class Meta:
        model = models.ProductVariationOptionCombination
        fields = '__all__'