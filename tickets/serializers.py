from rest_framework import serializers
from tickets.models import Guest, Movie, Reservation,Post


class MovieSerializers(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class ReservationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'


class GuestSerializers(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['pk', 'reservation', 'name', 'mobile']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields='__all__'