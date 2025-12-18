# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
import uuid
import random
import string
import shortuuid
import re
from datetime import time
import requests


# ----------------------------------------------------------------------
# UID generator (shared by User and Attendance)
# ----------------------------------------------------------------------
def generate_uid(prefix="U"):
    """6-char unique UID – no DB look-ups, no race conditions."""
    return f"{prefix}{shortuuid.uuid()[:6].upper()}"


ROLES = (
     ("SuperAdmin", "SuperAdmin"),
    ("admin", "Admin"),
    ("team_leader", "Team Leader"),
    ("staff", "Staff"),
   
)

role = models.CharField(max_length=20, choices=ROLES, default="staff")

class WorkLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    project = models.CharField(max_length=200)
    work = models.TextField(blank=True, null=True)
    time_taken = models.CharField(max_length=50, blank=True, null=True)
    progress = models.TextField(blank=True, null=True)

    check_in = models.TimeField()
    check_out = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.project} ({self.date})"


# ----------------------------------------------------------------------
# Profile
# ----------------------------------------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # --------------------
    # Basic Info (existing)
    # --------------------
    full_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    join_date = models.DateField(null=True, blank=True)

    # --------------------
    # Contact Information (NEW)
    # --------------------
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    reports_to = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Manager / Team Leader name"
    )

    # --------------------
    # Skills & Education (NEW)
    # --------------------
    education = models.CharField(max_length=200, null=True, blank=True)
    skills = models.TextField(
        null=True,
        blank=True,
        help_text="Comma separated skills (e.g. Python, Django, REST)"
    )

    # --------------------
    # System Fields
    # --------------------
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        db_index=True
    )
    delete_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------
    # Helpers
    # --------------------
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",")] if self.skills else []

    def save(self, *args, **kwargs):
        if not self.delete_code:
            self.delete_code = generate_uid("D")[:7]  # e.g. D9XK2MP
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.user.username


# ----------------------------------------------------------------------
# Attendance
# ----------------------------------------------------------------------
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts_attendance')
    date = models.DateField(default=date.today)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    uid = models.CharField(max_length=20, unique=True, blank=True, null=True)

    working_hours = models.DurationField(null=True, blank=True)

    # ✅ ADD THIS
    late_minutes = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=12,
        choices=(
            ("Present", "Present"),
            ("Half Day", "Half Day"),
            ("Checked In", "Checked In"),
            ("Absent", "Absent"),
        ),
        default="Absent",
    )

    class Meta:
        unique_together = ('user', 'date')


    # ------------------------------------------------------------------
    # AUTO-CALCULATE ON SAVE
    # ------------------------------------------------------------------
    

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = generate_uid("A")

        if self.check_in:
            # LATE CALCULATION
            OFFICE_START_TIME = time(9, 0)
            office_dt = datetime.combine(self.date, OFFICE_START_TIME)
            checkin_dt = datetime.combine(self.date, self.check_in)

            if checkin_dt > office_dt:
                self.late_minutes = int((checkin_dt - office_dt).total_seconds() / 60)
            else:
                self.late_minutes = 0

        if self.check_in and self.check_out:
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)

            if check_out_dt < check_in_dt:
                check_out_dt += timedelta(days=1)

            duration = check_out_dt - check_in_dt
            self.working_hours = duration

            hours = duration.total_seconds() / 3600
            self.status = "Present" if hours >= 8 else "Half Day"

        elif self.check_in:
            self.status = "Checked In"
            self.working_hours = None
        else:
            self.status = "Absent"

        super().save(*args, **kwargs)



# ----------------------------------------------------------------------
# Leave
# ----------------------------------------------------------------------
class Leave(models.Model):
    LEAVE_TYPES = (
        ("Sick", "Sick Leave"),
        ("Casual", "Casual Leave"),
        ("Earned", "Earned Leave"),
    )

    STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.CharField()

    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    status = models.CharField(max_length=10, choices=STATUS, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} → {self.end_date})"


# ----------------------------------------------------------------------
# Holiday
# ----------------------------------------------------------------------
class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.date})" 


# ----------------------------------------------------------------------
# Task
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Task
# ----------------------------------------------------------------------
class Task(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    )

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        limit_choices_to={'role': 'staff'}
    )
    created_by  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    due_date    = models.DateField(null=True, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    uid         = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = generate_uid("T")          # e.g. T9XK2M
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} – {self.assigned_to.username}"






def extract_lat_lng(map_link):
    """
    Supports:
    https://maps.google.com/?q=26.9124,75.7873
    https://www.google.com/maps/@26.9124,75.7873,17z
    """

    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', map_link)
    if match:
        return float(match.group(1)), float(match.group(2))

    match = re.search(r'q=(-?\d+\.\d+),(-?\d+\.\d+)', map_link)
    if match:
        return float(match.group(1)), float(match.group(2))

    return None, None


def get_location_name(lat, lng):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lng,
        "format": "json"
    }
    headers = {"User-Agent": "AttendanceApp"}

    res = requests.get(url, params=params, headers=headers, timeout=5)
    if res.status_code == 200:
        return res.json().get("display_name")

    return None


class AllowedLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    radius_meters = models.PositiveIntegerField(default=300)

    map_input = models.CharField(
        max_length=500,
        blank=True,
        help_text="Paste Google Maps link or 'lat,lng'"
    )

    def save(self, *args, **kwargs):
        # Auto-extract lat/lng if map_input is provided
        if self.map_input and (self.latitude is None or self.longitude is None):
            lat, lng = extract_lat_lng(self.map_input)
            if lat is not None and lng is not None:
                self.latitude = lat
                self.longitude = lng

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.radius_meters}m zone"


class UserLocation(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

