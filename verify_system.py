"""
verify_system.py

Comprehensive test suite verifying all design patterns and core components:
1. Singleton Pattern (Database connection class instance checks).
2. Factory Pattern (User and Classroom factory validations).
3. JWT Authentication & Security (Password hashing, verifying, JWT token encoding/decoding).
4. Observer Pattern (NoticeBoard and StudentNotificationObserver integrations).
"""

import sys
import datetime
from app.database import Database
from app.models.user_factory import UserFactory
from app.models.classroom_factory import ClassroomFactory
from app.security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from app.models.notice_board import NoticeBoard
from app.models.observer import StudentNotificationObserver, notification_logs
import jwt

def run_tests():
    print("==================================================")
    print("STARTING SYSTEM DESIGN PATTERNS VERIFICATION SUITE")
    print("==================================================\n")

    # 1. Verify Singleton Design Pattern (Database)
    print("[TEST 1] Testing Singleton Pattern on Database...")
    db1 = Database()
    db2 = Database()
    if db1 is db2:
        print("[SUCCESS] Database class utilizes Singleton Pattern. Same instance returned.")
    else:
        print("[FAILURE] Database class did not return the same instance.")
        sys.exit(1)
    print("")

    # 2. Verify Factory Design Pattern (Users & Classrooms)
    print("[TEST 2] Testing Factory Design Pattern (Users & Classrooms)...")
    try:
        # User factory
        teacher = UserFactory.create_user("Teacher")
        student = UserFactory.create_user("Student")
        print(f"[SUCCESS] UserFactory correctly created {teacher.get_role()} and {student.get_role()} objects.")
        
        # Classroom factory
        lecture = ClassroomFactory.create_classroom("lecture", "Software Design Pattern Lab", "L-3216", "teacher1", "CODE01")
        lab = ClassroomFactory.create_classroom("lab", "Operating Systems Lab", "L-3213", "teacher1", "CODE02")
        seminar = ClassroomFactory.create_classroom("seminar", "AI Trends", "L-3250", "teacher2", "CODE03")
        
        if lecture.get_class_type() == "Lecture" and lab.get_class_type() == "Lab" and seminar.get_class_type() == "Seminar":
            print(f"[SUCCESS] ClassroomFactory correctly created classes: {lecture.name} ({lecture.get_class_type()}), {lab.name} ({lab.get_class_type()}), {seminar.name} ({seminar.get_class_type()}).")
        else:
            raise ValueError("Classroom types mismatch")
    except Exception as e:
        print(f"[FAILURE] Factory validation failed. Details: {e}")
        sys.exit(1)
    print("")

    # 3. Verify JWT Authentication & Security
    print("[TEST 3] Testing Security & JWT Token Logic...")
    try:
        # Test password hashing
        raw_pw = "pass123"
        hashed = hash_password(raw_pw)
        if verify_password(raw_pw, hashed) and not verify_password("wrongpass", hashed):
            print("[SUCCESS] Password hashing and verification logic is correct.")
        else:
            raise ValueError("Password hash verification failed.")

        # Test JWT generation & decoding
        payload = {"sub": "user_id_123", "username": "alex", "role": "Student"}
        token = create_access_token(payload)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("sub") == payload.get("sub") and decoded.get("role") == payload.get("role"):
            print("[SUCCESS] JWT creation and decryption matches subject and role claims.")
        else:
            raise ValueError("JWT payload mismatch.")
    except Exception as e:
        print(f"[FAILURE] Security validation failed. Details: {e}")
        sys.exit(1)
    print("")

    # 4. Verify Observer Design Pattern
    print("[TEST 4] Testing Observer Pattern Notice Board Notifications...")
    try:
        # Reset log buffer
        notification_logs.clear()
        
        # Subject
        nb = NoticeBoard("cse_3216")
        
        # Observers
        student_alice = StudentNotificationObserver("std_1", "Alice", "alice@university.edu")
        student_bob = StudentNotificationObserver("std_2", "Bob", "bob@university.edu")
        
        # Attach observers
        nb.attach(student_alice)
        nb.attach(student_bob)
        
        # Notify
        broadcast_msg = "Software Engineering Assignment deadline is extended."
        nb.notify(broadcast_msg)
        
        # Check logs
        if len(notification_logs) == 2:
            log1, log2 = notification_logs[0], notification_logs[1]
            if (log1["username"] == "Alice" and log1["message"] == broadcast_msg and
                log2["username"] == "Bob" and log2["message"] == broadcast_msg):
                print("[SUCCESS] NoticeBoard correctly broadcasts notice to attached StudentNotificationObservers via update().")
            else:
                raise ValueError("Notification log data incorrect.")
        else:
            raise ValueError(f"Expected 2 notification log entries, found {len(notification_logs)}.")
    except Exception as e:
        print(f"[FAILURE] Observer pattern validation failed. Details: {e}")
        sys.exit(1)
    
    print("\n==================================================")
    print("ALL DESIGN PATTERN VERIFICATIONS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
