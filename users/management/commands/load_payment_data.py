from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Payment
from materials.models import Course, Lesson
from decimal import Decimal
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Load sample payment data into the database'

    def handle(self, *args, **options):
        self.stdout.write('Loading payment data...')
        
        # Create sample users if they don't exist
        users = []
        for i in range(3):
            email = f'user{i+1}@example.com'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'phone': f'+1234567890{i}', 'city': f'City{i+1}'}
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {email}')

        # Create sample courses if they don't exist
        courses = []
        for i in range(2):
            course, created = Course.objects.get_or_create(
                title=f'Sample Course {i+1}',
                defaults={'description': f'Description for course {i+1}'}
            )
            courses.append(course)
            if created:
                self.stdout.write(f'Created course: {course.title}')

        # Create sample lessons if they don't exist
        lessons = []
        for course in courses:
            for i in range(2):
                lesson, created = Lesson.objects.get_or_create(
                    title=f'Lesson {i+1} for {course.title}',
                    course=course,
                    defaults={'description': f'Description for lesson {i+1}'}
                )
                lessons.append(lesson)
                if created:
                    self.stdout.write(f'Created lesson: {lesson.title}')

        # Create sample payments
        payment_methods = ['cash', 'transfer']
        
        for i in range(10):
            user = random.choice(users)
            payment_method = random.choice(payment_methods)
            amount = Decimal(random.randint(50, 500))
            
            # Randomly choose between course or lesson payment
            if random.choice([True, False]):
                # Course payment
                course = random.choice(courses)
                payment, created = Payment.objects.get_or_create(
                    user=user,
                    paid_course=course,
                    payment_method=payment_method,
                    defaults={'payment_amount': amount}
                )
                if created:
                    self.stdout.write(f'Created course payment: {user.email} - {course.title} - ${amount}')
            else:
                # Lesson payment
                lesson = random.choice(lessons)
                payment, created = Payment.objects.get_or_create(
                    user=user,
                    paid_lesson=lesson,
                    payment_method=payment_method,
                    defaults={'payment_amount': amount}
                )
                if created:
                    self.stdout.write(f'Created lesson payment: {user.email} - {lesson.title} - ${amount}')

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded payment data!')
        )