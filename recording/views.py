from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Recording, Category, SubCategory
from .serializers import RecordingSerializer, RecordingCreateSerializer, RecordingUpdateSerializer

class RecordingView(APIView):
    def get(self, request):
        recordings = Recording.objects.select_related(
            'category'
        ).prefetch_related(
            'category__subcategories'
        ).all().order_by('-creation_date')
        
        status_filter = request.GET.get('status')
        category_filter = request.GET.get('category')
        type_filter = request.GET.get('type')
        search_query = request.GET.get('search')
        
        if status_filter:
            recordings = recordings.filter(status=status_filter)
        
        if category_filter:
            recordings = recordings.filter(category_id=category_filter)
        
        if type_filter:
            recordings = recordings.filter(category__type=type_filter)
        
        if search_query:
            recordings = recordings.filter(
                Q(comment__icontains=search_query) |
                Q(category__category__icontains=search_query)
            )
        
        if request.accepted_media_type == 'text/html' or not request.accepted_media_type:
            context = {
                'recordings': recordings,
                'categories': Category.objects.all(),
                'subcategories': SubCategory.objects.all(),
                'status_choices': Recording.Status.choices,
                'type_choices': Category.Type.choices,
                'current_filters': {
                    'status': status_filter,
                    'category': category_filter,
                    'type': type_filter,
                    'search': search_query,
                }
            }
            return render(request, 'recording/recording_list.html', context)
        
        serializer = RecordingSerializer(recordings, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'create_category':
            try:
                category = Category.objects.create(
                    category=request.POST.get('category_name'),
                    type=request.POST.get('category_type')
                )
                return redirect('recording:recording-list')
            except Exception as e:
                recordings = Recording.objects.all().order_by('-creation_date')
                context = {
                    'recordings': recordings,
                    'categories': Category.objects.all(),
                    'subcategories': SubCategory.objects.all(),
                    'status_choices': Recording.Status.choices,
                    'type_choices': Category.Type.choices,
                    'error': f'Ошибка создания категории: {str(e)}'
                }
                return render(request, 'recording/recording_list.html', context, status=400)
        
        elif action == 'create_subcategory':
            try:
                subcategory = SubCategory.objects.create(
                    subcategory=request.POST.get('subcategory_name'),
                    category_id=request.POST.get('parent_category')
                )
                return redirect('recording:recording-list')
            except Exception as e:
                recordings = Recording.objects.all().order_by('-creation_date')
                context = {
                    'recordings': recordings,
                    'categories': Category.objects.all(),
                    'subcategories': SubCategory.objects.all(),
                    'status_choices': Recording.Status.choices,
                    'type_choices': Category.Type.choices,
                    'error': f'Ошибка создания подкатегории: {str(e)}'
                }
                return render(request, 'recording/recording_list.html', context, status=400)
        
        else:
            if request.content_type == 'application/x-www-form-urlencoded':
                try:
                    recording = Recording.objects.create(
                        status=request.POST.get('status'),
                        category_id=request.POST.get('category'),
                        sum=request.POST.get('sum', 0),
                        comment=request.POST.get('comment', '')
                    )
                    return redirect('recording:recording-list')
                except Exception as e:
                    recordings = Recording.objects.all().order_by('-creation_date')
                    context = {
                        'recordings': recordings,
                        'categories': Category.objects.all(),
                        'subcategories': SubCategory.objects.all(),
                        'status_choices': Recording.Status.choices,
                        'type_choices': Category.Type.choices,
                        'error': f'Ошибка создания записи: {str(e)}'
                    }
                    return render(request, 'recording/recording_list.html', context, status=400)
            
            else:
                serializer = RecordingCreateSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    recording = Recording.objects.get(id=serializer.instance.id)
                    full_serializer = RecordingSerializer(recording)
                    return Response(full_serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        recording_id = request.data.get('id')
        if not recording_id:
            return Response({'error': 'ID записи обязателен'}, status=status.HTTP_400_BAD_REQUEST)
        
        recording = get_object_or_404(Recording, pk=recording_id)
        serializer = RecordingUpdateSerializer(recording, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            full_serializer = RecordingSerializer(recording)
            return Response(full_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        action = request.POST.get('action') if request.content_type == 'application/x-www-form-urlencoded' else request.data.get('action')
        
        if action == 'delete_category':
            category_id = request.POST.get('id') if request.content_type == 'application/x-www-form-urlencoded' else request.data.get('id')
            category = get_object_or_404(Category, pk=category_id)
            category.delete()
            return redirect('recording:recording-list')
        
        elif action == 'delete_subcategory':
            subcategory_id = request.POST.get('id') if request.content_type == 'application/x-www-form-urlencoded' else request.data.get('id')
            subcategory = get_object_or_404(SubCategory, pk=subcategory_id)
            subcategory.delete()
            return redirect('recording:recording-list')
        
        else:
            recording_id = request.POST.get('id') if request.content_type == 'application/x-www-form-urlencoded' else request.data.get('id')
            if not recording_id:
                return Response({'error': 'ID записи обязателен'}, status=status.HTTP_400_BAD_REQUEST)
            
            recording = get_object_or_404(Recording, pk=recording_id)
            recording.delete()
            
            if request.content_type == 'application/x-www-form-urlencoded':
                return redirect('recording:recording-list')
            
            return Response(status=status.HTTP_204_NO_CONTENT)