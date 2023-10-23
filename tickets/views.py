from django.shortcuts import render
from django.http.response import JsonResponse
from .models import Guest, Movie, Reservation,Post
from rest_framework.decorators import api_view
from .serializers import GuestSerializers, MovieSerializers, ReservationSerializers,PostSerializer
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from rest_framework import generics, mixins, viewsets
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly

# 1 without REST and no model query FBV
def no_rest_no_model(request):
    guests = [
        {
            'id': 1,
            'Name': 'Bakr',
            'mobile': 1000,
        },
        {
            'id': 2,
            'Name': 'Tamem',
            'mobile': '0100',
        },
    ]
    return JsonResponse(guests, safe=False)

# 2 model data default django without rest


def no_rest_from_model(request):
    data = Guest.objects.all()
    response = {
        'guests': list(data.values('name', 'mobile'))
    }
    return JsonResponse(response)

# 3 Function based views
# 3.1 GET POST


@api_view(['GET', 'POST'])
def FBV_List(request):

    # GET
    if request.method == 'GET':
        guests = Guest.objects.all()
        serializer = GuestSerializers(guests, many=True)
        return Response(serializer.data)
    # POST
    elif request.method == 'POST':
        serializer = GuestSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# 3.2 GET PUT DELETE


@api_view(['GET', 'PUT', 'DELETE'])
def FBV_pk(request, pk):

    # guest=Guest.objects.get(pk=pk)
    try:
        guest = Guest.objects.get(pk=pk)
    except Guest.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    if request.method == 'GET':
        serializer = GuestSerializers(guest)
        return Response(serializer.data)

    # PUT
    elif request.method == 'PUT':
        serializer = GuestSerializers(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    if request.method == 'DELETE':
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 4 CBV class based views
# 4.1 List and Create == GET and POST


class CBV_List(APIView):
    def get(self, request):
        guests = Guest.objects.all()
        serializer = GuestSerializers(guests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GuestSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.data,
            status=status.HTTP_400_BAD_REQUEST
        )

# 4.2 GET PUT DELETE class based views -- pk


class CBV_pk(APIView):

    def get_object(self, pk):
        try:
            return Guest.objects.get(pk=pk)
        except Guest.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializers(guest)
        return Response(serializer.data)

    def put(self, request, pk):
        guest = self.get_object(pk)
        serializer = GuestSerializers(guest, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        guest = self.get_object(pk)
        guest.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 5 Mixins
# 5.1 mixins list


class mixins_list(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView
):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializers

    def get(self, request):
        return self.list(request)

    def post(self, request):
        return self.create(request)

# 5.2 mixins get put delete


class mixins_pk(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        generics.GenericAPIView):

    queryset = Guest.objects.all()
    serializer_class = GuestSerializers

    def get(self, request, pk):
        return self.retrieve(request)

    def put(self, request, pk):
        return self.update(request)

    def delete(self, request, pk):
        return self.destroy(request)


# 6 Generics
# 6.1 GET and POST
class generics_list(generics.ListAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializers
    # authentication_classes=[BasicAuthentication]
    # permission_classes=[IsAuthenticated]  #for basic auth
    authentication_classes=[TokenAuthentication]
# 6.2 GET and PUT and DELETE


class generics_pk(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializers
    # authentication_classes=[BasicAuthentication]
    # permission_classes=[IsAuthenticated]   #for basic auth
    authentication_classes=[TokenAuthentication] 
# 7.1 viewsets


class viewsets_guest(viewsets.ModelViewSet):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializers


class viewsets_Movie(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializers
    filter_backend = [filters.SearchFilter]
    search_fields = ['movie']


class viewsets_Reservation(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializers

# 8 Find movie


@api_view(['GET'])
def find_movie(request):
    movies = Movie.objects.filter(
        hall=request.data['hall'],
        movie=request.data['movie'],
    )
    serializer = MovieSerializers(movies, many=True)
    return Response(serializer.data)

# 9 create new reservation


@api_view(['POST'])
def new_reservations(request):

    movie = Movie.objects.get(
        hall=request.data['hall'],
        movie=request.data['movie'],
    )
    guest = Guest()
    guest.name = request.data['name']
    guest.mobile = request.data['mobile']
    guest.save()

    reservation = Reservation()
    reservation.guest = guest
    reservation.movie = movie
    reservation.save()

    return Response(status=status.HTTP_201_CREATED)


#10 post author editor and anyone can read    
class Post_pk(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthorOrReadOnly]
    queryset=Post.objects.all()
    serializer_class=PostSerializer