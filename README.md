# DementiaCare AI

### AI-Powered Cognitive Health Monitoring and Assistance System for Dementia Patients

## Overview

DementiaCare AI is an intelligent healthcare support system designed to assist dementia patients and their caregivers through AI-powered monitoring, cognitive support, and safety features.

Dementia is a progressive neurological disorder that affects memory, thinking ability, and daily functioning. This project aims to provide an integrated AI-based solution that supports early risk prediction, patient assistance, caregiver monitoring, and real-time safety tracking.

The system combines machine learning, deep learning, and natural language processing to create a supportive digital companion that improves patient independence while helping caregivers monitor health conditions effectively.

---

## Key Features

### 1. Dementia Risk Prediction

A machine learning model predicts the likelihood and severity stage of dementia using patient symptoms, behavioral attributes, and cognitive assessment scores.

**Algorithm Used:** Random Forest Classifier

Functions:

* Symptom-based dementia prediction
* Cognitive assessment evaluation
* Risk level identification
* Early detection support

---

### 2. Relative Identification (Face Recognition)

A deep learning model identifies familiar individuals using facial recognition to help patients recognize family members and caregivers.

**Algorithm Used:** Convolutional Neural Network (CNN)

Functions:

* Detect faces using webcam
* Recognize trained family members
* Display person name and relationship
* Reduce confusion and anxiety

---

### 3. AI Chatbot Assistant

A conversational AI assistant helps patients with guidance, reminders, and health-related queries.

**Model Used:** Transformer-based BERT-style NLP model

Functions:

* Natural conversation support
* Medication information
* Appointment guidance
* Daily assistance and emotional support

---

### 4. Smart Reminder System

Automated reminders help patients follow daily routines and medical schedules.

Functions:

* Medicine reminders
* Doctor appointment alerts
* Activity notifications

---

### 5. Cognitive Training

Interactive exercises help maintain cognitive ability.

Examples:

* Memory games
* Attention training
* Cognitive performance tracking

---

### 6. Caretaker Dashboard

Caregivers can monitor patient health and activities through a dedicated interface.

Functions:

* View prediction reports
* Track medication adherence
* Monitor patient activities
* View cognitive performance

---

### 7. Real-Time Safety Monitoring

The system tracks patient location and detects wandering behavior to improve safety.

Functions:

* Live GPS tracking
* Geofencing alerts
* Emergency notifications

---

## System Architecture

The system integrates multiple AI modules:

1. Patient enters symptoms and completes cognitive assessment tests
2. Data is preprocessed and analyzed
3. Random Forest model predicts dementia risk
4. CNN model identifies known individuals
5. AI chatbot processes patient queries
6. Reminder system manages medicine and appointments
7. GPS module tracks patient location
8. Caretaker dashboard displays monitoring information

---

## Technologies Used

### Programming Language

* Python 3.x

### Machine Learning

* scikit-learn
* NumPy
* Pandas

### Deep Learning

* TensorFlow
* Keras

### Computer Vision

* OpenCV

### Natural Language Processing

* Transformers
* NLTK / spaCy

### Web Technologies

* HTML
* CSS
* JavaScript
* Flask (Python Web Framework)

### APIs

* Google Maps API (optional for GPS tracking)

---

## Project Structure

```
## Project Structure


dementiacare-ai/
│
├── app.py
├── train_model.py
├── train_relative_model.py
│
├── dementia_dataset.xlsx
├── dementia_knowledge.xlsx
│
├── dementia_model.pkl
├── dementia_encoders.pkl
├── relative_face_model.pkl
├── relative_label_encoder.pkl
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   └── other HTML pages
│
├── static/
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   ├── lib/
│   │   ├── scss/
│   │   └── images/
│   │
│   ├── accuracy_plot.png
│   ├── feature_importance.png
│   └── memory.mp4
│
├── dataset/
│   └── relatives/
│       └── training images for face recognition
│
├── database/
│   └── dementia_care.sql
│
└── README.md
```



---

## Actors of the System

### Dementia Patient

* Enters symptoms
* Receives predictions
* Uses chatbot assistance
* Plays cognitive games
* Receives reminders

### Caretaker

* Manages patient profile
* Tracks location and activity
* Receives alerts
* Monitors health reports

### Doctor / Medical Professional

* Reviews patient data
* Validates prediction results
* Updates treatment plans

### System Administrator

* Maintains database
* Manages system security
* Updates AI models

---

## Future Improvements

* Mobile application integration
* Wearable device support
* Voice-based interaction
* Advanced clinical decision support
* Real-time health sensor integration

---

## Purpose of the Project

The goal of this project is to demonstrate how artificial intelligence can assist in improving the quality of life for dementia patients while reducing the burden on caregivers through intelligent monitoring and assistance systems.

---

## Author

**Sudalaimuthumari M**
B.Tech – Artificial Intelligence and Data Science
Francis Xavier Engineering College

---

## License

This project is created for academic and research purposes.
