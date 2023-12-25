# Imports
from django.shortcuts import render
from .models import solanamysterybox
import time

# Function to acquire the lock
def acquire_lock():
    # Fetch the lock details from the database
    first = solanamysterybox.objects.first()
    current_time = time.time()
    lock = first.lock
    lock_time = first.lock_time
    # Check if the lock is open or has been locked for more than 15 seconds.
    # The timing is crucial because if the user abruptly terminates the view, 
    # the lock may remain engaged, potentially resulting in a deadlock.
    if lock == "Open" or (current_time - lock_time > 15):
        # If conditions met, acquire the lock
        first.lock = "Close"
        first.lock_time = current_time
        first.save()
        return True  # Lock acquired successfully
    return False  # Lock acquisition failed

# Function to release the lock
def release_lock():
    # Fetch the lock details from the database and release the lock
    first = solanamysterybox.objects.first()
    first.lock = "Open"
    first.save()

# Decorator for Implementing the Payment View Locking Mechanism
def payment_lock(view_func):
    def wrapper(request, *args, **kwargs):
        # Attempt to acquire the lock
        if acquire_lock():
            try:
                # Execute the view function
                return view_func(request, *args, **kwargs)
            finally:
                # Release the lock after the view function execution
                release_lock()
        else:
            # Render response if lock acquisition failed
            return render(request, "SolanaMysteryBox/solanaMB_response.html", {
                "payment_response": " ",
                "text1": "This payment is being processed. Please wait!",
                "link1": "Try again",
                "link2": "Learn More"
            })
    return wrapper
