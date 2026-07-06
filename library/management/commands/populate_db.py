import random
from django.core.management.base import BaseCommand
from library.models import Author, Book, Member, CirculationRecord
from django.utils import timezone
from datetime import timedelta, date

class Command(BaseCommand):
    help = 'Populates the database with sample library data: 20 authors, 100 books, 30 members, and random circulation records.'

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        CirculationRecord.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Member.objects.all().delete()

        self.stdout.write("Generating 20 Authors...")
        first_names = ["Aldous", "George", "Virginia", "Ernest", "F. Scott", "Jane", "Charles", "Leo", "Fyodor", "Gabriel", "Mark", "Arthur", "Mary", "Agatha", "Stephen", "Toni", "Haruki", "J.K.", "George R.R.", "Margaret"]
        last_names = ["Huxley", "Orwell", "Woolf", "Hemingway", "Fitzgerald", "Austen", "Dickens", "Tolstoy", "Dostoevsky", "Marquez", "Twain", "Conan Doyle", "Shelley", "Christie", "King", "Morrison", "Murakami", "Rowling", "Martin", "Atwood"]
        
        authors = []
        for i in range(20):
            name = f"{first_names[i]} {last_names[i]}"
            biography = (
                f"{name} was an influential writer known for contributing significantly to modern literature. "
                f"Born in the late 19th or early 20th century, their works explored complex themes of humanity, society, "
                f"science, and emotion. They received numerous accolades during their lifetime and continue to inspire millions."
            )
            author = Author.objects.create(name=name, biography=biography)
            authors.append(author)

        self.stdout.write("Generating 30 Members...")
        member_first = ["Amit", "Rahul", "Priya", "Sneha", "Vikram", "Rohan", "Anjali", "Siddharth", "Neha", "Arjun", "Karan", "Simran", "Aisha", "Aditya", "Divya", "Riya", "Varun", "Kabir", "Meera", "Zara", "Kunal", "Pooja", "Raj", "Nikhil", "Shreya", "Ishaan", "Tanvi", "Abhishek", "Rhea", "Manish"]
        member_last = ["Sharma", "Verma", "Patel", "Singh", "Gupta", "Mehra", "Sen", "Joshi", "Kapoor", "Kumar", "Iyer", "Nair", "Reddy", "Choudhury", "Bose", "Das", "Roy", "Malhotra", "Rao", "Shah", "Jadhav", "Deshmukh", "Nair", "Misra", "Pandey", "Trivedi", "Sinha", "Prasad", "Khanna", "Dwivedi"]
        
        members = []
        for i in range(30):
            name = f"{member_first[i]} {member_last[i]}"
            member_id = f"LIB-{1000 + i}"
            email = f"{member_first[i].lower()}.{member_last[i].lower()}{i}@example.com"
            phone = f"+91 {random.randint(7000, 9999)} {random.randint(100000, 999999)}"
            joined_date = date.today() - timedelta(days=random.randint(30, 365))
            member = Member.objects.create(
                name=name,
                member_id=member_id,
                email=email,
                phone=phone,
                joined_date=joined_date
            )
            members.append(member)

        self.stdout.write("Generating 100 Books...")
        genres = ["Fiction", "Dystopian", "Classic", "Science Fiction", "Fantasy", "Mystery", "Thriller", "Biography", "History", "Romance", "Adventure", "Poetry"]
        adjectives = ["The Great", "Silent", "Lost", "Golden", "Hidden", "Forgotten", "Dark", "Infinite", "Wandering", "Echoing", "Ancient", "Modern", "Midnight", "Crimson", "Shadowy", "Whispering", "Secret", "Burning", "Frozen", "Stellar"]
        nouns = ["Gatsby", "Chronicles", "Echoes", "Rivers", "Kingdoms", "Dreams", "Nights", "Labyrinth", "Journey", "Ocean", "Prophecy", "Starlight", "Empires", "Songs", "Silence", "Winds", "Shadows", "Skies", "Vortex", "Horizon"]
        
        books = []
        for i in range(100):
            title = f"{random.choice(adjectives)} {random.choice(nouns)}"
            if Book.objects.filter(title=title).exists():
                title = f"{title} (Vol. {random.randint(2, 5)})"
                
            author = random.choice(authors)
            isbn = f"978{random.randint(1000000000, 9999999999)}"
            while Book.objects.filter(isbn=isbn).exists():
                isbn = f"978{random.randint(1000000000, 9999999999)}"
                
            genre = random.choice(genres)
            total_copies = random.randint(2, 8)
            available_copies = random.randint(1, total_copies)
            
            # Using stable stock library image urls
            cover_url = f"https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&q=80"
            
            book = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                genre=genre,
                total_copies=total_copies,
                available_copies=available_copies,
                cover_url=cover_url
            )
            books.append(book)

        self.stdout.write("Generating Circulation Records...")
        for i in range(45):
            book = random.choice(books)
            member = random.choice(members)
            
            if CirculationRecord.objects.filter(book=book, member=member, is_returned=False).exists():
                continue
                
            issue_days_ago = random.randint(1, 45)
            issue_date = date.today() - timedelta(days=issue_days_ago)
            is_returned = random.choice([True, False])
            
            if is_returned:
                borrow_duration = random.randint(3, 20)
                return_date = issue_date + timedelta(days=borrow_duration)
                if return_date > date.today():
                    return_date = date.today()
                
                record = CirculationRecord(
                    book=book,
                    member=member,
                    issue_date=issue_date,
                    return_date=return_date,
                    is_returned=True
                )
                record.save()
            else:
                if book.available_copies > 0:
                    book.available_copies -= 1
                    book.save()
                    record = CirculationRecord(
                        book=book,
                        member=member,
                        issue_date=issue_date,
                        is_returned=False
                    )
                    record.save()

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))
