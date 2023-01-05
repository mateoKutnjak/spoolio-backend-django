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


class ProductSerializer(serializers.ModelSerializer):

    category = ProductCategorySerializer(read_only=True)
    subcategory = ProductSubcategorySerializer(read_only=True)

    productvariationoption_set = ProductVariationOptionSerializer(read_only=True, many=True)

    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = '__all__'

    def get_comment_count(self, instance):
        return instance.comments.filter(is_deleted=False).count()

    def get_like_count(self, instance):
        return instance.likes.filter(is_deleted=False).count()


class ProductVariationOptionCombinationSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    options = ProductVariationOptionSerializer(read_only=True, many=True)

    class Meta:
        model = models.ProductVariationOptionCombination
        fields = '__all__'