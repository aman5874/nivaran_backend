"""
System prompts for the Gemini service.
"""

# Default system prompt for doctor information retrieval
DOCTOR_SERVICE_PROMPT = """
Your Task is to format the given data based on the user query.
Understand the query and apply the filters and only return the results that is asked by the user.
Current date: {current_date}
Current time: {current_time}
Current day: {current_day}
Base your response on the user's query and extract relevant information about their specific needs, location, and medical concerns.
This is the complete data of the healthcare providers:
HEALTHCARE_PROVIDERS_DATA = {
    [
{
    "id": "sm_saurabh_10001-0",
    "metadata": {
        "provider_id": "sm_saurabh_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Saurabh Mishra",
        "specialty": "Anaesthesiology",
        "symptoms": [
            "pain management for surgery",
            "anaesthesia for surgical procedures",
            "pre-operative anaesthesia assessment",
            "post-operative pain relief",
            "critical care management",
            "intensive care support for critically ill patients",
            "life support management",
            "management of chronic pain (e.g., back pain, cancer pain)",
            "nerve blocks for pain relief",
            "pain relief during labor and childbirth (epidural)",
            "sedation for medical procedures"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-8795944222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Sunday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ]
        },
        "parent_id": "sm_saurabh_10001",
        "chunk_count": 1
    }
},
{
    "id": "gm_10001-0",
    "metadata": {
        "provider_id": "gm_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Gaurav Mishra",
        "specialty": "Pediatrics & Neonatology",
        "symptoms": [
            "Pediatric care (children's health)",
            "fever in children or infants",
            "cough in children",
            "cold in children",
            "breathing difficulties in children",
            "wheezing in children",
            "neonatal issues (problems in newborns)",
            "premature baby care",
            "low birth weight infants",
            "jaundice in newborns",
            "feeding difficulties in infants and children",
            "vomiting or diarrhea in children",
            "skin rashes in children",
            "child growth and development concerns",
            "vaccinations for children and infants",
            "common childhood illnesses",
            "ear infections in children",
            "allergies in children",
            "asthma in children",
            "nutritional advice for children",
            "fever in child"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-87959-44222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ]
        },
        "parent_id": "gm_10001",
        "chunk_count": 1
    }
},
{
    "id": "iy_10001-0",
    "metadata": {
        "provider_id": "iy_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Indu Yadav",
        "specialty": "Gynaecology & Obstetrics",
        "symptoms": [
            "irregular menstrual periods",
            "missed periods",
            "heavy menstrual bleeding",
            "painful periods",
            "PCOD / PCOS (Polycystic Ovary Syndrome)",
            "pregnancy care (prenatal, antenatal)",
            "childbirth and delivery services",
            "postnatal care (after delivery)",
            "high-risk pregnancy management",
            "gynecological disorders",
            "vaginal infections (e.g., yeast infection, bacterial vaginosis)",
            "vaginal discharge or itching",
            "ovarian cysts",
            "uterine fibroids",
            "endometriosis",
            "pelvic pain (chronic or acute)",
            "menopause symptoms (e.g., hot flashes, mood swings)",
            "uterine problems",
            "cervical screening (Pap smear)",
            "contraception advice and family planning",
            "infertility issues (female)",
            "urinary problems in women (e.g., incontinence)"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-87959-44222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                }
            ]
        },
        "parent_id": "iy_10001",
        "chunk_count": 1
    }
},
{
    "id": "py_10001-0",
    "metadata": {
        "provider_id": "py_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Pradeep Yadav",
        "specialty": "Orthopedics",
        "symptoms": [
            "joint pain (e.g., knee pain, shoulder pain, hip pain, elbow pain)",
            "fractures (broken bones)",
            "bone dislocation",
            "musculoskeletal issues",
            "muscle pain or weakness",
            "sprains and strains (ligament or muscle injuries)",
            "ligament tears",
            "tendonitis (inflammation of tendons)",
            "bursitis",
            "back pain (lower back pain, upper back pain)",
            "neck pain",
            "slipped disc (herniated disc)",
            "sciatica",
            "sports injuries",
            "arthritis (e.g., osteoarthritis, rheumatoid arthritis)",
            "gout",
            "osteoporosis (weak bones)",
            "bone deformities",
            "difficulty walking or moving limbs",
            "carpal tunnel syndrome"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-8795944222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Sunday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ]
        },
        "parent_id": "py_10001",
        "chunk_count": 1
    }
},
{
    "id": "rn_10001-0",
    "metadata": {
        "provider_id": "rn_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Rishabh Nayak",
        "specialty": "General Medicine",
        "symptoms": [
            "fever, chills, body aches",
            "common cold, runny nose",
            "sore throat, cough (general)",
            "general health issues",
            "fatigue, weakness",
            "dizziness, lightheadedness",
            "headaches (common types)",
            "infections (e.g., respiratory, skin - uncomplicated)",
            "digestive problems (e.g., indigestion, acidity, gas, mild constipation or diarrhea)",
            "blood pressure issues (hypertension/high blood pressure, hypotension/low blood pressure)",
            "diabetes management (routine care, initial advice)",
            "thyroid disorders (initial assessment, management)",
            "cholesterol problems",
            "routine health check-ups",
            "adult vaccinations",
            "allergies (general)",
            "unexplained weight loss or gain"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-87959-44222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ],
            "Sunday": [
                {
                    "start_time": "13:00",
                    "end_time": "15:00"
                }
            ]
        },
        "parent_id": "rn_10001",
        "chunk_count": 1
    }
},
{
    "id": "as_amit_10001-0",
    "metadata": {
        "provider_id": "as_amit_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Amit Saxena",
        "specialty": "General Surgeon",
        "symptoms": [
            "hernia (e.g., inguinal, umbilical, abdominal swelling)",
            "gallstones, gallbladder pain (cholecystitis)",
            "appendicitis, appendix pain",
            "abdominal pain requiring surgical evaluation",
            "piles (hemorrhoids)",
            "anal fissures or fistula",
            "abscess drainage",
            "lipoma removal (fatty lump removal)",
            "cyst removal",
            "pilonidal sinus",
            "varicose veins (surgical options)",
            "minor surgical procedures",
            "skin lesions requiring removal",
            "biopsy procedures",
            "initial management of trauma"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-87959-44222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Saturday only": [
                {
                    "start_time": "14:00",
                    "end_time": "21:00"
                }
            ]
        },
        "parent_id": "as_amit_10001",
        "chunk_count": 1
    }
},
{
    "id": "as_arjit_10001-0",
    "metadata": {
        "provider_id": "as_arjit_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Arjit Singh",
        "specialty": "Neurologist",
        "symptoms": [
            "severe or persistent headaches (associated with neurological conditions)",
            "migraines (if requiring surgical evaluation)",
            "spinal issues requiring surgery (e.g., severe slip disc, spinal stenosis)",
            "back or neck pain requiring surgical intervention",
            "sciatica (severe, for surgical consideration)",
            "neurological disorders requiring surgery",
            "brain tumors",
            "spinal tumors",
            "head injuries (e.g., concussion, skull fracture)",
            "spinal cord injury",
            "hydrocephalus (water on the brain)",
            "stroke requiring surgical intervention (e.g., brain hemorrhage)",
            "peripheral nerve disorders requiring surgery (e.g., severe carpal tunnel syndrome, nerve injury)",
            "numbness or weakness in limbs (neurological cause)",
            "seizures (if surgical cause suspected)"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-8795944222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ],
            "Sunday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "17:30",
                    "end_time": "20:00"
                }
            ]
        },
        "parent_id": "as_arjit_10001",
        "chunk_count": 1
    }
},
{
    "id": "mt_10001-0",
    "metadata": {
        "provider_id": "mt_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Mahesh Tripathi",
        "specialty": "Urology",
        "symptoms": [
            "urinary issues (e.g., difficulty urinating, frequent urination, urgency)",
            "painful urination (dysuria)",
            "blood in urine (hematuria)",
            "urinary incontinence (leakage of urine)",
            "recurrent urinary tract infections (UTIs)",
            "kidney stones, flank pain, renal colic",
            "prostate problems (e.g., enlarged prostate/BPH, prostatitis)",
            "difficulty starting or stopping urination",
            "weak urine stream",
            "male infertility",
            "erectile dysfunction (impotence)",
            "testicular pain or lumps",
            "vasectomy",
            "bladder problems (e.g., bladder pain, overactive bladder)",
            "kidney, bladder, or prostate cancer concerns"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-87959-44222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ],
            "Sunday": [
                {
                    "start_time": "10:00",
                    "end_time": "17:00"
                }
            ]
        },
        "parent_id": "mt_10001",
        "chunk_count": 1
    }
},
{
    "id": "av_10001-0",
    "metadata": {
        "provider_id": "av_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. Ankita Verma",
        "specialty": "Pulmonary Medicine",
        "symptoms": [
            "respiratory issues, lung diseases",
            "persistent or chronic cough",
            "coughing up blood (hemoptysis)",
            "shortness of breath (dyspnea), difficulty breathing",
            "wheezing",
            "chest pain or tightness (related to breathing)",
            "asthma diagnosis and management",
            "COPD (Chronic Obstructive Pulmonary Disease - emphysema, chronic bronchitis)",
            "bronchitis (acute or chronic)",
            "pneumonia (lung infection)",
            "tuberculosis (TB) diagnosis and treatment",
            "sleep apnea, snoring with breathing pauses",
            "lung infections",
            "pleural effusion (fluid around lungs)",
            "interstitial lung disease",
            "lung cancer diagnosis and management (non-surgical)"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur",
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-8795944222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ]
        },
        "parent_id": "av_10001",
        "chunk_count": 1
    }}
},
{
    "id": "sm_sp_10001-0",
    "metadata": {
        "provider_id": "sm_sp_10001",
        "provider_type": "doctor",
        "doctor_name": "Dr. S.P. Mishra",
        "specialty": "Sonology (Diagnostic Ultrasound)",
        "symptoms": [
            "need for ultrasound imaging",
            "diagnostic imaging using sound waves",
            "sonography tests",
            "abdominal ultrasound (for liver, gallbladder, spleen, pancreas, kidneys)",
            "pelvic ultrasound (for uterus, ovaries, bladder)",
            "obstetric ultrasound (pregnancy scans, fetal development monitoring)",
            "thyroid gland ultrasound",
            "musculoskeletal ultrasound (for joints, tendons, muscles)",
            "Doppler studies (for blood flow assessment, DVT check)",
            "imaging for suspected gallstones or kidney stones",
            "assessment of cysts or tumors",
            "guidance for medical procedures like biopsies",
            "soft tissue lump evaluation via ultrasound",
            "scrotal or testicular ultrasound"
        ],
        "hospital_id": "10001",
        "hospital_name": "Satyanand Hospital",
        "hospital_type": "General",
        "location": "Shahjahanpur", 
        "address": "Near Vrindavan Garden, Azizganj, Shahjahanpur",
        "contact_number": "+91-8795944222",
        "email": "satyanandhospitalspn@gmail.com",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ]
        },
        "parent_id": "sm_sp_10001",
        "chunk_count": 1
    }
},
{
    "id": "mg_10002-0",
    "metadata": {
        "provider_id": "mg_10002",
        "provider_type": "doctor",
        "doctor_name": "Dr. Manmohan Lal Gupta",
        "specialty": "Ophthalmology (Eye Specialist)",
        "symptoms": [
            "distorted or blurred vision",
            "sudden decrease or loss of vision",
            "eye pain or discomfort",
            "eye irritation, itching, or burning sensation",
            "redness of eyes (bloodshot eyes)",
            "watery eyes or excessive tearing",
            "dry eyes",
            "changes in vision like floaters (spots in vision)",
            "flashes of light in vision",
            "halos around lights",
            "double vision (diplopia)",
            "difficulty seeing at night",
            "sensitivity to light (photophobia)",
            "eye strain or fatigue",
            "headaches related to eye problems",
            "suspected cataract (cloudy vision)",
            "suspected glaucoma (increased eye pressure, peripheral vision loss)",
            "macular degeneration concerns",
            "diabetic eye check-up (retinopathy screening)",
            "conjunctivitis (pink eye) or other eye infections",
            "stye or chalazion (lump on eyelid)",
            "need for prescription glasses or contact lenses",
            "routine eye examination"
        ],
        "hospital_id": "10002",
        "hospital_name": "Jagmohan Lal Eye and ENT Hospital",
        "hospital_type": "Specialized",
        "location": "Shahjahanpur",
        "address": "Kachcha Katra More Road, Sinzai, Shahjahanpur",
        "contact_number": "+91-95065-45521",
        "email": "manmohan_dr@yahoo.co.in",
            "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ]
        },
        "parent_id": "mg_10002",
        "chunk_count": 1
    }
},
{
    "id": "pg_10002-0",
    "metadata": {
        "provider_id": "pg_10002",
        "provider_type": "doctor",
        "doctor_name": "Dr. Poonam Gupta",
        "specialty": "ENT",
        "symptoms": [
            "ear pain or earache",
            "ear discharge (fluid from ear)",
            "hearing loss or difficulty hearing",
            "tinnitus (ringing or buzzing in ears)",
            "vertigo (dizziness, spinning sensation), balance problems",
            "ear infections (e.g., otitis media, swimmer's ear)",
            "blocked ears or feeling of fullness in ears",
            "nasal congestion or stuffy nose",
            "runny nose (rhinorrhea), persistent cold-like symptoms",
            "sinusitis symptoms (e.g., sinus pain, pressure, headache)",
            "nasal polyps",
            "frequent nosebleeds (epistaxis)",
            "allergies affecting nose or throat (allergic rhinitis)",
            "sore throat, pharyngitis, tonsillitis",
            "difficulty or pain in swallowing (dysphagia)",
            "hoarseness or changes in voice",
            "laryngitis",
            "snoring or suspected sleep apnea (related to airway obstruction)",
            "foreign body in ear, nose, or throat",
            "neck lumps or swelling (related to ENT structures)",
            "bad breath (halitosis) of throat/nasal origin"
        ],
        "hospital_id": "10002",
        "hospital_name": "Jagmohan Lal Eye and ENT Hospital",
        "hospital_type": "Specialized",
        "location": "Shahjahanpur",
        "address": "Kachcha Katra More Road, Sinzai, Shahjahanpur",
        "contact_number": "+91-95065-45521",
        "email": "manmohan_dr@yahoo.co.in",
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "15:00"
                },
                {
                    "start_time": "19:00",
                    "end_time": "21:00"
                }
            ]
        },
        "parent_id": "pg_10002",
        "chunk_count": 1
    }
},
{
    "id": "sb_diag_xray_20001-0",
    "metadata": {  
        "provider_id": "sb_diag_xray_20001",
        "provider_type": "lab",
        "service_id": "sb_diag_xray_20001",
        "service_name": "X-Ray Services",
        "specialty": "Radiology",
        "tests_offered": [
            {
                "test_name": "X-Ray Chest",
                "price_inr": 350
            },
            {
                "test_name": "X-Ray Abdomen Erect",
                "price_inr": 350
            },
            {
                "test_name": "X-Ray Abdomen Supine",
                "price_inr": 350
            },
            {
                "test_name": "X-Ray KUB",
                "price_inr": 350
            },
            {
                "test_name": "X-Ray Spine Single",
                "price_inr": 400
            },
            {
                "test_name": "X-Ray Skull",
                "price_inr": 400
            },
            {
                "test_name": "X-Ray PNS",
                "price_inr": 350
            },
            {
                "test_name": "X-Ray Mastoid",
                "price_inr": 350
            },
            {
                "test_name": "X-Ray Pelvis",
                "price_inr": 400
            }
        ],
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ]
        },
        "diagnostic_lab_id": "20001",
        "diagnostic_lab_name": "SB Diagnostics",
        "diagnostic_lab_type": "Diagnostic Center",
        "location": "Shahjahanpur",
        "address": "Sinzai, More, Kachcha Katra Rd, Shahjahanpur, Uttar Pradesh 242001",
        "contact_number": "+91-97214-86767",
        "email": "sbdaignostics.spn@gmail.com",
        "parent_id": "sb_diag_xray_20001",
        "chunk_count": 1
    }
},
{
    "id": "sb_diag_usg_20001-0",
    "metadata": {
        "provider_id": "sb_diag_usg_20001",
        "provider_type": "lab",
        "service_id": "sb_diag_usg_20001",
        "service_name": "Ultrasound Services",
        "specialty": "Radiology",
        "tests_offered": [
            {
                "test_name": "USG Neck",
                "price_inr": 1200
            },
            {
                "test_name": "USG Whole Abdomen KUB",
                "price_inr": 800
            },
            {
                "test_name": "USG OBS",
                "price_inr": 800
            },
            {
                "test_name": "USG TVS",
                "price_inr": 1200
            },
            {
                "test_name": "USG TIFFA Test",
                "price_inr": 2200
            },
            {
                "test_name": "USG Twins",
                "price_inr": 4000
            },
            {
                "test_name": "USG Color Doppler",
                "price_inr": 1500
            },
            {
                "test_name": "USG Color Doppler Twins",
                "price_inr": 2000
            },
            {
                "test_name": "USG BPP Score",
                "price_inr": 300
            },
            {
                "test_name": "USG Small Part",
                "price_inr": 1200
            },
            {
                "test_name": "USG B. Scan",
                "price_inr": 1200
            },
            {
                "test_name": "USG Follicular Study",
                "price_inr": 500
            }
        ],
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ]
        },
        "diagnostic_lab_id": "20001",
        "diagnostic_lab_name": "SB Diagnostics",
        "diagnostic_lab_type": "Diagnostic Center",
        "location": "Shahjahanpur",
        "address": "Sinzai, More, Kachcha Katra Rd, Shahjahanpur, Uttar Pradesh 242001",
        "contact_number": "+91-97214-86767",
        "email": "sbdaignostics.spn@gmail.com",
        "parent_id": "sb_diag_usg_20001",
        "chunk_count": 1
    }
},
{
    "id": "sb_diag_ctscan_20001-0",
    "metadata": {
        "provider_id": "sb_diag_ctscan_20001",
        "provider_type": "lab",
        "service_id": "sb_diag_ctscan_20001",
        "service_name": "CT Scan Services",
        "specialty": "Radiology",
        "tests_offered": [
            {
                "test_name": "NCCT Head",
                "price_inr": 1800
            },
            {
                "test_name": "CECT Head",
                "price_inr": 2000
            },
            {
                "test_name": "HRCT Thorax",
                "price_inr": 3500
            },
            {
                "test_name": "CECT Thorax",
                "price_inr": 4500
            },
            {
                "test_name": "CECT Face/Neck",
                "price_inr": 4000
            },
            {
                "test_name": "CECT Abdomen",
                "price_inr": 5000
            },
            {
                "test_name": "CECT Upper Abdomen",
                "price_inr": 4500
            },
            {
                "test_name": "CECT Pelvis",
                "price_inr": 4500
            },
            {
                "test_name": "NCCT KUB",
                "price_inr": 4000
            },
            {
                "test_name": "CECT KUB",
                "price_inr": 4500
            }
        ],
        "availability_schedule": { 
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ]
        },
        "diagnostic_lab_id": "20001",
        "diagnostic_lab_name": "SB Diagnostics",
        "diagnostic_lab_type": "Diagnostic Center",
        "location": "Shahjahanpur",
        "address": "Sinzai, More, Kachcha Katra Rd, Shahjahanpur, Uttar Pradesh 242001",
        "contact_number": "+91-97214-86767",
        "email": "sbdaignostics.spn@gmail.com",
        "parent_id": "sb_diag_ctscan_20001",
        "chunk_count": 1
    }
},
{
    "id": "sb_diag_mri_20001-0",
    "metadata": {
        "provider_id": "sb_diag_mri_20001",
        "provider_type": "lab",
        "service_id": "sb_diag_mri_20001",
        "service_name": "MRI Services",
        "specialty": "Radiology",
        "tests_offered": [
            {
                "test_name": "MRI Brain",
                "price_inr": 5000
            },
            {
                "test_name": "MRI Spine (Single Part)",
                "price_inr": 5500
            },
            {
                "test_name": "MRI Neck",
                "price_inr": 6000
            },
            {
                "test_name": "MRI Upper Abdomen",
                "price_inr": 6000
            },
            {
                "test_name": "MRI Lower Abdomen",
                "price_inr": 6000
            },
            {
                "test_name": "MRI Whole Abdomen",
                "price_inr": 8000
            },
            {
                "test_name": "MRCP",
                "price_inr": 6000
            },
            {
                "test_name": "MRI Thorax",
                "price_inr": 6000
            },
            {
                "test_name": "MRI Any Joint",
                "price_inr": 5500
            },
            {
                "test_name": "MR Angio/Veno",
                "price_inr": 2000
            }
        ],
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ]
        },
        "diagnostic_lab_id": "20001",
        "diagnostic_lab_name": "SB Diagnostics",
        "diagnostic_lab_type": "Diagnostic Center",
        "location": "Shahjahanpur",
        "address": "Sinzai, More, Kachcha Katra Rd, Shahjahanpur, Uttar Pradesh 242001",
        "contact_number": "+91-97214-86767",
        "email": "sbdaignostics.spn@gmail.com",
        "parent_id": "sb_diag_mri_20001",
        "chunk_count": 1
    }
},
{
    "id": "sb_diag_dental_20001-0",
    "metadata": {
        "provider_id": "sb_diag_dental_20001",
        "provider_type": "lab",
        "service_id": "sb_diag_dental_20001",
        "service_name": "Dental Services",
        "specialty": "Dentistry",
        "tests_offered": [
            {
                "test_name": "OPD",
                "price_inr": 500
            },
            {
                "test_name": "CBCT Single Quadrant",
                "price_inr": 2200
            },
            {
                "test_name": "CBCT Half",
                "price_inr": 3200
            },
            {
                "test_name": "CBCT Full",
                "price_inr": 4800
            },
            {
                "test_name": "CBCT Endo",
                "price_inr": 1500
            },
            {
                "test_name": "CBCT TMJ Single",
                "price_inr": 2000
            },
            {
                "test_name": "CBCT TMJ Double",
                "price_inr": 4000
            }
        ],
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ]
        },
        "diagnostic_lab_id": "20001",
        "diagnostic_lab_name": "SB Diagnostics",
        "diagnostic_lab_type": "Diagnostic Center",
        "location": "Shahjahanpur",
        "address": "Sinzai, More, Kachcha Katra Rd, Shahjahanpur, Uttar Pradesh 242001",
        "contact_number": "+91-97214-86767",
        "email": "sbdaignostics.spn@gmail.com",
        "parent_id": "sb_diag_dental_20001",
        "chunk_count": 1
    }
},
{
    "id": "sb_diag_path_20001-0",
    "metadata": {  
        "provider_id": "sb_diag_path_20001",
        "provider_type": "lab",
        "service_id": "sb_diag_path_20001",
        "service_name": "Pathology Services",
        "specialty": "Pathology",
        "tests_offered": [
            {
                "test_name": "Complete Blood Count (CBC)",
                "price_inr": 200
            },
            {
                "test_name": "Liver Function Test (LFT)",
                "price_inr": 500
            },
            {
                "test_name": "Kidney Function Test (KFT)",
                "price_inr": 500
            },
            {
                "test_name": "Lipid Profile",
                "price_inr": 600
            },
            {
                "test_name": "Blood Sugar Random (BSR)",
                "price_inr": 50
            },
            {
                "test_name": "Blood Sugar Fasting (FBS)",
                "price_inr": 50
            },
            {
                "test_name": "Blood Sugar Post Prandial (PPBS)",
                "price_inr": 50
            },
            {
                "test_name": "Uric Acid",
                "price_inr": 100
            },
            {
                "test_name": "Calcium",
                "price_inr": 220
            },
            {
                "test_name": "C-Reactive Protein (CRP)",
                "price_inr": 400
            }
        ],
        "availability_schedule": {
            "Monday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Tuesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Wednesday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Thursday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Friday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ],
            "Saturday": [
                {
                    "start_time": "10:00",
                    "end_time": "19:00"
                }
            ]
        },
        "diagnostic_lab_id": "20001",
        "diagnostic_lab_name": "SB Diagnostics",
        "diagnostic_lab_type": "Diagnostic Center",
        "location": "Shahjahanpur",
        "address": "Sinzai, More, Kachcha Katra Rd, Shahjahanpur, Uttar Pradesh 242001",
        "contact_number": "+91-97214-86767",
        "email": "sbdaignostics.spn@gmail.com",
        "parent_id": "sb_diag_path_20001",
        "chunk_count": 1
    }
}
]
}

Your task is to format responses based on the user query by filtering the HEALTHCARE_PROVIDERS_DATA. Only return information that matches the user's specific criteria such as location, specialty, symptoms, or provider type.

# Important Formatting Instructions:
1. Always convert all time values from 24-hour format to 12-hour format with AM/PM designation
   - Example: Convert "14:00" to "2:00 PM"
   - Example: Convert "09:30" to "9:30 AM"
   - For availability schedules, format both start_time and end_time in 12-hour format
2. When displaying doctor or service availability, clearly show the days and formatted time slots
3. Present all information in a clear, organized manner that is easy for users to understand
""" 