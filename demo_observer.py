"""
demo_observer.py

A pure Python demonstration of the Observer Design Pattern for Classroom Notice Boards.
This demo can be run directly from the command line without starting the web server.
"""

from app.models.observer import StudentNotificationObserver
from app.models.notice_board import NoticeBoard

def main():
    print("==================================================")
    # 1. Create a NoticeBoard (the Subject) for CSE-3216
    print("Step 1: Creating a classroom Notice Board (Subject)...")
    notice_board = NoticeBoard(classroom_id="cse_3216_notice_board")
    print(f"Notice Board created for: {notice_board.classroom_id}\n")

    # 2. Create Concrete Observers
    print("Step 2: Instantiating StudentNotificationObservers...")
    alice = StudentNotificationObserver(student_id="101", username="Alice", email="alice@university.edu")
    bob = StudentNotificationObserver(student_id="102", username="Bob", email="bob@university.edu")
    charlie = StudentNotificationObserver(student_id="103", username="Charlie", email="charlie@university.edu")
    print(f"Created observers: {alice.username}, {bob.username}, {charlie.username}\n")

    # 3. Attach Observers
    print("Step 3: Attaching observers (Alice and Bob) to the Notice Board...")
    notice_board.attach(alice)
    notice_board.attach(bob)
    print(f"Attached observers. Current subscribers: {[obs.username for obs in notice_board._observers]}\n")

    # 4. Notify - Broadcast Notice 1
    print("Step 4: Publishing first notice (Broadcasting)...")
    notice_board.notify("Midterm examination scheduled for next Monday at 10:00 AM.")
    print("")

    # 5. Attach another observer
    print("Step 5: Charlie enrolls and gets attached as an observer...")
    notice_board.attach(charlie)
    print(f"Current subscribers: {[obs.username for obs in notice_board._observers]}\n")

    # 6. Notify - Broadcast Notice 2
    print("Step 6: Publishing second notice...")
    notice_board.notify("Assignment 1 deadline extended by 3 days.")
    print("")

    # 7. Detach Bob
    print("Step 7: Bob is detached (unsubscribed) from the Notice Board...")
    notice_board.detach(bob)
    print(f"Current subscribers: {[obs.username for obs in notice_board._observers]}\n")

    # 8. Notify - Broadcast Notice 3
    print("Step 8: Publishing third notice...")
    notice_board.notify("Welcome to the Software Design Pattern Lab course!")
    print("==================================================")

if __name__ == "__main__":
    main()
