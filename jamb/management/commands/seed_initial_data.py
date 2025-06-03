# jamb/management/commands/seed_initial_data.py

from django.core.management.base import BaseCommand
from jamb.models import JAMBSubject, JAMBQuestion, JAMBOption, Strategy
from testimonials.models import Testimonial

class Command(BaseCommand):
    help = "Seed initial JAMB subjects/questions/strategies and Testimonials."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding initial data..."))

        # ─────────── JAMB Subjects ───────────
        jamb_subjects = [
            {
                "name":     "English Language",
                "slug":     "english-language",
                "topics":   30,
                "duration": "45 hours",
            },
            {
                "name":     "Mathematics",
                "slug":     "mathematics",
                "topics":   25,
                "duration": "40 hours",
            },
            # add more subjects here if desired
        ]

        for subj in jamb_subjects:
            obj, created = JAMBSubject.objects.get_or_create(
                slug=subj["slug"],
                defaults={
                    "name":     subj["name"],
                    "topics":   subj["topics"],
                    "duration": subj["duration"],
                },
            )
            if created:
                self.stdout.write(f"  • Created JAMB Subject: {obj.name}")
            else:
                self.stdout.write(f"  • Already exists JAMB Subject: {obj.name}")

        # ─────────── JAMB Questions ───────────
        try:
            math_subject = JAMBSubject.objects.get(slug="mathematics")
        except JAMBSubject.DoesNotExist:
            self.stderr.write("ERROR: Cannot create question: 'Mathematics' subject not found.")
            math_subject = None

        if math_subject:
            question_text = "If z = 3 + 4i, what is the modulus of z?"
            existing_q = JAMBQuestion.objects.filter(
                subject=math_subject,
                question_text=question_text
            ).first()

            if not existing_q:
                # 1) Create the question row itself
                new_q = JAMBQuestion.objects.create(
                    subject=math_subject,
                    question_text=question_text
                )

                # 2) Create its options under JAMBOption
                choices = ["5", "7", "12", "25"]
                correct_idx = 0  # the correct answer is "5"
                for idx, opt_text in enumerate(choices):
                    JAMBOption.objects.create(
                        question   = new_q,
                        label      = chr(65 + idx),       # "A", "B", "C", "D"
                        text       = opt_text,
                        is_correct = (idx == correct_idx)
                    )
                self.stdout.write(f"  • Created JAMBQuestion (Mathematics): {new_q.id}")
            else:
                self.stdout.write("  • JAMBQuestion already exists for Mathematics")

        # ─────────── JAMB Strategies ───────────
        strategies = [
            {
                "category": "Time Management Tips",
                "content": (
                    "1. Spend no more than 45 seconds per question.\n"
                    "2. Answer easy questions first, then return to harder ones.\n"
                    "3. Practice with timed mock exams to build pace.\n"
                    "4. Allocate time to review your answers if possible."
                ),
            },
            {
                "category": "Answering Techniques",
                "content": (
                    "1. Look for absolute terms like “always” or “never”—these are often wrong.\n"
                    "2. Eliminate clearly wrong options first.\n"
                    "3. Watch for similar paired options—one is likely correct.\n"
                    "4. Pay attention to questions with “EXCEPT” or “NOT.”"
                ),
            },
        ]

        for strat in strategies:
            obj, created = Strategy.objects.get_or_create(
                category=strat["category"],
                defaults={"content": strat["content"]},
            )
            if created:
                self.stdout.write(f"  • Created Strategy: {obj.category}")
            else:
                self.stdout.write(f"  • Already exists Strategy: {obj.category}")

        # ─────────── Testimonials ───────────
        testimonials = [
            {
                "name":       "Henry Ifeanyi",
                "role":       "Software Developer",
                "avatar_url": "https://randomuser.me/api/portraits/men/32.jpg",
                "quote": (
                    "Edenites Academy transformed my career. The AWS certification course "
                    "helped me land my dream job at Amazon!"
                ),
                "rating": 5,
            },
            {
                "name":       "Chinaza Miracle O",
                "role":       "Fashion Designer",
                "avatar_url": "https://randomuser.me/api/portraits/women/44.jpg",
                "quote": (
                    "The leather crafting courses are exceptional. I started my own business "
                    "after completing just two courses!"
                ),
                "rating": 5,
            },
            # … feel free to add more testimonials here
        ]

        for t in testimonials:
            obj, created = Testimonial.objects.get_or_create(
                name=t["name"],
                defaults={
                    "role":       t["role"],
                    "avatar_url": t["avatar_url"],
                    "quote":      t["quote"],
                    "rating":     t["rating"],
                },
            )
            if created:
                self.stdout.write(f"  • Created Testimonial: {obj.name}")
            else:
                self.stdout.write(f"  • Already exists Testimonial: {obj.name}")

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
