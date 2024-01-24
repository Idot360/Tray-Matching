# 
# Should try to avoid floats
# 
import pandas as pd


# Constants

CSV_FILE = "Lettertray_Combined.csv"
NAME_W = 0.8
GENDER_W = 0.9
SUBJECT_W = 0.7
FULL_W = 0.8
PARTIAL_W = 0.4
M_BREAKPOINT = 0.8
H_BREAKPOINT = 1.5
DIFF_BREAKPOINT = 0.25
SUBJECT_SHORT = {"la": "Language Arts", "math": "Mathematics", "cl": "Chinese", "ml": "Malay", "mi": "Man & ideas", 
                 "bio": "Science", "biology": "Science", "phy": "Science", "physics": "Science", "chem": "Science", 
                 "chemistry": "Science", "com": "Computing", "english": "Language Arts", "econs": "Economics"}
GENDER_SHORT = {"m": "Male", "f": "Female"}


# Comparision Function;
def compare(field: str, keywords: str, issubject: bool = False):
    """
    Parameters:
        field string; the field of the row to be compared
        keywords string; the part of the user input corresponding to the field
    Output:
        Weight float; the numerical value of the weight given to the field
                      based on how much the keywords match the field
    """
    if keywords == "":
        return 0
    weight = float()
    partial_match = False
    #print(keywords, field)
    for word in keywords.split(" "):
        partial_match = word.casefold() in field.casefold()
        weight += PARTIAL_W*int(partial_match)
    weight += FULL_W*int(keywords.casefold() == field.casefold() and not issubject)
    return weight


# Sorting Criteria
# Note: originally planned to write as a single input function
#       to pass to sort, shortening the code
def weight_assignment(name: str, gender: str, subject: str, given_name: str, given_gender: str, given_subject: str):
    """
    Parameters:
            name string; the name given in the specific row
            gender string; the gender given in the specific row
            subject string; the subject given in the specific row
            given_name string; the name provided by the user
            given_gender string; the gender provided by the user
            given_subject string; the subject provided by the user
    Output:
            Weight float; the numerical value of the weight given to the row
    """
    subject_key = given_subject.lower()
    if subject_key in SUBJECT_SHORT.keys():
        subject_key = SUBJECT_SHORT[subject_key]
    gender_key = given_gender.lower()
    if gender_key in GENDER_SHORT.keys():
        gender_key = GENDER_SHORT[gender_key]

    return ( NAME_W*compare(name, given_name) + 
             GENDER_W*compare(gender, gender_key) + 
             SUBJECT_W*compare(subject, subject_key, True) )


# ???
def main():
    """
    Accepts three input from the user for identification of the teacher:
        Name
        Gender
        Subject taught / Department
    # Assumes unknown if left blank
    
    Approximates to find the highest matching teacher stored in the database (not user-inputted)
    """
    given_name = input("please input the name of the teacher: ")
    given_gender = input("please input the gender of the teacher: ")
    given_subject = input("please input the subject/department the teacher teaches: ")
    tray_database = pd.read_csv(CSV_FILE)
    names = tray_database["Full Name"].fillna("Unknown")
    genders = tray_database["Gender"].fillna("Unknown")
    subjects = tray_database["Subject"].fillna("Unknown")

    weights = list()
    for i in range(len(names)):
        weights.append(weight_assignment(names[i], genders[i], subjects[i], given_name, given_gender, given_subject))
    tray_database["Weight"] = weights
    sorted_data = (tray_database.sort_values(by="Weight", ascending=False))

    certainty = ""
    if sorted_data.Weight.iloc[0] > H_BREAKPOINT:
        certainty = "high"
    elif sorted_data.Weight.iloc[1] > M_BREAKPOINT:
        certainty = "medium"
    else:
        certainty = "low"

    print(f"You searched for Mr/Ms/Mrs/Mdm/Dr {given_name}, of gender {given_gender}, who teaches the {given_subject} subject.")
    
    if sorted_data.Weight.iloc[0] == 0:
        print("No Results\n")
        return
    
    list_value = 0
    for i in range(5):
        if sorted_data.Weight.iloc[i] == 0:
            break
        if sorted_data.Weight.iloc[0] - sorted_data.Weight.iloc[i] < DIFF_BREAKPOINT:
            list_value += 1
        
    print(f"""Likely teachers and locations, with a {certainty} degree of certainty:\n{sorted_data.iloc[:list_value]}""")
    
    if sorted_data.Weight.iloc[0] - sorted_data.Weight.iloc[1] >= DIFF_BREAKPOINT:
        print(f"""
Most likely location: 
    {sorted_data.Location.iloc[0]}
    column {sorted_data.Coordinates.iloc[0].split(',')[0]}  row {sorted_data.Coordinates.iloc[0].split(',')[1]}.
""")
    
    input("Please press return to close")


if __name__ == "__main__":
    main()